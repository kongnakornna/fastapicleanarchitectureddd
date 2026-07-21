from __future__ import annotations


class DashboardUseCase:
    async def get_dashboard_stats(self) -> dict[str, int]:
        return {
            "total_devices": 128,
            "online_devices": 95,
            "active_alerts": 3,
            "today_commands": 47,
        }

    async def get_revenue_chart(self, period: str = "daily") -> list[dict[str, str | float]]:
        return [
            {"period": "Mon", "amount": 1200.50},
            {"period": "Tue", "amount": 980.75},
            {"period": "Wed", "amount": 1350.00},
            {"period": "Thu", "amount": 1120.25},
            {"period": "Fri", "amount": 1580.00},
            {"period": "Sat", "amount": 870.50},
            {"period": "Sun", "amount": 650.00},
        ]

    async def get_top_parts(self, limit: int = 5) -> list[dict[str, str | int]]:
        return [
            {"part_name": "Sensor Module A", "count": 342},
            {"part_name": "Control Board v2", "count": 281},
            {"part_name": "Power Supply Unit", "count": 198},
            {"part_name": "Cable Assembly", "count": 156},
            {"part_name": "Housing Cover", "count": 134},
        ][:limit]

    async def get_job_status_summary(self) -> list[dict[str, str | int]]:
        return [
            {"status": "completed", "count": 85},
            {"status": "in_progress", "count": 12},
            {"status": "pending", "count": 8},
            {"status": "failed", "count": 3},
        ]
