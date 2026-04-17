"""Subgraph de consenso multi-proveedor verificable.

Seccion 36.6 del CONSOLIDADO. 10 componentes (C.1-C.10):
- C.1: ConsensoState + subgraph compilado
- C.2: Verificacion multi-proveedor
- C.3: Paralelizacion asyncio A/B
- C.4: Acuerdo sintactico + semantico
- C.5: Reinyeccion de contexto (stub, futuras fases)
- C.6: Criticas estructuradas al arbitro
- C.7: Gates red_team + stagnation (stub, futuras fases)
- C.8: Circuit breaker
- C.9: Observabilidad runtime JSON
- C.10: Golden tests 18-20

Opt-in: solo se activa con flag `consenso_activo=True` o comando
`/consenso` del empleado. Z.ai GLM-4.6 sigue siendo el default.
"""
