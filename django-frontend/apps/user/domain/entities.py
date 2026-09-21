from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: str
    full_name: str
    phone_number: str
    role_id: int
    role_name: str
    is_active: bool = True


@dataclass(frozen=True)
class Role:
    id: int
    name: str
    description: str
    permissions: list[str]
