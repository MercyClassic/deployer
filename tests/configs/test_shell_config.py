import pytest

from deployer.domain.entities.project_configs import ShellConfig


@pytest.mark.parametrize('commands', [
    ['echo hello'],
    ['echo hello', 'ls -la'],
    ['echo hello', 'ls -la', 'pwd'],
])
def test_shell_config_creates(commands):
    config = ShellConfig(commands=commands)
    assert config.commands == commands


@pytest.mark.parametrize('commands', [
    ['echo hello'],
    ['echo hello', 'ls -la'],
])
def test_shell_config_to_dict(commands):
    config = ShellConfig(commands=commands)
    assert config.to_dict() == {'commands': commands}


@pytest.mark.parametrize('kwargs', [
    {},
    {'commands': 'not a list'},
    {'commands': 123},
    {'commands': ['echo hello'], 'unexpected_field': 'value'},
])
def test_shell_config_fails(kwargs):
    with pytest.raises(ValueError):
        ShellConfig(**kwargs)