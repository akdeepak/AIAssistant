from __future__ import annotations

import uuid
from typing import Any, Dict, Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.config import settings


def get_collection_name(knowledge_base_id: str) -> str:
    return f"{settings.QDRANT_COLLECTION_PREFIX}_{knowledge_base_id}"


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)
    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        return

    info = client.get_collection(collection_name)
    try:
        existing_size = info.config.params.vectors.size
    except Exception:
        existing_size = None

    if existing_size is not None and int(existing_size) != int(vector_size):
        raise ValueError(
            f"Qdrant collection '{collection_name}' has vector size {existing_size} "
            f"but embeddings produced size {vector_size}."
        )


def upsert_chunks(
    client: QdrantClient,
    collection_name: str,
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
) -> None:
    points: List[PointStruct] = []
    for vector, payload in zip(vectors, payloads):
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
    client.upsert(collection_name=collection_name, points=points)


def search(
    client: QdrantClient,
    collection_name: str,
    query_vector: List[float],
    top_k: int,
    *,
    with_payload: bool = True,
) -> Iterable[Any]:
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=with_payload,
    )


def get_point_payload_text(payload: Optional[Dict[str, Any]]) -> str:
    if not payload:
        return ""
    text = payload.get("text")
    return text if isinstance(text, str) else ""
