"""
Core Retrieval-Augmented Generation (RAG) orchestration service.

This module coordinates the complete RAG workflow:

1. Builds conversation context from chat history.
2. Selects the appropriate knowledge-base route.
3. Rewrites context-dependent follow-up questions into standalone retrieval queries.
4. Retrieves relevant documents using the selected hybrid retriever (BM25 + Chroma).
5. Builds a source-labeled context for grounded generation.
6. Generates the final answer using the RAG prompt and GPT-4o-mini.
7. Returns the answer, selected route, retrieved context and source previews.
"""

from langchain_openai import ChatOpenAI

from backend.app.core.settings import CHAT_MODEL
from backend.app.services.memory_service import build_conversation_context
from backend.app.services.prompt_service import RAG_PROMPT
from backend.app.services.vectorstore_service import get_retriever

from backend.app.services.query_rewrite_service import rewrite_query

# LLM used for final RAG answer generation
llm = ChatOpenAI(
    model = CHAT_MODEL,
    temperature=0
)

def route_question(question: str) -> str:
    """
    Route a user question to the most appropriate knowledge base.

    This function acts as a fallback routing mechanism when a route is not explicitly provided by the LangGraph router.

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
        "τεχνικη υποστηριξη", "κατάστημα", "καταστημα",
    ]

    # Policies are checked first because questions may contain both a product term and a policy term, e.g. "εγγύηση laptop"
    if any(keyword in q for keyword in policy_keywords):
        return "policies"

    if any(keyword in q for keyword in product_keywords):
        return "products"

    if any(keyword in q for keyword in faq_keywords):
        return "faqs"

    # FAQs are used as the default fallback route.
    return "faqs"


def get_last_route_from_history(history: list[dict]) -> str | None:
    """
    Infer the latest meaningful route from previous user messages.

    This is used for generic follow-up questions that do not contain enough keywords to determine the route directly.

    Args:
        history: Previous chat messages.

    Returns:
        The latest non-FAQ route found in user history, or None.
    """

    # Search from the most recent message backwards.
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
        2. Use the LangGraph-selected route when available.
        3. Fall back to keyword/history-based routing when necessary.
        4. Rewrite follow-up questions into standalone retrieval queries.
        5. Retrieve relevant chunks using hybrid BM25 + Chroma retrieval.
        6. Build source-labeled context from retrieved documents.
        7. Generate a grounded answer using the RAG prompt.
        8. Return the answer, route, context and source previews.

    Args:
        question: Current user question.
        history: Previous chat messages.
        forced_route: Optional route selected by LangGraph.

    Returns:
        Dictionary containing:
        - answer: Generated assistant response.
        - route: Selected knowledge-base route.
        - context: Full retrieved context used for generation/evaluation.
        - sources: Short previews of the retrieved documents.
    """

    history = history or []

    # Build compact conversation memory.
    # Older messages may be summarized while recent ones are preserved.
    conversation_context = build_conversation_context(history)

    # This version of the question is used for the final answer generation.
    # It preserves both the current question and the conversation memory.
    question_with_context = f"""
Conversation context:
{conversation_context}

Current question:
{question}
"""

    # Use LangGraph route when available.
    if forced_route:
        route = forced_route
    else:       
        # Fallback keyword-based routing.
        route = route_question(question)

        # Generic follow-up questions may fall back to "faqs".
        # In that case, recover the previous meaningful route from history.
        if route == "faqs":
            previous_route = get_last_route_from_history(history)

            if previous_route:
                route = previous_route

    # When conversation history exists, rewrite context-dependent follow-up questions before searching the knowledge base.
    if history:
        retrieval_query = rewrite_query(
            question=question,
            conversation_context=conversation_context,
        )
    else:
        retrieval_query = question

    # Select the appropriate retriever for the chosen knowledge base.
    retriever = get_retriever(route)

    # Retrieve relevant chunks using BM25 + Chroma hybrid retrieval.
    retrieved_docs = retriever.invoke(retrieval_query)

    # Label each retrieved document so the LLM can generate citations such as [Source 1], [Source 2], etc.
    context = "\n\n".join(
        f"[Source {index}]\n{doc.page_content}"
        for index, doc in enumerate(retrieved_docs, start=1)
    )

    # Combine the RAG prompt with the LLM.
    chain = RAG_PROMPT | llm

    # Generate the final grounded answer.
    response = chain.invoke(
        {
            "route": route,
            "context": context,
            "question": question_with_context,
        }
    )

    # Return both user-facing data and the full context required by the automated evaluation pipeline.
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