# Plan de Trabajo — Prueba Técnica DataKnow

> **Caso:** Gestión de Costos Operativos en un Proyecto de Construcción  
> **Candidato:** Tomás Escobar  
> **Fecha:** Julio 2026

---

## 1. Resumen del Caso

Una empresa constructora necesita estimar los costos de adquisición de 2 equipos críticos para un proyecto. Tienen datos históricos de precios de materias primas (X, Y, Z) y precios de equipos (Equipo 1, Equipo 2). Se necesita:

1. Identificar qué materias primas explican el comportamiento de cada equipo
2. Construir un modelo que estime costos de forma sistemática
3. Proyectar costos futuros con intervalos de confianza
4. Exponer resultados a través de un **Agente de IA** conversacional
5. Diseñar una **arquitectura cloud** que soporte la solución

---

## 2. Entregables

| # | Entregable | Formato | Estado |
|---|-----------|---------|--------|
| 1 | **Código funcional** | Notebook Jupyter (.ipynb) | ✅ Base lista |
| 2 | **Resultados del análisis** | Markdown (.md) + Excel (.xlsx) | 📝 Por hacer |
| 3 | **Agente de IA conversacional** | Streamlit app (Python) | 📝 Por hacer |
| 4 | **Proyección de costos** | En notebook + Excel + agente | 📝 Por hacer |
| 5 | **Arquitectura cloud** | Diagrama (draw.io / excalidraw) | 📝 Por hacer |
| 6 | **Informe completo** | README.md / Markdown | 📝 Por hacer |
| 7 | **Repositorio GitHub** | Repo público con todo | 📝 Por hacer |
| 8 | **Despliegue en AWS (+5%)** | EC2 con el agente funcionando | 📝 Por hacer |

---

## 3. Arquitectura General

