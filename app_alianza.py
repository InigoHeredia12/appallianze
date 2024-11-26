import streamlit as st
from etfs_data import ETFs_Data
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
import plotly.express as px
from fpdf import FPDF

# Función para obtener datos financieros de un ETF de Yahoo Finance con caché
@st.cache_data
def obtener_datos_etf(ticker, periodo):
    etf = yf.Ticker(ticker)
    datos = etf.history(period=periodo)
    return datos

# Cálculo de rendimiento por periodo
def calcular_rendimientos(datos):
    datos['Mensual'] = datos['Close'].pct_change(periods=21)
    datos['Anual'] = datos['Close'].pct_change(periods=252)
    return datos

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
    max_selections=5
)

# Selección de periodo de análisis
periodo_seleccionado = st.sidebar.selectbox("Selecciona el periodo", ("1mo", "3mo", "6mo", "1y", "3y", "5y", "10y"))

if etfs_seleccionados:
    # Crear pestañas para organizar las secciones
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Detalles del ETF", "Visualización de Precios", "Análisis Estadístico", "Rendimiento", "Top 10 por Rendimiento", "Descargar Datos"])

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
                datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                if not datos_etf.empty:
                    st.write(f"### Gráfico de Precios de Cierre para {ticker}")
                    
                    # Crear gráfico con Plotly
                    fig = px.line(
                        datos_etf, 
                        x=datos_etf.index, 
                        y="Close", 
                        title=f"Precio de Cierre de {ticker} ({periodo_seleccionado})",
                        labels={"Close": "Precio de Cierre", "Date": "Fecha"}
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

    # Pestaña 3: Análisis Estadístico
    with tab3:
        st.write("### Análisis Estadístico de los ETFs Seleccionados")

        # Explicación sobre las métricas
        st.markdown("""
        **Análisis Estadístico**: Esta sección presenta estadísticas clave para ayudarte a evaluar el comportamiento y riesgo de los ETFs seleccionados. A continuación se presentan las métricas:

        - **Rendimiento Diario Promedio**: Muestra el rendimiento promedio diario del ETF durante el periodo seleccionado.
        - **Rendimiento Total**: El rendimiento total del ETF desde el inicio hasta el final del periodo.
        - **Riesgo Diario**: La desviación estándar de los rendimientos diarios, que mide la volatilidad del ETF.
        - **Ratio de Sharpe**: Mide el rendimiento ajustado por el riesgo. Es útil para evaluar si el rendimiento de un ETF compensa el riesgo asumido.

        ### Interpretación de las métricas:
        - Un **Ratio de Sharpe** más alto indica que el ETF ha generado un mayor rendimiento por unidad de riesgo, lo que generalmente se interpreta como una mejor opción de inversión.
        """)

        resultados_estadisticos = []

        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)

                if not datos_etf.empty:
                    rendimiento = datos_etf['Close'].pct_change().mean()
                    riesgo = datos_etf['Close'].pct_change().std()
                    ratio_riesgo_rendimiento = rendimiento / riesgo if riesgo != 0 else np.nan
                    ratio_sharpe = rendimiento / riesgo if riesgo != 0 else np.nan

                    resultados_estadisticos.append({
                        "ETF": etf_name,
                        "Rendimiento Diario Promedio (%)": rendimiento * 100,
                        "Riesgo Diario (Desviación Estándar) (%)": riesgo * 100,
                        "Relación Riesgo/Rendimiento": ratio_riesgo_rendimiento,
                        "Ratio de Sharpe": ratio_sharpe,
                    })

        if resultados_estadisticos:
            # Mostrar tabla consolidada
            df_estadistica = pd.DataFrame(resultados_estadisticos)
            st.write("#### Tabla de Estadísticas")
            st.dataframe(
                df_estadistica.style.format({
                    "Rendimiento Diario Promedio (%)": "{:.2f} %",
                    "Riesgo Diario (Desviación Estándar) (%)": "{:.2f} %",
                    "Relación Riesgo/Rendimiento": "{:.2f}",
                    "Ratio de Sharpe": "{:.2f}"
                }),
                use_container_width=True,
            )

    # Pestaña 4: Rendimiento
    with tab4:
        st.header("Cálculo de Rendimientos")
        monto_inversion = st.number_input("Ingresa la cantidad de inversión inicial:", min_value=0.0, format="%.2f")
        if monto_inversion > 0:
            resultados = []
            grafica_datos = {}

            for etf_name in etfs_seleccionados:
                etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
                if etf_info:
                    ticker = etf_info['simbolo']
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                    datos_etf = calcular_rendimientos(datos_etf)

                    if not datos_etf.empty:
                        rendimiento_mensual = datos_etf['Mensual'].mean()
                        rendimiento_anual = datos_etf['Anual'].mean()

                        rendimiento_dinero_anual = monto_inversion * (1 + rendimiento_anual)
                        rendimiento_dinero_mensual = monto_inversion * (1 + rendimiento_mensual)

                        resultados.append({
                            "ETF": etf_name,
                            "Rendimiento Mensual (%)": f"{rendimiento_mensual:.2%}",
                            "Rendimiento Anual (%)": f"{rendimiento_anual:.2%}",
                            "Dinero Mensual": f"${rendimiento_dinero_mensual:,.2f}",
                            "Dinero Anual": f"${rendimiento_dinero_anual:,.2f}",
                        })

                        grafica_datos[etf_name] = rendimiento_dinero_anual

            if resultados:
                st.write("### Rendimientos Comparativos")
                df_resultados = pd.DataFrame(resultados)
                st.dataframe(df_resultados)


    # Pestaña 5: Top 10 por Rendimiento
    with tab5:
        st.write("### Top 10 ETFs por Rendimiento en el Periodo Seleccionado")

        rendimiento_por_etf = []

        for etf_name in etfs_seleccionados:
            etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
            if etf_info:
                ticker = etf_info['simbolo']
                datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                if not datos_etf.empty:
                    rendimiento_anual = datos_etf['Close'].pct_change(periods=252).mean()
                    rendimiento_por_etf.append({
                        "ETF": etf_name,
                        "Rendimiento Anual (%)": rendimiento_anual * 100,
                    })

        # Ordenar y mostrar los 10 mejores ETFs
        if rendimiento_por_etf:
            top_etfs = sorted(rendimiento_por_etf, key=lambda x: x['Rendimiento Anual (%)'], reverse=True)[:10]
            st.write("#### Los 10 mejores ETFs por rendimiento anual:")
            df_top_etfs = pd.DataFrame(top_etfs)
            st.dataframe(df_top_etfs)

        # Pestaña 6: Descargar Datos como CSV
    with tab6:
        st.write("### Descargar Datos de ETFs Seleccionados")

        def generar_csv(datos):
            # Convertir el DataFrame de datos a un archivo CSV
            csv = datos.to_csv(index=True)
            return csv.encode('utf-8')

        if st.button("Generar CSV de Datos"):
            # Crear un DataFrame con los datos históricos de los ETFs seleccionados
            all_data = []

            for etf_name in etfs_seleccionados:
                etf_info = next((etf for etf in ETFs_Data if etf['nombre'] == etf_name), None)
                if etf_info:
                    ticker = etf_info['simbolo']
                    datos_etf = obtener_datos_etf(ticker, periodo_seleccionado)
                    if not datos_etf.empty:
                        datos_etf['ETF'] = etf_name  # Añadir nombre de ETF a los datos
                        all_data.append(datos_etf)

            if all_data:
                # Concatenar todos los datos de ETFs seleccionados en un solo DataFrame
                df_all_etfs = pd.concat(all_data)
                
                # Generar el archivo CSV
                csv_data = generar_csv(df_all_etfs)

                # Descargar el archivo CSV
                st.download_button(
                    label="Descargar Datos en CSV",
                    data=csv_data,
                    file_name="Datos_Etfs.csv",
                    mime="text/csv"
                )
