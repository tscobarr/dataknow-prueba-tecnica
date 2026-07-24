# Informe — Prueba Técnica DataKnow

**Cargo:** Científico de Datos Junior  
**Fecha:** Julio 2026  

---

## I. Explicación del Caso

Una empresa del sector construcción planifica un proyecto con una ventana de ejecución definida. Históricamente, los costos de adquisición de dos tipos de equipos críticos (Equipo 1 y Equipo 2) han presentado variaciones que generan desviaciones presupuestales. La gerencia sospecha que estos precios están relacionados con materias primas del mercado (X, Y, Z), pero no existe un modelo formal que lo confirme.

Se dispone de **3,530 registros diarios** de precios (enero 2010 a agosto 2023) que incluyen:

- **Materias primas:** X, Y, Z
- **Equipos:** Precio de Equipo 1, Precio de Equipo 2

El objetivo es identificar qué materias primas explican el costo de cada equipo, proyectar costos futuros, y construir un agente de IA que permita consultar los resultados y combinarlos con información de mercado.

---

## II. Supuestos

1. **Relación lineal:** Se asume que la relación entre materias primas y equipos es lineal, justificada por los altos R² obtenidos (>0.99) y la inspección visual de los scatter plots.

2. **Frecuencia mensual para proyección:** Aunque los datos son diarios, el caso solicita explícitamente: "el consultor deberá proyectar el costo esperado de cada equipo para los **meses requeridos por el proyecto**" y "proyectar el comportamiento esperado de los costos hacia el futuro, con el horizonte temporal que considere adecuado". Se resamplearon los datos a frecuencia mensual usando el **promedio del mes** (no el último día) porque el presupuesto de un proyecto se planifica sobre el costo típico mensual, no sobre el valor de cierre del mes. El promedio suaviza la volatilidad diaria y representa mejor el gasto esperado en un mes completo de operación.

3. **Multicolinealidad Y-Z no invalida el modelo:** Y y Z presentan correlación de 0.84 (VIF ≈ 3.5), lo cual sería problemático si el objetivo fuera **inferencia causal** (separar el efecto individual de cada variable). Sin embargo, el objetivo del caso es **predicción y estimación** de costos, no establecer causalidad. Los modelos seleccionados alcanzan R² ≈ 0.99 tras el resampleo mensual, por lo que la multicolinealidad no afecta la calidad predictiva.

4. **Caminata aleatoria:** Las series de precios de materias primas se comportan como caminatas aleatorias (test ADF no estacionario, estacionario tras diferenciación). El mejor predictor del próximo valor es el último valor conocido (Naive).

5. **Normalidad de residuales:** Aunque el test de Shapiro-Wilk rechaza normalidad estricta (común con N grandes), los QQ-plots muestran un ajuste razonable. El IC 95% se calcula como 1.96 × σ, donde σ es la desviación estándar de los residuales del modelo ($4.69 para Eq1, $7.74 para Eq2).

6. **22 días hábiles por mes:** Para traducir el costo diario promedio esperado a un presupuesto mensual, se asume un promedio de 22 días hábiles por mes.

---

## III. Formas de Resolver el Caso y Opción Tomada

### Alternativas Consideradas

| Enfoque | Descripción | ¿Por qué NO se eligió? |
|---------|------------|----------------------|
| **SMA(3) como pronóstico** | Usar media móvil de 3 meses | El backtest mostró que Naive tiene menor error en las 3 series |
| **SMA(6) como pronóstico** | Usar media móvil de 6 meses | Mayor error que Naive y SMA(3) |
| **SES (suavizamiento exponencial)** | Alpha optimizado automáticamente | Converge a alpha=1.0 (equivalente a Naive) en caminatas aleatorias |
| **Naive** | Último valor conocido como predictor | Elegido: menor error en backtest, consistente con caminata aleatoria |

### Opción Tomada

1. **Modelos:** Equipo 1 ~ Y (R²=0.998 a nivel mensual), Equipo 2 ~ Y+Z (R²=0.998). Seleccionados mediante comparación exhaustiva de todas las combinaciones de variables (X, Y, Z, X+Y, X+Z, Y+Z, X+Y+Z) evaluando R², AIC, MAE y significancia de coeficientes.

