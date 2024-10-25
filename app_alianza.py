import streamlit as st
from etfs_data import ETFs_Data


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