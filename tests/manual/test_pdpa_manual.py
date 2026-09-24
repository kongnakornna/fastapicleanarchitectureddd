"""Manual tests — ต้องรันด้วยมือ (RLS, Kafka, LLM)"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.manual


class TestManual:
    def test_rls_requires_app_current_tenant(self) -> None:
        """TH: ต้องตั้ง app.current_tenant ก่อน query | EN: manual check"""
        pytest.skip("manual: verify RLS via psql session")

    def test_kafka_event_actually_published(self) -> None:
        """TH: ตรวจ Kafka topic pdpa.events | EN: manual check"""
        pytest.skip("manual: verify Kafka topic")

    def test_llm_never_receives_raw_pii(self) -> None:
        """TH: ตรวจว่า anonymize_pii ถูกเรียกก่อนส่ง LLM | EN: manual check"""
        pytest.skip("manual: inspect LLM request payload")