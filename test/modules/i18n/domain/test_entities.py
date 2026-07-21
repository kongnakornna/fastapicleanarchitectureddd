from app.modules.i18n.domain.entities.translation import Translation


def _make_translation(**overrides):
    defaults = {
        "locale": "en",
        "key": "common.save",
        "value": "Save",
    }
    defaults.update(overrides)
    return Translation(**defaults)


# ============================================================
# TRANSLATION
# ============================================================


class TestTranslation:
    def test_create_translation(self):
        t = _make_translation()
        assert t.locale == "en"
        assert t.key == "common.save"
        assert t.value == "Save"

    def test_translation_tablename(self):
        assert Translation.__tablename__ == "m_translation"

    def test_translation_with_overrides(self):
        t = _make_translation(locale="pt-BR", key="common.cancel", value="Cancelar")
        assert t.locale == "pt-BR"
        assert t.key == "common.cancel"
        assert t.value == "Cancelar"
