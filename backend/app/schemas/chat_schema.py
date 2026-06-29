from pydantic import BaseModel, Field

class Source(BaseModel):
    """
    Retrieved source preview used by the RAG pipeline.
    """

    source: str = Field(
        ...,
        description="The source file used during retrieval.",
    )

    preview: str = Field(
        ...,
        description="Short preview of the retrieved chunk.",
    )

class ChatMessage(BaseModel):
    """
    Single chat history message.
    """

    role: str
    content: str

class ChatRequest(BaseModel):
    """
    Request schema for user chat messages.
    """

    message: str = Field(
        ...,
        min_length=1,
        description="The user's question or message",
        examples=["Θέλω laptop για gaming μέχρι 900€"],
    )

    history: list[ChatMessage] = Field(default_factory=list)



class ChatResponse(BaseModel):
    """
    Response schema returned by the chat endpoint.
    """

    answer: str = Field(
        ...,
        description="The AI-generated answer.",
    )

    route: str = Field(
        ...,
        description="The selected knowledge base route.",
    )

    sources: list[Source] = Field(
        ...,
        description="Retrieved document snippets used to answer the question.",
    )