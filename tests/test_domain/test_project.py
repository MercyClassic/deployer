import pytest

from deployer.domain.entities.deployment import DeploymentStatus
from deployer.domain.entities.project import DeployStrategy, Project
from deployer.domain.exceptions.deployment import DeployAlreadyRunning, DeployFailed
from deployer.domain.exceptions.project import (
    ActiveConfigNotFound,
    ImpossibleProjectConfigVersion,
    InvalidConfigFormat,
    InvalidDeployStrategy,
)
from deployer.domain.exceptions.user import AccessDenied
from tests.conftest import (
    make_deployment,
    make_project,
    make_server,
    make_shell_config,
)


class TestCheckUserPermitted:
    def test_owner_has_access(self, project):
        project.check_user_permitted(user_id=project.user_id)

    def test_other_user_raises(self, project):
        with pytest.raises(AccessDenied):
            project.check_user_permitted(user_id=999)

    @pytest.mark.parametrize(
        'owner_id,caller_id',
        [
            (1, 2),
            (42, 1),
            (100, 99),
        ],
    )
    def test_various_user_combinations(self, owner_id, caller_id):
        p = make_project(user_id=owner_id)
        with pytest.raises(AccessDenied):
            p.check_user_permitted(user_id=caller_id)


class TestCheckDeployPossible:
    def test_fails_without_servers(self, project):
        project.configs.append(make_shell_config())
        with pytest.raises(DeployFailed):
            project.check_deploy_possible()

    def test_fails_without_active_config(self, project, server):
        project.servers.append(server)
        with pytest.raises(DeployFailed):
            project.check_deploy_possible()

    def test_fails_when_deploy_already_running(self, project, server):
        project.servers.append(server)
        project.configs.append(make_shell_config())
        project.deployments.append(make_deployment(status=DeploymentStatus.running))
        with pytest.raises(DeployAlreadyRunning):
            project.check_deploy_possible()

    def test_passes_when_all_conditions_met(self, project, server):
        project.servers.append(server)
        project.configs.append(make_shell_config())
        project.check_deploy_possible()  # не падает

    def test_passes_when_previous_deploy_finished(self, project, server):
        project.servers.append(server)
        project.configs.append(make_shell_config())
        project.deployments.append(make_deployment(status=DeploymentStatus.success))
        project.check_deploy_possible()  # не падает

    @pytest.mark.parametrize(
        'status',
        [
            DeploymentStatus.success,
            DeploymentStatus.failed,
            DeploymentStatus.pending,
        ],
    )
    def test_passes_for_non_running_statuses(self, project, server, status):
        project.servers.append(server)
        project.configs.append(make_shell_config())
        project.deployments.append(make_deployment(status=status))
        project.check_deploy_possible()  # не падает


class TestUpdateConfig:
    def test_first_config_is_version_1(self, project):
        config = project.update_config({'commands': ['echo hello']})
        assert config.version == 1
        assert config.is_active is True

    def test_new_config_deactivates_old(self, project):
        old = project.update_config({'commands': ['echo hello']})
        assert old.is_active is True

        project.update_config({'commands': ['echo world']})
        assert old.is_active is False

    def test_new_config_increments_version(self, project):
        project.update_config({'commands': ['echo hello']})
        new = project.update_config({'commands': ['echo world']})
        assert new.version == 2

    def test_only_one_active_config_at_a_time(self, project):
        project.update_config({'commands': ['echo 1']})
        project.update_config({'commands': ['echo 2']})
        project.update_config({'commands': ['echo 3']})

        active = [c for c in project.configs if c.is_active]
        assert len(active) == 1

    def test_invalid_config_format_raises(self, project):
        with pytest.raises(InvalidConfigFormat):
            project.update_config({'invalid_key': 'value'})

    def test_active_config_returns_latest(self, project):
        project.update_config({'commands': ['echo 1']})
        project.update_config({'commands': ['echo 2']})
        assert project.active_config.version == 2

    def test_active_config_raises_when_no_configs(self, project):
        with pytest.raises(ActiveConfigNotFound):
            _ = project.active_config


class TestRollbackConfig:
    def test_rollback_to_previous_version(self, project):
        project.update_config({'commands': ['echo 1']})
        project.update_config({'commands': ['echo 2']})

        rolled = project.rollback_config(version=1)
        assert rolled.version == 1
        assert rolled.is_active is True

    def test_rollback_removes_newer_versions(self, project):
        project.update_config({'commands': ['echo 1']})
        project.update_config({'commands': ['echo 2']})
        project.update_config({'commands': ['echo 3']})

        project.rollback_config(version=1)
        versions = [
            c.version
            for c in project.configs
            if c.strategy == project.deploy_strategy
        ]
        assert 2 not in versions
        assert 3 not in versions

    @pytest.mark.parametrize('version', [0, 999])
    def test_rollback_to_nonexistent_version_raises(self, project, version):
        project.update_config({'commands': ['echo 1']})
        with pytest.raises(ImpossibleProjectConfigVersion):
            project.rollback_config(version=version)

    def test_rollback_to_current_version_raises(self, project):
        project.update_config({'commands': ['echo 1']})
        with pytest.raises(ImpossibleProjectConfigVersion):
            project.rollback_config(version=1)


class TestServerManagement:
    def test_create_server_appends_to_list(self, project):
        project.create_server(
            name='srv',
            host='1.2.3.4',
            ssh_user='user',
            ssh_secret='secret',
            workdir='/app',
            port=22,
        )
        assert len(project.servers) == 1

    def test_delete_server_removes_from_list(self, project, server):
        project.servers.append(server)
        project.delete_server(server_id=server.id)
        assert len(project.servers) == 0

    def test_delete_nonexistent_server_is_noop(self, project):
        project.delete_server(server_id=999)
        assert len(project.servers) == 0

    def test_multiple_servers_delete_only_target(self, project):
        s1 = make_server()
        s1.id = 1
        s2 = make_server()
        s2.id = 2
        project.servers = [s1, s2]

        project.delete_server(server_id=1)
        assert len(project.servers) == 1
        assert project.servers[0].id == 2


class TestDeployStrategy:
    @pytest.mark.parametrize('strategy', ['shell', 'git', 'docker'])
    def test_valid_strategy(self, project, strategy):
        project.set_deploy_strategy(strategy)
        assert project.deploy_strategy == DeployStrategy(strategy)

    def test_invalid_strategy_raises(self, project):
        with pytest.raises(InvalidDeployStrategy):
            project.set_deploy_strategy('kubernetes')

    def test_create_project_with_invalid_strategy_raises(self):
        with pytest.raises(InvalidDeployStrategy):
            Project.create(user_id=1, name='test', deploy_strategy='invalid')
