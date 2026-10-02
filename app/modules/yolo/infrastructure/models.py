"""YOLO SQLAlchemy 2.0 models — schema=public, prefix=yolo_"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Index, Integer,
    Numeric, String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    pass


class DatasetModel(Base):
    __tablename__ = "yolo_datasets"
    __table_args__ = (
        CheckConstraint("format IN ('yolo','coco','roboflow','labelimg')",
                         name="ck_yolo_ds_format"),
        CheckConstraint("status IN ('DRAFT','READY','TRAINING','ARCHIVED')",
                         name="ck_yolo_ds_status"),
        UniqueConstraint("tenant_id", "name", "version", name="uq_yolo_ds_name_ver"),
        Index("ix_yolo_ds_tenant", "tenant_id"),
        Index("ix_yolo_ds_status", "tenant_id", "status"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False, server_default="yolo")
    root_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    class_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    splits_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
        server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="DRAFT")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
        server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class ClassModel(Base):
    __tablename__ = "yolo_classes"
    __table_args__ = (
        UniqueConstraint("dataset_id", "class_index", name="uq_yolo_class_idx"),
        UniqueConstraint("dataset_id", "name", name="uq_yolo_class_name"),
        Index("ix_yolo_class_tenant", "tenant_id"),
        Index("ix_yolo_class_dataset", "dataset_id"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    class_index: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False, server_default="#FF0000")
    count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class ImageModel(Base):
    __tablename__ = "yolo_images"
    __table_args__ = (
        CheckConstraint("split IN ('train','val','test')", name="ck_yolo_img_split"),
        UniqueConstraint("dataset_id", "content_hash", name="uq_yolo_img_hash"),
        Index("ix_yolo_img_tenant", "tenant_id"),
        Index("ix_yolo_img_dataset", "dataset_id", "split"),
        Index("ix_yolo_img_hash", "content_hash"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    uri: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    height: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    split: Mapped[str] = mapped_column(String(10), nullable=False, server_default="train")
    annotation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class AnnotationModel(Base):
    __tablename__ = "yolo_annotations"
    __table_args__ = (
        CheckConstraint("x_center >= 0 AND x_center <= 1", name="ck_yolo_ann_x"),
        CheckConstraint("y_center >= 0 AND y_center <= 1", name="ck_yolo_ann_y"),
        CheckConstraint("width > 0 AND width <= 1", name="ck_yolo_ann_w"),
        CheckConstraint("height > 0 AND height <= 1", name="ck_yolo_ann_h"),
        Index("ix_yolo_ann_tenant", "tenant_id"),
        Index("ix_yolo_ann_image", "image_id"),
        Index("ix_yolo_ann_class", "class_id"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    image_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    x_center: Mapped[float] = mapped_column(nullable=False)
    y_center: Mapped[float] = mapped_column(nullable=False)
    width: Mapped[float] = mapped_column(nullable=False)
    height: Mapped[float] = mapped_column(nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False,
        server_default="1.0")
    is_hard: Mapped[bool] = mapped_column(Boolean, nullable=False,
        server_default=text("false"))
    source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class TrainingModel(Base):
    __tablename__ = "yolo_trainings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED')",
            name="ck_yolo_tr_status"),
        Index("ix_yolo_tr_tenant", "tenant_id", "status"),
        Index("ix_yolo_tr_dataset", "dataset_id", "created_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_type: Mapped[str] = mapped_column(String(20), nullable=False)
    epochs: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
    batch_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="16")
    imgsz: Mapped[int] = mapped_column(Integer, nullable=False, server_default="640")
    lr0: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False,
        server_default="0.01")
    device: Mapped[str] = mapped_column(String(20), nullable=False, server_default="auto")
    patience: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")
    optimizer: Mapped[str] = mapped_column(String(20), nullable=False, server_default="auto")
    aug_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
        server_default=text("'{}'::jsonb"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    best_model_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class ModelModel(Base):
    __tablename__ = "yolo_models"
    __table_args__ = (
        CheckConstraint("format IN ('pt','onnx','engine','torchscript','coreml')",
                         name="ck_yolo_model_format"),
        UniqueConstraint("tenant_id", "name", "version", name="uq_yolo_model_name_ver"),
        Index("ix_yolo_model_tenant", "tenant_id"),
        Index("ix_yolo_model_training", "training_id"),
        Index("ix_yolo_model_active", "tenant_id", "is_active"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    training_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    weights_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    weights_hash: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    export_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    format: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pt")
    mAP50: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
    mAP50_95: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
    precision_: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
    recall_: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
        server_default=text("'{}'::jsonb"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False,
        server_default=text("true"))
    is_deployed: Mapped[bool] = mapped_column(Boolean, nullable=False,
        server_default=text("false"))
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())


class InferenceModel(Base):
    __tablename__ = "yolo_inferences"
    __table_args__ = (
        CheckConstraint("source IN ('api','batch','stream','upload')",
                         name="ck_yolo_inf_source"),
        Index("ix_yolo_inf_tenant", "tenant_id", "created_at"),
        Index("ix_yolo_inf_model", "model_id", "created_at"),
        Index("ix_yolo_inf_hash", "image_hash"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    image_hash: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    detections_json: Mapped[list] = mapped_column(JSONB, nullable=False,
        server_default=text("'[]'::jsonb"))
    detection_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="api")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False, server_default=func.now(), onupdate=func.now())
