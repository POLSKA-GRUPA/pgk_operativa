"""Checks estaticos del verificador.

Cada modulo expone una funcion `run(manifest, repo_root, repos_root) -> list[Finding]`.
"""

from pgk_operativa.verificador.checks.fidelity_check import run as fidelity_check
from pgk_operativa.verificador.checks.imports_check import run as imports_check
from pgk_operativa.verificador.checks.lines_check import run as lines_check
from pgk_operativa.verificador.checks.shell_check import run as shell_check
from pgk_operativa.verificador.checks.targets_check import run as targets_check
from pgk_operativa.verificador.checks.tests_check import run as tests_check
from pgk_operativa.verificador.checks.todo_check import run as todo_check

__all__ = [
    "fidelity_check",
    "imports_check",
    "lines_check",
    "shell_check",
    "targets_check",
    "tests_check",
    "todo_check",
]
