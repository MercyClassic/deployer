from deployer.domain.exceptions.base import DomainError


class UserNotFound(DomainError):
    pass


class AccessDenied(DomainError):
    pass
