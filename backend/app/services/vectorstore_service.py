from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.retrievers import BM25Retriever 
from langchain_classic.retrievers import EnsembleRetriever



from backend.app.core.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_DIR,
    EMBED_MODEL,
    TOP_K_RESULTS,
    VECTORSTORE_DIR,
)

load_dotenv()

embedder = OpenAIEmbeddings(model=EMBED_MODEL)

def build_retriever(file_name: str, collection_name: str):
    """
    Build a retriever for a specific knowledge base file.

    Args:
        file_name: Name of the source text file.
        collection_name: Chroma collection identifier.

    Returns:
        A retriever configured to return relevant chunks.
    """

    loader = TextLoader(
        str(DATA_DIR / file_name),
        encoding="utf-8",
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP, 
        separators=[
        "\n\nΠροϊόν:",
        "\n\nΕρώτηση:",
        "\n\n------------------------------------------------",
        "\n\n========================================",
        "\n\n",
        "\n",
        " ",
        "",
        ],   
    )


    kb_chunks = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        kb_chunks,
        embedding=embedder,
        collection_name=collection_name,
        persist_directory=str(VECTORSTORE_DIR / collection_name)
    )

    # Dense retriever: semantic search using Chroma vector similarity
    dense_retriever = vectorstore.as_retriever(
        search_kwargs = {"k": TOP_K_RESULTS}
    )

    # BM25 retriever: keyword-based search for exact terms
    bm25_retriever = BM25Retriever.from_documents(kb_chunks)
    bm25_retriever.k = TOP_K_RESULTS

    # Hybrid retriever: combines semantic and keyword retrieval
    retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            dense_retriever,
        ],
        weights=[
            0.5,
            0.5,
        ],
)

    print(
        f"{collection_name}: "
        f"{vectorstore._collection.count()} chunks indexed"
    )

    return retriever

# Individual knowledge base retrievers
faqs_retriever = build_retriever("faqs.txt", "faqs_kb")
policies_retriever = build_retriever("policies.txt", "policies_kb")
products_retriever = build_retriever("products.txt", "products_kb")


def get_retriever(route: str):
    """
    Return the retriever associated with a route.

    Args:
        route: Selected route.

    Returns:
        Retriever for products, policies, or FAQs.
    """

    if route == "products":
        return products_retriever
    
    if route == "policies":
        return policies_retriever
    
    return faqs_retriever