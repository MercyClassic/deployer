from deployer.application.deployers.base import DeployerStrategy
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import ShellConfig


class ShellDeployer(DeployerStrategy):
    async def _deploy(
        self,
        config: ShellConfig,
        servers: list[Server],
    ) -> None:
        for server in servers:
            with self._ssh_client(
                host=server.host,
                user=server.ssh_user,
                password=server.ssh_secret,
                port=server.port,
            ) as ssh_client:
                for command in config.commands:
                    self._run_command(
                        ssh_client, f'cd {server.workdir} && {command}'
                    )
