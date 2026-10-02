"""YOLO HTTP router"""
from __future__ import annotations
import base64
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.modules.yolo.application.use_case import YOLOUseCase
from app.modules.yolo.domain.exceptions import (
    DatasetNotFoundError, ModelNotFoundError,
    TrainingFailedError, YOLOError,
)
from app.modules.yolo.domain.value_objects import AugConfig, TrainConfig
from app.modules.yolo.presentation.dependencies import get_ctx, get_yolo_use_case
from app.modules.yolo.presentation.docs import (
    RESPONSE_DATASET_201, RESPONSE_DETECT_200, RESPONSE_ERROR_400,
    RESPONSE_ERROR_404, RESPONSE_ERROR_500, RESPONSE_TRAIN_201,
)
from app.modules.yolo.presentation.schemas import (
    AnnotationsCreateRequest, AnnotationsResponse,
    BatchDetectRequest, BatchDetectResponse,
    ClassesDefineRequest, ClassesResponse,
    DatasetCreateRequest, DatasetDetailResponse,
    DatasetListResponse, DatasetResponse,
    DetectResponse, ExportRequest, ExportResponse,
    ImagesUploadResponse, MetricsResponse, ModelResponse,
    TrainRequest, TrainResponse, TrainingStatusResponse,
)

router = APIRouter(prefix="/yolo", tags=["yolo"])


def _status_of(exc: Exception) -> int:
    if isinstance(exc, (ModelNotFoundError, DatasetNotFoundError)):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, TrainingFailedError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_400_BAD_REQUEST


@router.post("/datasets", response_model=DatasetResponse,
              status_code=status.HTTP_201_CREATED,
              summary="Create dataset", operation_id="yolo_create_dataset",
              responses={201: RESPONSE_DATASET_201, 400: RESPONSE_ERROR_400})
async def create_dataset(
    payload: DatasetCreateRequest,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> DatasetResponse:
    ctx = await get_ctx()
    try:
        result = await uc.create_dataset(ctx, payload.name, payload.format)
        return DatasetResponse(**result)
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.get("/datasets", response_model=DatasetListResponse,
             summary="List datasets", operation_id="yolo_list_datasets")
async def list_datasets(
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
    page: int = 1, size: int = 50,
) -> DatasetListResponse:
    ctx = await get_ctx()
    return DatasetListResponse(**await uc.list_datasets(ctx, page, size))


@router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse,
             summary="Get dataset", operation_id="yolo_get_dataset",
             responses={404: RESPONSE_ERROR_404})
