"""Vertex AI RAG Engine integration for knowledge base queries."""

from typing import Any
from vertexai.preview import rag

from .config import (
    CORPUS_ID,
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
    LOCATION,
    PROJECT_ID,
)


def query_knowledge_base(query: str) -> dict[str, Any]:
    """Query Vertex AI RAG corpus and retrieve relevant information.

    Args:
        query: User query to search knowledge base.

    Returns:
        dict[str, Any]: Dictionary containing query results with status,
            message, and results list.
    """
    try:
        corpus_resource_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_ID}"

        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=corpus_resource_name)],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx in response.contexts.contexts:
                results.append({
                    "text": ctx.text if hasattr(ctx, "text") else "",
                    "score": ctx.score if hasattr(ctx, "score") else 0.0,
                    "source_uri": ctx.source_uri if hasattr(ctx, "source_uri") else "",
                })

        return {
            "status": "success" if results else "warning",
            "message": f"Found {len(results)} results" if results else "No results found",
            "query": query,
            "results": results,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error querying corpus: {str(e)}",
            "query": query,
        }
