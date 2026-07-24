# Resultados del Analisis - DataKnow
---

## 1. Resumen Ejecutivo

* **Registros analizados:** 3530 dias habiles
* **Periodo:** 2010-01-04 a 2023-08-31
* **Variables:** X, Y, Z (materias primas), Equipo 1, Equipo 2
* **Modelo Equipo 1:** Y sola - R2 = 0.9932, MAE = $7.64
* **Modelo Equipo 2:** Y + Z - R2 = 0.9897, MAE = $14.40
* **Metodo de pronostico:** Naive (ultimo mes)

## 2. Analisis Exploratorio

### Correlaciones

| Par | Correlacion |
|-----|------------|
| Y - Z | 0.8442 |
| X - Y | 0.4916 |
| X - Z | 0.4757 |
| Y - Equipo 1 | 0.9966 |
| Z - Equipo 2 | 0.9827 |

### Multicolinealidad

Y y Z presentan VIF ~ 3.5, consistente con su correlacion de 0.844.
Esto indica que comparten informacion y no es posible separar
sus efectos individuales con los datos disponibles.

## 3. Construccion de Modelos

### 3.1 Variables individuales

| Variable | R2 Eq1 | MAE Eq1 | R2 Eq2 | MAE Eq2 |
|----------|--------|---------|--------|---------|
| X | 0.2739 | $70.27 | 0.2813 | $111.46 |
| Y | 0.9932 | $7.64 | 0.8330 | $54.00 |
| Z | 0.7124 | $47.50 | 0.9656 | $25.14 |

### 3.2 Combinaciones evaluadas

| Variables | R2 Eq1 | AIC Eq1 | R2 Eq2 | AIC Eq2 |
|----------|--------|--------|--------|--------|
| X | 0.2739 | 42309 | 0.2813 | 45115 |
| Y | 0.9932 | 25797 | 0.8330 | 39963 |
| Z | 0.7124 | 39040 | 0.9656 | 34381 |
| X + Y | 0.9947 | 24932 | 0.8418 | 39774 |
| X + Z | 0.7315 | 38798 | 0.9708 | 33815 |
| Y + Z | 0.9933 | 25786 | 0.9897 | 30131 |
| X + Y + Z | 0.9947 | 24934 | 0.9915 | 29448 |

## 4. Modelos Seleccionados

### Equipo 1 ~ Y

* Ecuacion: Equipo1 = 5.5646 + 0.8181 * Y
* R2: 0.9932
* MAE: $7.64
* Error estandar residual: $9.34

| Variable | Coeficiente | p-value | Significancia |
|----------|------------|---------|--------------|
| const | 5.5646 | 0.000000 | *** |
| Y | 0.8181 | 0.000000 | *** |

### Equipo 2 ~ Y + Z

* Ecuacion: Equipo2 = 7.0220 + 0.3552 * Y + 0.3365 * Z
* R2: 0.9897
* MAE: $14.40
* Error estandar residual: $17.26

| Variable | Coeficiente | p-value | Significancia |
|----------|------------|---------|--------------|
| const | 7.0220 | 0.000020 | *** |
| Y | 0.3552 | 0.000000 | *** |
| Z | 0.3365 | 0.000000 | *** |

## 5. Validacion

### Residuales

| Modelo | Media residual | Std residual | Shapiro p-value |
|--------|---------------|-------------|----------------|
| Eq1 ~ Y | 0.0000 | 9.34 | 0.0000 |
| Eq2 ~ Y+Z | 0.0000 | 17.26 | 0.0000 |

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
* Naive Y = $557.08
* Naive Z = $2135.61

| Equipo | Proyeccion | IC 95% Inferior | IC 95% Superior |
|--------|-----------|-----------------|-----------------|
| Equipo 1 | $461.31 | $443.00 | $479.62 |
| Equipo 2 | $923.57 | $889.75 | $957.39 |

* Ultimo precio real (2023-08-31): Equipo 1 = $451.73, Equipo 2 = $955.35

### Intervalos de confianza

Se usa IC 95% = 1.96 * std residual. Asume errores aproximadamente normales.
* Equipo 1: std residual = $9.34, IC = +/- $18.31
* Equipo 2: std residual = $17.26, IC = +/- $33.82

---
*Documento generado el Julio 2026 para prueba tecnica DataKnow*
