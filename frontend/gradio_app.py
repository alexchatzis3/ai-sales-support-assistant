"""
AI Sales & Support Assistant — Gradio UI
=======================================

Gradio web interface for the AI Sales & Support Assistant.

The UI is responsible for:
- collecting user messages
- keeping visible chat history
- keeping backend-compatible conversation history
- sending requests to the FastAPI /chat endpoint
- displaying the generated answer
- displaying the selected knowledge-base route
- displaying retrieved source previews

The frontend does not execute the RAG pipeline itself.
All routing, memory, query rewriting, retrieval and answer generation are handled by the FastAPI backend.
"""

from __future__ import annotations

import requests
import gradio as gr
from config import API_URL


def call_chat_api(message: str, history: list) -> dict:
    """
    Send the current user message and conversation history to FastAPI.

    Args:
        message: The user's current message.
        history: Previous conversation history in OpenAI-style format.

    Returns:
        Parsed JSON response returned by the backend.

    Raises:
        requests.RequestException: 
            If the HTTP request fails or the backend returns
            a non-success status code.
    """

    # Send both the current user message and previous conversation history.
    # The request body matches the backend ChatRequest schema:
    #
    # {
    #     "message": str,
    #     "history": list[ChatMessage]
    # }
    response = requests.post(
        API_URL,
        json={
            "message": message,
            "history": history,
        },
        timeout=60,
    )

    # Raise an exception for non-success status codes.
    response.raise_for_status()

    # FastAPI returns JSON containing:
    # answer, route and retrieved sources.
    return response.json()


def format_sources(sources: list[dict]) -> str:
    """
    Convert retrieved source information into Markdown for the UI.

    Args:
        sources: List of retrieved source dictionaries returned by FastAPI.

    Returns:
        Markdown-formatted source information.
    """

    if not sources:
        return "No sources retrieved."

    markdown = "### Retrieved Sources\n\n"

    # Number the sources starting from 1 so that the UI presentation matches the [Source N] convention used by the RAG pipeline.
    for index, source in enumerate(sources, start=1):
        source_name = source.get("source", "unknown")
        preview = source.get("preview", "")

        markdown += f"**Source {index}:** `{source_name}`\n\n"
        markdown += f"> {preview}\n\n"

    return markdown


def respond(
    message: str,
    chatbot_history: list,
    api_history: list,
):
    """
    Handle one complete user interaction from the Gradio UI.

    The function:
    1. validates the user message
    2. sends the message and API history to FastAPI
    3. reads the answer, route and sources
    4. updates the visible chat
    5. updates the backend-compatible conversation history
    6. updates the route and source panels

    Args:
        message: Current message entered by the user.
        chatbot_history: History displayed by the Gradio Chatbot.
        api_history: Conversation history sent to the FastAPI backend.

    Returns:
        Updated textbox value, visible chat history, API history, selected route display and retrieved source display.
    """

    # Ignore empty or whitespace-only messages.
    # This avoids unnecessary calls to the backend.
    if not message or not message.strip():
        return (
            "",
            chatbot_history,
            api_history,
            "Route: -",
            "No sources retrieved.",
        )

    try:
        # Send only the previous conversation history together with the new current message. 
        # The current message is added to api_history after the backend response is received.
        result = call_chat_api(
            message=message,
            history=api_history,
        )

        # Extract the fields defined by the backend ChatResponse schema.
        answer = result.get("answer", "No answer returned.")
        route = result.get("route", "unknown")
        sources = result.get("sources", [])

        # Update the visible Gradio conversation.
        # These messages are displayed directly inside gr.Chatbot.
        chatbot_history.append(
            {
                "role": "user",
                "content": message,
            }
        )
        chatbot_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        # Keep a separate backend-compatible conversation history.
        #
        # This state is sent with the next request so that the backend can use conversation memory, previous routing intent and query rewriting for follow-up questions.
        api_history.append(
            {
                "role": "user",
                "content": message,
            }
        )
        api_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        # Prepare metadata panels shown next to the conversation.
        route_markdown = f"### Selected Route\n\n`{route}`"
        sources_markdown = format_sources(sources)

        # Gradio maps these return values to the outputs configured in msg.submit() and send_btn.click().
        return (
            "",                 # Clear the message textbox
            chatbot_history,    # Updated visible conversation
            api_history,        # Updated backend memory state
            route_markdown,     # Selected knowledge-base route
            sources_markdown,   # Retrieved document previews
        )

    except requests.RequestException as exc:
        # Handle connection errors, timeouts and backend HTTP errors without crashing the Gradio application.
        error_message = (
            "Δεν μπόρεσα να συνδεθώ με το backend. "
            "Βεβαιώσου ότι το FastAPI backend είναι διαθέσιμο."
        )

        # Display the failed interaction in the visible chat.
        chatbot_history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        chatbot_history.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )

        # Store the interaction in API history as well so both frontend state representations remain synchronized.
        api_history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        api_history.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )

        return (
            "",
            chatbot_history,
            api_history,
            "Route: error",
            f"Backend error: `{exc}`",
        )


