import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Anuncios de coches", layout="wide")
st.title("Análisis de anuncios de coches")

# -------------------------------
# Carga de datos (cacheada)
# -------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    # columnas útiles si existen
    keep = [c for c in ["price", "odometer", "model_year", "condition", "type",
                        "transmission", "fuel", "paint_color"] if c in df.columns]
    df = df[keep].copy()
    # quitar nulos básicos
    for col in ["price", "odometer"]:
        if col in df.columns:
            df = df[df[col].notna()]
    # age (si hay model_year)
    if "model_year" in df.columns:
        df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce")
        df = df[df["model_year"].notna()]
        current_year = datetime.now().year
        df["age"] = current_year - df["model_year"].astype(int)
    return df

csv_path = Path("vehicles_us.csv")
if not csv_path.exists():
    st.error(f"No encuentro el archivo: {csv_path.resolve()}")
    st.stop()

df = load_data(csv_path)

st.markdown(
    "Usa los **filtros de la izquierda** y mira las **gráficas y conclusiones**. "
    "La idea es responder preguntas simples como:"
    " *¿a mayor kilometraje, el auto es más barato?*, "
    "*¿los autos más nuevos cuestan más?*, "
    "*¿qué tipo/condición suele ser más caro?*"
)

# -------------------------------
# Sidebar: filtros sencillos
# -------------------------------
st.sidebar.header("Filtros")

# Recorte de outliers por percentiles (para que los gráficos sean legibles)
if "price" in df.columns:
    p1, p99 = df["price"].quantile([0.01, 0.99]).astype(int)
    price_range = st.sidebar.slider("Precio (USD)", int(p1), int(p99), (int(p1), int(p99)))
else:
    price_range = None

if "odometer" in df.columns:
    o1, o99 = df["odometer"].quantile([0.01, 0.99]).astype(int)
    odo_range = st.sidebar.slider("Odómetro (mi)", int(o1), int(o99), (int(o1), int(o99)))
else:
    odo_range = None

if "model_year" in df.columns:
    y_min, y_max = int(df["model_year"].min()), int(df["model_year"].max())
    year_range = st.sidebar.slider("Año del vehículo", y_min, y_max, (y_min, y_max))
else:
    year_range = None

def multi(cat):
    return st.sidebar.multiselect(cat.capitalize(), sorted(df[cat].dropna().unique())) if cat in df.columns else []

cond_vals  = multi("condition")
type_vals  = multi("type")
fuel_vals  = multi("fuel")

# Aplicar filtros
f = df.copy()
if price_range and "price" in f.columns:
    f = f[(f["price"] >= price_range[0]) & (f["price"] <= price_range[1])]
if odo_range and "odometer" in f.columns:
    f = f[(f["odometer"] >= odo_range[0]) & (f["odometer"] <= odo_range[1])]
if year_range and "model_year" in f.columns:
    f = f[(f["model_year"] >= year_range[0]) & (f["model_year"] <= year_range[1])]
if cond_vals:
    f = f[f["condition"].isin(cond_vals)]
if type_vals:
    f = f[f["type"].isin(type_vals)]
if fuel_vals:
    f = f[f["fuel"].isin(fuel_vals)]

# -------------------------------
# KPIs arriba (para dar contexto rápido)
# -------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Publicaciones (después de filtros)", f"{len(f):,}")

if "price" in f.columns and len(f) > 0:
    c2.metric("Precio mediano", f"${int(f['price'].median()):,}")
if "odometer" in f.columns and len(f) > 0:
    c3.metric("Odómetro medio", f"{int(f['odometer'].mean()):,} mi")

st.markdown("---")

# -------------------------------
# Pestañas: Histogramas / Dispersión / Boxplot / Conclusiones
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Histograma", "Dispersión", "Boxplot", "Conclusiones"])

# Histograma configurable (price por defecto con opción log)
with tab1:
    st.subheader("Distribución")
    num_cols = [c for c in ["price", "odometer", "age"] if c in f.columns]
    if not num_cols or len(f) == 0:
        st.info("No hay datos disponibles con los filtros actuales.")
    else:
        default_idx = num_cols.index("price") if "price" in num_cols else 0
        col = st.selectbox("Columna", num_cols, index=default_idx, help="Variable a analizar")
        bins = st.slider("Bins", 10, 120, 40)
        log_scale = st.checkbox("Escala logarítmica (recomendado para precio)", value=(col=="price"))
        fig = px.histogram(f, x=col, nbins=bins)
        fig.update_layout(height=480, bargap=0.05, title=f"Distribución de {col}")
        fig.update_xaxes(type="log" if log_scale else "linear")
        st.plotly_chart(fig, use_container_width=True)

