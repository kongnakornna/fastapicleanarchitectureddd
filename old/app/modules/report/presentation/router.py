from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from app.modules.report.presentation.schemas import ReportResponse

router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/daily-sales/pdf")
async def get_daily_sales_report(
    date: str = Query(default=datetime.now().strftime("%Y-%m-%d")),
) -> ReportResponse:
    return ReportResponse(
        message="Daily sales report PDF generation is pending implementation.",
        report_type="daily-sales",
        generated_at=datetime.now().isoformat(),
    )


@router.get("/inventory-summary/pdf")
async def get_inventory_summary_report() -> ReportResponse:
    return ReportResponse(
        message="Inventory summary report PDF generation is pending implementation.",
        report_type="inventory-summary",
        generated_at=datetime.now().isoformat(),
    )


@router.get("/customer-list/pdf")
async def get_customer_list_report() -> ReportResponse:
    return ReportResponse(
        message="Customer list report PDF generation is pending implementation.",
        report_type="customer-list",
        generated_at=datetime.now().isoformat(),
    )


@router.get("/invoice/pdf")
async def get_invoice_report(
    source: str = Query(...),
) -> ReportResponse:
    return ReportResponse(
        message="Invoice report PDF generation is pending implementation.",
        report_type="invoice",
        generated_at=datetime.now().isoformat(),
    )


@router.get("/credit-note/pdf")
async def get_credit_note_report() -> ReportResponse:
    return ReportResponse(
        message="Credit note report PDF generation is pending implementation.",
        report_type="credit-note",
        generated_at=datetime.now().isoformat(),
    )


@router.get("/debit-note/pdf")
async def get_debit_note_report() -> ReportResponse:
    return ReportResponse(
        message="Debit note report PDF generation is pending implementation.",
        report_type="debit-note",
        generated_at=datetime.now().isoformat(),
    )
