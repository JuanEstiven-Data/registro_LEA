from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="LEA Analytics",
    page_icon="LEA",
    layout="wide",
    initial_sidebar_state="expanded",
)


COLORWAY = ["#276EF1", "#00A6A6", "#4C956C", "#F28F3B", "#D1495B", "#7A5CFA"]
BACKGROUND = "#F6F8FB"
BACKGROUND_SOFT = "#EEF4F8"
SURFACE = "#FFFFFF"
TEXT = "#17324D"
MUTED = "#667085"
MONTH_ORDER = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def format_int(value: float | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def safe_ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0


def wrap_plotly_label(label: object, max_chars: int = 16) -> str:
    words = str(label).split()
    if not words:
        return ""

    lines: list[str] = []
    current = ""
    for word in words:
        next_line = f"{current} {word}".strip()
        if len(next_line) <= max_chars:
            current = next_line
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "<br>".join(lines)


def apply_wrapped_ticks(
    fig: go.Figure,
    *,
    x_values: list[object] | pd.Index | None = None,
    y_values: list[object] | pd.Index | None = None,
    max_chars: int = 16,
) -> go.Figure:
    if x_values is not None:
        values = list(x_values)
        fig.update_xaxes(
            tickmode="array",
            tickvals=values,
            ticktext=[wrap_plotly_label(value, max_chars) for value in values],
            tickangle=0,
            automargin=True,
        )
    if y_values is not None:
        values = list(y_values)
        fig.update_yaxes(
            tickmode="array",
            tickvals=values,
            ticktext=[wrap_plotly_label(value, max_chars + 6) for value in values],
            automargin=True,
        )
    return fig


def clean_heatmap_axes(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
    )
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    return fig


def style_figure(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        colorway=COLORWAY,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=12, r=12, t=52, b=28),
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", color=TEXT),
        title_font=dict(color=TEXT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        legend_font=dict(color=TEXT),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor="#D7E0EA", font=dict(color=TEXT)),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
        tickcolor=TEXT,
        linecolor="#D7E0EA",
    )
    fig.update_yaxes(
        gridcolor="#E7EEF6",
        zeroline=False,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
        tickcolor=TEXT,
        linecolor="#D7E0EA",
    )
    fig.update_coloraxes(
        colorbar_tickfont=dict(color=TEXT),
        colorbar_title_font=dict(color=TEXT),
    )
    return fig


def metric_card(label: str, value: str, helper: str = "", accent: str = "#276EF1") -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="border-top-color:{accent}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-helper">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_mode(series: pd.Series, fallback: str = "Sin datos") -> str:
    valid = series.dropna()
    return fallback if valid.empty else str(valid.mode().iloc[0])


@st.cache_data
def load_data() -> pd.DataFrame:
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_candidates = [
        base_dir / "data" / "public" / "registro_consolidado.csv",
        base_dir / "data" / "processed" / "registro_consolidado.csv",
    ]
    data_path = next((path for path in data_candidates if path.exists()), None)

    if data_path is None:
        st.error(
            "No se encontro el archivo de datos. Ejecuta el pipeline para generar "
            "data/public/registro_consolidado.csv."
        )
        st.stop()

    data = pd.read_csv(data_path)
    data["fecha"] = pd.to_datetime(data["fecha"])
    data["mes"] = pd.Categorical(data["mes"], categories=MONTH_ORDER, ordered=True)
    data["ciclo_lectivo"] = data["ciclo_lectivo"].astype(str)
    return data


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown('<div class="sidebar-title">LEA Analytics</div>', unsafe_allow_html=True)
    st.sidebar.caption("Filtros globales")

    ciclos = sorted(data["ciclo_lectivo"].dropna().unique())
    ciclos_sel = st.sidebar.multiselect("Ciclo lectivo", ciclos, default=ciclos)

    carreras = sorted(data["carrera"].dropna().unique())
    carreras_sel = st.sidebar.multiselect("Carrera", carreras, default=carreras)

    actividades = sorted(data["actividades"].dropna().unique())
    actividades_sel = st.sidebar.multiselect("Actividad", actividades, default=actividades)

    meses = [mes for mes in MONTH_ORDER if mes in set(data["mes"].dropna().astype(str))]
    meses_sel = st.sidebar.multiselect("Mes", meses, default=meses)

    filtered = data[
        data["ciclo_lectivo"].isin(ciclos_sel)
        & data["carrera"].isin(carreras_sel)
        & data["actividades"].isin(actividades_sel)
        & data["mes"].astype(str).isin(meses_sel)
    ].copy()

    st.sidebar.divider()
    st.sidebar.metric("Registros filtrados", format_int(len(filtered)))
    st.sidebar.metric("Usuarios filtrados", format_int(filtered["estudiante_id"].nunique()))
    return filtered


