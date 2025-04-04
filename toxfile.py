"""Project-local tox env customizations."""

from base64 import b64encode
from functools import cached_property
from hashlib import sha256
from logging import getLogger
from os import environ, getenv
from pathlib import Path
from sys import path as _sys_path
from typing import cast

from tox.config.types import Command
from tox.execute.request import StdinSource
from tox.plugin import impl
from tox.tox_env.api import ToxEnv
from tox.tox_env.python.api import Python
from tox.tox_env.python.pip.pip_install import Pip as PipInstaller
from tox.tox_env.python.virtual_env.package.cmd_builder import (
    VirtualEnvCmdBuilder,
)
from tox.tox_env.python.virtual_env.package.pyproject import (
    Pep517VirtualEnvPackager,
)
from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner
from tox.tox_env.register import ToxEnvRegister


_sys_path[:0] = ['bin/']  # noqa: WPS362

# pylint: disable-next=wrong-import-position
from pip_constraint_helpers import (  # noqa: E402
    get_constraint_file_path, get_runtime_python_tag,
)


IS_GITHUB_ACTIONS_RUNTIME = getenv('GITHUB_ACTIONS') == 'true'
FILE_APPEND_MODE = 'a'
UNICODE_ENCODING = 'utf-8'
_PINNED_PREFIX = 'pinned-'


logger = getLogger(__name__)


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    """Inject SOURCE_DATE_EPOCH env var into build-dists."""
    if tox_env.name == 'build-dists':
        logger.debug(
            'toxfile:tox_before_run_commands> Setting the Git HEAD-based '
            'epoch for reproducibility in GHA...',
        )
        git_executable = 'git'
        git_log_cmd = (
            git_executable,
            '-c', 'core.pager=',  # prevents ANSI escape sequences
            'log',
            '-1',
            '--pretty=%ct',  # noqa: WPS323
        )
        tox_env.conf['allowlist_externals'].append(git_executable)
        git_log_outcome = tox_env.execute(git_log_cmd, StdinSource.OFF)
        tox_env.conf['allowlist_externals'].pop()
        if git_log_outcome.exit_code:
            logger.warning(
                'Failed to look up Git HEAD timestamp. %s',  # noqa: WPS323
                git_log_outcome,
            )
            return

        git_head_timestamp = git_log_outcome.out.strip()

        logger.info(
            'Setting `SOURCE_DATE_EPOCH=%s` environment '  # noqa: WPS323
            'variable to facilitate with build reproducibility',
            git_head_timestamp,
        )
        tox_env.environment_variables['SOURCE_DATE_EPOCH'] = git_head_timestamp


def _compute_sha256sum(file_path: Path) -> str:
    return sha256(file_path.read_bytes()).hexdigest()


def _produce_sha256sum_line(file_path: Path) -> str:
    sha256_str = sha256(file_path.read_bytes()).hexdigest()
    return f'{sha256_str !s}  {file_path.name !s}'


@impl
def tox_after_run_commands(tox_env: ToxEnv) -> None:
    """Compute combined dists hash post build-dists under GHA."""
    if tox_env.name == 'build-dists' and IS_GITHUB_ACTIONS_RUNTIME:
        logger.debug(
            'toxfile:tox_after_run_commands> Computing and storing the base64 '
            'representation of the combined dists SHA-256 hash in GHA...',
        )
        dists_dir_path = Path(__file__).parent / 'dist'
        emulated_sha256sum_output = '\n'.join(
            _produce_sha256sum_line(artifact_path)
            for artifact_path in dists_dir_path.glob('*')
        )
        emulated_base64_w0_output = b64encode(
            emulated_sha256sum_output.encode(),
        ).decode()

        with Path(environ['GITHUB_OUTPUT']).open(
            encoding=UNICODE_ENCODING,
            mode=FILE_APPEND_MODE,
        ) as outputs_file:
            print(  # noqa: WPS421
                'combined-dists-base64-encoded-sha256-hash='
                f'{emulated_base64_w0_output !s}',
                file=outputs_file,
            )


