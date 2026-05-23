import datetime

import pytest

from deployer.domain.entities.deployment import Deployment, DeploymentStatus
from tests.conftest import make_deployment


class TestDeploymentCreate:
    def test_create_sets_status(self):
        d = Deployment.create(project_id=1, status=DeploymentStatus.pending)
        assert d.status == DeploymentStatus.pending

    def test_create_sets_project_id(self):
        d = Deployment.create(project_id=42, status=DeploymentStatus.pending)
        assert d.project_id == 42

    def test_create_has_no_std(self):
        d = Deployment.create(project_id=1, status=DeploymentStatus.pending)
        assert d.std is None

    def test_create_has_no_finished_at(self):
        d = Deployment.create(project_id=1, status=DeploymentStatus.pending)
        assert d.finished_at is None


class TestDeploymentStatusTransitions:
    def test_set_running_status(self):
        d = make_deployment(status=DeploymentStatus.pending)
        d.set_running_status()
        assert d.status == DeploymentStatus.running

    def test_set_success_status(self):
        d = make_deployment(status=DeploymentStatus.running)
        d.set_success_status()
        assert d.status == DeploymentStatus.success

    def test_set_failed_status(self):
        d = make_deployment(status=DeploymentStatus.running)
        d.set_failed_status()
        assert d.status == DeploymentStatus.failed

    @pytest.mark.parametrize(
        'initial_status',
        [
            DeploymentStatus.pending,
            DeploymentStatus.running,
            DeploymentStatus.success,
            DeploymentStatus.failed,
        ],
    )
    def test_set_running_from_any_status(self, initial_status):
        d = make_deployment(status=initial_status)
        d.set_running_status()
        assert d.status == DeploymentStatus.running

    def test_typical_flow_pending_running_success(self):
        d = make_deployment(status=DeploymentStatus.pending)
        d.set_running_status()
        assert d.status == DeploymentStatus.running
        d.set_success_status()
        assert d.status == DeploymentStatus.success

    def test_typical_flow_pending_running_failed(self):
        d = make_deployment(status=DeploymentStatus.pending)
        d.set_running_status()
        assert d.status == DeploymentStatus.running
        d.set_failed_status()
        assert d.status == DeploymentStatus.failed


class TestDeploymentFields:
    def test_set_std(self):
        d = make_deployment()
        d.set_std('some logs')
        assert d.std == 'some logs'

    def test_set_std_overwrites(self):
        d = make_deployment()
        d.set_std('first')
        d.set_std('second')
        assert d.std == 'second'

    def test_set_finished_at_sets_utc_datetime(self):
        d = make_deployment()
        before = datetime.datetime.now(datetime.UTC)
        d.set_finished_at()
        after = datetime.datetime.now(datetime.UTC)
        assert before <= d.finished_at <= after

    def test_set_finished_at_is_aware(self):
        d = make_deployment()
        d.set_finished_at()
        assert d.finished_at.tzinfo is not None