def clear_chat():
    """
    Reset the complete frontend conversation state.

    Returns:
        Empty visible chat history, empty backend conversation history, default route text and default source text.
    """

    # Clearing both histories is important:
    # otherwise the chat could appear empty while the backend would still receive previous conversation context.
    return (
        [],
        [],
        "Route: -",
        "No sources retrieved.",
    )


with gr.Blocks(title="AI Sales & Support Assistant") as app:

    # Hidden state used only for backend conversation memory.
    api_history = gr.State([])

    gr.Markdown(
        """
# AI Sales & Support Assistant

Ask questions about products, store policies, shipping, returns or request product recommendations.

**Architecture:** Gradio UI → FastAPI → LangGraph Routing → Hybrid RAG (BM25 + Chroma) → OpenAI
"""
    )

    # Main two-column application layout.
    with gr.Row():

        # Left column: conversation and user controls.
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversation",
                height=450,
            )

            with gr.Row():
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Example: Θέλω laptop για gaming μέχρι 1900€",
                    scale=4,
                )

                send_btn = gr.Button(
                    "Send",
                    variant="primary",
                    scale=1,
                )

            clear_btn = gr.Button("Clear Chat")

        # Right column: routing information, retrieved sources and example user questions.
        with gr.Column(scale=2):
            route_output = gr.Markdown("Route: -")
            sources_output = gr.Markdown("No sources retrieved.")

            gr.Markdown(
    """
### Example Questions

**Product Recommendation**
- Θέλω laptop για gaming μέχρι 900€
- Θέλω laptop για gaming μέχρι 1900€
- Έχετε monitor για design;

**Product Comparison**
- Σύγκρινε GamePro 15 με NitroPlay 15
- Σύγκρινε ProColor 32 με StudioColor 27

**Conversation Memory**
- Τι μου πρότεινες τελικά;

**Store Policies & FAQs**
- Πόσα χρόνια εγγύηση έχουν τα laptops;
- Σε πόσες δόσεις μπορώ να πληρώσω;
- Υπάρχει τεχνική υποστήριξη;
- Υποστηρίζετε Box Now;

**Out-of-scope Handling**
- Ποιος κέρδισε το Champions League;
"""
)


    # Event wiring
    # Pressing Enter inside the textbox executes respond().
    msg.submit(
        respond,
        inputs=[msg, chatbot, api_history],
        outputs=[
            msg,
            chatbot,
            api_history,
            route_output,
            sources_output,
        ],
    )

    # Clicking Send executes the exact same workflow.
    send_btn.click(
        respond,
        inputs=[msg, chatbot, api_history],
        outputs=[
            msg,
            chatbot,
            api_history,
            route_output,
            sources_output,
        ],
    )

    # Reset both visible and hidden conversation state.
    clear_btn.click(
        clear_chat,
        inputs=[],
        outputs=[
            chatbot,
            api_history,
            route_output,
            sources_output,
        ],
    )


if __name__ == "__main__":
    # Start the Gradio interface locally.
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )