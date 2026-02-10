from deployer.application.deployers.base import DeployerStrategy
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import GitConfig


class GitDeployer(DeployerStrategy):
    async def _deploy(
        self,
        config: GitConfig,
        servers: list[Server],
    ) -> None:
        for server in servers:
            with self._ssh_client(
                host=server.host,
                user=server.ssh_user,
                password=server.ssh_secret,
                port=server.port,
            ) as ssh_client:
                cmd = f'cd {server.workdir} && git clone -b {config.branch} {config.repository_url}'
                if config.with_entrypoint:
                    cmd += ' && entrypoint.sh'

                self._run_command(ssh_client, cmd)
