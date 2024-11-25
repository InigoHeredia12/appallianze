import streamlit as st
from etfs_data import ETFs_Data
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

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

# Función para generar un PDF con los datos del ETF
def generar_pdf(ticker, datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"Reporte de Datos del ETF: {ticker}", ln=True, align='C')
    pdf.ln(10)  # Espaciado

    # Tabla de datos
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, "Fecha", border=1)
    pdf.cell(40, 10, "Precio de Cierre", border=1)
    pdf.cell(40, 10, "Volumen", border=1)
    pdf.cell(40, 10, "Precio de Apertura", border=1)
    pdf.ln()

    for index, row in datos.iterrows():
        pdf.cell(40, 10, str(index.date()), border=1)
        pdf.cell(40, 10, f"{row['Close']:.2f}", border=1)
        pdf.cell(40, 10, str(int(row['Volume'])), border=1)
        pdf.cell(40, 10, f"{row['Open']:.2f}", border=1)
        pdf.ln()

    # Retornar el PDF como bytes
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Detalles del ETF", "Visualización de Precios", "Análisis Estadístico", "Rendimiento", "Descargar Datos"])

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
                    st.line_chart(datos_etf['Close'], use_container_width=True)

                else:
                    st.write(f"No se encontraron datos para el ETF {ticker} en el periodo especificado.")

    # Pestaña 3: Análisis Estadístico
    with tab3:
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                if not datos_etf.empty:
                    rendimiento, riesgo = calcular_rendimiento_riesgo(datos_etf)
                    st.write(f"**Rendimiento Anualizado para {ticker}:** {rendimiento:.2%}")
                    st.write(f"**Riesgo para {ticker}:** {riesgo:.2%}")
                else:
                    st.write(f"No se encontraron datos para el ETF {ticker}.")

    # Pestaña 4: Rendimiento
    with tab4:
        monto_inversion = st.number_input("Ingresa la cantidad de inversión inicial:", min_value=0.0, format="%.2f")
        if monto_inversion > 0:
            for etf_name in etfs_seleccionados:
                etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
                if etf_info:
                    ticker = etf_info['simbolo']
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                    if not datos_etf.empty:
                        rendimiento, _ = calcular_rendimiento_riesgo(datos_etf)
                        st.write(f"Rendimiento estimado para {ticker}: {monto_inversion * (1 + rendimiento):.2f}")

    # Pestaña 5: Descargar Datos
    with tab5:
        st.write("### Descargar Datos de ETFs Seleccionados")
        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                if not datos_etf.empty:
                    pdf_bytes = generar_pdf(ticker, datos_etf)
                    st.download_button(
                        label=f"Descargar reporte PDF de {ticker}",
                        data=pdf_bytes,
                        file_name=f"{ticker}_reporte.pdf",
                        mime="application/pdf"
                    )
else:
    st.warning("Por favor, selecciona al menos un ETF para continuar.")


