from __future__ import annotations

import logging
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class EmbedModelName(str, Enum):
    QWEN = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"


EMBED_MODEL_REGISTRY: Dict[EmbedModelName, Dict[str, Any]] = {
    EmbedModelName.QWEN: {"type": "huggingface", "dimensions": 1536},
}


def _check_azure_credentials() -> None:
    if not settings.AZURE_KEY:
        logger.warning(
            "AZURE_KEY is not set — Azure OpenAI calls will fail. "
            "Set the AZURE_KEY and AZURE_ENDPOINT environment variables."
        )


def get_embed_model_by_name(name: EmbedModelName) -> BaseEmbedding:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    return HuggingFaceEmbedding(model_name=name.value)


@lru_cache(maxsize=1)
def get_embed_model() -> AzureOpenAIEmbedding:
    _check_azure_credentials()
    return AzureOpenAIEmbedding(
        deployment_name=settings.AZURE_EMBED_DEPLOYMENT,
        api_key=settings.AZURE_KEY,
        azure_endpoint=settings.AZURE_ENDPOINT,
        api_version=settings.AZURE_API_VERSION,
    )


@lru_cache(maxsize=1)
def get_llm() -> AzureOpenAI:
    _check_azure_credentials()
    return AzureOpenAI(
        deployment_name=settings.AZURE_LLM_DEPLOYMENT,
        api_key=settings.AZURE_KEY,
        azure_endpoint=settings.AZURE_ENDPOINT,
        api_version=settings.AZURE_API_VERSION,
    )


def list_embed_models() -> List[Dict[str, Any]]:
    return [
        {"name": name.value, **info}
        for name, info in EMBED_MODEL_REGISTRY.items()
    ]


def evaluate_embed_model(
    name: EmbedModelName,
    kb_dir: Path,
    queries: List[str],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    embed_model = get_embed_model_by_name(name)
    storage_context = StorageContext.from_defaults(persist_dir=str(kb_dir))
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    query_engine = index.as_query_engine(similarity_top_k=top_k)

    results = []
    for query in queries:
        logger.info("Evaluating model=%s query='%s'", name.value, query)
        response = query_engine.query(query)
        results.append({
            "model": name.value,
            "query": query,
            "response": str(response),
            "source_nodes": [
                {
                    "text": node.node.get_content()[:200],
                    "score": node.score,
                }
                for node in response.source_nodes
            ],
        })
    return results
