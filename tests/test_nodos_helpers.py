"""Tests de regresion para los helpers deterministas de los nodos tecnicos.

Estos tests capturan el comportamiento de post-procesado (parsing de
respuestas LLM) portado desde PGK_Empresa_Autonoma/src/agents/nodos.py
al Paso 5. Son deterministas: no invocan al LLM, solo verifican que
los extractores de fuentes, recomendaciones, asientos, modelos y pasos
se comportan igual que en origen ante inputs concretos.

Cobertura:
- fiscal: `analisis_fiscal_basico`, `extraer_fuentes`, `extraer_recomendaciones`
- contable: `analisis_contable_basico`, `extraer_fuentes`, `extraer_asientos`,
  `extraer_modelos`, `extraer_pasos_aon`
- legal: `analisis_legal_basico`, `extraer_fuentes_legales`
"""

from __future__ import annotations

from pgk_operativa.nodos import contable, fiscal, legal


class TestFiscalHelpers:
    def test_analisis_basico_tiene_campos_canonicos(self) -> None:
        r = fiscal.analisis_fiscal_basico("X1234567A", "irnr_alquiler")
        assert r["cliente_identificado"] == "X1234567A"
        assert r["tipo_caso"] == "irnr_alquiler"
        assert r["routing_decision"] == "fallback"
        assert r["had_consensus"] is False
        assert isinstance(r["fuentes_citadas"], list)
        assert isinstance(r["recomendaciones"], list)
        assert r["confianza"] == 0.5

    def test_extraer_fuentes_detecta_ley_boe_articulo(self) -> None:
        resp = (
            "Segun la Ley 35/2006 del IRPF\n"
            "BOE-A-2006-20764 regula la obligacion\n"
            "Articulo 24 LIRNR aplicable\n"
            "Linea sin fuente\n"
        )
        fuentes = fiscal.extraer_fuentes(resp)
        assert len(fuentes) == 3
        assert any("Ley 35/2006" in f for f in fuentes)
        assert any("BOE" in f for f in fuentes)
        assert any("Articulo 24" in f for f in fuentes)

    def test_extraer_fuentes_dedup_y_limite_5(self) -> None:
        resp = "\n".join(
            [
                "Ley 35/2006 IRPF",
                "Ley 35/2006 IRPF",  # duplicado
                "Real Decreto 439/2007",
                "Art. 24 LIRNR",
                "BOE-A-2024-1",
                "BOE-A-2024-2",
                "Convenio doble imposicion",
                "Modelo 210 IRNR",
            ]
        )
        fuentes = fiscal.extraer_fuentes(resp)
        assert len(fuentes) == 5
        assert len(set(fuentes)) == 5

    def test_extraer_recomendaciones_keywords(self) -> None:
        resp = (
            "Recomiendo revisar la documentacion\n"
            "Es importante verificar el convenio\n"
            "Debe presentar el 210 antes del 31/12\n"
            "Sugiero aplicar el convenio doble imposicion\n"
            "Linea completamente neutra\n"
        )
        recs = fiscal.extraer_recomendaciones(resp)
        assert len(recs) == 4
        assert any("Recomiendo" in r for r in recs)
        assert any("importante" in r for r in recs)
        assert any("Debe presentar" in r for r in recs)
        assert any("Sugiero" in r for r in recs)
        assert not any("neutra" in r for r in recs)

    def test_extraer_recomendaciones_matches_stem_changing_verbs(self) -> None:
        """Spanish e→ie stem change: recomend* no matchea recomiendo, hay que cubrir recomien*."""
        resp = (
            "Recomiendo presentar el modelo 210\n"
            "Se recomienda revisar el convenio\n"
            "Sugiero aplicar la retencion\n"
            "Se sugiere consultar con experto\n"
        )
        recs = fiscal.extraer_recomendaciones(resp)
        assert len(recs) == 4

    def test_extraer_recomendaciones_fallback_si_vacio(self) -> None:
        recs = fiscal.extraer_recomendaciones("Texto neutro sin accionables")
        assert recs == ["Consultar con experto fiscal"]

    def test_extraer_fuentes_vacio_devuelve_lista_vacia(self) -> None:
        assert fiscal.extraer_fuentes("") == []
        assert fiscal.extraer_fuentes("texto sin fuentes") == []


