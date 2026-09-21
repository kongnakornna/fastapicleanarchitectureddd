"""Money presentation routers — API endpoints"""

from fastapi import APIRouter, Depends, HTTPException

from ..application.exceptions import MoneyException
from ..application.use_cases import MoneyUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import ExchangeRate
from .dependencies import get_money_use_cases
from .schemas import ExchangeRateSchema, MoneySchema, VATRequest, VATResponse

router = APIRouter(prefix="/api/v1/money", tags=["Money"])


@router.post("/add/", response_model=MoneySchema)
async def add(
    a: MoneySchema,
    b: MoneySchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """บวกเงิน — Add money"""
    try:
        result = uc.add(a.to_money(), b.to_money())
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/subtract/", response_model=MoneySchema)
async def subtract(
    a: MoneySchema,
    b: MoneySchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """ลบเงิน — Subtract money"""
    try:
        result = uc.subtract(a.to_money(), b.to_money())
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/vat/calculate/", response_model=VATResponse)
async def vat_calculate(
    req: VATRequest,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """คำนวณ VAT — Calculate VAT"""
    try:
        base = req.base.to_money()
        vat = uc.calculate_vat(base, req.rate)
        total = base + vat
        return VATResponse(
            vat=MoneySchema(amount=vat.amount, currency=vat.currency),
            total=MoneySchema(amount=total.amount, currency=total.currency),
        )
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/vat/extract/", response_model=VATResponse)
async def vat_extract(
    req: VATRequest,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """แยก VAT — Extract VAT"""
    try:
        total = req.base.to_money()
        vat = uc.extract_vat(total, req.rate)
        base = total - vat
        return VATResponse(
            vat=MoneySchema(amount=vat.amount, currency=vat.currency),
            total=MoneySchema(amount=base.amount, currency=base.currency),
        )
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/convert/", response_model=MoneySchema)
async def convert(
    amount: MoneySchema,
    rate: ExchangeRateSchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """แปลงสกุลเงิน — Convert currency"""
    try:
        er = ExchangeRate(
            from_currency=rate.from_currency,
            to_currency=rate.to_currency,
            rate=rate.rate,
            as_of=rate.as_of,
        )
        result = uc.convert(amount.to_money(), er)
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