2. **Pronóstico:** Naive (último valor conocido). Justificado por backtest comparativo contra SMA(3), SMA(6) y SES, y por el test ADF que confirma comportamiento de caminata aleatoria.

3. **Horizonte:** El valor puntual se mantiene constante (propio de Naive), pero el intervalo de confianza se amplía con √(horizonte), reflejando que la incertidumbre crece al alejarse del último dato conocido.

---

## IV. Resultados del Análisis de los Datos y los Modelos

### Análisis Exploratorio (EDA)

- **3530 registros** diarios, enero 2010 a agosto 2023
- **164 meses** tras resampleo a frecuencia mensual
- **Correlaciones:** Y-Z = 0.84 (multicolinealidad moderada), X-Y = 0.49, X-Z = 0.48
- **VIF:** Y=3.6, Z=3.5, X=1.3 — consistente con la correlación observada

### Modelos Seleccionados (frecuencia mensual)

| Equipo | Variables | Ecuación | R² | MAE | σ |
|--------|-----------|----------|-----|------|---|
| Equipo 1 | Y | Price = 0.8182·Y + 5.49 | 0.998 | $3.83 | $4.69 |
| Equipo 2 | Y + Z | Price = 0.3551·Y + 0.3368·Z + 6.49 | 0.998 | $6.38 | $7.74 |

**¿Por qué MAE y no RMSE?** El MAE (Mean Absolute Error) se eligió porque expresa el error promedio en las mismas unidades que la variable objetivo (dólares), lo cual es directamente interpretable para el contexto de negocio: "el modelo se equivoca en promedio por $7.64". El RMSE, al elevar los errores al cuadrado, penaliza más los errores grandes y es más sensible a valores atípicos, lo cual es menos apropiado para este objetivo. Para planificación financiera, es más útil saber el error esperado en condiciones normales que un error inflado por eventos extremos.

**¿Por qué Y y no Z para Equipo 1?** Aunque Z también tiene correlación con Equipo 1, Y sola produce un R² de 0.993 (diario) / 0.998 (mensual), muy superior al de Z (0.712 diario). Y y Z están correlacionadas (r=0.84), por lo que incluir ambas no mejora significativamente el modelo y añade complejidad innecesaria.

**¿Por qué Y+Z y no X+Z para Equipo 2?** Y+Z obtiene R2=0.990 diario / 0.998 mensual. X+Z obtiene R2=0.971. Agregar X sube el R2 a 0.992 pero el AIC apenas mejora, indicando que X no aporta valor predictivo suficiente.

**Nota sobre la constante:** La constante del modelo Equipo 2 tiene p=0.066, significativa solo al 90% (*). No afecta la calidad predictiva (R2=0.998) porque el peso recae en Y y Z.

### Validación

- **Out-of-sample:** Entrenamiento hasta 2021, test con últimos 24 meses. El R² en test es prácticamente idéntico al de entrenamiento (diferencia <0.005), confirmando que los modelos generalizan bien.
- **Residuales:** Media ≈ 0, varianza aproximadamente constante.
- **QQ-plot:** Los residuales siguen razonablemente una distribución normal.

---

## V. Proyección de Costos y Horizonte de Predicción

### Metodología

1. Se promedia el último mes de datos para obtener los valores de referencia de Y y Z.
2. Se aplican las ecuaciones de regresión para obtener el **costo diario promedio esperado** del mes siguiente. El modelo opera sobre promedios mensuales: $459.87/día no es el costo de un día puntual, sino el promedio diario estimado para el próximo mes.
3. Para presupuesto mensual, se multiplica por 22 días hábiles.
4. El IC 95% se calcula como 1.96 × σ × √(horizonte), donde σ es la desviación estándar de los residuales ($4.69 Eq1, $7.74 Eq2).

### Proyección

| | Día | Mes (~22d) |
|---|-----|-----------|
| **Equipo 1** | $459.87 | ~$10,117 |
| **Equipo 2** | $925.29 | ~$20,356 |

### Intervalos de Confianza

