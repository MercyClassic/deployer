from typing import Any

import pytest

from deployer.domain.entities.project_configs import DockerConfig

REQUIRED = {
    'image': 'myapp:latest',
    'registry_url': 'registry.example.com',
    'volumes': None,
    'ports': None,
    'network': None,
    'env': None,
}


@pytest.mark.parametrize('kwargs,expected', [
    (
        REQUIRED,
        REQUIRED,
    ),
    (
        {**REQUIRED, 'ports': [('8080', '80'), ('4430', '443')]},
        {**REQUIRED, 'ports': [('8080', '80'), ('4430', '443')]},
    ),
    (
        {**REQUIRED, 'volumes': {'/host/data': '/container/data'}},
        {**REQUIRED, 'volumes': {'/host/data': '/container/data'}},
    ),
    (
        {**REQUIRED, 'network': 'mynetwork'},
        {**REQUIRED, 'network': 'mynetwork'},
    ),
    (
        {**REQUIRED, 'env': {'DEBUG': 'true', 'PORT': '8080'}},
        {**REQUIRED, 'env': {'DEBUG': 'true', 'PORT': '8080'}},
    ),
])
def test_docker_config_creates(kwargs: dict[str, Any], expected: dict[str, Any]):
    config = DockerConfig(**kwargs)
    assert config.to_dict() == expected


@pytest.mark.parametrize('kwargs', [
    {},
    {'image': 'myapp:latest'},
    {**REQUIRED, 'image': 123},
    {**REQUIRED, 'ports': '8080:80'},
    {**REQUIRED, 'volumes': 'not a dict'},
    {**REQUIRED, 'unexpected_field': 'value'},
])
def test_docker_config_fails(kwargs: dict[str, Any]):
    with pytest.raises(ValueError):
        DockerConfig(**kwargs)