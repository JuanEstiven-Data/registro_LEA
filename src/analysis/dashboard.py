import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# Esto debe ser el primer comando de Streamlit
st.set_page_config(
    page_title="Dashboard LEA - Brechas de Tiempo",
    page_icon="📊",
    layout="wide" # Ocupa todo el ancho de la pantalla
)

# --- 2. CARGA DE DATOS ---
# Usamos @st.cache_data para que el CSV no se recargue cada vez que mueves un filtro
@st.cache_data
def load_data():
    # Construimos la ruta dinámica hacia data/processed/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', 'data', 'processed', 'registro_consolidado.csv')
    
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo en: {file_path}. Ejecuta el pipeline primero.")
        st.stop()
        
    return pd.read_csv(file_path)

df = load_data()

# --- 3. BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros de Análisis")

# Filtro interactivo por Carrera
todas_las_carreras = df['carrera'].dropna().unique().tolist()
carreras_seleccionadas = st.sidebar.multiselect(
    "Selecciona la Carrera:",
    options=todas_las_carreras,
    default=todas_las_carreras # Por defecto muestra todas
)

# Filtro interactivo por Semestre (Slider)
min_semestre = int(df['semestre'].min())
max_semestre = int(df['semestre'].max())
semestre_rango = st.sidebar.slider(
    "Rango de Semestre:",
    min_value=min_semestre,
    max_value=max_semestre,
    value=(min_semestre, max_semestre)
)

# Aplicar los filtros al DataFrame
df_filtrado = df[
    (df['carrera'].isin(carreras_seleccionadas)) &
    (df['semestre'] >= semestre_rango[0]) &
    (df['semestre'] <= semestre_rango[1])
]

# --- 4. CUERPO PRINCIPAL DEL DASHBOARD ---
st.title("📊 Análisis de Monitorías - Laboratorio LEA")
st.markdown("Visualización interactiva generada a partir del *pipeline* automatizado ETL.")

# Tarjetas de Resumen (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Total Registros (Filtrados)", len(df_filtrado))
col2.metric("Estudiantes Únicos", df_filtrado['estudiante_id'].nunique())
col3.metric("Carreras Distintas", df_filtrado['carrera'].nunique())

st.divider() # Línea horizontal separadora

# --- 5. GRÁFICOS CON PLOTLY ---
# Fila 1 de gráficos (Dividida en 2 columnas)
graf_col1, graf_col2 = st.columns(2)

with graf_col1:
    st.subheader("Uso por Carrera")
    # Agrupamos los datos
    conteo_carrera = df_filtrado['carrera'].value_counts().reset_index()
    conteo_carrera.columns = ['carrera', 'cantidad']
    
    # Gráfico de barras interactivo
    fig_carrera = px.bar(
        conteo_carrera, 
        x='cantidad', 
        y='carrera', 
        orientation='h',
        color='cantidad',
        color_continuous_scale='Blues',
        title="Top Carreras en el Laboratorio"
    )
    fig_carrera.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_carrera, use_container_width=True)

with graf_col2:
    st.subheader("Distribución por Semestre")
    # Excluimos el semestre 0 (Profesores/Egresados) para no sesgar
    df_estudiantes = df_filtrado[df_filtrado['semestre'] > 0]
    conteo_semestre = df_estudiantes['semestre'].value_counts().reset_index()
    conteo_semestre.columns = ['semestre', 'cantidad']
    
    # Gráfico de Torta interactivo
    fig_semestre = px.pie(
        conteo_semestre, 
        values='cantidad', 
        names='semestre',
        hole=0.4, # Lo convierte en una dona (más moderno)
        title="Estudiantes por Semestre Activo"
    )
    st.plotly_chart(fig_semestre, use_container_width=True)

# Fila 2 de gráficos (Tabla de datos crudos opcional)
with st.expander("Ver Datos Crudos (Anonimizados)"):
    st.dataframe(df_filtrado.head(100)) # Mostramos solo las primeras 100 para no saturar