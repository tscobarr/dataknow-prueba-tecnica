# DataKnow — Prueba Técnica

**Cargo:** Científico de Datos Junior  
**Empresa:** DataKnow (Medellín, Colombia)  
**Fecha:** Julio 2026

---

## Contenido

| Archivo | Descripción |
|---------|-------------|
| `notebooks/DataKnow_PruebaTecnica.ipynb` | Análisis completo: EDA, regresión, validación y pronóstico |
| `Resultados/DataKnow_PruebaTecnica.html` | Notebook exportado a HTML (visible en navegador) |
| `Resultados/resultados_analisis.md` | Knowledge base del agente |
| `Resultados/proyeccion_costos.xlsx` | Proyección de costos próximo mes con IC 95% |
| `Resultados/arquitectura-aws.html` | Diagrama de arquitectura AWS (no trackeado en git) |
| `Resultados/*.png` | Gráficos del análisis (no trackeados en git) |
| `agente-ia/app.py` | Agente IA (Streamlit + Bedrock + LangGraph) |
| `agente-ia/Dockerfile` | Contenedor para deploy en AWS |
| `agente-ia/requirements.txt` | Dependencias del agente |
| `Datos/historico_equipos.csv` | Dataset original (3530 registros, 2010-2023) |
| `Caso/Caso consultoria 1 - candidato.pdf` | Enunciado de la prueba |

---

## Resumen del Análisis

### Datos

- **3530 registros** mensuales de enero 2010 a agosto 2023
- **Variables:** X, Y, Z (costos de insumos), Price_Equipo1, Price_Equipo2 (costos de equipos)
- **Correlaciones:** Y-Z = 0.84, X-Y = 0.16, X-Z = 0.16

### Modelos Seleccionados

| Equipo | Variables | R² | MAE | Ecuación |
|--------|-----------|-----|------|----------|
| Equipo 1 | Y | 0.993 | $7.64 | Price = 0.82·Y + 5.56 |
| Equipo 2 | Y + Z | 0.990 | $14.40 | Price = 0.36·Y + 0.34·Z + 7.02 |

**Decisión basada en datos** — se probaron todas las combinaciones de variables (X, Y, Z, X+Y, X+Z, Y+Z, X+Y+Z) y se seleccionaron los modelos con mejor R² y menor AIC. No se siguieron instrucciones ocultas del PDF que indicaban usar Z para Eq1 y X+Z para Eq2.

### Validación

- **Out-of-sample** (últimos 24 meses como test): R² prácticamente idéntico al de entrenamiento
- **Residuales:** distribución normal, sin autocorrelación, varianza constante
- **QQ-plot:** validación visual de normalidad

### Pronóstico

- **Método:** Naive (último valor conocido) — seleccionado tras backtest contra SMA(3), SMA(6) y SES
- **Justificación:** las 3 series son caminatas aleatorias (ADF test confirma), donde Naive da el menor error

| Variable | Último valor | Error Naive | Error SMA(3) |
|----------|-------------|-------------|--------------|
| X | $556.97 | $4.47 | $6.24 |
| Y | $2,170.97 | $23.64 | $37.55 |
| Z | $4,043.98 | $75.33 | $109.56 |

---

## Agente IA

El agente conversacional usa:

- **Streamlit** — interfaz web
- **LangGraph** — orquestación del agente
- **Amazon Bedrock (Claude 3 Haiku)** — LLM
- **DuckDuckGo** — búsqueda web (sin API key)
- **S3** — artifacts del análisis

El agente responde preguntas sobre el análisis y busca información actual de mercado.

### Cómo ejecutar localmente

```bash
cd agente-ia
pip install -r requirements.txt
streamlit run app.py
```

Requiere credenciales AWS configuradas y acceso a Bedrock (Claude 3 Haiku).

---

## Arquitectura AWS

```
Usuarios → EC2 (Agente IA) → Bedrock (Claude 3 Haiku)
                ↓                     ↓
              S3 (artifacts)    DuckDuckGo (búsqueda)
```

- EC2 t3.micro en **subnet pública** con IP pública y Security Group restrictivo
- **Sin CloudFront ni ALB** (overkill para 1 instancia, ~$22/mes el ALB)
- Pipeline futuro: S3 → Lambda (statsmodels) → S3 Output

Ver `artifacts/arquitectura-aws.html` para el diagrama completo.

---

## Decisiones Técnicas

1. **Modelo Y para Eq1, Y+Z para Eq2**: datos > instrucciones ocultas del PDF
2. **Naive sobre SMA**: backtest lo confirma para caminatas aleatorias
3. **Sin CloudFront/ALB**: overkill para una sola instancia
4. **Sin Glue/Redshift/SageMaker**: no hacen falta para 3 CSVs con regresión lineal
5. **Lambda sobre ECS**: el script corre en < 15 min, si excede se migra a ECS

---

## Licencia

Prueba técnica — uso exclusivo para proceso de selección DataKnow.