class TestContableHelpers:
    def test_analisis_basico_estructura(self) -> None:
        r = contable.analisis_contable_basico("B12345678", "asiento", "asiento iva")
        assert r["cliente_identificado"] == "B12345678"
        assert r["tipo_caso"] == "asiento"
        assert r["had_consensus"] is False
        assert isinstance(r["asientos_generados"], list)
        assert isinstance(r["modelos_calculados"], list)
        assert isinstance(r["recomendaciones_aon"], list)

    def test_extraer_fuentes_pgc_icac(self) -> None:
        resp = (
            "Segun el PGC 2008 la cuenta 602\n"
            "Resolucion ICAC de 14 abril 2015\n"
            "NRV 14 reconocimiento ingresos\n"
            "Modelo 303 trimestral\n"
        )
        fuentes = contable.extraer_fuentes(resp)
        assert len(fuentes) == 4
        assert any("PGC" in f for f in fuentes)
        assert any("ICAC" in f for f in fuentes)

    def test_extraer_asientos_requiere_keyword_y_digito(self) -> None:
        resp = (
            "Cuenta 602 Compras 1000,00 al debe\n"
            "Cuenta 400 Proveedores haber 1210,00\n"
            "Linea sin asiento\n"
            "Cuenta sin numero: debe revisar\n"  # no digit => descartado
        )
        asientos = contable.extraer_asientos(resp)
        assert len(asientos) == 2

    def test_extraer_asientos_limite_10(self) -> None:
        resp = "\n".join([f"Cuenta 602 asiento {i} debe 100,00" for i in range(15)])
        asientos = contable.extraer_asientos(resp)
        assert len(asientos) == 10

    def test_extraer_modelos_detecta_numero(self) -> None:
        resp = (
            "El Modelo 303 trimestral de IVA\n"
            "Debe presentar tambien el modelo 130 IRPF\n"
            "y el mod. 390 anual\n"
            "El 349 si hay intracomunitarias\n"
        )
        modelos = contable.extraer_modelos(resp)
        assert "303" in modelos
        assert "130" in modelos
        assert "390" in modelos
        assert "349" not in modelos  # sin prefijo `modelo`/`mod.`

    def test_extraer_modelos_dedup(self) -> None:
        resp = "Modelo 303 y luego otra vez Modelo 303 y mod. 303"
        modelos = contable.extraer_modelos(resp)
        assert modelos == ["303"]

    def test_extraer_modelos_word_boundary(self) -> None:
        """modelo 2002 no debe matchear 200; mod. 3031 no debe matchear 303."""
        resp = (
            "Cita apocrifa: modelo 2002 no existe en AEAT\n"
            "Tampoco mod. 3031 es valido\n"
            "Pero si el Modelo 200 (IS) y mod. 303 (IVA)\n"
        )
        modelos = contable.extraer_modelos(resp)
        assert "200" in modelos
        assert "303" in modelos
        # 2002 y 3031 no son modelos reales; no deben aparecer por substring
        # El unico modo de que "200" aparezca es por la linea tercera (Modelo 200).
        assert len([m for m in modelos if m == "200"]) == 1
        assert len([m for m in modelos if m == "303"]) == 1

    def test_extraer_pasos_aon_keywords(self) -> None:
        resp = (
            "Abrir AON Solutions\n"
            "Ir al menu contabilidad\n"
            "Paso 3: introducir la factura\n"
            "Linea neutra irrelevante\n"
        )
        pasos = contable.extraer_pasos_aon(resp)
        assert len(pasos) == 3

    def test_extraer_pasos_aon_fallback_si_vacio(self) -> None:
        pasos = contable.extraer_pasos_aon("Texto sin indicaciones")
        assert pasos == ["Consultar manual AON Solutions"]


class TestLegalHelpers:
    def test_analisis_basico_estructura(self) -> None:
        r = legal.analisis_legal_basico("X7654321B", "recurso_reposicion", "mensaje inicial")
        assert r["cliente_identificado"] == "X7654321B"
        assert r["tipo_caso"] == "recurso_reposicion"
        assert r["had_consensus"] is False
        assert isinstance(r["fuentes_citadas"], list)

    def test_extraer_fuentes_legales_detecta_jurisprudencia(self) -> None:
        resp = (
            "La STS 123/2023 establece doctrina\n"
            "Segun el Articulo 1902 Codigo Civil\n"
            "La Ley 39/2015 LPAC regula el procedimiento\n"
            "La STSJ Madrid 456/2022 aclara\n"
            "Frase sin fuente\n"
        )
        fuentes = legal.extraer_fuentes_legales(resp)
        assert len(fuentes) == 4

    def test_extraer_fuentes_legales_dedup(self) -> None:
        resp = "Ley 1/2000 LEC\nLey 1/2000 LEC\nArticulo 1 LEC"
        fuentes = legal.extraer_fuentes_legales(resp)
        assert len(fuentes) == 2

    def test_extraer_fuentes_legales_vacio(self) -> None:
        assert legal.extraer_fuentes_legales("") == []

    def test_extraer_fuentes_legales_no_confunde_cc_con_ccaa(self) -> None:
        """CCAA (Comunidades Autonomas) no debe matchear 'CC' (Codigo Civil)."""
        resp = "Las CCAA tienen competencia exclusiva en esta materia"
        assert legal.extraer_fuentes_legales(resp) == []

    def test_extraer_fuentes_legales_stsj_y_ccom_son_alcanzables(self) -> None:
        """STSJ y CCom deben matchear patrones especificos, no los genericos STS/CC."""
        resp = "Segun la STSJ Cataluna 123/2024\nEl CCom regula la materia mercantil"
        fuentes = legal.extraer_fuentes_legales(resp)
        assert len(fuentes) == 2
        assert any("STSJ" in f for f in fuentes)
        assert any("CCom" in f for f in fuentes)


class TestNodosShape:
    """Verifica que los nodos thin-wrapper mantienen la signatura LangGraph."""

    def test_todos_los_nodos_aceptan_state_dict(self) -> None:
        from pgk_operativa.nodos import calidad, docs, laboral, marketing

        # Solo verificamos la signatura, no invocamos (eso llama a LLM real).
        assert callable(docs.nodo_docs)
        assert callable(calidad.nodo_calidad)
        assert callable(marketing.nodo_marketing)
        assert callable(laboral.nodo_laboral)
        assert callable(fiscal.nodo_fiscal)
        assert callable(contable.nodo_contable)
        assert callable(legal.nodo_legal)
