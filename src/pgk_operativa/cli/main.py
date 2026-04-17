"""CLI principal. Entry point: `pgk ...`.

Subcomandos iniciales (esqueleto):
- `pgk ana "<mensaje>"`: conversacion con Ana.
- `pgk doctor`: comprueba entorno (BDs, LLMs, rutas).
- `pgk version`: version del paquete.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from pgk_operativa import __version__
from pgk_operativa.core.config import get_settings
from pgk_operativa.core.llm import available_providers, default_config, pick_consensus_pair
from pgk_operativa.core.paths import (
    REPO_ROOT,
    data_root,
    engram_path,
    memoria_operativa_path,
)

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
) -> None:
    """Envia un mensaje a Ana.

    Por defecto Ana responde con 1 solo modelo (Z.ai GLM coding plan).
    Con `--consenso`, dispara 2 proveedores distintos (assert en runtime).
    """
    cfg = default_config()
    console.print(f"[bold cyan]Ana[/bold cyan] (default: {cfg.provider.value}/{cfg.model})")
    if consenso:
        pair = pick_consensus_pair()
        if pair is None:
            console.print(
                "[yellow]Aviso:[/yellow] solo 1 proveedor disponible. "
                "Degradando a consensus_type=single_model."
            )
        else:
            a, b = pair
            console.print(
                f"[green]Consenso activo:[/green] "
                f"{a.provider.value}/{a.model} vs {b.provider.value}/{b.model}"
            )
    console.print(f"[dim]Cliente:[/dim] NIF={nif} Nombre={nombre}")
    console.print(f"[dim]Mensaje:[/dim] {mensaje}")
    console.print()
    console.print(
        "[yellow]pgk ana aun no esta cableado al grafo.[/yellow] "
        "Esta version es el esqueleto del CLI. "
        "El router Ana se activa en Semana 1."
    )


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
