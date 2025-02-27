"""A pip-wrapper that injects platform-specific constraints into pip."""

from __future__ import annotations

import sys

from pip_constraint_helpers import (
    get_constraint_file_path, get_runtime_python_tag, make_pip_cmd, run_cmd,
)


def main(req_dir: str, toxenv: str, *pip_args: tuple[str, ...]) -> None:
    """Invoke pip with the matching constraints file, if present.

    :param req_dir: Requirements directory path.
    :param toxenv: Tox env name.
    :param pip_args: Iterable of args to bypass to pip.
    """
    constraint_file_path = get_constraint_file_path(
        req_dir=req_dir,
        toxenv=toxenv,
        python_tag=get_runtime_python_tag(),
    )
    pip_cmd = make_pip_cmd(
        pip_args=list(pip_args),
        constraint_file_path=constraint_file_path,
    )
    run_cmd(pip_cmd)


if __name__ == '__main__':
    main(*sys.argv[1:])