```
┌──────────────────────────────────────────────────────────────────────┐
│                        LOCAL (tu PC)                                  │
│                                                                       │
│  ┌─────────────────────────────────────────────┐                     │
│  │  1. Notebook Jupyter                         │                     │
│  │     - EDA, modelos, proyecciones             │────┐                │
│  └─────────────────────────────────────────────┘    │                │
│                                                      │ Genera          │
│  ┌─────────────────────────────────────────────┐    │                 │
│  │  2. Script genera artifacts:                │◄───┘                │
│  │     - resultados_analisis.md                │                     │
│  │     - proyeccion_costos.xlsx                │                     │
│  │     - graficos/ (PNG)                       │                     │
│  └─────────────────────────────────────────────┘                     │
│                                                                       │
│  ┌─────────────────────────────────────────────┐                     │
│  │  3. Push a GitHub                            │                     │
│  └─────────────────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (sube a S3)
┌──────────────────────────────────────────────────────────────────────┐
│                         AWS CLOUD                                     │
│                                                                       │
│  ┌─────────────────────────────────────────────┐                     │
│  │  Amazon S3                                   │                     │
│  │  - resultados_analisis.md                    │                     │
│  │  - proyeccion_costos.xlsx                    │                     │
│  │  - graficos/                                 │                     │
│  └──────────────┬──────────────────────────────┘                     │
│                 │ Lee al iniciar                                     │
│  ┌──────────────▼──────────────────────────────┐                     │
│  │  EC2 t3.micro (Free Tier)                   │                     │
│  │                                             │                     │
│  │  ┌──────────────────────────────────────┐   │                     │
│  │  │  Streamlit App — Agente IA            │   │                     │
│  │  │                                       │   │                     │
│  │  │  Knowledge Base (cargada al inicio)   │   │                     │
│  │  │  • resultados_analisis.md (contexto)  │   │                     │
│  │  │  • proyeccion_costos.xlsx (tablas)    │   │                     │
│  │  │                                       │   │                     │
│  │  │  Herramientas del agente:             │   │                     │
│  │  │  • DuckDuckGo Search (búsqueda web)   │   │                     │
│  │  │  • Amazon Bedrock (Claude Haiku)      │   │                     │
│  │  └──────────────────────────────────────┘   │                     │
│  └──────────────────────────────────────────────┘                     │
│                                                                       │
│  ┌──────────────────────────────────────────────┐                    │
│  │  Amazon Bedrock                                │                    │
│  │  • Claude 3 Haiku (respuestas del agente)    │                    │
│  │  • (Solo se paga por uso ~$0.03 la demo)     │                    │
│  └──────────────────────────────────────────────┘                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. Tech Stack

| Componente | Tecnología | Por qué |
|-----------|-----------|---------|
| **Análisis de datos** | Python (pandas, numpy, sklearn) | Estándar en DS |
| **Modelos** | Regresión Lineal (sklearn) | Simple, interpretable, explicable |
| **Visualización** | matplotlib + seaborn | Gráficos profesionales para el informe |
| **Agente IA** | Streamlit + LangChain | Rápido de prototipar, perfecto para demos |
| **LLM** | Amazon Bedrock — Claude 3 Haiku | Barato ($0.00025/input), rápido, buen español |
| **Búsqueda web** | DuckDuckGo (via LangChain) | Gratis, sin API key |
| **Vector store** | FAISS + S3 (para el RAG básico) | Simple, sin costos adicionales |
| **Contenedor** | Docker | Portabilidad, despliegue fácil |
| **Cloud** | AWS (EC2 + S3 + Bedrock) | Free tier, servicio que piden para bonus |
| **Diagrama** | Excalidraw / Draw.io | Profesional, gratis |

---

## 5. Flujo de Datos

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Datos     │ → │ Notebook │ → │ Artifacts│ → │ S3       │
│ CSV       │   │ EDA +    │   │ .md      │   │          │
│ (X,Y,Z,  │   │ Modelos  │   │ .xlsx    │   │          │
│  Equipos) │   │          │   │ .png     │   │          │
└──────────┘   └──────────┘   └──────────┘   └─────┬────┘
                                                    │
                                                    ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Usuario  │ ← │ Agente   │ ← │ LangChain│ ← │ EC2      │
│ (evalua- │   │ Streamlit│   │ + Bedrock│   │ (descarga│
│  dor)    │   │          │   │ + Search │   │  de S3)  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

**Knowledge Base del agente (RAG básico):**

1. Al iniciar, el agente descarga `resultados_analisis.md` y `proyeccion_costos.xlsx` de S3
2. Convierte el .md en texto plano y lo guarda como contexto
3. Convierte el .xlsx en una tabla que el LLM puede consultar
4. Cuando el evaluador pregunta:
   - **Dato técnico** → lo obtiene del contexto local (sin búsqueda web)
   - **Contexto de mercado** → usa DuckDuckGo para buscar noticias actuales
   - **Ambos** → combina en una respuesta

---

## 6. Implementación — Paso a Paso

### Fase 1: Análisis de Datos (Notebook)

- [ ] 1.1 Cargar y limpiar `historico_equipos.csv`
- [ ] 1.2 EDA completo: estadísticas, series temporales, correlaciones
- [ ] 1.3 Modelo Equipo 1 ~ Z (regresión lineal simple)
- [ ] 1.4 Modelo Equipo 2 ~ X + Z (regresión lineal múltiple)
- [ ] 1.5 Validación: residuales, R², MAE, MAPE
- [ ] 1.6 Pronóstico con SMA 3 meses + intervalos de confianza
- [ ] 1.7 Visualizaciones (guardar PNGs)

### Fase 2: Generación de Artifacts

- [ ] 2.1 Script que desde el notebook genera:
  - `resultados_analisis.md` — hallazgos formateados
  - `proyeccion_costos.xlsx` — tabla profesional con intervalos
- [ ] 2.2 Subir artifacts a S3

### Fase 3: Infraestructura AWS

- [ ] 3.1 Crear cuenta AWS (si no existe)
- [ ] 3.2 Crear bucket S3 (resultados)
- [ ] 3.3 Habilitar Bedrock + solicitar acceso a Claude 3 Haiku
- [ ] 3.4 Crear IAM Role para EC2 (permisos: S3 read + Bedrock invoke)
- [ ] 3.5 Opcional: subir artifacts al bucket

### Fase 4: Agente IA (Streamlit + LangChain + Bedrock)

- [ ] 4.1 Construir `app.py` (Streamlit):
  - Carga artifacts desde S3 al iniciar
  - Interfaz tipo chat
  - LangChain Agent con herramientas:
    - Bedrock LLM (Claude Haiku)
    - DuckDuckGo Search
  - Prompts personalizados con contexto del análisis
- [ ] 4.2 Crear `Dockerfile`
- [ ] 4.3 Probar localmente

### Fase 5: Despliegue AWS

- [ ] 5.1 Lanzar EC2 t3.micro (Amazon Linux 2023)
- [ ] 5.2 Instalar Docker en EC2
- [ ] 5.3 Subir imagen Docker a ECR (o correr directo)
- [ ] 5.4 Ejecutar contenedor con las variables de entorno necesarias
- [ ] 5.5 Abrir puerto en Security Group (Streamlit corre en 8501)
- [ ] 5.6 Verificar que el agente responde

### Fase 6: Diagrama de Arquitectura

- [ ] 6.1 Crear diagrama en draw.io / excalidraw
- [ ] 6.2 Mostrar: S3 → EC2 → Bedrock + DuckDuckGo + User
- [ ] 6.3 Incluir versión "producción" (Redshift, SageMaker, Feature Store) para mostrar conocimiento

### Fase 7: Documentación y Repo

- [ ] 7.1 Crear README.md con:
  - Descripción del caso
  - Arquitectura
  - Instrucciones de uso
  - Link a la app en AWS (si aplica)
- [ ] 7.2 Informe como sección del README con:
  - Explicación del caso
  - Supuestos
  - Opciones consideradas y decisión
  - Resultados del análisis
  - Proyección de costos
  - Futuros ajustes
  - Apreciaciones personales
- [ ] 7.3 Subir todo a GitHub
- [ ] 7.4 Agregar sección de "Diferencia entre modelo y agente IA" (punto del entregable)

---

## 7. Costos Estimados

| Servicio | Recurso | Costo |
|----------|---------|-------|
| **EC2** | t3.micro (free tier) | $0.00 (primeros 12 meses) |
| **S3** | ~100MB almacenamiento | $0.00 (free tier: 5GB) |
| **Bedrock** | Claude 3 Haiku | ~$0.03 toda la demo |
| **Total** | | **~$0.03** |

---

## 8. Estructura de Carpetas Propuesta

```
📦 DataKnow-PruebaTecnica/
├── 📁 datos/                    # CSVs originales
│   ├── historico_equipos.csv
│   └── ...
├── 📁 notebook/
│   └── DataKnow_Analisis.ipynb  # Análisis completo
├── 📁 artifacts/                 # Resultados generados
│   ├── resultados_analisis.md
│   ├── proyeccion_costos.xlsx
│   └── 📁 graficos/
├── 📁 agente-ia/                # Código del agente
│   ├── app.py                   # Streamlit app
│   ├── agente.py                # Lógica del agente LangChain
│   ├── tools.py                 # Herramientas (search, etc.)
│   ├── requirements.txt
│   └── Dockerfile
├── 📁 docs/
│   └── diagrama-arquitectura.png
├── README.md                    # Informe completo
└── PLAN.md                      # Este archivo
```

---

## 9. Notas Clave para el Informe

### Diferencia entre Modelo y Agente IA (entregable explícito)

Basado en lo que pide el PDF:

| Aspecto | Modelo IA (tradicional) | Agente IA |
|---------|------------------------|-----------|
| **Entrada** | Datos estructurados | Percepción del entorno (datos + búsqueda web + contexto) |
| **Salida** | Predicción numérica | Acción/razonamiento contextualizado |
| **Autonomía** | Ninguna (se ejecuta y ya) | Decide cuándo buscar, qué herramientas usar |
| **Memoria** | No tiene | Mantiene contexto de la conversación |
| **Herramientas** | Ninguna | Puede usar APIs, buscadores, bases de datos |
| **Ejemplo en este caso** | Regresión lineal → $441.50 | "El costo es $441.50, y según las noticias de esta semana, el precio de Z subió 2%, por lo que..." |

### Supuestos del Análisis

- Los datos históricos (2010-2023) son representativos de la relación subyacente
- La relación entre materias primas y equipos es lineal (justificado por R² > 0.96)
- No hay estacionalidad significativa en los precios (validado en EDA)
- El promedio móvil simple de 3 meses es adecuado para pronóstico a corto plazo

---

## 10. Timeline

| Paso | Tiempo estimado |
|------|----------------|
| Finalizar notebook + artifacts | ⏱️ < 1 hora |
| Setup AWS (cuenta, S3, Bedrock, IAM) | ⏱️ 30 min |
| Construir agente IA (Streamlit + LangChain) | ⏱️ 2-3 horas |
| Dockerizar y desplegar en EC2 | ⏱️ 1 hora |
| Diagrama de arquitectura | ⏱️ 30 min |
| README + GitHub | ⏱️ 30 min |
| **Total** | **~5-6 horas** |

---

*Plan creado el — Julio 2026*
*Última actualización: Julio 2026*
