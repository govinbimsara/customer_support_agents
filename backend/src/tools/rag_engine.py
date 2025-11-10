"""Vertex AI RAG Engine integration for knowledge base queries."""

import logging
from typing import Any

from google.api_core import exceptions as google_exceptions
from vertexai.preview import rag

from .config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
    get_corpus_id,
    get_location,
    get_project_id,
)

logger = logging.getLogger(__name__)


def query_knowledge_base(query: str) -> str:
    """Query Vertex AI RAG corpus and retrieve relevant information.

    Args:
        query: User query to search knowledge base.

    Returns:
        str: Formatted string containing query results.
    """
    try:
        project_id = get_project_id()
        location = get_location()
        corpus_id = get_corpus_id()
        corpus_resource_name = f"projects/{project_id}/locations/{location}/ragCorpora/{corpus_id}"

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

        if not results:
            return "No relevant information found in the knowledge base."
        
        formatted_results = "\n\n".join(
            f"Result {i+1} (relevance: {r['score']:.2f}):\n{r['text']}"
            for i, r in enumerate(results)
        )
        return f"Found {len(results)} relevant results:\n\n{formatted_results}"

    except google_exceptions.NotFound:
        logger.error(f"RAG corpus not found: {get_corpus_id()}")
        return {
            "status": "error",
            "message": "Knowledge base not configured",
            "query": query,
        }
    except google_exceptions.PermissionDenied:
        logger.error("Permission denied accessing RAG corpus")
        return {
            "status": "error",
            "message": "Access denied to knowledge base",
            "query": query,
        }
    except google_exceptions.DeadlineExceeded:
        logger.warning(f"RAG query timeout for: {query}")
        return {
            "status": "error",
            "message": "Knowledge base query timeout",
            "query": query,
        }
    except Exception as e:
        logger.exception(f"Unexpected error querying RAG: {query}")
        return {
            "status": "error",
            "message": f"Knowledge base error: {type(e).__name__}",
            "query": query,
        }