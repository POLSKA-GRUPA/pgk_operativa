"""Circuit breaker para el subgraph de consenso (C.8).

Contador de fallos consecutivos. Si supera umbral (5 en 30 min):
- Desactiva consenso temporalmente.
- Pasa a single-model con aviso.
- Reintentos cada 15 min. Recuperacion automatica.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta


class CircuitBreaker:
    """Circuit breaker thread-safe para el subgraph de consenso."""

    def __init__(
        self,
        *,
        max_fallos: int = 5,
        ventana: timedelta = timedelta(minutes=30),
        cooldown: timedelta = timedelta(minutes=15),
    ) -> None:
        self._max_fallos = max_fallos
        self._ventana = ventana
        self._cooldown = cooldown
        self._fallos: list[datetime] = []
        self._abierto_desde: datetime | None = None
        self._lock = threading.Lock()

    @property
    def abierto(self) -> bool:
        """True si el circuit breaker esta abierto (consenso degradado)."""
        with self._lock:
            if self._abierto_desde is None:
                return False
            ahora = datetime.now(UTC)
            if ahora - self._abierto_desde >= self._cooldown:
                self._abierto_desde = None
                self._fallos.clear()
                return False
            return True

    def registrar_fallo(self) -> bool:
        """Registra un fallo. Devuelve True si el breaker se abre."""
        with self._lock:
            ahora = datetime.now(UTC)
            corte = ahora - self._ventana
            self._fallos = [t for t in self._fallos if t > corte]
            self._fallos.append(ahora)
            if len(self._fallos) >= self._max_fallos:
                self._abierto_desde = ahora
                return True
            return False

    def registrar_exito(self) -> None:
        """Registra un exito. Limpia fallos acumulados."""
        with self._lock:
            self._fallos.clear()
            self._abierto_desde = None

    def estado(self) -> dict[str, object]:
        """Snapshot del estado para telemetria (C.9)."""
        with self._lock:
            return {
                "abierto": self._abierto_desde is not None,
                "fallos_recientes": len(self._fallos),
                "max_fallos": self._max_fallos,
                "abierto_desde": (self._abierto_desde.isoformat() if self._abierto_desde else None),
            }


# Instancia singleton del circuit breaker.
_breaker = CircuitBreaker()


def get_breaker() -> CircuitBreaker:
    """Devuelve la instancia singleton del circuit breaker."""
    return _breaker


__all__ = ["CircuitBreaker", "get_breaker"]
