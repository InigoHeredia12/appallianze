import streamlit as st
from etfs_data import ETFs_Data
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Función para obtener datos financieros de un ETF de Yahoo Finance con caché
@st.cache_data
def obtener_datos_etf(ticker, periodo):
    etf = yf.Ticker(ticker)
    datos = etf.history(period=periodo)
    return datos

# Cálculo de rendimiento y riesgo
def calcular_rendimiento_riesgo(datos):
    rendimiento = datos['Close'].pct_change().mean() * 252  # 252 días hábiles
    riesgo = datos['Close'].pct_change().std() * (252 ** 0.5)
    return rendimiento, riesgo

# Cálculo del Sharpe Ratio
def calcular_sharpe_ratio(rendimientos, tasa_libre_de_riesgo=0.02):
    exceso_rendimiento = rendimientos - tasa_libre_de_riesgo
    sharpe_ratio = exceso_rendimiento.mean() / exceso_rendimiento.std() * (252 ** 0.5)
    return sharpe_ratio

# Establecer el tema de la aplicación
st.set_page_config(page_title="Simulador Financiero de ETFs", layout="wide")

# Título de la aplicación
st.title("Simulador Financiero de ETFs - Allianz Patrimonial")
st.write("Esta aplicación permite analizar ETFs y calcular el rendimiento y riesgo para diferentes periodos de tiempo.")

# Mostrar la fecha y hora actual
fecha_hora = datetime.now().strftime("%A, %d de %B de %Y - %H:%M")
st.markdown(f"<small style='font-size: 14px; color: gray;'>{fecha_hora}</small>", unsafe_allow_html=True)

# Sidebar para selección de ETFs
st.sidebar.header("Configuraciones")
etfs_seleccionados = st.sidebar.multiselect(
    "Selecciona uno o más ETFs para ver los detalles:",
    options=[etf['nombre'] for etf in ETFs_Data],
    default=[],
    max_selections=5  # Limitar a un máximo de 5 ETFs seleccionados
)

# Selección de periodo de análisis
periodo_seleccionado = st.sidebar.selectbox("Selecciona el periodo", ("1mo", "3mo", "6mo", "1y", "3y", "5y", "10y"))

# Verificar si hay algún ETF seleccionado
if etfs_seleccionados:
    # Crear pestañas para organizar las secciones
    tab1, tab2, tab3, tab4 = st.tabs(["Detalles del ETF", "Visualización de Precios", "Análisis Estadístico", "Descargar Datos"])

    # Pestaña 1: Detalles del ETF
    with tab1:
        st.write("### Detalles de los ETFs Seleccionados:")
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                st.write(f"**Nombre**: {etf_info['nombre']}")
                st.write(f"**Descripción**: {etf_info['descripcion']}")
                st.write(f"**Símbolo**: {etf_info['simbolo']}")
                st.markdown("---")

    # Pestaña 2: Visualización de Precios
    with tab2:
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                
                with st.spinner(f'Cargando datos para {ticker}...'):
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)

                if not datos_etf.empty:
                    st.write(f"### Gráfico de Precios de Cierre para {ticker}")
                    st.line_chart(datos_etf['Close'], width=0, height=0, use_container_width=True)

                    # Gráfico de Dispersión (Open vs Close)
                    st.write("### Gráfico de Dispersión (Open vs Close)")
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.scatter(datos_etf.index, datos_etf['Open'], color='blue', label='Precio de Apertura', alpha=0.5)
                    ax.scatter(datos_etf.index, datos_etf['Close'], color='red', label='Precio de Cierre', alpha=0.5)
                    ax.set_title(f'Gráfico de Dispersión: Open vs Close para {ticker}')
                    ax.set_xlabel('Fecha')
                    ax.set_ylabel('Precio')
                    ax.grid(True)
                    ax.legend()
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                    # Gráfico de Volumen de Trading
                    st.write("### Volumen de Trading para ", ticker)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.bar(datos_etf.index, datos_etf['Volume'], color='purple', alpha=0.6)
                    ax.set_title(f'Volumen de Trading para {ticker}')
                    ax.set_xlabel('Fecha')
                    ax.set_ylabel('Volumen')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                else:
                    st.write(f"No se encontraron datos para el ETF {ticker} en el periodo especificado.")

    # Pestaña 3: Análisis Estadístico
    with tab3:
        rendimientos_totales = []
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                
                with st.spinner(f'Cargando datos para {ticker}...'):
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)

                if not datos_etf.empty:
                    # Resumen estadístico
                    st.write(f"### Resumen Estadístico para {ticker}")
                    st.write(datos_etf.describe())

                    # Calcular rendimiento y riesgo
                    rendimiento, riesgo = calcular_rendimiento_riesgo(datos_etf)
                    rendimientos_totales.append(datos_etf['Close'].pct_change().dropna())
                    st.write(f"**Rendimiento Anualizado:** {rendimiento:.2%}")
                    st.write(f"**Riesgo (Desviación Estándar Anualizada):** {riesgo:.2%}")

                    # Cálculo del Sharpe Ratio
                    sharpe_ratio = calcular_sharpe_ratio(datos_etf['Close'].pct_change().dropna())
                    st.write(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")

                    # Histograma de rendimientos diarios
                    rendimientos_diarios = datos_etf['Close'].pct_change().dropna()
                    st.write("### Histograma de Rendimientos Diarios")
                    fig, ax = plt.subplots()
                    ax.hist(rendimientos_diarios, bins=30, edgecolor='black')
                    ax.set_title(f'Histograma de Rendimientos Diarios para {ticker}')
                    ax.set_xlabel('Rendimiento')
                    ax.set_ylabel('Frecuencia')
                    st.pyplot(fig)

                    # Gráfico de rendimiento vs riesgo
                    st.write("### Gráfico de Rendimiento vs Riesgo")
                    st.scatter_chart(pd.DataFrame({'Rendimiento': [rendimiento], 'Riesgo': [riesgo]}))

                else:
                    st.write(f"No se encontraron datos para el ETF {ticker} en el periodo especificado.")

        # Tabla de correlación de rendimientos diarios entre los ETFs seleccionados
        if len(etfs_seleccionados) > 1:
            rendimientos_df = pd.DataFrame()
            for etf_name in etfs_seleccionados:
                etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
                if etf_info:
                    ticker = etf_info['simbolo']
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                    rendimientos_df[etf_name] = datos_etf['Close'].pct_change().dropna()

            st.write("### Tabla de Correlación de Rendimientos entre ETFs Seleccionados")
            st.write(rendimientos_df.corr())

    # Pestaña 4: Descargar Datos
    with tab4:
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                
                with st.spinner(f'Cargando datos para {ticker}...'):
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)

                if not datos_etf.empty:
                    # Opción para descargar los datos
                    st.write("### Descargar Datos")
                    csv = datos_etf.to_csv().encode('utf-8')
                    st.download_button(
                        label=f"Descargar datos históricos de {ticker} como CSV",
                        data=csv,
                        file_name=f"{ticker}_datos_historicos.csv",
                        mime='text/csv'
                    )
                else:
                    st.write(f"No se encontraron datos para el ETF {ticker} en el periodo especificado.")
else:
    st.warning("Por favor, selecciona al menos un ETF para continuar.")