def build_cross_table(
    data: pd.DataFrame,
    row_dim: str,
    col_dim: str,
    metric: str,
    top_rows: int,
    top_cols: int,
) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    row_values = data[row_dim].value_counts().head(top_rows).index
    col_values = data[col_dim].value_counts().head(top_cols).index
    scoped = data[data[row_dim].isin(row_values) & data[col_dim].isin(col_values)]

    if metric == "Usuarios únicos":
        table = pd.pivot_table(
            scoped,
            index=row_dim,
            columns=col_dim,
            values="estudiante_id",
            aggfunc=pd.Series.nunique,
            fill_value=0,
        )
    elif metric == "Visitas por usuario":
        visits = pd.crosstab(scoped[row_dim], scoped[col_dim])
        users = pd.pivot_table(
            scoped,
            index=row_dim,
            columns=col_dim,
            values="estudiante_id",
            aggfunc=pd.Series.nunique,
            fill_value=0,
        )
        table = (visits / users.replace(0, pd.NA)).fillna(0).round(2)
    else:
        table = pd.crosstab(scoped[row_dim], scoped[col_dim])

    row_order = table.sum(axis=1).sort_values(ascending=False).index
    col_order = table.sum(axis=0).sort_values(ascending=False).index
    return table.loc[row_order, col_order]


