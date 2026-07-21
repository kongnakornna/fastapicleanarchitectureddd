from logging.config import fileConfig

from alembic import context

from app.core.database import pg_engine
from app.modules.authentication.infrastructure.models import (
    SessionModel,
    AccessTokenModel,
    RefreshTokenModel,
)
from app.modules.batch.domain.entities.batch_job import BatchJob
from app.modules.batch.domain.entities.batch_job_log import BatchJobLog
from app.modules.customer.domain.entities.car import Car
from app.modules.customer.domain.entities.customer import Customer
from app.modules.document.domain.entities.document import Document as DocumentEntity
from app.modules.email.domain.entities.email_config import EmailConfig
from app.modules.email.domain.entities.email_log import EmailLog
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.i18n.domain.entities.translation import Translation
from app.modules.iot.domain.entities.activity_log import ActivityLog
from app.modules.iot.domain.entities.alarm_log import AlarmLog
from app.modules.iot.domain.entities.device import Device
from app.modules.iot.domain.entities.device_alert import DeviceAlert
from app.modules.iot.domain.entities.device_config import DeviceConfig
from app.modules.iot.domain.entities.device_status import DeviceStatus
from app.modules.iot.domain.entities.iot_data import IoTData
from app.modules.iot.domain.entities.schedule import Schedule
from app.modules.items.domain.entities.item import Item
from app.modules.payment.domain.entities.payment import Payment
from app.modules.payment.domain.entities.payment_history import PaymentHistory
from app.modules.payment.domain.entities.receipt import Receipt
from app.modules.purchaseorder.domain.entities.purchase_order_detail import (
    PurchaseOrderDetail,
)
from app.modules.purchaseorder.domain.entities.purchase_order_header import (
    PurchaseOrderHeader,
)
from app.modules.purchaseorder.domain.entities.purchase_order_status_history import (
    PurchaseOrderStatusHistory,
)
from app.modules.quotation.domain.entities.quotation import Quotation
from app.modules.shared.infrastructure.models import Base
from app.modules.user.infrastructure.models import UserModel
from app.modules.user.infrastructure.permission_models import (
    RoleModel,
    PermissionModel,
    UserRoleModel,
    RolePermissionModel,
)
from app.modules.wos.domain.entities.order import WosOrder


_ = [
    AccessTokenModel,
    AlembicModel,
    BatchJob,
    BatchJobLog,
    Car,
    Customer,
    DocumentEntity,
    EmailConfig,
    EmailLog,
    RefreshTokenModel,
    SessionModel,
    Translation,
    UserModel,
    RoleModel,
    PermissionModel,
    UserRoleModel,
    RolePermissionModel,
    Device,
    DeviceConfig,
    DeviceStatus,
    DeviceAlert,
    IoTData,
    AlarmLog,
    ActivityLog,
    Schedule,
    Item,
    Payment,
    PaymentHistory,
    Receipt,
    PurchaseOrderHeader,
    PurchaseOrderDetail,
    PurchaseOrderStatusHistory,
    Quotation,
    WosOrder,
]

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = pg_engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with pg_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
