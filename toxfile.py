"""Project-local tox env customizations."""

from logging import getLogger

from tox.execute.request import StdinSource
from tox.plugin import impl
from tox.tox_env.api import ToxEnv


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
