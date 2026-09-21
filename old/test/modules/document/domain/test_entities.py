from app.modules.document.domain.entities.document import Document


def _make_document(**overrides):
    defaults = {
        "filename": "abc123.pdf",
        "original_name": "invoice.pdf",
        "mime_type": "application/pdf",
        "size": 1024,
    }
    defaults.update(overrides)
    return Document(**defaults)


# ============================================================
# DOCUMENT
# ============================================================


class TestDocument:
    def test_create_document(self):
        doc = _make_document()
        assert doc.filename == "abc123.pdf"
        assert doc.original_name == "invoice.pdf"
        assert doc.mime_type == "application/pdf"
        assert doc.size == 1024

    def test_document_tablename(self):
        assert Document.__tablename__ == "m_document"

    def test_document_size_type(self):
        doc = _make_document(size=5_000_000)
        assert doc.size == 5_000_000

    def test_document_with_overrides(self):
        doc = _make_document(filename="xyz.png", mime_type="image/png", size=2048)
        assert doc.filename == "xyz.png"
        assert doc.mime_type == "image/png"
        assert doc.size == 2048
