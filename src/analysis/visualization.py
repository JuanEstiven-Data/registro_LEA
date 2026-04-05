import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="LEA Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARGA DE DATOS (CON CACHÉ) ---
@st.cache_data
def load_data():
    # Rutas dinámicas usando Pathlib
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / 'data' / 'processed' / 'registro_consolidado.csv'
    
    if not data_path.exists():
        st.error(f"No se encontró el archivo de datos en: {data_path}")
        st.stop()
        
    df = pd.read_csv(data_path)
    # Aseguramos que la fecha sea tipo Datetime para las gráficas
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

df_raw = load_data()

# --- 3. BARRA LATERAL: FILTROS ESTRATÉGICOS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Logo_Javeriana.svg/1200px-Logo_Javeriana.svg.png", width=150) # Cambia por el logo de tu U si quieres
st.sidebar.title("Filtros Globales")

# Filtro de Año (Slider Rango)
min_year = int(df_raw['año'].min())
max_year = int(df_raw['año'].max())
rango_anios = st.sidebar.slider("Rango de Años", min_year, max_year, (min_year, max_year))

# Filtro de Periodo Académico
periodos_disp = df_raw['periodo_academico'].unique()
periodos_sel = st.sidebar.multiselect("Periodo Académico", periodos_disp, default=periodos_disp)

# Filtro de Mes
meses_disp = df_raw['mes'].dropna().unique()
meses_sel = st.sidebar.multiselect("Meses Específicos", meses_disp, default=meses_disp)

# Filtro de Carrera
carreras_disp = df_raw['carrera'].dropna().unique()
carreras_sel = st.sidebar.multiselect("Carrera del Estudiante", carreras_disp, default=carreras_disp)

# APLICAR FILTROS
df = df_raw[
    (df_raw['año'] >= rango_anios[0]) & 
    (df_raw['año'] <= rango_anios[1]) &
    (df_raw['periodo_academico'].isin(periodos_sel)) &
    (df_raw['mes'].isin(meses_sel)) &
    (df_raw['carrera'].isin(carreras_sel))
]

# --- 4. KPIs (TARJETAS DE RESUMEN) ---
st.title("📊 Monitorías LEA - Panel Estratégico")
st.markdown("Análisis de demanda, uso de espacios y carga operativa del laboratorio.")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Visitas Totales", value=len(df))
with kpi2:
    estudiantes_unicos = df['estudiante_id'].nunique()
    st.metric(label="Estudiantes Únicos", value=estudiantes_unicos)
with kpi3:
    # Calculamos el promedio de visitas por estudiante (Fidelización)
    tasa_retencion = len(df) / estudiantes_unicos if estudiantes_unicos > 0 else 0
    st.metric(label="Visitas por Estudiante", value=f"{tasa_retencion:.1f}")
with kpi4:
    top_actividad = df['actividades'].mode()[0] if not df.empty else "N/A"
    st.metric(label="Actividad Principal", value=top_actividad)

st.divider()

# --- 5. VISUALIZACIONES (PLOTLY EXPRESS) ---

# FILA 1: El Pulso del Laboratorio (Serie de Tiempo Completa)
st.subheader("📈 El Pulso del Laboratorio (Tendencia de Asistencia)")
df_tiempo = df.groupby('fecha').size().reset_index(name='asistencias')
fig_tiempo = px.area(
    df_tiempo, x='fecha', y='asistencias', 
    color_discrete_sequence=['#1f77b4'],
    markers=True
)
fig_tiempo.update_layout(xaxis_title="Fecha de Registro", yaxis_title="Número de Estudiantes")
st.plotly_chart(fig_tiempo, use_container_width=True)


# FILA 2: Sunburst (Flujo) y Heatmap (Densidad)
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("🎯 Flujo de Usuarios (Carrera ➔ Actividad)")
    # Diagrama de ráfaga solar (Sunburst)
    fig_sunburst = px.sunburst(
        df, path=['carrera', 'actividades'], 
        color='carrera',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_sunburst.update_traces(textinfo="label+percent parent")
    st.plotly_chart(fig_sunburst, use_container_width=True)

with col_der:
    st.subheader("🔥 Mapa de Calor: Semestre vs Actividad")
    # Filtramos semestres atípicos (como 0 o mayores a 10 si aplican) para limpiar la gráfica
    df_heat = df[(df['semestre'] > 0) & (df['semestre'] <= 10)]
    fig_heat = px.density_heatmap(
        df_heat, x='semestre', y='actividades', 
        color_continuous_scale='Viridis',
        text_auto=True # Muestra el número exacto dentro del cuadro
    )
    fig_heat.update_layout(xaxis_title="Semestre Académico", yaxis_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# FILA 3: Análisis de Cursos Reales
st.subheader("📚 Demanda por Curso Específico")
# Filtramos el "ruido" de quienes solo van a usar el espacio libremente
df_cursos = df[df['curso'] != 'Sin Informacion']
if not df_cursos.empty:
    conteo_cursos = df_cursos['curso'].value_counts().reset_index()
    conteo_cursos.columns = ['curso', 'asistencias']
    
    # Tomamos el Top 15 para no saturar la pantalla
    fig_cursos = px.bar(
        conteo_cursos.head(15), 
        x='asistencias', y='curso', 
        orientation='h',
        color='asistencias',
        color_continuous_scale='Blues'
    )
    fig_cursos.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title="")
    st.plotly_chart(fig_cursos, use_container_width=True)
else:
    st.info("No hay datos de cursos específicos para los filtros seleccionados.")