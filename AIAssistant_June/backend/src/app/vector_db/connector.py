from typing import Any, Dict, Optional


class VectorDBConnector:
    def __init__(self, db_type: str, config: Dict[str, Any]):
        self.db_type = db_type
        self.db_config = config
        self.db_client = self._initialize_client()

    def _initialize_client(self):
        # TODO: Implement concrete clients (Qdrant, Pinecone, Azure Search).
        return None

    def _require_client(self) -> None:
        if self.db_client is None:
            raise NotImplementedError(
                f"VectorDBConnector for '{self.db_type}' is not implemented yet. "
                "Configure a supported vector database backend or use the "
                "/knowledge-service endpoints instead."
            )

    def insert(self, vector: list, metadata: Dict[str, Any]):
        self._require_client()
        return self.db_client.insert(vector, metadata)

    def query(
        self,
        vector: list,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ):
        self._require_client()
        return self.db_client.query(vector, top_k, metadata_filter)

    def delete(self, vector_id: str):
        self._require_client()
        return self.db_client.delete(vector_id)

    def update(self, vector_id: str, vector: list, metadata: Dict[str, Any]):
        self._require_client()
        return self.db_client.update(vector_id, vector, metadata)
