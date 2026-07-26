"""
Agente IA - DataKnow
Asistente conversacional para resultados de análisis de costos
Basado en: Amazon Bedrock (Amazon Nova Lite) + LangGraph + Streamlit
"""
import os
import json
import streamlit as st
import boto3
from langchain_aws import ChatBedrock
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from ddgs import DDGS

# ── Config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="DataKnow - Agente IA", layout="wide")

# ── Knowledge Base ──────────────────────────────────────────────────
@st.cache_data
def load_knowledge_base():
    paths = [
        "../Resultados/resultados_analisis.md",
        "Resultados/resultados_analisis.md",
        "/app/Resultados/resultados_analisis.md",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p) as f:
                return f.read()
    return "Knowledge base no encontrado."

# ── Cliente Bedrock ─────────────────────────────────────────────────
@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime")

@st.cache_resource
def get_llm():
    return ChatBedrock(
        model_id="amazon.nova-lite-v1:0",
        client=get_bedrock_client(),
        model_kwargs={"max_tokens": 1500, "temperature": 0.3, "top_p": 0.9}
    )

# ── Tools ───────────────────────────────────────────────────────────
def buscar_internet(query: str) -> str:
    """Busca informacion actual en internet y devuelve resultados con fuentes."""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=5))
        if not results:
            # Try a more specific fallback query
            results = list(ddgs.text(f"{query} precios 2026", max_results=5))
        if not results:
            return "No se encontraron resultados para esta busqueda."
        output = []
        for i, r in enumerate(results, 1):
            title = r.get('title', '').strip()
            body = r.get('body', '').strip()
            href = r.get('href', '')
            if title and body:
                output.append(f"{i}. {title}")
                output.append(f"   {body[:200]}")
                output.append(f"   Fuente: {href}")
        return "\n".join(output) if output else "Sin resultados."
    except Exception as e:
        return f"Error al buscar: {str(e)}"

tools = [
    Tool(
        name="buscar_en_internet",
        func=buscar_internet,
        description=(
            "Usa esta herramienta para buscar en internet informacion actual sobre: "
            "precios de materias primas, tendencias del sector construccion, "
            "contexto economico, noticias del mercado. "
            "DEBES usarla cuando la pregunta requiera informacion que no esta en el analisis."
        )
    )
]

# ── Agente ──────────────────────────────────────────────────────────
@st.cache_resource
def get_agent():
    llm = get_llm()
    kb = load_knowledge_base()

    system_prompt = f"""Eres un asistente de IA especializado en análisis de datos y costos de construcción.

CONOCIMIENTOS DEL ANÁLISIS:
{kb}

INSTRUCCIONES:
1. Si la pregunta es sobre el análisis (R2, MAE, modelos, proyeccion, coeficientes, resultados), responde usando la informacion del analisis. NO uses la herramienta de busqueda para esto.
2. Si la pregunta es sobre el mercado actual, tendencias de precios, noticias del sector, o cualquier informacion que NO este en el analisis, DEBES usar la herramienta buscar_en_internet. No digas que no tienes acceso a internet. Cuando busques, se especifico: si preguntan por "materias primas", busca "materiales construccion acero hierro cemento precios" o el material relevante. Incluye las fuentes de los resultados en tu respuesta.
3. Se preciso: menciona R2, MAE, coeficientes cuando sea relevante.
4. Responde en espanol de forma clara y profesional.
5. Combina los resultados de busqueda con el analisis cuando sea pertinente.

CÓMO PROYECTAR COSTOS A N MESES (si preguntan):
1. Usa los ultimos valores mensuales conocidos:
   - Y ultimo mes: $555.33 por dia promedio
   - Z ultimo mes: $2,142.52 por dia promedio
2. Aplica las ecuaciones del modelo mensual (costo prom. diario):
   - Eq1/día = 5.49 + 0.8182 * Y
   - Eq2/día = 6.49 + 0.3551 * Y + 0.3368 * Z
   - Resultado: Eq1 = $459.87/día, Eq2 = $925.29/día
3. Para PRESUPUESTO TOTAL a N meses:
   - Costo por mes = valor_diario * 22 (dias habiles aprox.)
   - Eq1/mes = $459.87 * 22 = $10,117
   - Eq2/mes = $925.29 * 22 = $20,356
   - PRESUPUESTO ACUMULADO = costo_mes × N
   - IC acumulado = 1.96 × sigma × sqrt(N) × 22
   - sigma(Eq1) = $4.69/día, sigma(Eq2) = $7.74/día
4. Ejemplo para 3 meses:
   | Mes | Eq1/día | Eq2/día | Eq1/mes (~22d) | Eq2/mes (~22d) |
   |-----|---------|---------|-----------------|-----------------|
   | 1   | $459.87 | $925.29 | ~$10,117        | ~$20,356        |
   | 2   | $459.87 | $925.29 | ~$10,117        | ~$20,356        |
   | 3   | $459.87 | $925.29 | ~$10,117        | ~$20,356        |
   PRESUPUESTO TOTAL 3 meses: Eq1 = ~$30,351 | Eq2 = ~$61,068
   IC TOTAL 95%: Eq1 ± $1,214 | Eq2 ± $2,003
5. Siempre muestra el IC y explica que se amplía con sqrt(meses).
6. Si preguntan por presupuesto para una FECHA ESPECÍFICA (ej: "enero 2024"):
   - Calcula meses desde ago/2023: enero 2024 = 5 meses
   - Presupuesto total = costo_mes × 5
   - IC = 1.96 × sigma × sqrt(5) × 22

DIFERENCIA ENTRE MODELO Y AGENTE (si preguntan):
- Un modelo de IA recibe datos y produce predicciones. Ej: el modelo de regresión lineal.
- Un agente de IA es un sistema autónomo que percibe su entorno, usa herramientas (búsqueda web),
  mantiene memoria, y ejecuta acciones para alcanzar un objetivo. Yo soy un agente: puedo buscar
  información externa, recordar la conversación y combinar fuentes para responder."""

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )

