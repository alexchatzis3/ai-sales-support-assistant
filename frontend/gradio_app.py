"""
AI Sales & Support Assistant — Gradio UI
=======================================

Gradio web interface for the AI Sales & Support Assistant.

The UI sends user messages and conversation history to the FastAPI backend
and displays:
- the assistant answer
- the selected RAG route
- the retrieved source previews
"""

from __future__ import annotations

import requests
import gradio as gr
from config import API_URL

API_URL = API_URL


def call_chat_api(message: str, history: list) -> dict:
    """
    Send a user message and conversation history to the FastAPI chat endpoint.

    Args:
        message: The user's current message.
        history: Previous conversation history in OpenAI-style format.

    Returns:
        API response as a dictionary.

    Raises:
        requests.RequestException: If the backend request fails.
    """

    # Send both the current user message and previous conversation history
    response = requests.post(
        API_URL,
        json={
            "message": message,
            "history": history,
        },
        timeout=60,
    )

    # Raise an exception for non-success status codes
    response.raise_for_status()

    return response.json()


def format_sources(sources: list[dict]) -> str:
    """
    Format retrieved sources for display in the UI.

    Args:
        sources: List of retrieved source dictionaries.

    Returns:
        Markdown-formatted source information.
    """

    if not sources:
        return "No sources retrieved."

    markdown = "### Retrieved Sources\n\n"

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
    Handle a user message from the Gradio UI.

    Args:
        message: The message typed by the user.
        chatbot_history: Visible Gradio chatbot history.
        api_history: Backend-compatible conversation history.

    Returns:
        Updated textbox, chatbot history, API history, route and sources.
    """

    # Ignore empty messages
    if not message or not message.strip():
        return (
            "",
            chatbot_history,
            api_history,
            "Route: -",
            "No sources retrieved.",
        )

    try:
        # Send backend-compatible history to FastAPI
        result = call_chat_api(
            message=message,
            history=api_history,
        )

        answer = result.get("answer", "No answer returned.")
        route = result.get("route", "unknown")
        sources = result.get("sources", [])

        # Update visible chat history
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

        # Update backend-compatible memory history
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

        route_markdown = f"### Selected Route\n\n`{route}`"
        sources_markdown = format_sources(sources)

        return (
            "",
            chatbot_history,
            api_history,
            route_markdown,
            sources_markdown,
        )

    except requests.RequestException as exc:
        # Show backend/API errors in the chat
        error_message = (
            "Δεν μπόρεσα να συνδεθώ με το backend. "
            "Βεβαιώσου ότι το FastAPI τρέχει στο http://127.0.0.1:8000."
        )

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
    Clear the visible chat, API history and metadata panels.

    Returns:
        Empty visible chat, empty API history and default metadata text.
    """

    return (
        [],
        [],
        "Route: -",
        "No sources retrieved.",
    )


with gr.Blocks(title="AI Sales & Support Assistant") as app:
    # Backend-compatible memory state
    api_history = gr.State([])

    gr.Markdown(
        """
# AI Sales & Support Assistant

Ask questions about products, store policies, shipping, returns or request product recommendations.

**Architecture:** Gradio UI → FastAPI Backend → LangChain RAG → OpenAI
"""
    )

    with gr.Row():
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
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )