from uuid import uuid4

from app.modules.user.domain.permission_entities import (
    Permission,
    Role_,
    RolePermission,
    UserRole,
)


class TestPermission:
    def test_construction(self):
        p = Permission(name="read", resource="users", action="read")
        assert p.name == "read"
        assert p.resource == "users"
        assert p.action == "read"
        assert p.description is None
        assert p.is_active is True

    def test_with_description(self):
        p = Permission(
            name="write",
            resource="posts",
            action="create",
            description="Can create posts",
        )
        assert p.description == "Can create posts"

    def test_id_defaults_to_none(self):
        p = Permission(name="x", resource="x", action="x")
        assert p.id is None

    def test_with_explicit_id(self):
        uid = uuid4()
        p = Permission(name="x", resource="x", action="x", id=uid)
        assert p.id == uid


class TestRole:
    def test_construction(self):
        r = Role_(name="admin")
        assert r.name == "admin"
        assert r.description is None
        assert r.is_active is True

    def test_with_description(self):
        r = Role_(name="manager", description="Can manage users")
        assert r.description == "Can manage users"

    def test_id_defaults_to_none(self):
        r = Role_(name="x")
        assert r.id is None


class TestUserRole:
    def test_construction(self):
        uid, rid = uuid4(), uuid4()
        ur = UserRole(user_id=uid, role_id=rid)
        assert ur.user_id == uid
        assert ur.role_id == rid
        assert ur.id is None


class TestRolePermission:
    def test_construction(self):
        rid, pid = uuid4(), uuid4()
        rp = RolePermission(role_id=rid, permission_id=pid)
        assert rp.role_id == rid
        assert rp.permission_id == pid
        assert rp.id is None
