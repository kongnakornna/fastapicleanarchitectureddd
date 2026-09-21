from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeDocument:
    id: int
    title: str
    source: str
    chunk_count: int
    status: str          # ready | processing | failed
    created_at: str

    @property
    def badge_class(self) -> str:
        return {"ready": "bg-success", "processing": "bg-warning", "failed": "bg-danger"}.get(self.status, "bg-secondary")