# Dispersión centrada en preguntas simples
with tab2:
    st.subheader("Relación entre variables")
    st.caption("Ejemplos útiles: **odometer vs price** (¿más millas ⇒ más barato?) • **age vs price** (¿más nuevo ⇒ más caro?)")
    # elegir pares típicos
    pairs = []
    if {"odometer", "price"}.issubset(f.columns):
        pairs.append(("odometer", "price"))
    if {"age", "price"}.issubset(f.columns):
        pairs.append(("age", "price"))
    if not pairs or len(f) == 0:
        st.info("No hay columnas numéricas suficientes.")
    else:
        label = {"odometer":"odometer vs price", "age":"age vs price"}
        options = [f"{x} vs {y}" for x,y in pairs]
        choice = st.selectbox("Par de variables", options, index=0)
        x, y = choice.split(" vs ")
        color_by = st.selectbox("Color por", [None]+[c for c in ["condition","type","fuel"] if c in f.columns], index=0)
        fig = px.scatter(f, x=x, y=y, color=color_by if color_by else None, opacity=0.6)
        fig.update_layout(height=500, title=f"{x} vs {y}")
        st.plotly_chart(fig, use_container_width=True)

# Boxplot para comparar categorías por precio
with tab3:
    st.subheader("Comparar precios por categoría")
    if "price" in f.columns and len(f) > 0:
        cats = [c for c in ["type", "condition", "transmission", "fuel"] if c in f.columns]
        if cats:
            cat = st.selectbox("Categoría", cats, index=0)
            fig = px.box(f, x=cat, y="price", points="suspectedoutliers")
            fig.update_layout(height=500, title=f"Distribución de precio por {cat}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay columnas categóricas disponibles.")
    else:
        st.info("No hay datos de precio disponibles.")

# Conclusiones automáticas (texto llano)
with tab4:
    st.subheader("¿Qué se observa?")
    if len(f) == 0:
        st.info("Ajusta los filtros para ver conclusiones con datos.")
    else:
        bullets = []

        # Correlación odometer-price (si existen)
        if {"odometer", "price"}.issubset(f.columns):
            corr_op = f[["odometer","price"]].corr(method="spearman").iloc[0,1]
            if corr_op < -0.05:
                msg = f"A **mayor odómetro, menor precio** (correlación Spearman = {corr_op:.2f})."
            elif corr_op > 0.05:
                msg = f"A **mayor odómetro, mayor precio** (inusual) — revisar filtros (corr = {corr_op:.2f})."
            else:
                msg = f"No hay relación clara entre **odómetro** y **precio** (corr ≈ {corr_op:.2f})."
            bullets.append(msg)

        # Correlación age-price (si existen)
        if {"age", "price"}.issubset(f.columns):
            corr_ap = f[["age","price"]].corr(method="spearman").iloc[0,1]
            if corr_ap > 0.05:
                msg = f"**Autos más nuevos tienden a costar más** (menos edad ⇒ mayor precio) (corr = {corr_ap:.2f})."
            elif corr_ap < -0.05:
                msg = f"**Autos más viejos a veces se ofrecen más caros** (inusual) — revisar filtros (corr = {corr_ap:.2f})."
            else:
                msg = f"No hay relación fuerte entre **edad** y **precio** (corr ≈ {corr_ap:.2f})."
            bullets.append(msg)

        # Precios medianos por categoría (si hay)
        if "price" in f.columns:
            for cat in ["type", "condition"]:
                if cat in f.columns:
                    med = (f[[cat,"price"]]
                           .dropna()
                           .groupby(cat)["price"].median()
                           .sort_values(ascending=False)
                           .head(5).astype(int))
                    if len(med) > 0:
                        top = " • ".join([f"{k}: ${v:,}" for k,v in med.items()])
                        bullets.append(f"**Precios medianos por {cat} (top)** → {top}")

        # Mostrar en lista
        for b in bullets:
            st.markdown(f"- {b}")

st.caption("Fuente: vehicles_us.csv — Los cálculos usan los datos después de aplicar filtros.")

