from fastapi import APIRouter, HTTPException

from backend.app.schemas.chat_schema import ChatRequest, ChatResponse
from backend.app.services.rag_service import ask_rag

from backend.app.services.graph_service import get_route

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def normalize_history(history: list) -> list[dict]:
    """
    Convert UI chat history into OpenAI-style message dictionaries.

    Args:
        history: Chat history coming from the UI.

    Returns:
        Normalized history as a list of dictionaries.
    """

    normalized_history = []

    for item in history:
        # Pydantic model format
        if hasattr(item, "model_dump"):
            normalized_history.append(item.model_dump())

        # Dictionary format
        elif isinstance(item, dict):
            normalized_history.append(item)

        # Gradio pair format: [user_message, assistant_message]
        elif isinstance(item, list) and len(item) == 2:
            user_message, assistant_message = item

            normalized_history.append(
                {"role": "user", "content": user_message}
            )
            normalized_history.append(
                {"role": "assistant", "content": assistant_message}
            )

    return normalized_history

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Process a user message using the RAG pipeline.

    The endpoint receives a user question, normalizes chat history,
    routes the question to the proper knowledge base, retrieves relevant
    context and returns an AI answer.
    """

    try:
        # Convert UI history into a consistent internal format
        normalized_history = normalize_history(request.history)

        # Use LangGraph to determine the selected knowledge base
        selected_route = get_route(request.message)

        # For generic follow-up messages, allow rag_service to infer the route from history
        if selected_route == "faqs" and normalized_history:
            selected_route = None

        # Execute the RAG workflow
        result = ask_rag(
            question=request.message,
            history=normalized_history,
            forced_route=selected_route
        )

        return ChatResponse(
            answer=result["answer"],
            route=result["route"],
            sources=result["sources"],
        )

    except Exception as exc:
        # Log internal error for debugging
        print("CHAT ERROR:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Chat service failed: {str(exc)}",
        )