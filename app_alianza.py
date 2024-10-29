import streamlit as st
from etfs_data import ETFs_Data
import yfinance as yf
import pandas as pd

# Título de la aplicación
st.title("Análisis de ETFs")

#### Selector de Datos ####


# Crear un multiselector usando st.multiselect
etfs_seleccionados = st.multiselect(
    "Selecciona uno o más ETFs para ver los detalles:",
    options=[etf['nombre'] for etf in ETFs_Data],  # Opciones basadas en los nombres de los ETFs
    default=[]  # Por defecto no seleccionamos ninguno
)

# Verificar si hay algún ETF seleccionado
if etfs_seleccionados:
    # Mostrar detalles de los ETFs seleccionados
    st.write("### Detalles de los ETFs Seleccionados:")
    for etf_name in etfs_seleccionados:
        # Buscar en la lista ETFs_Data el diccionario que tenga ese nombre
        etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
        if etf_info:
            # Mostrar la información del ETF seleccionado
            st.write(f"**Nombre**: {etf_info['nombre']}")
            st.write(f"**Descripción**: {etf_info['descripcion']}")
            st.write(f"**Símbolo**: {etf_info['simbolo']}")
            st.markdown("---")  # Línea divisoria entre cada ETF
else:
    st.write("Por favor, selecciona al menos un ETF para ver los detalles.")
    # Función para obtener datos financieros de un ETF de Yahoo Finance
def obtener_datos_etf(ticker, periodo):
    # Descarga los datos históricos del ETF
    etf = yf.Ticker(ticker)
    datos = etf.history(period=periodo)
    return datos

# Cálculo de rendimiento y riesgo
def calcular_rendimiento_riesgo(datos):
    # Calcula el rendimiento
    rendimiento = datos['Close'].pct_change().mean() * 252  # 252 días hábiles
    # Calcula el riesgo (desviación estándar anualizada)
    riesgo = datos['Close'].pct_change().std() * (252 ** 0.5)
    return rendimiento, riesgo

# Configuración de la aplicación
st.title("Simulador Financiero de ETFs - Allianz Patrimonial")
st.write("Esta aplicación permite analizar ETFs y calcular el rendimiento y riesgo para diferentes periodos de tiempo.")

# Selección de ETF y periodo de análisis
etf_seleccionado = st.selectbox("Selecciona el ETF", ("SPY", "IVV", "VOO", "QQQ"))  # Ejemplo de algunos ETFs populares
periodo_seleccionado = st.selectbox("Selecciona el periodo", ("1mo", "3mo", "6mo", "1y", "3y", "5y", "10y"))

# Obtención de datos
st.write(f"Mostrando datos para el ETF {etf_seleccionado} en el periodo {periodo_seleccionado}.")
datos_etf = obtener_datos_etf(etf_seleccionado, periodo_seleccionado)

# Verificación de que los datos fueron obtenidos
if not datos_etf.empty:
    st.write("### Datos Históricos del ETF")
    st.write(datos_etf.tail())  # Muestra los últimos datos

    # Calcula rendimiento y riesgo
    rendimiento, riesgo = calcular_rendimiento_riesgo(datos_etf)
    st.write(f"**Rendimiento Anualizado:** {rendimiento:.2%}")
    st.write(f"**Riesgo (Desviación Estándar Anualizada):** {riesgo:.2%}")

    # Visualización de los datos
    st.line_chart(datos_etf['Close'], width=0, height=0, use_container_width=True)
else:
    st.write("No se encontraron datos para el ETF seleccionado en el periodo especificado.")
