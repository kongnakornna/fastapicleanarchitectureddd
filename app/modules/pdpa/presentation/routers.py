"""pdpa HTTP routers — 4 groups ตามสเปค §4"""
from __future__ import annotations
import uuid
from typing import Annotated

from app.core.logging import logger
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.modules.pdpa.application.exceptions import (
    ConsentNotFoundAppError, CookieConsentNotFoundAppError,
    DSARNotFoundAppError, DuplicateConsentError,
    IdempotencyConflictError, IdempotencyMismatchError,
    IdentityVerificationRequiredError, PolicyNotFoundAppError,
)
from app.modules.pdpa.application.use_cases import (
    EraseDataUseCase, ExportDataUseCase, GetCurrentPolicyUseCase,
    ProcessDSARUseCase, PublishPrivacyPolicyUseCase,
    RecordConsentUseCase, RecordCookieConsentUseCase,
    RevokeConsentUseCase, SubmitDSARUseCase,
    UpdateCookieConsentUseCase,
)
from app.modules.pdpa.domain.exceptions import PDPAError
from app.modules.pdpa.presentation.dependencies import (
    get_current_pp_uc, get_erase_data_uc, get_export_data_uc,
    get_process_dsar_uc, get_publish_pp_uc,
    get_record_consent_uc, get_record_cookie_uc,
    get_revoke_consent_uc, get_submit_dsar_uc,
    get_update_cookie_uc,
)
from app.modules.pdpa.presentation.docs import (
    RESPONSE_CREATE_201, RESPONSE_ERROR_400,
    RESPONSE_ERROR_404, RESPONSE_ERROR_409, RESPONSE_ERROR_422,
)
from app.modules.pdpa.presentation.schemas import (
    ConsentCreateRequest, ConsentResponse, ConsentRevokeRequest,
    CookieConsentRequest, CookieConsentResponse, CookieConsentUpdateRequest,
    DSARCreateRequest, DSARProcessRequest, DSARResponse,
    PrivacyPolicyCreateRequest, PrivacyPolicyResponse,
)

router = APIRouter(prefix="/pdpa", tags=["PDPA"])

IdemKey = Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=255)]