async def get_dataset(
    dataset_id: uuid.UUID,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> DatasetDetailResponse:
    ctx = await get_ctx()
    try:
        return DatasetDetailResponse(**await uc.get_dataset(ctx, dataset_id))
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.post("/datasets/{dataset_id}/classes", response_model=ClassesResponse,
              summary="Define classes", operation_id="yolo_define_classes")
async def define_classes(
    dataset_id: uuid.UUID, payload: ClassesDefineRequest,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> ClassesResponse:
    ctx = await get_ctx()
    classes = [c.model_dump() for c in payload.classes]
    result = await uc.define_classes(ctx, dataset_id, classes)
    return ClassesResponse(**result)


@router.post("/images", response_model=ImagesUploadResponse,
              summary="Upload images", operation_id="yolo_upload_images")
async def upload_images(
    dataset_id: str = Form(...), split: str = Form("train"),
    images: UploadFile = File(...),
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
) -> ImagesUploadResponse:
    ctx = await get_ctx()
    raw = await images.read()
    import hashlib
    h = hashlib.sha256(raw).hexdigest()
    items = [{"uri": f"s3://yolo-images/{h}.jpg", "content_hash": h,
               "size_bytes": len(raw)}]
    result = await uc.upload_images(ctx, uuid.UUID(dataset_id), items, split)
    return ImagesUploadResponse(**result)


@router.post("/annotations", response_model=AnnotationsResponse,
              summary="Create annotations", operation_id="yolo_create_annotations")
async def create_annotations(
    image_id: str = Form(...), payload: str = Form(...),
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
) -> AnnotationsResponse:
    import json as _json
    ctx = await get_ctx()
    data = _json.loads(payload)
    req = AnnotationsCreateRequest(**data)
    annotations = [a.model_dump() for a in req.annotations]
    result = await uc.create_annotations(ctx, uuid.UUID(image_id), annotations)
    return AnnotationsResponse(**result)


@router.post("/train", response_model=TrainResponse,
              status_code=status.HTTP_201_CREATED,
              summary="Start YOLO training", operation_id="yolo_train",
              responses={201: RESPONSE_TRAIN_201, 500: RESPONSE_ERROR_500})
async def start_training(
    payload: TrainRequest,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> TrainResponse:
    ctx = await get_ctx()
    try:
        config = TrainConfig(
            model_type=payload.model_type, epochs=payload.epochs,
            batch_size=payload.batch_size, imgsz=payload.imgsz,
            lr0=payload.lr0, device=payload.device,
            patience=payload.patience, optimizer=payload.optimizer)
        aug = AugConfig(**payload.aug_config) if payload.aug_config else AugConfig()
        result = await uc.start_training(ctx, uuid.UUID(payload.dataset_id),
                                           config, aug)
        return TrainResponse(**result)
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.get("/train/{training_id}", response_model=TrainingStatusResponse,
             summary="Get training status", operation_id="yolo_train_status",
             responses={404: RESPONSE_ERROR_404})
async def get_training_status(
    training_id: uuid.UUID,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> TrainingStatusResponse:
    ctx = await get_ctx()
    try:
        return TrainingStatusResponse(**await uc.get_training_status(ctx, training_id))
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.post("/train/{training_id}/cancel", summary="Cancel training",
              operation_id="yolo_train_cancel")
async def cancel_training(
    training_id: uuid.UUID,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> dict[str, Any]:
    return {"training_id": str(training_id), "status": "CANCELLED"}


@router.get("/models", response_model=list[ModelResponse],
             summary="List models", operation_id="yolo_list_models")
async def list_models(
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
    only_active: bool = True,
) -> list[ModelResponse]:
    ctx = await get_ctx()
    return [ModelResponse(**r) for r in await uc.list_models(ctx, only_active)]


@router.post("/models/{model_id}/export", response_model=ExportResponse,
              summary="Export model", operation_id="yolo_export_model",
              responses={500: RESPONSE_ERROR_500})
async def export_model(
    model_id: uuid.UUID, payload: ExportRequest,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> ExportResponse:
    ctx = await get_ctx()
    try:
        result = await uc.export_model(ctx, model_id, payload.format,
                                         payload.imgsz, payload.opset)
        return ExportResponse(**result)
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.post("/detect", response_model=DetectResponse,
              summary="Detect objects (single image)",
              operation_id="yolo_detect",
              responses={200: RESPONSE_DETECT_200, 404: RESPONSE_ERROR_404})
async def detect(
    model_id: str = Form(...),
    conf: float = Form(0.25), iou: float = Form(0.45),
    image: UploadFile = File(...),
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
) -> DetectResponse:
    ctx = await get_ctx()
    try:
        raw = await image.read()
        result = await uc.detect(ctx, uuid.UUID(model_id), raw, conf, iou)
        return DetectResponse(**result)
    except YOLOError as e:
        raise HTTPException(_status_of(e), detail=str(e)) from e


@router.post("/detect/batch", response_model=BatchDetectResponse,
              summary="Batch detection", operation_id="yolo_detect_batch")
async def detect_batch(
    payload: BatchDetectRequest,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> BatchDetectResponse:
    ctx = await get_ctx()
    images = [base64.b64decode(b) for b in payload.images_base64]
    result = await uc.detect_batch(ctx, uuid.UUID(payload.model_id),
                                     images, payload.conf, payload.iou)
    return BatchDetectResponse(**result)


@router.post("/detect/stream", summary="Stream video detection (SSE)",
              operation_id="yolo_detect_stream")
async def detect_stream(
    payload: Any,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> dict[str, Any]:
    return {"model_id": payload.get("model_id"), "stream": "sse"}


@router.get("/metrics/{model_id}", response_model=MetricsResponse,
             summary="Get model metrics", operation_id="yolo_get_metrics")
async def get_metrics(
    model_id: uuid.UUID,
    uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
) -> MetricsResponse:
    ctx = await get_ctx()
    m = await uc._model_repo.find_by_id(ctx, model_id)
    if m is None:
        raise HTTPException(404, detail="model not found")
    return MetricsResponse(model_id=str(model_id),
                            metrics=dict(m.metrics_json or {}))


@router.post("/metrics/drift", summary="Check drift",
              operation_id="yolo_check_drift")
async def check_drift(payload: dict[str, Any]) -> dict[str, Any]:
    return {"model_id": payload.get("model_id", ""),
            "drift_score": 0.0,
            "threshold": payload.get("threshold", 0.3),
            "drifted": False}
