"""Project-local tox env customizations."""

from base64 import b64encode
from hashlib import sha256
from logging import getLogger
from os import environ, getenv
from pathlib import Path

from tox.execute.request import StdinSource
from tox.plugin import impl
from tox.tox_env.api import ToxEnv


IS_GITHUB_ACTIONS_RUNTIME = getenv('GITHUB_ACTIONS') == 'true'
FILE_APPEND_MODE = 'a'


logger = getLogger(__name__)


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    """Inject SOURCE_DATE_EPOCH env var into build-dists."""
    if tox_env.name == 'build-dists':
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
        dists_dir_path = Path(__file__).parent / 'dist'
        emulated_sha256sum_output = '\n'.join(
            _produce_sha256sum_line(artifact_path)
            for artifact_path in dists_dir_path.glob('*')
        )
        emulated_base64_w0_output = b64encode(
            emulated_sha256sum_output.encode(),
        ).decode()

        with Path(environ['GITHUB_OUTPUT']).open(
            mode=FILE_APPEND_MODE,
        ) as outputs_file:
            print(  # noqa: WPS421
                'combined-dists-base64-encoded-sha256-hash='
                f'{emulated_base64_w0_output !s}',
                file=outputs_file,
            )