def build_cross_detail(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(
            columns=["Carrera", "Actividad", "Visitas", "Usuarios únicos", "Visitas por usuario"]
        )

    detail = (
        data.groupby(["carrera", "actividades"])
        .agg(visitas=("estudiante_id", "size"), usuarios=("estudiante_id", "nunique"))
        .assign(visitas_por_usuario=lambda table: table["visitas"] / table["usuarios"])
        .reset_index()
        .rename(
            columns={
                "carrera": "Carrera",
                "actividades": "Actividad",
                "visitas": "Visitas",
                "usuarios": "Usuarios únicos",
                "visitas_por_usuario": "Visitas por usuario",
            }
        )
    )
    detail["Visitas por usuario"] = detail["Visitas por usuario"].round(2)
    return detail.sort_values(["Visitas", "Usuarios únicos"], ascending=False)


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #F6F8FB 0%, #EEF4F8 100%);
        color: #17324D;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F6F8FB 0%, #EEF4F8 100%);
    }
    [data-testid="stHeader"] {
        background: rgba(246, 248, 251, .88);
        backdrop-filter: blur(8px);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #FFFFFF;
        border-right: 1px solid #D7E0EA;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    .stRadio label,
    .stSlider label,
    .stMultiSelect label {
        color: #17324D !important;
    }
    [data-baseweb="select"],
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #B8C7D9 !important;
        color: #17324D !important;
    }
    [data-baseweb="select"] *,
    [data-baseweb="tag"] *,
    [data-baseweb="popover"] *,
    [data-baseweb="menu"] * {
        color: #17324D !important;
    }
    [data-baseweb="tag"] {
        background-color: #EAF2FF !important;
        border: 1px solid #C9DDFF !important;
    }
    [data-baseweb="menu"],
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    input,
    textarea,
    div[contenteditable="true"] {
        color: #17324D !important;
        caret-color: #17324D !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1440px;
    }
    .main-header {
        border-bottom: 1px solid #D7E0EA;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid #D7E0EA;
    }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF;
        border: 1px solid #D7E0EA;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        color: #344054;
        padding: .65rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #17324D;
        font-weight: 800;
        box-shadow: inset 0 3px 0 #276EF1;
    }
    .main-title {
        color: #17324D;
        font-size: 2.1rem;
        line-height: 1.15;
        font-weight: 800;
        margin: 0;
    }
    .main-subtitle {
        color: #667085;
        font-size: 1rem;
        margin-top: .35rem;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #D7E0EA;
        border-top: 4px solid #276EF1;
        border-radius: 10px;
        padding: 1rem 1.05rem;
        min-height: 112px;
        box-shadow: 0 6px 18px rgba(16, 42, 67, .06);
    }
    .metric-label {
        color: #667085;
        font-size: .8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .02em;
    }
    .metric-value {
        color: #17324D;
        font-size: 1.75rem;
        line-height: 1.2;
        font-weight: 800;
        margin-top: .3rem;
        overflow-wrap: anywhere;
    }
    .metric-helper {
        color: #667085;
        font-size: .82rem;
        margin-top: .2rem;
    }
    .section-title {
        color: #17324D;
        font-size: 1.05rem;
        font-weight: 800;
        margin: .2rem 0 .55rem 0;
    }
    .insight-box {
        background: #F3F8FF;
        border: 1px solid #D8E8FF;
        border-radius: 10px;
        padding: .85rem 1rem;
        color: #344054;
        font-size: .94rem;
    }
    .sidebar-title {
        color: #17324D;
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: .2rem;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E6EDF5;
        border-radius: 8px;
        padding: .7rem .8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


df_raw = load_data()
df = apply_filters(df_raw)

st.markdown(
    """
    <div class="main-header">
        <p class="main-title">Monitorías LEA - Panel Estratégico</p>
        <p class="main-subtitle">Demanda, públicos y evolución por ciclo lectivo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada.")
    st.stop()

page_exec, page_matrix, page_cycles = st.tabs(
    ["Resumen Ejecutivo", "Matriz de Demanda", "Ciclos y Evolución"]
)

with page_exec:
    usuarios_unicos = df["estudiante_id"].nunique()
    visitas_por_usuario = safe_ratio(len(df), usuarios_unicos)
    actividad_principal = top_mode(df["actividades"])
    carrera_principal = top_mode(df["carrera"])

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        metric_card("Visitas totales", format_int(len(df)), "Registros de asistencia", "#276EF1")
    with kpi_cols[1]:
        metric_card("Usuarios únicos", format_int(usuarios_unicos), "Estudiantes anonimizados", "#00A6A6")
    with kpi_cols[2]:
        metric_card("Visitas por usuario", f"{visitas_por_usuario:.1f}", "Recurrencia promedio", "#4C956C")
    with kpi_cols[3]:
        metric_card("Actividad principal", actividad_principal, carrera_principal, "#F28F3B")

    st.divider()
    trend_col, activity_col = st.columns([1.15, 1])

    with trend_col:
        st.markdown('<div class="section-title">Tendencia mensual</div>', unsafe_allow_html=True)
        monthly = (
            df.groupby("fecha")
            .agg(visitas=("estudiante_id", "size"), usuarios=("estudiante_id", "nunique"))
            .reset_index()
            .sort_values("fecha")
        )
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["fecha"],
                y=monthly["visitas"],
                mode="lines+markers",
                name="Visitas",
                line=dict(color="#276EF1", width=3),
                fill="tozeroy",
                fillcolor="rgba(39, 110, 241, .16)",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["fecha"],
                y=monthly["usuarios"],
                mode="lines+markers",
                name="Usuarios únicos",
                line=dict(color="#00A6A6", width=3),
            )
        )
        fig_trend.update_layout(xaxis_title="", yaxis_title="Registros")
        st.plotly_chart(style_figure(fig_trend, 430), width="stretch")

    with activity_col:
        st.markdown('<div class="section-title">Top actividades</div>', unsafe_allow_html=True)
        top_activities = df["actividades"].value_counts().head(8).reset_index()
        top_activities.columns = ["Actividad", "Visitas"]
        fig_activities = px.bar(
            top_activities.sort_values("Visitas"),
            x="Visitas",
            y="Actividad",
            orientation="h",
            color="Visitas",
            color_continuous_scale=["#D9F7F6", "#00A6A6"],
            text="Visitas",
        )
        fig_activities.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(style_figure(fig_activities, 430), width="stretch")

    st.markdown('<div class="section-title">Cruces que explican el volumen</div>', unsafe_allow_html=True)
    top_cross = (
        df.groupby(["carrera", "actividades"])
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="visitas")
    )
    top_cross["cruce"] = top_cross["carrera"] + " / " + top_cross["actividades"]
    fig_cross = px.bar(
        top_cross.sort_values("visitas"),
        x="visitas",
        y="cruce",
        orientation="h",
        color="visitas",
        color_continuous_scale=["#FFF1DC", "#F28F3B"],
        text="visitas",
    )
    fig_cross.update_layout(coloraxis_showscale=False, xaxis_title="Visitas", yaxis_title="")
    st.plotly_chart(style_figure(fig_cross, 430), width="stretch")

    top_cycle = df["ciclo_lectivo"].value_counts().idxmax()
    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Lectura rápida:</strong> el ciclo con mayor volumen filtrado es
            <strong>{top_cycle}</strong>. El resumen combina visitas y usuarios para evitar
            confundir alcance con recurrencia.
        </div>
        """,
        unsafe_allow_html=True,
    )

with page_matrix:
    control_cols = st.columns([1, 1, 1])
    with control_cols[0]:
        metric = st.radio(
            "Métrica",
            ["Visitas", "Usuarios únicos", "Visitas por usuario"],
            horizontal=True,
        )
    with control_cols[1]:
        top_rows = st.slider("Carreras visibles", 5, 15, 9)
    with control_cols[2]:
        top_cols = st.slider("Actividades visibles", 5, 12, 8)

    matrix = build_cross_table(df, "carrera", "actividades", metric, top_rows, top_cols)

    if matrix.empty:
        st.info("No hay datos suficientes para construir la matriz.")
    else:
        fig_matrix = px.imshow(
            matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=["#F2F8FF", "#276EF1"],
            labels=dict(x="Actividad", y="Carrera", color=metric),
        )
        apply_wrapped_ticks(fig_matrix, x_values=matrix.columns, y_values=matrix.index, max_chars=15)
        clean_heatmap_axes(fig_matrix)
        fig_matrix.update_xaxes(side="top")
        st.plotly_chart(style_figure(fig_matrix, 560), width="stretch")

    detail = build_cross_detail(df)
    st.markdown('<div class="section-title">Detalle operativo de cruces</div>', unsafe_allow_html=True)
    min_visits = st.slider("Mínimo de visitas para la tabla", 1, 100, 10)
    detail_filtered = detail[detail["Visitas"] >= min_visits].copy()

    table_cols = ["Carrera", "Actividad", "Visitas", "Usuarios únicos", "Visitas por usuario"]
    st.dataframe(
        detail_filtered[table_cols].head(25),
        hide_index=True,
        width="stretch",
        column_config={
            "Visitas": st.column_config.NumberColumn(format="%d"),
            "Usuarios únicos": st.column_config.NumberColumn(format="%d"),
            "Visitas por usuario": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    if not detail_filtered.empty:
        recurrence = detail_filtered.sort_values(
            ["Visitas por usuario", "Visitas"], ascending=False
        ).head(5)
        st.markdown(
            f"""
            <div class="insight-box">
                <strong>Recurrencia integrada:</strong> el mayor cruce por visitas por usuario es
                <strong>{recurrence.iloc[0]["Carrera"]} / {recurrence.iloc[0]["Actividad"]}</strong>
                con <strong>{recurrence.iloc[0]["Visitas por usuario"]:.2f}</strong> visitas por usuario.
            </div>
            """,
            unsafe_allow_html=True,
        )

with page_cycles:
    cycle_summary = (
        df.groupby("ciclo_lectivo")
        .agg(
            visitas=("estudiante_id", "size"),
            usuarios=("estudiante_id", "nunique"),
            meses=("fecha", "nunique"),
            actividades=("actividades", "nunique"),
        )
        .assign(
            visitas_mes=lambda table: table["visitas"] / table["meses"],
            usuarios_mes=lambda table: table["usuarios"] / table["meses"],
            visitas_usuario=lambda table: table["visitas"] / table["usuarios"],
        )
        .round({"visitas_mes": 1, "usuarios_mes": 1, "visitas_usuario": 2})
        .reset_index()
        .sort_values("ciclo_lectivo")
    )
    cycle_order = cycle_summary["ciclo_lectivo"].tolist()

    cycle_cols = st.columns([1.1, 1])
    with cycle_cols[0]:
        st.markdown('<div class="section-title">Visitas y usuarios por ciclo</div>', unsafe_allow_html=True)
        fig_cycles = go.Figure()
        fig_cycles.add_trace(
            go.Bar(
                x=cycle_summary["ciclo_lectivo"],
                y=cycle_summary["visitas"],
                name="Visitas",
                marker_color="#276EF1",
                text=cycle_summary["visitas"],
                textposition="outside",
            )
        )
        fig_cycles.add_trace(
            go.Bar(
                x=cycle_summary["ciclo_lectivo"],
                y=cycle_summary["usuarios"],
                name="Usuarios únicos",
                marker_color="#00A6A6",
                text=cycle_summary["usuarios"],
                textposition="outside",
            )
        )
        fig_cycles.update_layout(barmode="group", xaxis_title="", yaxis_title="Registros")
        fig_cycles.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=cycle_order,
            tickmode="array",
            tickvals=cycle_order,
            ticktext=cycle_order,
        )
        st.plotly_chart(style_figure(fig_cycles, 430), width="stretch")

    with cycle_cols[1]:
        st.markdown('<div class="section-title">Resumen por ciclo lectivo</div>', unsafe_allow_html=True)
        st.dataframe(
            cycle_summary.rename(
                columns={
                    "ciclo_lectivo": "Ciclo",
                    "visitas": "Visitas",
                    "usuarios": "Usuarios",
                    "meses": "Meses",
                    "actividades": "Actividades",
                    "visitas_mes": "Visitas/mes",
                    "usuarios_mes": "Usuarios/mes",
                    "visitas_usuario": "Visitas/usuario",
                }
            ),
            hide_index=True,
            width="stretch",
        )

    st.markdown('<div class="section-title">Mezcla de actividades por ciclo</div>', unsafe_allow_html=True)
    top_cycle_activities = df["actividades"].value_counts().head(10).index
    activity_cycle = pd.crosstab(
        df[df["actividades"].isin(top_cycle_activities)]["actividades"],
        df[df["actividades"].isin(top_cycle_activities)]["ciclo_lectivo"],
    )
    activity_cycle = activity_cycle.loc[
        activity_cycle.sum(axis=1).sort_values(ascending=False).index,
        sorted(activity_cycle.columns),
    ]
    fig_activity_cycle = px.imshow(
        activity_cycle,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=["#FFF7ED", "#D1495B"],
        labels=dict(x="Ciclo lectivo", y="Actividad", color="Visitas"),
    )
    apply_wrapped_ticks(fig_activity_cycle, y_values=activity_cycle.index, max_chars=22)
    clean_heatmap_axes(fig_activity_cycle)
    fig_activity_cycle.update_xaxes(
        side="top",
        type="category",
        categoryorder="array",
        categoryarray=cycle_order,
        tickmode="array",
        tickvals=cycle_order,
        ticktext=cycle_order,
    )
    st.plotly_chart(style_figure(fig_activity_cycle, 520), width="stretch")

    st.markdown('<div class="section-title">Carrera por ciclo</div>', unsafe_allow_html=True)
    top_cycle_careers = df["carrera"].value_counts().head(10).index
    career_cycle = pd.crosstab(
        df[df["carrera"].isin(top_cycle_careers)]["carrera"],
        df[df["carrera"].isin(top_cycle_careers)]["ciclo_lectivo"],
    )
    career_cycle = career_cycle.loc[
        career_cycle.sum(axis=1).sort_values(ascending=False).index,
        sorted(career_cycle.columns),
    ]
    fig_career_cycle = px.imshow(
        career_cycle,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=["#F2FCF5", "#4C956C"],
        labels=dict(x="Ciclo lectivo", y="Carrera", color="Visitas"),
    )
    apply_wrapped_ticks(fig_career_cycle, y_values=career_cycle.index, max_chars=22)
    clean_heatmap_axes(fig_career_cycle)
    fig_career_cycle.update_xaxes(
        side="top",
        type="category",
        categoryorder="array",
        categoryarray=cycle_order,
        tickmode="array",
        tickvals=cycle_order,
        ticktext=cycle_order,
    )
    st.plotly_chart(style_figure(fig_career_cycle, 480), width="stretch")

    if not cycle_summary.empty:
        best_users = cycle_summary.sort_values("usuarios_mes", ascending=False).iloc[0]
        best_visits = cycle_summary.sort_values("visitas_mes", ascending=False).iloc[0]
        st.markdown(
            f"""
            <div class="insight-box">
                <strong>Lectura de ciclo:</strong> el mayor alcance mensual ocurre en
                <strong>{best_users["ciclo_lectivo"]}</strong>
                ({best_users["usuarios_mes"]:.1f} usuarios/mes), mientras que el mayor volumen mensual
                ocurre en <strong>{best_visits["ciclo_lectivo"]}</strong>
                ({best_visits["visitas_mes"]:.1f} visitas/mes).
            </div>
            """,
            unsafe_allow_html=True,
        )
