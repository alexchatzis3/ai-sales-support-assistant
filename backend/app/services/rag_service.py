"""
The `rag_service.py` file is the core service responsible for executing the Retrieval Augmented Generation (RAG) workflow.

First, it builds conversation context from chat history using the memory service. This allows the assistant to handle follow-up questions and maintain context across multiple interactions.

Next, it determines the appropriate knowledge base route, either from the LangGraph router or through fallback keyword-based routing.

Based on the selected route, it retrieves the corresponding retriever from the vector store service and performs hybrid retrieval using Chroma and BM25, to obtain the most relevant document chunks.

The retrieved context, together with the user's question and conversation history, is then passed to the RAG prompt.

Finally, GPT-4o-mini generates a grounded response using the retrieved information, and the service returns the answer, selected route, and source references.
"""

from langchain_openai import ChatOpenAI

from backend.app.core.settings import CHAT_MODEL
from backend.app.services.memory_service import build_conversation_context
from backend.app.services.prompt_service import RAG_PROMPT
from backend.app.services.vectorstore_service import get_retriever

from backend.app.services.query_rewrite_service import rewrite_query

llm = ChatOpenAI(
    model = CHAT_MODEL,
    temperature=0
)

def route_question(question: str) -> str:
    """
    Route a user question to the most appropriate knowledge base.

    Args:
        question: User question.
    Returns:
        The selected route: "products", "policies", or "faqs".
    """

    q = question.lower()

    product_keywords = [
        "laptop", "desktop", "monitor", "smartphone", "tablet",
        "mouse", "keyboard", "headset", "printer", "gaming",
        "streaming", "smart home", "προϊόν", "προϊόντα",
        "αγορά", "πρότεινε", "προτείνεις", "προτεινες",
        "σύγκρινε", "συγκρινε", "τιμή", "budget", "μέχρι", "κάτω από", "δουλειά", "σπουδές", "rtx", "gpu", "cpu", "ram",
        "ssd", "οθόνη", "καμερα", "μπαταρία", "setup",
    ]

    policy_keywords = [
        "επιστροφή", "επιστροφές", "εγγύηση", "εγγυηση",
        "πολιτική", "πολιτικη", "ακύρωση", "ακυρωση",
        "πληρωμή", "πληρωμη", "αντικαταβολή", "αντικαταβολη",
        "δόσεις", "δοσεις", "δεδομένα", "προσωπικά δεδομένα",
        "αποστολή", "αποστολη", "box now", "courier",
    ]

    faq_keywords = [
        "ώρες", "ωρες", "λειτουργίας", "λειτουργιας",
        "τηλέφωνο", "τηλεφωνο", "παραγγελία", "παραγγελια",
        "παραλαβή", "παραλαβη", "τεχνική υποστήριξη",
        "τεχνικη υποστηριξη", "κατάστημα", "καταστημα", "δόσεις", "δοσεις",
    ]

    if any(keyword in q for keyword in policy_keywords):
        return "policies"

    if any(keyword in q for keyword in product_keywords):
        return "products"

    if any(keyword in q for keyword in faq_keywords):
        return "faqs"

    # Default route
    return "faqs"


def get_last_route_from_history(history: list[dict]) -> str | None:
    """
    Infer the latest meaningful route from previous user messages.

    This helps with follow-up questions.

    Args:
        history: Previous chat messages.

    Returns:
        The last detected route or None.
    """

    for message in reversed(history):
        if message.get("role") != "user":
            continue

        route = route_question(message.get("content", ""))

        # Ignore the default FAQ route when looking for previous intent
        if route != "faqs":
            return route

    return None


def ask_rag(
    question: str,
    history: list[dict] | None = None,
    forced_route: str | None = None,
) -> dict:
    """
    Execute the complete RAG workflow.

    Steps:
        1. Build conversation context from chat history.
        2. Use the graph-selected route or fallback routing.
        3. Retrieve relevant chunks from Chroma.
        4. Generate an answer using the retrieved context.

    Args:
        question: Current user question.
        history: Previous chat messages.
        forced_route: Optional route selected by LangGraph.

    Returns:
        Dictionary containing the answer, selected route, and source previews.
    """

    history = history or []

    # Build memory context using summary 
    conversation_context = build_conversation_context(history)

    # Add conversation memory to the current question
    retrieval_question = f"""
Conversation context:
{conversation_context}

Current question:
{question}
"""

    # Use LangGraph route when available
    if forced_route:
        route = forced_route
    else:       
        route = route_question(question)

        # For follow-up questions 
        if route == "faqs":
            previous_route = get_last_route_from_history(history)

            if previous_route:
                route = previous_route

    # Rewrite follow-up questions into standalone retrieval queries
    if history:
        retrieval_query = rewrite_query(
            question=question,
            conversation_context=conversation_context,
        )
    else:
        retrieval_query = question

    # Select the appropriate retriever
    retriever = get_retriever(route)

    # Retrieve relevant chunks using both history and current question
    retrieved_docs = retriever.invoke(retrieval_query)

    # Build RAG context from retrieved chunks
    context = "\n\n".join(
        f"[Source {index}]\n{doc.page_content}"
        for index, doc in enumerate(retrieved_docs, start=1)
    )

    # Generate final answer
    chain = RAG_PROMPT | llm

    response = chain.invoke(
        {
            "route": route,
            "context": context,
            "question": retrieval_question,
        }
    )

    return {
        "answer": response.content,
        "route": route,
        "context": context,
        "sources": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "preview": doc.page_content[:120].replace("\n", " "),
            }
            for doc in retrieved_docs
        ],
    }