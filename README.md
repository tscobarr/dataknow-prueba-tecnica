# DataKnow — Prueba Tecnica

**Cargo:** Cientifico de Datos Junior  
**Empresa:** DataKnow (Medellin, Colombia)  
**Fecha:** Julio 2026

---

## Contenido

| Archivo | Descripcion |
|---------|-------------|
| `notebooks/DataKnow_PruebaTecnica.ipynb` | Analisis completo: EDA, regresion, validacion y pronostico |
| `Resultados/DataKnow_PruebaTecnica.html` | Notebook exportado a HTML (visible en navegador) |
| `Resultados/resultados_analisis.md` | Knowledge base del agente |
| `Resultados/proyeccion_costos.xlsx` | Proyeccion detallada con IC y backtest |
| `Resultados/Arquitectura.png` | Diagrama de arquitectura AWS |
| `Resultados/Informe DataKnow.pdf` | Informe completo con 7 secciones y graficos (APA) |
| `Resultados/Presentacion DataKnow.pdf` | Presentacion del proyecto |
| `agente-ia/app.py` | Agente IA (Streamlit + Bedrock + LangGraph) |
| `agente-ia/Dockerfile` | Contenedor para deploy en AWS |
| `agente-ia/requirements.txt` | Dependencias del agente |
| `Datos/historico_equipos.csv` | Dataset original (3530 registros diarios, 2010-2023) |
| `Caso/Caso consultoria 1 - candidato.pdf` | Enunciado de la prueba |
| `Resultados/Informe DataKnow.pdf` | Informe completo con 7 secciones y graficos (APA) |

---

## Resumen del Analisis

### Datos

- **3530 registros diarios** de enero 2010 a agosto 2023, resampleados a **164 meses** para modelado
- **Variables:** X, Y, Z (costos de insumos), Price_Equipo1, Price_Equipo2 (costos de equipos)
- **Correlaciones:** Y-Z = 0.84, X-Y = 0.49, X-Z = 0.48

### Modelos Seleccionados (frecuencia mensual)

| Equipo | Variables | R2 | MAE | sigma | Ecuacion |
|--------|-----------|-----|------|-------|----------|
| Equipo 1 | Y | 0.998 | $3.83 | $4.69 | Price = 0.8182*Y + 5.49 |
| Equipo 2 | Y + Z | 0.998 | $6.38 | $7.74 | Price = 0.3551*Y + 0.3368*Z + 6.49 |

**Decision basada en datos** — se probaron todas las combinaciones de variables (X, Y, Z, X+Y, X+Z, Y+Z, X+Y+Z) evaluando R2, AIC y MAE. Y resulto ser el mejor predictor para Equipo 1; Y+Z para Equipo 2.

### Validacion

- **Out-of-sample** (train 2010-2021, test 2021-2023): R2 practicamente identico al de entrenamiento (diferencia < 0.005)
- **Residuales:** Media ~ 0, varianza aproximadamente constante
- **QQ-plot:** validacion visual de normalidad razonable

### Pronostico (Naive, frecuencia mensual)

- **Metodo:** Naive (ultimo valor conocido) — seleccionado tras backtest contra SMA(3), SMA(6) y SES
- **Justificacion:** las 3 series son caminatas aleatorias (ADF test: no estacionarias en niveles, si en 1a diferencia)

| Materia Prima | Naive MAE | SMA(3) MAE | SMA(6) MAE | Ganador |
|--------------|-----------|-----------|-----------|---------|
| X | $4.48 | $6.19 | $7.88 | Naive |
| Y | $24.28 | $38.27 | $49.50 | Naive |
| Z | $78.13 | $111.09 | $148.74 | Naive |

### Proyeccion a futuro (horizonte principal: 1 mes)

| Equipo | Diario | Mensual (~22d) | IC 95% (1 mes) |
|--------|--------|-----------------|----------------|
| Equipo 1 | $459.87 | ~$10,117 | +-$9.19 |
| Equipo 2 | $925.29 | ~$20,356 | +-$15.17 |

---

## Agente IA

El agente conversacional usa:

- **Streamlit** — interfaz web
- **LangGraph** — orquestacion del agente
- **Amazon Bedrock (Amazon Nova Lite)** — LLM
- **DuckDuckGo** — busqueda web (sin API key)
- **S3** — artifacts del analisis

El agente responde preguntas sobre el analisis y busca informacion actual de mercado.

**Desplegado en:** http://100.59.157.21:8501

### Como ejecutar localmente

```bash
cd agente-ia
pip install -r requirements.txt
streamlit run app.py
```

Requiere credenciales AWS configuradas y acceso a Bedrock (Amazon Nova Lite).

---

## Arquitectura AWS (4 servicios implementados)

```
Usuarios → EC2 (Agente IA) → Bedrock (Nova Lite)
                ↓                     ↓
              S3 (datos + resultados)  DuckDuckGo (busqueda)
                ↑
            Lambda (pipeline)
```

- **EC2** t3.micro — agente Streamlit vivo (http://100.59.157.21:8501)
- **Bedrock** — Amazon Nova Lite
- **S3** — datos de entrada, notebook HTML, resultados del pipeline
- **Lambda** — pipeline automatizado (dataknow-proyeccion)
- **Sin CloudFront ni ALB** (overkill para 1 instancia)
- Pipeline funcional: S3 → Lambda (numpy+pandas) → S3 Output

Ver `Resultados/Arquitectura.png` para el diagrama completo.

---

## Decisiones Tecnicas

1. **Modelo Y para Eq1, Y+Z para Eq2**: evidencia de datos sobre cualquier hipotesis previa
2. **Naive sobre SMA**: backtest lo confirma para caminatas aleatorias
3. **Sin CloudFront/ALB**: overkill para una sola instancia
4. **Sin Glue/Redshift/SageMaker**: no hacen falta para 3 variables con regresion lineal
5. **Lambda sobre ECS**: el script corre en < 15 min

---

## Licencia

Prueba tecnica — uso exclusivo para proceso de seleccion DataKnow.
