"""CLI principal. Entry point: `pgk ...`.

Subcomandos iniciales (esqueleto):
- `pgk ana "<mensaje>"`: conversacion con Ana.
- `pgk doctor`: comprueba entorno (BDs, LLMs, rutas).
- `pgk version`: version del paquete.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from pgk_operativa import __version__
from pgk_operativa.core.config import get_settings
from pgk_operativa.core.graph import run as run_graph
from pgk_operativa.core.llm import available_providers, default_config, pick_consensus_pair
from pgk_operativa.core.paths import (
    REPO_ROOT,
    data_root,
    engram_path,
    memoria_operativa_path,
)
from pgk_operativa.verificador.auditor import audit, default_repos_root, informes_dir
from pgk_operativa.verificador.manifest import Manifest, list_manifests, manifests_dir
from pgk_operativa.verificador.report import Severity

app = typer.Typer(
    help="pgk_operativa: super-agente unificado PGK.",
    no_args_is_help=True,
    rich_markup_mode=None,
)
console = Console()


@app.command()
def version() -> None:
    """Muestra la version instalada."""
    console.print(f"pgk_operativa {__version__}")


@app.command()
def ana(
    mensaje: str = typer.Argument(..., help="Mensaje para Ana."),
    consenso: bool = typer.Option(
        False,
        "--consenso",
        help="Activa consenso explicito (2 proveedores distintos).",
    ),
    nif: str | None = typer.Option(None, "--nif", help="NIF/NIE del cliente."),
    nombre: str | None = typer.Option(None, "--nombre", help="Nombre del cliente."),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Modo diagnostico: muestra modulo interno y razonamiento (uso tecnico).",
    ),
) -> None:
    """Envia un mensaje a Ana.

    Por defecto Ana responde con 1 solo modelo (Z.ai GLM coding plan).
    Con `--consenso`, dispara 2 proveedores distintos (assert en runtime).

    Ana es la unica cara visible: por defecto NO se exponen nombres de
    modulos internos (fiscal, contable, laboral, legal, docs, marketing).
    Usar `--debug` solo en desarrollo para inspeccionar el routing.
    """
    cfg = default_config()
    console.print(f"[bold cyan]Ana[/bold cyan] (default: {cfg.provider.value}/{cfg.model})")
    if consenso:
        pair = pick_consensus_pair()
        if pair is None:
            console.print(
                "[yellow]Aviso:[/yellow] solo 1 proveedor disponible. "
                "Consenso degradado a single_model."
            )
        else:
            a, b = pair
            console.print(
                f"[green]Consenso activo:[/green] "
                f"{a.provider.value}/{a.model} vs {b.provider.value}/{b.model}"
            )
    console.print(f"[dim]Cliente:[/dim] NIF={nif or '(sin nif)'} Nombre={nombre or '(sin nombre)'}")
    console.print(f"[dim]Mensaje:[/dim] {mensaje}")
    console.print()

    try:
        resultado = run_graph(mensaje, nif=nif, nombre=nombre, consenso=consenso)
    except RuntimeError as exc:
        console.print(f"[red]Error de configuracion:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    respuesta = resultado.get("respuesta_final", "(respuesta vacia)")
    if debug:
        modulo = resultado.get("modulo_tecnico", "general")
        razon = resultado.get("clasificacion_razonamiento", "")
        console.print(f"[dim]debug modulo={modulo} razon={razon}[/dim]")
        console.print()
    console.print(respuesta)


@app.command()
def doctor() -> None:
    """Diagnostico del entorno: rutas, BDs, proveedores LLM."""
    s = get_settings()
    providers = available_providers()
    pair = pick_consensus_pair()

    table = Table(title="pgk_operativa doctor", show_header=True)
    table.add_column("Componente")
    table.add_column("Estado")
    table.add_column("Detalle")

    table.add_row("Version", "OK", __version__)
    table.add_row("Entorno", "OK", s.environment)
    table.add_row("Repo root", "OK", str(REPO_ROOT))
    table.add_row("Data root", "OK", str(data_root()))
    table.add_row(
        "memoria_operativa.db",
        "OK" if memoria_operativa_path().parent.exists() else "PEND",
        str(memoria_operativa_path()),
    )
    table.add_row(
        "engram.db", "OK" if engram_path().parent.exists() else "PEND", str(engram_path())
    )

    table.add_row(
        "Postgres remoto",
        "CONFIG" if s.ssh_user else "PEND",
        f"{s.ssh_user or '?'}@{s.ssh_host}:{s.ssh_port} -> {s.db_name}.{s.db_schema}",
    )

    table.add_row(
        "LLM default (Z.ai)",
        "OK" if s.has_zai() else "FALTA",
        f"{s.zai_openai_base_url} model={s.zai_openai_model}",
    )
    table.add_row(
        "Proveedores disponibles",
        f"{len(providers)} / 6",
        ", ".join(p.value for p in providers) or "(ninguno)",
    )
    if pair:
        a, b = pair
        table.add_row(
            "Consenso opt-in listo",
            "OK",
            f"{a.provider.value}/{a.model} vs {b.provider.value}/{b.model}",
        )
    else:
        table.add_row(
            "Consenso opt-in listo",
            "NO",
            "Se necesitan al menos 2 proveedores distintos.",
        )

    console.print(table)


@app.command()
def verificar(
    pr: int | None = typer.Option(
        None, "--pr", help="Numero de PR a auditar. Si se omite, auditar --all."
    ),
    todos: bool = typer.Option(False, "--all", help="Audita todos los manifests disponibles."),
    repos_root: Path | None = typer.Option(
        None,
        "--repos-root",
        help="Directorio raiz de repos origen. Default: ~/repos/.",
        exists=False,
    ),
    salida: Path | None = typer.Option(
        None,
        "--salida",
        help="Directorio destino de informes. Default: informes/auditoria/.",
    ),
    bloquear_high: bool = typer.Option(
        False,
        "--bloquear-high",
        help="Sale con codigo 3 si hay HIGH (ademas del 2 por CRITICAL).",
    ),
    semantico: bool = typer.Option(
        False,
        "--semantico",
        help="Anade check LLM (Z.ai GLM-4.6) que compara origen con destino. Coste extra.",
    ),
) -> None:
    """Auditor hacia atras: verifica fidelidad de un PR contra su manifest.

    Genera informe Markdown en `informes/auditoria/PR-XXXX.md`.

    Exit codes:
    - 0: sin hallazgos CRITICAL.
    - 2: al menos un hallazgo CRITICAL (bloquea merge), o error de carga
      del manifest cuando no hay hallazgos de mayor prioridad.
    - 3: con --bloquear-high, al menos un hallazgo HIGH.
    """
    rr = repos_root or default_repos_root()
    out_dir = salida or informes_dir()

    if pr is not None and todos:
        console.print("[red]Error:[/red] --pr y --all son mutuamente excluyentes.")
        raise typer.Exit(code=2)

    if pr is None and not todos:
        console.print("[yellow]Uso:[/yellow] pgk verificar --pr N  |  pgk verificar --all")
        raise typer.Exit(code=2)

    # Sin esta guarda, `--pr 0` generaba `PR-0000.yaml` (no existe: el
    # numerado empieza en 1) y `--pr -5` generaba `PR--005.yaml` (Path
    # invalido). En ambos casos terminaba en FileNotFoundError confuso.
    if pr is not None and pr <= 0:
        console.print(f"[red]Error:[/red] --pr debe ser entero positivo, got {pr}.")
        raise typer.Exit(code=2)

    manifests: list[Path]
    if pr is not None:
        manifests = [manifests_dir() / f"PR-{pr:04d}.yaml"]
    else:
        manifests = list_manifests()
        if not manifests:
            console.print(f"[yellow]No hay manifests en {manifests_dir()}.[/yellow]")
            raise typer.Exit(code=0)

    any_critical = False
    any_high = False
    any_load_error = False
    for manifest_path in manifests:
        try:
            manifest = Manifest.load(manifest_path)
        except (FileNotFoundError, ValueError) as exc:
            console.print(f"[red]Error leyendo {manifest_path.name}:[/red] {exc}")
            any_load_error = True
            continue

        report = audit(manifest, repo_root=REPO_ROOT, repos_root=rr, semantico=semantico)
        out_path = out_dir / f"PR-{manifest.pr:04d}.md"
        report.save(out_path)

        table = Table(title=f"PR #{manifest.pr:04d} - {manifest.titulo}", show_header=True)
        table.add_column("Severidad")
        table.add_column("N")
        for sev in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW):
            n = len(report.by_severity(sev))
            color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "dim"}[sev.label]
            table.add_row(f"[{color}]{sev.label}[/{color}]", str(n))
        console.print(table)
        console.print(f"[dim]Informe: {out_path}[/dim]")

        if report.has_critical:
            any_critical = True
        if report.has_high:
            any_high = True

    # Prioridad explicita: CRITICAL > HIGH (cuando --bloquear-high) > error de carga > OK.
    # Jamas enmascarar CRITICAL con un codigo mayor. Error de carga es la prioridad
    # mas baja entre las fallas: solo reporta exit 2 si no hubo HIGH con bloqueo activo.
    if any_critical:
        raise typer.Exit(code=2)
    if bloquear_high and any_high:
        raise typer.Exit(code=3)
    if any_load_error:
        raise typer.Exit(code=2)


@app.command("admin-alta")
def admin_alta(
    email: str = typer.Option(..., "--email", help="Email logico del empleado."),
    nombre: str = typer.Option(..., "--nombre", help="Nombre del empleado."),
) -> None:
    """Alta de empleado nuevo (stub, activa en Semana 1)."""
    console.print(
        f"[yellow]STUB[/yellow] alta empleado "
        f"email={email} nombre={nombre}. "
        f"Generara emp_<slug>_<uuid4> y fila en users (grupo pgk_empleado)."
    )


if __name__ == "__main__":
    app()
