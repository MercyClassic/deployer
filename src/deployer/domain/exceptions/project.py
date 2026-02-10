from deployer.domain.exceptions.base import DomainError


class ActiveConfigNotFound(DomainError):
    pass


class ImpossibleProjectConfigVersion(DomainError):
    pass


class ProjectNotFound(DomainError):
    pass


class InvalidConfigFormat(DomainError):
    pass


class InvalidDeployStrategy(DomainError):
    pass
