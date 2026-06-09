# AI Sales & Support Assistant

AI-powered sales and customer support assistant for a technology store.

The application helps users ask questions about products, store policies, shipping, returns and warranties. It can also recommend products based on budget and use case.

## Features

- FastAPI backend
- Gradio chat UI
- LangChain RAG pipeline
- OpenAI LLM integration
- Chroma vector store
- Product recommendation support
- FAQ, policies and product catalog retrieval
- Conversation memory
- Summary of older chat history
- LangGraph-based routing

## Architecture

The following diagram illustrates the overall system architecture.

![Architecture Diagram](docs/architecture_diagram.png)

## Screenshots

### Product Recommendation

![UI Screenshot](docs/ui_screenshot.png)

### Conversation Memory

![Memory Screenshot](docs/memory_screenshot.png)

## Project Structure

```text
backend/
  app/
    core/
      settings.py
    data/
      faqs.txt
      policies.txt
      products.txt
    routers/
      chat.py
    schemas/
      chat_schema.py
    services/
      graph_service.py
      memory_service.py
      prompt_service.py
      rag_service.py
      vectorstore_service.py
    vectorstore/
      faqs_kb/
      policies_kb/
      products_kb/
    main.py

frontend/
  config.py
  gradio_app.py
  
docs/
  architecture_diagram.png
  memory_screenshot.png
  project_report.md
  swagger_screenshot.png
  test_cases.md
  ui_screenshot.png

.gitignore
LICENSE
README.md
requirements.txt
```

## Installation

Create and activate a virtual environment:
```cmd
py -3.12 -m venv venv
venv\Scripts\activate
```

Install dependencies:
```cmd
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run Backend
```cmd
uvicorn backend.app.main:app --reload
```

Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

## Run Frontend

In a second terminal:

```cmd
python frontend/gradio_app.py
```

Open:

```
http://127.0.0.1:7860
```

## Example Questions

```text
Θέλω laptop για gaming μέχρι 900€
Τι μου πρότεινες τελικά;
Ποια είναι η πολιτική επιστροφών;
Υποστηρίζετε Box Now;
Έχετε monitor για design;
```

## Testing

Manual test cases are available in:

```text
docs/test_cases.md
```

## GenAI Techniques Used

### Prompt Engineering

The assistant uses structured prompts to answer as a sales and support assistant for a technology store.

### Retrieval-Augmented Generation

The application loads business knowledge from text files, splits it into chunks, creates embeddings and stores them in Chroma. The RAG pipeline uses chunk size 700, overlap 120 and retrieves the top 5 most relevant chunks.

### Conversation Memory

The system keeps recent chat messages and summarizes older messages, allowing follow-up questions.

### LangGraph Routing

LangGraph is used to route user questions to the correct knowledge base:
- products
- policies
- FAQs

## Notes

The application was developed as an educational project for the AI for Developers program.

The project demonstrates the integration of FastAPI, LangChain, LangGraph, Chroma, OpenAI models, Retrieval-Augmented Generation (RAG) and conversation memory in a complete end-to-end AI application.

## License

This project is publicly visible for portfolio, review and educational demonstration purposes only.

You may view and study the source code, but you may not copy, modify, redistribute, republish, submit, or present this work as your own without explicit permission from the author.

© 2026 Alexandros Paschalis Chatzis. All rights reserved.