# ═══════════════════════════════════════════════════════════════
# Consent
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/consent/",
    status_code=status.HTTP_201_CREATED,
    summary="บันทึกความยินยอม",
    operation_id="record_consent",
    response_model=ConsentResponse,
    responses={201: RESPONSE_CREATE_201, 400: RESPONSE_ERROR_400,
               409: RESPONSE_ERROR_409, 422: RESPONSE_ERROR_422},
)
async def record_consent(
    request: Request,
    payload: ConsentCreateRequest,
    idem_key: IdemKey,
    uc: Annotated[RecordConsentUseCase, Depends(get_record_consent_uc)],
) -> ConsentResponse:
    """TH: บันทึกความยินยอมรายข้อ (idempotent) | EN: Record granular consent"""
    try:
        entity = await uc.execute(
            user_id=payload.user_id, purpose_code=payload.purpose_code,
            ip_address=payload.ip_address, user_agent=payload.user_agent,
            expires_at=payload.expires_at, idempotency_key=idem_key,
            request_method=request.method,
            request_path=request.url.path,
        )
    except DuplicateConsentError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyMismatchError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e),
        ) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return ConsentResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/consent/{consent_id}/revoke",
    summary="ถอนความยินยอม",
    operation_id="revoke_consent",
    response_model=ConsentResponse,
    responses={404: RESPONSE_ERROR_404, 400: RESPONSE_ERROR_400},
)
async def revoke_consent(
    consent_id: uuid.UUID,
    payload: ConsentRevokeRequest,
    uc: Annotated[RevokeConsentUseCase, Depends(get_revoke_consent_uc)],
) -> ConsentResponse:
    try:
        entity = await uc.execute(consent_id=consent_id, reason=payload.reason)
    except ConsentNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return ConsentResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# DSAR
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/dsar/",
    status_code=status.HTTP_201_CREATED,
    summary="ยื่นคำร้อง DSAR",
    operation_id="submit_dsar",
    response_model=DSARResponse,
    responses={201: RESPONSE_CREATE_201, 409: RESPONSE_ERROR_409,
               422: RESPONSE_ERROR_422},
)
async def submit_dsar(
    request: Request,
    payload: DSARCreateRequest,
    idem_key: IdemKey,
    uc: Annotated[SubmitDSARUseCase, Depends(get_submit_dsar_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(
            user_id=payload.user_id, type=payload.type, reason=payload.reason,
            idempotency_key=idem_key,
            request_method=request.method,
            request_path=request.url.path,
        )
    except IdempotencyConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except IdempotencyMismatchError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e),
        ) from e
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


@router.post(
    "/dsar/{dsar_id}/process",
    summary="ประมวลผล DSAR",
    operation_id="process_dsar",
    response_model=DSARResponse,
    responses={404: RESPONSE_ERROR_404, 400: RESPONSE_ERROR_400},
)
async def process_dsar(
    dsar_id: uuid.UUID,
    payload: DSARProcessRequest,
    uc: Annotated[ProcessDSARUseCase, Depends(get_process_dsar_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(
            dsar_id=dsar_id, response_payload=payload.response_payload)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (PDPAError, IdentityVerificationRequiredError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/dsar/{dsar_id}/export",
    summary="Export ข้อมูลผู้ใช้ (JSON)",
    operation_id="export_dsar_data",
    responses={404: RESPONSE_ERROR_404},
)
async def export_dsar_data(
    dsar_id: uuid.UUID,
    user_id: uuid.UUID,
    uc: Annotated[ExportDataUseCase, Depends(get_export_data_uc)],
) -> dict:
    try:
        return await uc.execute_json(dsar_id=dsar_id, user_id=user_id)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/dsar/{dsar_id}/erase",
    summary="ลบ/anonymize ข้อมูล",
    operation_id="erase_dsar_data",
    response_model=DSARResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def erase_dsar_data(
    dsar_id: uuid.UUID,
    user_id: uuid.UUID,
    uc: Annotated[EraseDataUseCase, Depends(get_erase_data_uc)],
) -> DSARResponse:
    try:
        entity = await uc.execute(dsar_id=dsar_id, user_id=user_id)
    except DSARNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return DSARResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Privacy Policy
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/privacy-policy/current",
    summary="นโยบายปัจจุบัน",
    operation_id="get_current_policy",
    response_model=PrivacyPolicyResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_current_policy(
    uc: Annotated[GetCurrentPolicyUseCase, Depends(get_current_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute()
    except PolicyNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/privacy-policy/{version}",
    summary="นโยบายตาม version",
    operation_id="get_policy_version",
    response_model=PrivacyPolicyResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_policy_version(
    version: int,
    uc: Annotated[GetCurrentPolicyUseCase, Depends(get_current_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute(version=version)
    except PolicyNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


@router.post(
    "/privacy-policy/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง/publish privacy policy (admin)",
    operation_id="publish_privacy_policy",
    response_model=PrivacyPolicyResponse,
    responses={201: RESPONSE_CREATE_201, 400: RESPONSE_ERROR_400},
)
async def publish_privacy_policy(
    payload: PrivacyPolicyCreateRequest,
    uc: Annotated[PublishPrivacyPolicyUseCase, Depends(get_publish_pp_uc)],
) -> PrivacyPolicyResponse:
    try:
        entity = await uc.execute(
            version=payload.version,
            content_th=payload.content_th,
            content_en=payload.content_en)
    except PDPAError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return PrivacyPolicyResponse.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# Cookie Consent
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/cookie-consent/",
    status_code=status.HTTP_201_CREATED,
    summary="บันทึก cookie consent (no pre-tick)",
    operation_id="record_cookie_consent",
    response_model=CookieConsentResponse,
    responses={201: RESPONSE_CREATE_201, 422: RESPONSE_ERROR_422},
)
async def record_cookie_consent(
    payload: CookieConsentRequest,
    uc: Annotated[RecordCookieConsentUseCase, Depends(get_record_cookie_uc)],
) -> CookieConsentResponse:
    entity = await uc.execute(
        session_id=payload.session_id,
        analytics=payload.analytics, marketing=payload.marketing,
        functional=payload.functional)
    return CookieConsentResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/cookie-consent/{consent_id}",
    summary="แก้ไข cookie consent",
    operation_id="update_cookie_consent",
    response_model=CookieConsentResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def update_cookie_consent(
    consent_id: uuid.UUID,
    payload: CookieConsentUpdateRequest,
    uc: Annotated[UpdateCookieConsentUseCase, Depends(get_update_cookie_uc)],
) -> CookieConsentResponse:
    try:
        entity = await uc.execute(
            consent_id=consent_id,
            analytics=payload.analytics, marketing=payload.marketing,
            functional=payload.functional)
    except CookieConsentNotFoundAppError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return CookieConsentResponse.model_validate(entity, from_attributes=True)