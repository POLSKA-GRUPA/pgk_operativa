"""Verificador de fidelidad: auditor hacia atras de PRs.

Objetivo: asegurar que el codigo portado desde los repos origen
(PGK_Empresa_Autonoma, conta-pgk-hispania, pgk-laboral-desk, junior,
PROGRAMADOR_FRIKI_PGK) se ha copiado de forma fiel, sin caparazones
vacios, imports rotos, rutas obsoletas o funciones sin cuerpo.

Uso:
    pgk verificar --pr 4
    pgk verificar --all

Manifest obligatorio por PR en `docs/pr_manifests/PR-XXXX.yaml`.
"""

from pgk_operativa.verificador.manifest import Manifest, Relacion
from pgk_operativa.verificador.report import Report, Severity

__all__ = ["Manifest", "Relacion", "Report", "Severity"]
