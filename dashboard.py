import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt

st.set_page_config(page_title="Dashboard de Delitos en Argentina", layout="wide")

@st.cache_data
def cargar_datos():
    return pd.read_csv("snic-provincias.csv")

datos = cargar_datos()

st.markdown(
    """
    <style>
    .titulo-principal {
        color: #4B0082;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .subtitulo {
        color: #FF4500;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
    }
    .separador {
        border-top: 3px solid #4B0082;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='titulo-principal'>🔍 Dashboard Interactivo: Análisis de Delitos en Argentina</div>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navegación",
    ["Introducción", "Distribución Geográfica", "Tipos de Delitos", "Distribución de Víctimas", "Relaciones entre Variables", "Provincias con tasas destacadas", "Conclusión General"]
)

st.sidebar.header("Filtros")
provincia = st.sidebar.multiselect("Selecciona una o más provincias", datos["provincia_nombre"].unique(), default=datos["provincia_nombre"].unique()[:3])
año = st.sidebar.slider("Selecciona un rango de años", int(datos["anio"].min()), int(datos["anio"].max()), (2000, 2023))
tipo_delito = st.sidebar.multiselect("Selecciona tipos de delito", datos["codigo_delito_snic_nombre"].unique(), default=datos["codigo_delito_snic_nombre"].unique()[:5])
tasa_min, tasa_max = st.sidebar.slider("Rango de tasa ajustada (hechos por 100,000 habitantes)", float(datos["tasa_hechos"].min()), float(datos["tasa_hechos"].max()), (0.0, float(datos["tasa_hechos"].max())))

datos_filtrados = datos[
    (datos["provincia_nombre"].isin(provincia)) &
    (datos["anio"] >= año[0]) & (datos["anio"] <= año[1]) &
    (datos["codigo_delito_snic_nombre"].isin(tipo_delito)) &
    (datos["tasa_hechos"] >= tasa_min) & (datos["tasa_hechos"] <= tasa_max)
]

tasas_provincias = datos_filtrados.groupby("provincia_nombre")["tasa_hechos"].mean().sort_values(ascending=False)

if menu == "Introducción":
    st.header("Introducción")
    
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_Argentina.svg", 
                 caption="Análisis de la Seguridad Pública en Argentina", 
                 width=600)  
    
    st.markdown("""
    **Bienvenido al Dashboard Interactivo sobre Delitos en Argentina**  
    Este dashboard ha sido diseñado para proporcionar una visión integral y detallada sobre la evolución de los delitos registrados en el país. A través de gráficos, tablas y filtros dinámicos, podrás explorar cómo varían los delitos según distintas regiones y períodos de tiempo.

    ### ¿Qué puedes encontrar aquí?
    - **Distribución geográfica:** Identifica qué provincias presentan las tasas más altas o más bajas de delitos ajustados por población. Esto te permitirá entender patrones regionales y las posibles causas subyacentes.
    - **Tendencias temporales:** Analiza cómo han cambiado las tasas de delitos a lo largo de los años. ¿Ha habido un incremento o disminución notable en ciertas provincias?
    - **Tipos de delitos:** Descubre cuáles son los delitos más comunes en el país y cómo estos varían según las provincias seleccionadas.
    - **Distribución de víctimas:** Explora cómo se distribuyen las víctimas de delitos por género y provincia. Esto puede ayudarte a identificar patrones importantes, como posibles desigualdades de género en ciertos delitos.
    - **Relaciones entre variables:** Examina la relación entre la cantidad de delitos y las tasas ajustadas por población, considerando factores demográficos y socioeconómicos.

    ### **Cómo utilizar este dashboard**
    - **Selecciona provincias específicas:** Puedes elegir una o más provincias utilizando el menú lateral.
    - **Filtra por años:** Ajusta el rango de años para enfocarte en períodos de interés.
    - **Tipos de delitos:** Elige los delitos que deseas analizar.
    - **Tasas ajustadas:** Define un rango de tasas de delitos para identificar patrones específicos.

    Este dashboard está pensado no solo para expertos en seguridad pública, sino también para investigadores, responsables de políticas públicas y cualquier persona interesada en entender cómo varía la seguridad en Argentina.

    ¡Explora los datos y obtén insights clave para tomar decisiones informadas! 🚀
    """)


elif menu == "Distribución Geográfica":
    st.markdown("<div class='subtitulo'>Distribución Geográfica</div>", unsafe_allow_html=True)
    
    tasas_df = tasas_provincias.reset_index().rename(columns={"provincia_nombre": "Provincia", "tasa_hechos": "Tasa Promedio"})
    
    chart = alt.Chart(tasas_df).mark_bar().encode(
        y=alt.Y("Provincia:N", sort="-x", title="Provincias"),
        x=alt.X("Tasa Promedio:Q", title="Tasa Promedio de Delitos"),
        color=alt.Color("Tasa Promedio:Q", scale=alt.Scale(scheme="blues")), 
        tooltip=["Provincia", "Tasa Promedio"]  
    ).properties(
        width=600,
        height=400,
        title="Distribución Geográfica de las Tasas de Delitos en Argentina"
    )

    st.altair_chart(chart, use_container_width=True)




elif menu == "Tipos de Delitos":
    st.markdown("<div class='subtitulo'>Tipos de Delitos</div>", unsafe_allow_html=True)
    
    delitos_comunes = datos_filtrados["codigo_delito_snic_nombre"].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(3, 2))  
    colores = sns.color_palette("Set3", len(delitos_comunes))  
    
    barras = ax.barh(delitos_comunes.index[::-1], delitos_comunes.values[::-1], color=colores)
    
    for i, barra in enumerate(barras):
        ax.text(barra.get_width() + 5, barra.get_y() + barra.get_height() / 2, 
                f'{delitos_comunes.values[::-1][i]}', va='center', fontsize=7, color='black')

    ax.set_title("Delitos más comunes", fontsize=9, pad=5)
    ax.set_xlabel("Frecuencia", fontsize=7)
    ax.set_ylabel("Tipo de Delito", fontsize=7)
    ax.tick_params(axis='both', which='major', labelsize=6)
    
    plt.tight_layout()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.pyplot(fig) 






elif menu == "Distribución de Víctimas":
    st.markdown("<div class='subtitulo'>Distribución de Víctimas</div>", unsafe_allow_html=True)
    
    victimas_por_genero = datos_filtrados[["cantidad_victimas_masc", "cantidad_victimas_fem", "cantidad_victimas_sd"]].sum()
    victimas_df = pd.DataFrame({
        "Género": ["Masculino", "Femenino", "Sin Determinar"],
        "Cantidad de Víctimas": victimas_por_genero.values
    })

    chart = alt.Chart(victimas_df).mark_bar().encode(
        x=alt.X("Género", sort=["Masculino", "Femenino", "Sin Determinar"]),
        y="Cantidad de Víctimas",
        color=alt.Color("Género", scale=alt.Scale(
            domain=["Masculino", "Femenino", "Sin Determinar"],
            range=["#1f77b4", "#e377c2", "#7f7f7f"]  
        )),
        tooltip=["Género", "Cantidad de Víctimas"]
    ).properties(
        width=400,  
        height=300
    )

    st.altair_chart(chart, use_container_width=True)



elif menu == "Relaciones entre Variables":
    st.markdown("<div class='subtitulo'>Relación entre cantidad de delitos y tasas ajustadas</div>", unsafe_allow_html=True)
    
    relacion_delitos = datos_filtrados.groupby("provincia_nombre")[["cantidad_hechos", "tasa_hechos"]].sum().reset_index()

    scatter_chart = alt.Chart(relacion_delitos).mark_circle(size=80).encode(
        x=alt.X("cantidad_hechos", title="Cantidad total de delitos", scale=alt.Scale(zero=False)),
        y=alt.Y("tasa_hechos", title="Tasa ajustada (por 100,000 habitantes)", scale=alt.Scale(zero=False)),
        color=alt.Color("provincia_nombre", legend=None, scale=alt.Scale(scheme='viridis')),  
        tooltip=["provincia_nombre", "cantidad_hechos", "tasa_hechos"]  
    ).properties(
        width=500,
        height=400,
        title="Relación entre cantidad de delitos y tasas ajustadas por provincia"
    ).interactive()  

    st.altair_chart(scatter_chart, use_container_width=True)




elif menu == "Provincias con tasas destacadas":
    st.markdown("<div class='subtitulo'>Provincias con tasas más altas y más bajas</div>", unsafe_allow_html=True)
    
    top_tasas = tasas_provincias.head(3).reset_index().rename(columns={"tasa_hechos": "Tasa Promedio"})
    bottom_tasas = tasas_provincias.tail(3).reset_index().rename(columns={"tasa_hechos": "Tasa Promedio"})
    
    tasas_destacadas = pd.concat([top_tasas, bottom_tasas])
    tasas_destacadas["Categoría"] = ["Alta"] * len(top_tasas) + ["Baja"] * len(bottom_tasas)

    chart = alt.Chart(tasas_destacadas).mark_bar().encode(
        x=alt.X("Tasa Promedio:Q", title="Tasa Promedio de Delitos"),
        y=alt.Y("provincia_nombre:N", title="Provincias", sort="-x"),
        color=alt.Color("Categoría:N", scale=alt.Scale(domain=["Alta", "Baja"], range=["#e63946", "#457b9d"])),  
        tooltip=["provincia_nombre", "Tasa Promedio"]  
    ).properties(
        width=600,
        height=300,
        title="Provincias con Tasas de Delitos Más Altas y Más Bajas"
    )

    st.altair_chart(chart, use_container_width=True)


elif menu == "Conclusión General":
    st.markdown("""### 📊 **Conclusión General**""", unsafe_allow_html=True)
    
    st.markdown("""
      
    Este análisis de los delitos en Argentina ha permitido identificar patrones clave relacionados con la distribución geográfica, los tipos de delitos y la distribución de las víctimas. A continuación, destacamos los principales hallazgos:
    
    - **Desigualdad regional:** Provincias como Mendoza, Ciudad Autónoma de Buenos Aires y Salta presentan tasas delictivas más altas en comparación con otras regiones como Buenos Aires o Corrientes. Este patrón podría estar relacionado con factores urbanos, económicos y sociales específicos.
    
    - **Tendencias en los tipos de delitos:** Los delitos más frecuentes en el país están relacionados con la libertad individual y la propiedad, como robos, hurtos y violencia de género. Esto refleja preocupaciones constantes sobre la protección de los bienes y la seguridad de las personas.
    
    - **Diferencias en la distribución de víctimas:** La mayoría de las víctimas registradas son de género masculino, pero se observan tasas significativas de mujeres en delitos específicos como violencia de género. Este patrón resalta la necesidad de políticas específicas para proteger a las poblaciones más vulnerables.

    - **Relaciones entre variables:** Provincias con alta población, como Buenos Aires, muestran una cantidad elevada de delitos, pero tasas ajustadas más bajas debido a su densidad poblacional. Por el contrario, provincias más pequeñas presentan altas tasas ajustadas, lo que sugiere la importancia de considerar la población en el análisis.

    ### 🔍 **Recomendaciones**
    - Implementar estrategias de prevención específicas en provincias con alta incidencia delictiva, enfocadas en factores locales.
    - Analizar en mayor profundidad las causas de los delitos contra la libertad y la propiedad, para diseñar políticas públicas más eficaces.
    - Fortalecer los sistemas de registro de datos para reducir la cantidad de víctimas clasificadas como "sin determinar", lo que permitiría un análisis más preciso y mejores intervenciones.

    Este dashboard muestra que, aunque ciertas provincias enfrentan desafíos significativos en términos de seguridad, también existen casos de éxito que podrían replicarse en otras regiones. Las políticas públicas basadas en datos pueden ser clave para reducir los niveles delictivos y mejorar la seguridad en todo el país.
    """)

    st.markdown("**Nota:** Este análisis se basa en los datos proporcionados por el sistema SNIC. Asegúrate de cargar un archivo actualizado para mantener la precisión.")

