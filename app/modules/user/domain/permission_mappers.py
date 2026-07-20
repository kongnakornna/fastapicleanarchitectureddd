from typing import Union

from automapper import mapper

from app.modules.user.domain.permission_entities import (
    Permission,
    Role_,
    UserRole,
    RolePermission,
)
from app.modules.user.infrastructure.permission_models import (
    PermissionModel,
    RoleModel,
    UserRoleModel,
    RolePermissionModel,
)


async def permission_model_entity_mapper(
    obj: Union[PermissionModel, Permission],
) -> Union[Permission, PermissionModel]:
    if isinstance(obj, PermissionModel):
        return mapper.to(Permission).map(obj)
    else:
        return mapper.to(PermissionModel).map(obj)


async def role_model_entity_mapper(
    obj: Union[RoleModel, Role_],
) -> Union[Role_, RoleModel]:
    if isinstance(obj, RoleModel):
        return mapper.to(Role_).map(obj)
    else:
        return mapper.to(RoleModel).map(obj)


async def user_role_model_entity_mapper(
    obj: Union[UserRoleModel, UserRole],
) -> Union[UserRole, UserRoleModel]:
    if isinstance(obj, UserRoleModel):
        return mapper.to(UserRole).map(obj)
    else:
        return mapper.to(UserRoleModel).map(obj)


async def role_permission_model_entity_mapper(
    obj: Union[RolePermissionModel, RolePermission],
) -> Union[RolePermission, RolePermissionModel]:
    if isinstance(obj, RolePermissionModel):
        return mapper.to(RolePermission).map(obj)
    else:
        return mapper.to(RolePermissionModel).map(obj)
