"""
Agente IA - DataKnow
Asistente conversacional para resultados de análisis de costos
Basado en: Amazon Bedrock (Claude 3 Haiku) + LangGraph + Streamlit
"""
import os
import json
import streamlit as st
import boto3
from langchain_aws import ChatBedrock
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from duckduckgo_search import DDGS

# ── Config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="DataKnow - Agente IA", page_icon="📊", layout="wide")

# ── Knowledge Base ──────────────────────────────────────────────────
@st.cache_data
def load_knowledge_base():
    paths = [
        "../artifacts/resultados_analisis.md",
        "artifacts/resultados_analisis.md",
        "/app/artifacts/resultados_analisis.md",
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
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=get_bedrock_client(),
        model_kwargs={"max_tokens": 1500, "temperature": 0.3, "top_p": 0.9}
    )

# ── Tools ───────────────────────────────────────────────────────────
def buscar_internet(query: str) -> str:
    """Busca información actual sobre precios, tendencias y noticias del mercado."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No se encontraron resultados."
            output = []
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                output.append(f"**{title}**\n{body}\nFuente: {href}")
            return "\n\n".join(output)
    except Exception as e:
        return f"Error al buscar: {str(e)}"

tools = [
    Tool(
        name="buscar_en_internet",
        func=buscar_internet,
        description=(
            "Útil cuando necesitas información actual sobre precios de materias primas, "
            "tendencias del sector construcción, contexto económico o noticias del mercado."
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
1. Responde preguntas sobre el análisis usando la información proporcionada.
2. Si necesitas información actual de mercado, usa buscar_en_internet.
3. Sé preciso: menciona R², MAE, coeficientes cuando sea relevante.
4. Responde en español de forma clara y profesional.
5. Combina los resultados de búsqueda con el análisis cuando sea pertinente.

DIFERENCIA ENTRE MODELO Y AGENTE (si preguntan):
- Un modelo de IA recibe datos y produce predicciones. Ej: el modelo de regresión lineal.
- Un agente de IA es un sistema autónomo que percibe su entorno, usa herramientas (búsqueda web),
  mantiene memoria, y ejecuta acciones para alcanzar un objetivo. Yo soy un agente: puedo buscar
  información externa, recordar la conversación y combinar fuentes para responder."""

    return create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=system_prompt,
    )

# ── UI ──────────────────────────────────────────────────────────────
def main():
    st.title("📊 DataKnow - Agente de Análisis")

    with st.sidebar:
        st.header("🔍 Acerca del análisis")
        st.markdown("""
        **Datos:** 3,530 registros diarios (2010–2023)

        **Modelos:**
        - Equipo 1 ~ Y → R² = 0.993, MAE = $7.64
        - Equipo 2 ~ Y+Z → R² = 0.990, MAE = $14.40

        **Pronóstico (Naive):**
        - Eq1: $461.31 ± $18.31
        - Eq2: $923.57 ± $33.82
        """)
        st.divider()
        st.caption("💡 Preguntas sugeridas:")
        st.caption("- ¿Cuál es el R² del modelo de Equipo 1?")
        st.caption("- ¿Qué variables explican el Equipo 2?")
        st.caption("- ¿Cuál es la proyección de costos?")
        st.caption("- ¿Cómo se comporta el mercado actual de materias primas?")
        st.caption("- Explica la diferencia entre modelo y agente")

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
                    # Invoke the agent with the full conversation history
                    response = agent.invoke(
                        {"messages": [
                            *st.session_state.chat_history,
                            {"role": "user", "content": prompt}
                        ]}
                    )
                    # Extract the last AI message
                    ai_msg = response["messages"][-1].content
                    st.markdown(ai_msg)
                    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                    # Update stored history
                    st.session_state.chat_history = response["messages"]
                except Exception as e:
                    error_msg = f"Error al procesar la consulta: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