# ── UI ──────────────────────────────────────────────────────────────
def main():
    st.title("DataKnow - Agente de Analisis")

    with st.sidebar:
        st.header("Acerca del analisis")
        st.text("Datos: 3,530 registros diarios (2010-2023)\n")
        st.text("Modelos:\n  Equipo 1 ~ Y: R2 = 0.993, MAE = $7.64\n  Equipo 2 ~ Y+Z: R2 = 0.990, MAE = $14.40\n")
        st.text("Pronostico mensual (Naive + IC creciente):\n  Eq1: $460.67/mes +- $9.19 (1er mes)\n  Eq2: $922.44/mes +- $15.17 (1er mes)\n  El IC se amplia con sqrt(meses)")
        st.divider()
        st.caption("Preguntas sugeridas:")
        st.caption("- Cual es el R2 del modelo de Equipo 1?")
        st.caption("- Que variables explican el Equipo 2?")
        st.caption("- Cual es la proyeccion de costos?")
        st.caption("- Como se comporta el mercado actual de materias primas? busca en internet")
        st.caption("- Explica la diferencia entre modelo y agente")
        st.caption("- Proyecta costos a 3 meses para el Equipo 1")
        st.caption("- Cual es el presupuesto para 6 meses del Equipo 2?")

    # Inicializar chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "¡Hola! Soy el agente de análisis de DataKnow. "
                "Puedo responder preguntas sobre el análisis de costos de equipos "
                "y buscar información actual del mercado. ¿En qué puedo ayudarte?"
            )
        })

    if "agent" not in st.session_state:
        st.session_state.agent = get_agent()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Haz una pregunta sobre el análisis..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                try:
                    agent = st.session_state.agent
                    response = agent.invoke(
                        {"messages": [
                            *st.session_state.chat_history,
                            {"role": "user", "content": prompt}
                        ]})
                    # Extract the last AI message - handle content blocks
                    ai_response = response["messages"][-1].content
                    import sys; print(f'DEBUG ai_response type={type(ai_response).__name__}, len={len(ai_response) if isinstance(ai_response, (list,str)) else "N/A"}', file=sys.stderr)
                    if isinstance(ai_response, list) and len(ai_response) > 0: print(f'DEBUG first={ai_response[0]}', file=sys.stderr)
                    if isinstance(ai_response, list):
                        # Filter out reasoning_content, keep only text blocks
                        import re
                        texts = []
                        for b in ai_response:
                            if isinstance(b, dict) and b.get("type") == "text":
                                t = b.get("text", "")
                                # Strip <thinking>...</thinking> tags that Nova may include
                                t = re.sub(r'<thinking>.*?</thinking>\s*', '', t, flags=re.DOTALL)
                                if t.strip():
                                    texts.append(t)
                        ai_msg = "\n".join(texts) if texts else str(ai_response)
                    else:
                        ai_msg = str(ai_response)
                    # Strip <thinking> tags from Nova before displaying
                    ai_msg = __import__("re").sub(r"<thinking>.*?</thinking>\s*", "", ai_msg, flags=__import__("re").DOTALL).strip()
                    if not ai_msg: ai_msg = "Sin respuesta."
                    st.markdown(ai_msg)
                    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                    st.session_state.chat_history = response["messages"]
                except Exception as e:
                    error_msg = f"Error al procesar la consulta: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
