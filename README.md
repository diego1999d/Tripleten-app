# Tripleten-app

## Demo en vivo
https://tripleten-app.onrender.com

Aplicación web en **Streamlit** para explorar anuncios de coches de forma sencilla y visual.

### ¿Qué puedes hacer?
- **Filtrar** por precio, odómetro, año, tipo, condición y combustible.
- Ver **KPIs** rápidos (número de registros, precio mediano, odómetro medio).
- Navegar 3 **gráficas** en pestañas:
  - **Histograma** (precio/odómetro/edad, con opción de escala log).
  - **Dispersión** (ej. `odometer vs price` o `age vs price`, con color por categoría).
  - **Boxplot** (precio por tipo/condición/transmisión/combustible).
- Leer **Conclusiones** automáticas en texto (correlaciones y medianas por categoría).

### Ejecutar localmente
```bash
conda activate tripleten
cd "C:\Users\Control Escolar\Documents\Tripleten-app"
streamlit run app.py
