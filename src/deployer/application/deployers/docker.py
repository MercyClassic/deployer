from deployer.application.deployers.base import DeployerStrategy
from deployer.domain.entities.project import Server
from deployer.domain.entities.project_configs import DockerConfig


class DockerDeployer(DeployerStrategy):
    async def _deploy(
        self,
        config: DockerConfig,
        servers: list[Server],
    ) -> None:
        for server in servers:
            with self._ssh_client(
                host=server.host,
                user=server.ssh_user,
                password=server.ssh_secret,
                port=server.port,
            ) as ssh_client:
                self._run_command(
                    ssh_client,
                    f'docker pull {config.registry_url}/{config.image}',
                )

                cmd = f'docker run -d --name {config.image.replace(":", "_")}'
                if config.volumes:
                    cmd += ''.join(
                        f' -v {host}:{container}'
                        for host, container in config.volumes.items()
                    )
                if config.ports:
                    cmd += ''.join(
                        f' -p {host}:{container}' for host, container in config.ports
                    )
                if config.network:
                    cmd += f' --network {config.network}'
                if config.env:
                    cmd += ''.join(f' -e {k}="{v}"' for k, v in config.env.items())
                cmd += f' {config.registry_url}/{config.image}'

                self._run_command(ssh_client, cmd)