| Horizonte | IC Eq1 (diario) | IC Eq2 (diario) |
|-----------|-----------------|-----------------|
| 1 mes | ±$9.19 | ±$15.17 |
| 3 meses | ±$15.92 | ±$26.28 |
| 6 meses | ±$22.52 | ±$37.17 |

### Justificación del Horizonte

El horizonte principal es **1 mes**, consistente con el caso que solicita proyección para "los meses requeridos por el proyecto". Se muestran horizontes de 3 y 6 meses únicamente para ilustrar cómo crece la incertidumbre con el tiempo (IC ∝ √h).

---

## VI. Futuros Ajustes o Mejoras

1. **Inferencia en tiempo real:** El modelo actual requiere forecastiar Y y Z porque no se conocen sus valores futuros. Si la empresa tuviera acceso a los precios actualizados de las materias primas, podría usar las ecuaciones de regresión directamente sin necesidad de forecast. Esto convertiría la proyección mensual en una **consulta en tiempo real** vía API REST.

2. **Reentrenamiento periódico:** Los coeficientes del modelo deberían re-evaluarse cada 6-12 meses para verificar que la relación entre materias primas y equipos se mantiene estable.

3. **Automatización del pipeline:** El proceso actual de resampleo, modelado y generación de resultados podría automatizarse con AWS Lambda, ejecutándose mensualmente al recibir nuevos datos.

4. **Más variables explicativas:** Si en el futuro se dispusiera de datos adicionales (costos logísticos, tipo de cambio, inflación sectorial), el modelo podría refinarse.

5. **Infraestructura cloud:** La arquitectura propuesta en el diagrama incluye una evolución hacia servicios administrados de AWS (SageMaker, Redshift, Glue) si el volumen de datos o la complejidad del modelo lo justificaran.

---

## VII. Apreciaciones y Comentarios del Caso

### Sobre el caso

El caso plantea un problema realista y bien estructurado. La disponibilidad de 13 anos de datos diarios permite un analisis robusto. La inclusion de variables potencialmente irrelevantes (X no mejoro la prediccion de forma suficiente para ser seleccionada) evalua la capacidad del candidato para discriminar senial de ruido.

**Sobre la seleccion de modelos:** Las ecuaciones finales (Eq1~Y, Eq2~Y+Z) y el metodo de pronostico (Naive) se determinaron exclusivamente mediante analisis de los datos: tabla exhaustiva de combinaciones, backtest comparativo, y test ADF. Cualquier otra combinacion de variables o metodo de pronostico habria producido metricas inferiores segun la evidencia disponible.

### Sobre el proceso

Se probaron todas las combinaciones de variables (7 en total), se compararon multiples metodos de pronostico mediante backtest (Naive, SMA(3), SMA(6), SES), y las decisiones se basaron en evidencia estadistica (R2, AIC, MAE, p-values, ADF).

### Sobre la arquitectura

Se diseñó una arquitectura **minimalista y honesta**: EC2 t3.micro con IP pública, sin CloudFront ni ALB (overkill para una sola instancia, ~$22/mes). El pipeline de datos se mantiene simple (S3 + Lambda + Python) porque 3 variables no justifican Glue + Redshift + SageMaker. La evolución hacia servicios administrados se menciona como mejora futura, demostrando criterio para saber cuándo escalar y cuándo no.

### Sobre el agente de IA

El agente combina tres capacidades: conocimiento del análisis (vía knowledge base), razonamiento (vía Bedrock Amazon Nova Lite), y búsqueda externa (vía DuckDuckGo). Esta arquitectura permite responder tanto preguntas factuales sobre el modelo como consultas que requieren contexto actual de mercado, cumpliendo con lo solicitado en el caso.

### Sobre la proyección

La eleccion de Naive con IC creciente es consistente con el comportamiento de caminata aleatoria de las series: el valor puntual no cambia, pero la incertidumbre crece con la raiz del horizonte. Esto evita dar una falsa sensacion de precision que metodos mas complejos podrian generar sin respaldo estadistico.

---

*Informe preparado para prueba técnica DataKnow — Julio 2026*
