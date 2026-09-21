from apps.dashboard.domain.entities import (
    DashboardStats,
    JobStatusSummary,
    Report,
    RevenueData,
    revenue_bar_height,
    status_percent,
    total_revenue,
)
from apps.dashboard.domain.use_cases import GetDashboardStatsUseCase


class FakeRepo:
    def get_stats(self) -> DashboardStats:
        return DashboardStats(
            total_devices=120, online_devices=90,
            active_alerts=3, today_commands=45,
        )

    def get_revenue_chart(self, period): return []
    def get_job_status(self): return []
    def get_top_parts(self, limit=None): return []
    def get_reports(self): return []
    def generate_report(self, **kw): return b""


def test_get_stats_use_case():
    uc = GetDashboardStatsUseCase(FakeRepo())
    stats = uc.execute()
    assert stats.total_devices == 120
    assert stats.online_devices == 90
    assert stats.online_rate == 75


def test_online_rate_zero_when_no_devices():
    s = DashboardStats(total_devices=0, online_devices=0, active_alerts=0, today_commands=0)
    assert s.online_rate == 0


def test_revenue_bar_height():
    data = [RevenueData("Jan", 100), RevenueData("Feb", 200)]
    assert revenue_bar_height(200, data) == 100
    assert revenue_bar_height(100, data) == 50


def test_total_revenue():
    data = [RevenueData("Jan", 100), RevenueData("Feb", 200)]
    assert total_revenue(data) == 300


def test_status_percent():
    data = [JobStatusSummary("pending", 5), JobStatusSummary("completed", 20)]
    assert status_percent(20, data) == 80


def test_report_can_download():
    r = Report(id="1", name="A", type="Sales", created_at="", status="ready", report_type="sales")
    assert r.can_download is True
    assert r.badge_class == "bg-green"
