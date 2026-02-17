from deployer.domain.exceptions.base import DomainError


class UnsupportedStrategy(DomainError):
    pass


class DeploymentNotFound(DomainError):
    pass


class DeployFailed(DomainError):
    pass


class DeployAlreadyRunning(DomainError):
    pass
