"""Project-local tox env customizations."""

from logging import getLogger
from subprocess import SubprocessError, check_output  # noqa: S404

from tox.plugin import impl
from tox.tox_env.api import ToxEnv


logger = getLogger(__name__)


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    """Inject SOURCE_DATE_EPOCH env var into build-dists."""
    if tox_env.name == 'build-dists':
        # NOTE: `tox_env.execute()` produces ANSI escape sequences that cannot
        # NOTE: be turned off for some reason. This is why the following
        # NOTE: invocation relies on the good old `subprocess` from stdlib.
        git_log_cmd = 'git', 'log', '-1', '--pretty=%ct'  # noqa: WPS323
        try:
            git_head_timestamp = check_output(  # noqa: S603
                git_log_cmd, text=True,
            ).strip()
        except SubprocessError as git_err:
            logger.warning(
                'Failed to look up Git HEAD timestamp: %s',  # noqa: WPS323
                str(git_err),
            )
            return

        logger.info(
            'Setting `SOURCE_DATE_EPOCH=%s` environment '  # noqa: WPS323
            'variable to facilitate with build reproducibility',
            git_head_timestamp,
        )
        tox_env.environment_variables['SOURCE_DATE_EPOCH'] = git_head_timestamp