class PinnedPipInstaller(PipInstaller):
    """A constraint-aware pip installer."""

    _non_existing_constraint_files: set[Path] = set()

    def post_process_install_command(self, cmd: Command) -> Command:
        """Inject an env-specific constraint into pip install."""
        constraint_file_path = get_constraint_file_path(
            req_dir='dependencies/lock-files/',
            toxenv=self._env.name,
            python_tag=get_runtime_python_tag(),
        )
        constraint_cli_arg = f'--constraint={constraint_file_path !s}'
        if constraint_cli_arg in cmd.args:
            logger.debug(
                'tox-lock:%s> `%s` CLI option is already a '  # noqa: WPS323
                'part of the install command. Skipping...',
                self._env.name,
                constraint_cli_arg,
            )
        elif constraint_file_path.is_file():
            logger.info(
                'tox-lock:%s> Applying the pinned constraints '  # noqa: WPS323
                'file `%s` to the current env...',  # noqa: WPS323
                self._env.name,
                constraint_file_path,
            )
            logger.debug(
                'tox-lock:%s> Injecting `%s` into the install '  # noqa: WPS323
                'command...',
                self._env.name,
                constraint_cli_arg,
            )
            cmd.args.append(constraint_cli_arg)
        else:
            if constraint_file_path not in self._non_existing_constraint_files:
                logger.warning(
                    'tox-lock:%s> The expected pinned '  # noqa: WPS323
                    'constraints file for the current env does not exist '
                    '(should be `%s`). Skipping...',  # noqa: WPS323
                    self._env.name,
                    constraint_file_path,
                )
            self._non_existing_constraint_files.add(constraint_file_path)

        return super().post_process_install_command(cmd)


# pylint: disable-next=too-few-public-methods
class PinnedPipInstallerSelectedMixin:
    """A base class with pinned pip installer."""

    @cached_property
    def installer(self) -> PinnedPipInstaller:
        """Return a constraint-aware pip installer."""
        return PinnedPipInstaller(cast(Python, self))


# pylint: disable-next=too-many-ancestors
class PinnedPep517VirtualEnvPackager(
        PinnedPipInstallerSelectedMixin, Pep517VirtualEnvPackager,
):
    """A pinned package env."""

    @staticmethod
    def id() -> str:  # noqa: WPS602, WPS605
        """Render a pinned virtualenv packager identifier."""
        return f'{_PINNED_PREFIX}{Pep517VirtualEnvPackager.id()}'


# pylint: disable-next=too-many-ancestors
class PinnedVirtualEnvCmdBuilder(
        PinnedPipInstallerSelectedMixin,
        VirtualEnvCmdBuilder,
):
    """A pinned run env."""

    @staticmethod
    def id() -> str:  # noqa: WPS602, WPS605
        """Render a pinned virtualenv command builder identifier."""
        return f'{_PINNED_PREFIX}{VirtualEnvCmdBuilder.id()}'


# pylint: disable-next=too-many-ancestors
class PinnedVirtualEnvRunner(
        PinnedPipInstallerSelectedMixin,
        VirtualEnvRunner,
):
    """A pinned virtualenv."""

    @staticmethod
    def id() -> str:  # noqa: WPS602, WPS605
        """Render a pinned virtualenv runner identifier."""
        return f'{_PINNED_PREFIX}{VirtualEnvRunner.id()}'

    @property
    def _package_tox_env_type(self) -> str:
        return f'{_PINNED_PREFIX}{super()._package_tox_env_type}'

    @property
    def _external_pkg_tox_env_type(self) -> str:
        return f'{_PINNED_PREFIX}{super()._external_pkg_tox_env_type}'


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    """Register locked virtualenv wrappers."""
    run_env_id = PinnedVirtualEnvRunner.id()

    logger.debug(
        'tox-lock:tox_register_tox_env> Registering the '  # noqa: WPS323
        'following run environment: %s',
        run_env_id,
    )
    register.add_run_env(PinnedVirtualEnvRunner)

    logger.debug(
        'tox-lock:tox_register_tox_env> Registering the '  # noqa: WPS323
        'following package environment: %s',
        PinnedPep517VirtualEnvPackager.id(),
    )
    register.add_package_env(PinnedPep517VirtualEnvPackager)

    logger.debug(
        'tox-lock:tox_register_tox_env> Registering the '  # noqa: WPS323
        'following package environment: %s',
        PinnedVirtualEnvCmdBuilder.id(),
    )
    register.add_package_env(PinnedVirtualEnvCmdBuilder)

    logger.debug(
        'tox-lock:tox_register_tox_env> Setting the default '  # noqa: WPS323
        'run environment to `%s`',
        run_env_id,
    )
    # pylint: disable-next=protected-access
    register._default_run_env = run_env_id  # noqa: SLF001, WPS437


def tox_append_version_info() -> str:
    """Produce text to be rendered in ``tox --version``."""
    return '[toxfile]'  # Broken: https://github.com/tox-dev/tox/issues/3508
