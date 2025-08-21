import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.header("Análisis de anuncios de coches — Tripleten")

car_data = pd.read_csv("vehicles_us.csv")

hist_button = st.button("Construir histograma")
if hist_button:
    st.write("Creación de un histograma para la columna **odometer**")
    fig = go.Figure(data=[go.Histogram(x=car_data["odometer"])])
    fig.update_layout(title_text="Distribución del Odómetro")
    st.plotly_chart(fig, use_container_width=True)

scatter_button = st.button("Construir diagrama de dispersión")
if scatter_button:
    st.write("Relación entre **odometer** y **price**")
    fig2 = go.Figure(
        data=[go.Scatter(x=car_data["odometer"], y=car_data["price"], mode="markers")]
    )
    fig2.update_layout(
        title_text="Relación entre Odómetro y Precio",
        xaxis_title="odometer",
        yaxis_title="price",
    )
    st.plotly_chart(fig2, use_container_width=True)

