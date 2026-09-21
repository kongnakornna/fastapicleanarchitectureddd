from .entities import Role, User


class ListUsersUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, *, page: int = 1, q: str = "") -> dict:
        return self.repo.list_users(page=page, q=q)


class GetUserUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, user_id: int) -> User:
        return self.repo.get_user(user_id)


class CreateUserUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, payload: dict) -> User:
        return self.repo.create_user(payload)


class UpdateUserUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, user_id: int, payload: dict) -> User:
        return self.repo.update_user(user_id, payload)


class DeleteUserUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, user_id: int) -> None:
        return self.repo.delete_user(user_id)


# ─── Roles ─────────────────────────────
class ListRolesUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self) -> list[Role]:
        return self.repo.list_roles()


class GetRoleUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, role_id: int) -> Role:
        return self.repo.get_role(role_id)


class CreateRoleUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, payload: dict) -> Role:
        return self.repo.create_role(payload)


class UpdateRoleUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, role_id: int, payload: dict) -> Role:
        return self.repo.update_role(role_id, payload)


class DeleteRoleUseCase:
    def __init__(self, repo): self.repo = repo
    def execute(self, role_id: int) -> None:
        return self.repo.delete_role(role_id)
