# Arquitectura AWS — DataKnow

## Visión General

La solución se divide en tres capas principales dentro de una misma región de AWS (us-east-1):

1. **Agente IA** — implementado y funcionando
2. **Pipeline de Datos** — propuesta de automatización
3. **Seguridad y Observabilidad** — transversal

La EC2 tiene IP pública y está en una **subnet pública**. No se requiere NAT Gateway.
El Security Group permite únicamente HTTP (8501) y SSH desde IPs autorizadas.

---

## Capa 1: Agente IA

### Flujo

```
Usuarios → EC2 (Agente IA - Streamlit :8501)
              ↓
      Amazon Bedrock (Claude 3 Haiku)
              ↓
      DuckDuckGo (Búsqueda web)
              ↓
      S3 (Artifacts del análisis)
```

> **CloudFront + ALB:** No se usan por ser overkill para una sola instancia (~$22/mes el ALB). Se agregarían si hubiera múltiples instancias o se requiriera HTTPS.

### Componentes

| Componente | Servicio | Rol |
|------------|----------|-----|
| **EC2 t3.micro** | EC2 (Free Tier) | Hostea Streamlit con el agente IA. IP pública, puerto 8501. Security Group restrictivo. |
| **Amazon Bedrock** | Bedrock | LLM Claude 3 Haiku para respuestas del agente. |
| **DuckDuckGo** | Externo | Búsqueda web para contexto de mercado. Sin API key. |
| **S3** | S3 | Almacena artifacts (.md, .xlsx, .png, .html). |

### Flujo detallado

1. El evaluador accede vía HTTP a la IP pública de la EC2, puerto 8501
2. Streamlit renderiza el agente conversacional
3. El agente (LangGraph) recibe la pregunta y:
   - **Si es sobre el análisis**: responde desde el knowledge base en memoria (resultados_analisis.md)
   - **Si requiere contexto de mercado**: usa DuckDuckGo para buscar información actual
   - **En ambos casos**: usa Bedrock Claude 3 Haiku para procesar y formular la respuesta
4. Los artifacts se leen desde S3

---

## Capa 2: Pipeline de Datos

### Flujo

```
S3 Input → Lambda (Script Python statsmodels + pandas) → S3 Output
                                                              ↓
                                                      Agente IA
```

> **Nota:** Si el tiempo de ejecución superara el límite de Lambda (15 min), se migraría a ECS Fargate. SageMaker + Glue + Redshift servirían si el modelo escalara a miles de variables o requiriera reentrenamiento automático.

En este prototipo el entrenamiento se ejecuta localmente y los artifacts se publican en S3 para que el agente los consuma. En producción este proceso se automatizaría mediante Lambda.

| Componente | Servicio | Rol |
|------------|----------|-----|
| **S3 Input** | S3 | Almacena CSVs originales |
| **Lambda** | Lambda | Ejecuta el script de entrenamiento (statsmodels + pandas) |
| **S3 Output** | S3 | Almacena resultados, proyecciones y artifacts |

---

## Capa 3: Seguridad y Observabilidad

| Componente | Rol |
|------------|-----|
| **AWS IAM** | Control de acceso con políticas de mínimo privilegio |
| **Amazon CloudWatch** | Logs de EC2, métricas, alarmas |
| **AWS Budgets** | Alerta configurada para notificar si el gasto supera $1 |
| **AWS KMS** | Encriptación de datos en reposo en S3 |
| **Amazon VPC** | Aislamiento de red |

---

## Costos

### Implementado (servicios activos)

| Servicio | Free Tier | Costo |
|----------|-----------|-------|
| EC2 t3.micro | 750h/mes (12 meses) | $0 |
| S3 | 5GB (12 meses) | $0 |
| Bedrock Claude Haiku | No free tier | ~$0.08 |
| **Total** | | **~$0.08** |

### Producción (opcional, si escalara)

| Servicio | Costo estimado |
|----------|---------------|
| CloudFront | ~$0.01/GB |
| ALB | ~$22/mes |
| NAT Gateway | ~$32/mes |

---

## Servicios AWS Utilizados (implementados)

1. EC2
2. S3
3. Amazon Bedrock
4. AWS IAM
5. Amazon CloudWatch
6. AWS Budgets
7. AWS KMS
8. Amazon VPC

*Documento generado para prueba técnica DataKnow — Julio 2026*
