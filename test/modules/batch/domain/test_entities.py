from uuid import uuid4

from app.modules.batch.domain.entities.batch_job import BatchJob
from app.modules.batch.domain.entities.batch_job_log import BatchJobLog


def _make_batch_job(**overrides):
    defaults = {
        "name": "Export CSV",
        "type": "export",
        "config": {"format": "csv"},
        "schedule": "0 */6 * * *",
        "status": "pending",
        "total_count": 0,
        "success_count": 0,
        "fail_count": 0,
    }
    defaults.update(overrides)
    return BatchJob(**defaults)


def _make_batch_job_log(**overrides):
    defaults = {
        "job_id": uuid4(),
        "message": "Job started",
        "level": "info",
    }
    defaults.update(overrides)
    return BatchJobLog(**defaults)


# ============================================================
# BATCH JOB
# ============================================================


class TestBatchJob:
    def test_create_job(self):
        job = _make_batch_job()
        assert job.name == "Export CSV"
        assert job.type == "export"
        assert job.status == "pending"

    def test_job_tablename(self):
        assert BatchJob.__tablename__ == "m_batch_job"

    def test_job_defaults(self):
        job = _make_batch_job()
        assert job.total_count == 0
        assert job.success_count == 0
        assert job.fail_count == 0

    def test_job_nullable_fields(self):
        job = _make_batch_job(config=None, schedule=None)
        assert job.config is None
        assert job.schedule is None

    def test_job_with_overrides(self):
        job = _make_batch_job(name="Import XLSX", type="import", status="running")
        assert job.name == "Import XLSX"
        assert job.type == "import"
        assert job.status == "running"


# ============================================================
# BATCH JOB LOG
# ============================================================


class TestBatchJobLog:
    def test_create_log(self):
        log = _make_batch_job_log()
        assert log.message == "Job started"
        assert log.level == "info"

    def test_log_tablename(self):
        assert BatchJobLog.__tablename__ == "m_batch_job_log"

    def test_log_job_id_type(self):
        job_id = uuid4()
        log = _make_batch_job_log(job_id=job_id)
        assert log.job_id == job_id

    def test_log_with_overrides(self):
        log = _make_batch_job_log(message="Failed row 42", level="error")
        assert log.message == "Failed row 42"
        assert log.level == "error"
