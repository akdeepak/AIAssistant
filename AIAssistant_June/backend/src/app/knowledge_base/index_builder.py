"""Strategy classes for building LlamaIndex vector store indexes."""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Sequence

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.schema import Document
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

logger = logging.getLogger(__name__)


class IndexBuilder(ABC):

    @abstractmethod
    def build(self, documents: Sequence[Document]) -> VectorStoreIndex:
        ...


class DefaultIndexBuilder(IndexBuilder):

    def __init__(self, embed_model: AzureOpenAIEmbedding) -> None:
        self._embed_model = embed_model

    def build(self, documents: Sequence[Document]) -> VectorStoreIndex:
        logger.info("Building default index with %d documents", len(documents))
        return VectorStoreIndex.from_documents(documents, embed_model=self._embed_model)


class SemanticIndexBuilder(IndexBuilder):

    def __init__(
        self,
        embed_model: AzureOpenAIEmbedding,
        buffer_size: int = 1,
        breakpoint_percentile_threshold: int = 95,
    ) -> None:
        self._embed_model = embed_model
        self._buffer_size = buffer_size
        self._breakpoint_percentile_threshold = breakpoint_percentile_threshold

    def build(self, documents: Sequence[Document]) -> VectorStoreIndex:
        splitter = SemanticSplitterNodeParser.from_defaults(
            embed_model=self._embed_model,
            buffer_size=self._buffer_size,
            breakpoint_percentile_threshold=self._breakpoint_percentile_threshold,
        )
        doc_list = list(documents)
        nodes = splitter.get_nodes_from_documents(doc_list)
        logger.info(
            "Semantic splitter produced %d nodes from %d documents",
            len(nodes),
            len(doc_list),
        )
        return VectorStoreIndex(nodes)
