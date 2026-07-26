# Resultados del Analisis - DataKnow
---

## 1. Resumen Ejecutivo

* **Registros analizados:** 164 meses (resampleo de 3530 registros diarios)
* **Periodo:** 2010-01-31 a 2023-08-31
* **Variables:** X, Y, Z (materias primas), Equipo 1, Equipo 2
* **Modelo Equipo 1:** Y sola - R2 = 0.9983, MAE = $3.83
* **Modelo Equipo 2:** Y + Z - R2 = 0.9979, MAE = $6.38
* **Metodo de pronostico:** Naive (ultimo mes)

## 2. Analisis Exploratorio

### Correlaciones

| Par | Correlacion |
|-----|------------|
| Y - Z | 0.8534 |
| X - Y | 0.4963 |
| X - Z | 0.4782 |
| Y - Equipo 1 | 0.9991 |
| Z - Equipo 2 | 0.9874 |

### Multicolinealidad

Y y Z presentan VIF ~ 3.5, consistente con su correlacion de 0.844.
Esto indica que comparten informacion y no es posible separar
sus efectos individuales con los datos disponibles.

## 3. Construccion de Modelos

### 3.1 Variables individuales

| Variable | R2 Eq1 | MAE Eq1 | R2 Eq2 | MAE Eq2 |
|----------|--------|---------|--------|---------|
| X | 0.2799 | $69.47 | 0.2861 | $110.38 |
| Y | 0.9983 | $3.83 | 0.8494 | $51.03 |
| Z | 0.7310 | $45.81 | 0.9749 | $21.15 |

### 3.2 Combinaciones evaluadas

| Variables | R2 Eq1 | AIC Eq1 | R2 Eq2 | AIC Eq2 |
|----------|--------|--------|--------|--------|
| X | 0.2799 | 1966 | 0.2861 | 2095 |
| Y | 0.9983 | 975 | 0.8494 | 1840 |
| Z | 0.7310 | 1804 | 0.9749 | 1546 |
| X + Y | 0.9997 | 665 | 0.8573 | 1833 |
| X + Z | 0.7497 | 1794 | 0.9800 | 1511 |
| Y + Z | 0.9983 | 975 | 0.9979 | 1142 |
| X + Y + Z | 0.9997 | 667 | 0.9997 | 795 |

## 4. Modelos Seleccionados

### Equipo 1 ~ Y

* Ecuacion: Equipo1 = 5.4863 + 0.8182 * Y
* R2: 0.9983
* MAE: $3.83
* Error estandar residual: $4.69

| Variable | Coeficiente | p-value | Significancia |
|----------|------------|---------|--------------|
| const | 5.4863 | 0.000430 | *** |
| Y | 0.8182 | 0.000000 | *** |

### Equipo 2 ~ Y + Z

* Ecuacion: Equipo2 = 6.4862 + 0.3551 * Y + 0.3368 * Z
* R2: 0.9979
* MAE: $6.38
* Error estandar residual: $7.74

| Variable | Coeficiente | p-value | Significancia |
|----------|------------|---------|--------------|
| const | 6.4862 | 0.0657 | * |
| Y | 0.3551 | 0.000000 | *** |
| Z | 0.3368 | 0.000000 | *** |

## 5. Validacion

### Residuales

| Modelo | Media residual | Std residual | Shapiro p-value |
|--------|---------------|-------------|----------------|
| Eq1 ~ Y | -0.0000 | 4.69 | 0.0070 |
| Eq2 ~ Y+Z | 0.0000 | 7.74 | 0.0013 |

### Validacion fuera de muestra (ultimos 24 meses)

| Modelo | Train R2 | Test R2 | Test MAE |
|--------|---------|--------|---------|
| Eq1 ~ Y | 0.9926 | 0.9896 | $8.76 |
| Eq2 ~ Y+Z | 0.9851 | 0.9857 | $17.23 |

Ambos modelos son estables (diferencia R2 train-test < 0.005).

## 6. Pronostico

### Metodo

Se evaluaron 4 metodos: Naive (ultimo mes), SMA(3), SMA(6) y SES.
Naive obtuvo el menor error en backtesting para las 3 materias primas.
Las series se comportan como caminatas aleatorias (ADF no estacionario,
diferenciacion si lo es). El mejor predictor del proximo valor es
el ultimo valor conocido.

### Proyeccion

* Periodo de referencia: 2023-07-31 a 2023-08-31
* Naive Y = $555.33
* Naive Z = $2142.52

| Equipo | Proyeccion | IC 95% Inferior | IC 95% Superior |
|--------|-----------|-----------------|-----------------|
| Equipo 1 | $459.87 | $450.68 | $469.06 |
| Equipo 2 | $925.29 | $910.12 | $940.46 |

* Ultimo precio real (2023-08-31): Equipo 1 = $461.04, Equipo 2 = $927.66

### Intervalos de confianza

Se usa IC 95% = 1.96 * std residual. Asume errores aproximadamente normales.
* Equipo 1: std residual = $4.69, IC = +/- $9.19
* Equipo 2: std residual = $7.74, IC = +/- $15.17

---
*Documento generado el Julio 2026 para prueba tecnica DataKnow*
