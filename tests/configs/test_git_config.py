import pytest

from deployer.domain.entities.project_configs import GitConfig


@pytest.mark.parametrize(
    'kwargs,expected',
    [
        (
            {'repository_url': 'https://github.com/user/repo'},
            {
                'repository_url': 'https://github.com/user/repo',
                'branch': 'master',
                'with_entrypoint': True,
            },
        ),
        (
            {'repository_url': 'https://github.com/user/repo', 'branch': 'develop'},
            {
                'repository_url': 'https://github.com/user/repo',
                'branch': 'develop',
                'with_entrypoint': True,
            },
        ),
        (
            {
                'repository_url': 'https://github.com/user/repo',
                'branch': 'main',
                'with_entrypoint': False,
            },
            {
                'repository_url': 'https://github.com/user/repo',
                'branch': 'main',
                'with_entrypoint': False,
            },
        ),
    ],
)
def test_git_config_creates(kwargs, expected):
    config = GitConfig(**kwargs)
    assert config.to_dict() == expected


@pytest.mark.parametrize(
    'kwargs',
    [
        {},
        {'repository_url': 123},
        {'repository_url': 'https://github.com/user/repo', 'branch': 123},
        {'repository_url': 'https://github.com/user/repo', 'with_entrypoint': 'yes'},
        {
            'repository_url': 'https://github.com/user/repo',
            'unexpected_field': 'value',
        },
    ],
)
def test_git_config_fails(kwargs):
    with pytest.raises(ValueError):
        GitConfig(**kwargs)
