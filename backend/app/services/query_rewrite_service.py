"""
Query rewriting service for conversation-aware retrieval.

This service converts follow-up user questions into standalone retrieval queries using the available conversation context.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.app.core.settings import CHAT_MODEL

llm = ChatOpenAI(
    model=CHAT_MODEL,
    temperature=0,
)


QUERY_REWRITE_PROMPT = ChatPromptTemplate.from_template("""
Rewrite the current user question into a standalone retrieval query.

Use the conversation context only when necessary to resolve references
or missing information from follow-up questions.

Rules:
- Preserve the user's original intent.
- Preserve product names exactly.
- Preserve prices and budget constraints.
- Preserve product categories and use cases.
- Do not invent information.
- Do not answer the question.
- Return only the rewritten query.
- If the current question is already standalone, return it unchanged.

Conversation context:
{conversation_context}

Current question:
{question}

Standalone retrieval query:
""")


def rewrite_query(
    question: str,
    conversation_context: str,
) -> str:
    """
    Rewrite a user question into a standalone retrieval query.

    Args:
        question: Current user question.
        conversation_context: Conversation memory built from chat history.

    Returns:
        Standalone query suitable for document retrieval.
    """

    if not conversation_context:
        return question

    chain = QUERY_REWRITE_PROMPT | llm

    response = chain.invoke(
        {
            "question": question,
            "conversation_context": conversation_context,
        }
    )

    rewritten_query = response.content.strip()

    return rewritten_query or question