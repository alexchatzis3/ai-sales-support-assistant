# AI Sales & Support Assistant

## 1. Project Overview

The AI Sales & Support Assistant is a Generative AI application designed for technology stores.

The assistant helps customers:

* Find suitable products based on budget and use case
* Ask questions about store policies
* Learn about shipping and payment methods
* Receive customer support information
* Continue multi-turn conversations using memory
* Compare products side-by-side
* Display retrieved sources for answer transparency

The project combines Retrieval-Augmented Generation (RAG), conversation memory and workflow orchestration through LangGraph.

---

## 2. Objectives

The main objectives of the project are:

* Build an AI-powered customer support assistant
* Implement a RAG pipeline using company knowledge
* Support product recommendations
* Maintain conversation context across multiple messages
* Demonstrate LangGraph routing capabilities
* Provide a user-friendly chat interface

---

## 3. Technologies Used

### Backend

* Python
* FastAPI
* LangChain
* LangGraph

### Frontend

* Gradio

### AI Components

* OpenAI GPT-4o-mini
* OpenAI Embeddings (text-embedding-3-small)
* Chroma Vector Store
* BM25 Retrieval

---

## 4. Knowledge Base

The application uses three separate knowledge bases:

### Products

Contains:

* Product catalog
* Product specifications
* Product pricing
* Product categories

### Policies

Contains:

* Return policy
* Warranty policy
* Shipping policy
* Payment methods

### FAQs

Contains:

* Store information
* Customer support information
* Order questions
* General assistance

---

## 5. Architecture

The following diagram illustrates the overall architecture of the AI Sales & Support Assistant.

![Architecture Diagram](architecture_diagram.png)

### Workflow Description
1. The user interacts with the Gradio interface.
2. FastAPI receives the request through the /chat endpoint.
3. LangGraph routes the question to the most appropriate knowledge base:
    - Products
    - Policies
    - FAQs
4. The RAG Service orchestrates retrieval and answer generation.
5. Memory Service provides conversation context and summaries.
6. Vectorstore Service performs hybrid retrieval using Chroma vector search and BM25 keyword retrieval.
7. OpenAI GPT-4o-mini generates the final response.
8. The answer is returned to the user interface.

---

## 6. System Components

The application is organized using separation of concerns principles.

### FastAPI Layer
Handles HTTP requests and responses through the `/chat` endpoint.

### LangGraph Router
Classifies user questions and selects the most relevant knowledge base.

### Memory Service
Maintains conversation history and summarizes older messages.

### Vectorstore Service
Loads documents, creates embeddings and retrieves relevant information from Chroma.

### RAG Service
Combines retrieval results, memory context and prompts to generate responses.

### Gradio Interface
Provides a simple chat interface for end users.

---

## 7. RAG Pipeline

The Retrieval-Augmented Generation pipeline performs the following steps:

1. Load business knowledge from text files
2. Split documents into chunks
3. Generate embeddings
4. Store vectors in Chroma
5. Perform hybrid retrieval:
   - Chroma vector similarity search
   - BM25 keyword retrieval
6. Combine retrieval results using an Ensemble Retriever
7. Generate grounded responses using GPT-4o-mini

---

## 8. Conversation Memory

The assistant maintains conversation context.

Features:

* Stores recent messages
* Summarizes older messages
* Supports follow-up questions
* Remembers recommendations and preferences

---

## 9. LangGraph Workflow

LangGraph is used to route user questions to the appropriate knowledge base.

Available routes:

* Products
* Policies
* FAQs

This improves retrieval quality and reduces irrelevant results.

---

## 10. GenAI Techniques

The project demonstrates several Generative AI concepts:

### Prompt Engineering
Custom prompts guide the assistant's behavior and reduce hallucinations.

### Retrieval-Augmented Generation (RAG)

The assistant retrieves relevant business knowledge before generating a response.

### Embeddings

OpenAI embeddings are used to transform text into vector representations.

### Hybrid Retrieval

The system combines two retrieval strategies:

- Chroma vector similarity search for semantic retrieval
- BM25 keyword retrieval for exact term matching

The results are combined using an ensemble retriever, improving retrieval robustness.

### Vector Search

Chroma performs similarity search to find relevant information.

### Conversation Memory

Recent messages are preserved while older messages are summarized.

### LangGraph Routing

Questions are routed to specialized knowledge bases before retrieval.

### Source Transparency

The assistant exposes retrieved source previews and the selected retrieval route. This improves explainability and allows users to understand how answers were generated.

### Product Comparison

The assistant can compare multiple products using retrieved catalog information and present differences in a structured format.

User:

"Compare GamePro 15 and NitroPlay 15"

Assistant:

Retrieves product specifications and presents a structured comparison using only available catalog information.

---

## 11. Example Use Cases

### Product Recommendation

User:

"Θέλω laptop για gaming μέχρι 900€"

Assistant:

Recommends suitable gaming laptops and explains the recommendation.

### Policy Question

User:

"Ποια είναι η πολιτική επιστροφών;"

Assistant:

Retrieves and explains the return policy.

### Follow-up Question

User:

"Τι μου πρότεινες τελικά;"

Assistant:

Uses conversation memory and recalls the previous recommendation.

---

## 12. Results

### Gradio User Interface

![Gradio UI](ui_screenshot.png)

The assistant successfully recommends products based on user requirements and budget constraints.

### Conversation Memory

![Conversation Memory](memory_screenshot.png)

The assistant preserves conversation context and can answer follow-up questions without requiring the user to repeat previous requirements.


### FastAPI Swagger Documentation

![Swagger UI](swagger_screenshot.png)

The API exposes a `/chat` endpoint that returns the generated answer, selected route and retrieved sources.

---

## 13. Future Improvements

Potential future enhancements include:

- Database integration
- User authentication
- Order tracking tools
- Multi-language support
- LLM-based reranking
- Multi-agent architecture
- Integration with real-time inventory systems

---

## 14. Conclusion

The AI Sales & Support Assistant demonstrates how modern Generative AI technologies can be combined to create a practical customer support solution.

The project integrates RAG, conversation memory, vector databases, workflow orchestration and LLMs into a complete end-to-end application.
