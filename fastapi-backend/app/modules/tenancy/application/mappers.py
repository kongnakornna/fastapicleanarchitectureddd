"""tenancy application mappers."""

from ..domain.entities import Tenant


class TenantMapper:
    """TenantMapper — แปลง Tenant <-> dict."""

    @staticmethod
    def to_dict(t: Tenant) -> dict:
        return {
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "plan": t.plan,
            "status": t.status,
            "schema_name": t.schema_name,
            "owner_email": t.owner_email,
            "max_users": t.max_users,
            "max_storage_gb": t.max_storage_gb,
        }

    @staticmethod
    def from_dict(data: dict) -> Tenant:
        return Tenant(
            id=data.get("id", ""),
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            plan=data.get("plan", "FREE"),
            status=data.get("status", "ACTIVE"),
            schema_name=data.get("schema_name", ""),
            owner_email=data.get("owner_email", ""),
            max_users=data.get("max_users", 5),
            max_storage_gb=data.get("max_storage_gb", 1),
        )
