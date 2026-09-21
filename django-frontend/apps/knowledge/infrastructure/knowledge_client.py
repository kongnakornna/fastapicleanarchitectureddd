from apps.shared.infrastructure.fastapi_client import fastapi

from ..domain.entities import KnowledgeDocument


class KnowledgeClient:
    def __init__(self, token: str | None = None):
        self.token = token

    def list_documents(self, *, page: int = 1, q: str = "") -> dict:
        params = {"page": page}
        if q:
            params["q"] = q
        data = fastapi.json("GET", "/knowledge", token=self.token, params=params)
        return {
            "items": [self._to_doc(x) for x in data.get("items", [])],
            "total": data.get("total", 0),
        }

    def get_document(self, doc_id: int) -> KnowledgeDocument:
        return self._to_doc(fastapi.json("GET", f"/knowledge/{doc_id}", token=self.token))

    def create_document(self, *, title: str, source: str, content: str) -> KnowledgeDocument:
        data = fastapi.json("POST", "/knowledge", token=self.token, json={
            "title": title, "source": source, "content": content,
        })
        return self._to_doc(data)

    def delete_document(self, doc_id: int) -> None:
        fastapi.request("DELETE", f"/knowledge/{doc_id}", token=self.token)

    @staticmethod
    def _to_doc(d: dict) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=d["id"], title=d["title"],
            source=d.get("source", ""),
            chunk_count=d.get("chunkCount", 0),
            status=d.get("status", "ready"),
            created_at=d.get("createdAt", ""),
        )
