from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from backend.app.core.settings import (
    CHAT_MODEL,
    KEEP_RECENT_MESSAGES
)

from backend.app.services.prompt_service import SUMMARY_PROMPT

load_dotenv()

llm = ChatOpenAI(
    model=CHAT_MODEL,
    temperature=0,
)


def format_history_messages(history: list[dict]) -> str:
    """
    Format chat history messages into readable text.

    Args:
        history: List of chat messages with role and content.

    Returns:
        Formatted conversation history.
    """

    return "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in history
    )


def build_conversation_context(history: list[dict]) -> str:
    """
    Build conversation context for memory-aware RAG.
    Older messages are summarized, while the latest messages are kept unchanged.

    Args:
        history: Full chat history.

    Returns:
        Conversation context text.
    """

    if not history:
        return "No previous conversation."
    
    if len(history) <= KEEP_RECENT_MESSAGES:
        return format_history_messages(history)
    
    old_messages = history[:-KEEP_RECENT_MESSAGES]
    recent_messages = history[-KEEP_RECENT_MESSAGES:]

    old_history_text = format_history_messages(old_messages)
    recent_history_text = format_history_messages(recent_messages)

    # Summarize older messages to keep context compact
    chain = SUMMARY_PROMPT | llm

    summary = chain.invoke(
        {
            "old_history": old_history_text
        }
    )

    return f"""
Conversation summary:
{summary.content}

Recent messages:
{recent_history_text}
"""