import os
import json

import lenguaje

from matplotlib import pyplot as plt
from scipy import stats as stat
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from statsmodels.graphics.tsaplots import plot_acf

l = lenguaje.tu_idioma()

@st.cache_resource
def acceso_datos_ventas():
    RUTA_DATOS = 'ventas_limpias_providencia.json'
    try:
        if os.path.exists(RUTA_DATOS) and os.path.getsize(RUTA_DATOS) > 0:
            with open(RUTA_DATOS,'r',encoding='utf-8') as f:
                df = pd.DataFrame(data=json.load(f))
                return df
        else:
            st.warning('El Archivo Esta Vacio')
    except (KeyError, json.JSONDecodeError):
        st.error('Error Al Acceder Al Archivo')

def ventas_mensuales(df):
    st.header(f':material/analytics: {l.phrase[109]}')
    # Creo una copia del DF original. Hago un pivot table que ocupe los meses como indices.
    pivot_1 = df.copy()
    pivot_1 = pd.pivot_table(data=pivot_1,values='Total',index='Month',columns='Year',aggfunc='sum',observed=True)
    meses= {'01':'Enero','02':'Febrero','03':'Marzo','04':'Abril','05':'Mayo','06':'Junio','07':'Julio','08':'Agosto','09':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre'}
    pivot_1 = pivot_1.rename(index = meses)

    # Calculamos venta total por anho:
    total_2023 = pivot_1['2023'].sum()
    total_2024 = pivot_1['2024'].sum()
    total_2025 = pivot_1['2025'].sum()

    # Calculamos la media de venta por mes:
    mean_2023_mes = np.mean(pivot_1['2023'])
    mean_2024_mes = np.mean(pivot_1['2024'])
    mean_2025_mes = np.mean(pivot_1['2025'])

    # Calculamos la mediana de venta por mes:
    mediana_2023_mes = np.median(pivot_1['2023'])
    mediana_2024_mes = np.median(pivot_1['2024'])
    mediana_2025_mes = np.median(pivot_1['2025'])

    # Creo un DataFrame con para los valores de media,mediana y total:
    total_tabla = pd.DataFrame(data={
        'TOTAL AÑO':[total_2023,total_2024,total_2025],
        'MEDIA-VENTA MES':[mean_2023_mes,mean_2024_mes,mean_2025_mes],
        'MEDIANA-VENTA MES':[mediana_2023_mes,mediana_2024_mes,mediana_2025_mes]
        },index=(2023,2024,2025))
    
    # 1. Preparación de los datos para Plotly
    # Plotly Express funciona mejor con datos en formato 'largo' (long format)
    # En lugar del formato 'ancho' (wide format) de pivot_1.
    df_plot = pivot_1.reset_index().melt(
        id_vars='Month',          # Columna de meses (eje X)
        var_name='Año',           # Nombre de la nueva columna para los años
        value_name='Ventas'       # Nombre de la nueva columna para los valores de venta (eje Y)
    )

    # 2. Creación del gráfico de barras con Plotly Express
    fig = px.bar(
        df_plot,
        x='Month',                  # Eje X: Meses
        y='Ventas',                 # Eje Y: Valores de venta
        color='Año',                # Colorea las barras según el año (agrupa las barras)
        barmode='group',            # Muestra las barras agrupadas (una al lado de la otra)
        title=l.phrase[115],
        labels={'Ventas': 'Venta en Millones $MXN', 'Month': 'Mes'}
    )

    # 3. Adición de las líneas de la media (similar a plt.axhline)
    # Media 2023 (rojo)
    fig.add_hline(
        y=mean_2023_mes,
        annotation_text="Media 2023",
        line_dash="dash",
        line_color="red"
    )
    
    # Media 2025 (azul, color por defecto o similar al de las barras 2025)
    fig.add_hline(
        y=mean_2025_mes,
        annotation_text="Media 2025",
        line_dash="dash",
        line_color="blue"
    )

    # 4. Personalización y Mejora de la Visualización
    fig.update_layout(
        xaxis_title='Mes',
        yaxis_title='Venta en Millones $MXN',
        legend_title='Año',
        hovermode="x unified" # Hace que al pasar el mouse se muestren los valores de todos los años para ese mes
    )
    
    # Formato del eje Y para evitar notación científica y mejorar lectura
    fig.update_yaxes(tickformat = ',.0f') # Sin decimales y con separador de miles

    # 5. Muestra el gráfico en Streamlit
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.write('Aparente Aumento en la media de venta por mes. :red[Línea roja] (media de venta del 2023). :blue[Línea azul] (media de venta del 2025)')

    st.divider()
    col1,col2 = st.columns(2)
    ver_estimados_de_locacion_generales = col2.toggle(
        label='MOSTRAR ESTIMADOS DE LOCACION',
        key='ver_estimados_de_locacion_generales',
        width='stretch'
        )
    ver_tabla_mensual = col1.toggle(
        label='MOSTRAR VENTA MENSUAL',
        key='ver_tabla_mensual',
        width='stretch'
    )
    if ver_tabla_mensual:
        st.dataframe(
            data=pivot_1,
            column_config={
                '2023':st.column_config.NumberColumn(format='dollar',step=0.01),
                '2024':st.column_config.NumberColumn(format='dollar',step=0.01),
                '2025':st.column_config.NumberColumn(format='dollar',step=0.01)
            }
            )
    if ver_estimados_de_locacion_generales:
        st.dataframe(
            data=total_tabla,
            column_config={
                'TOTAL AÑO':st.column_config.NumberColumn(format='dollar',step=0.01),
                'MEDIA-VENTA MES':st.column_config.NumberColumn(format='dollar',step=0.01),
                'MEDIANA-VENTA MES':st.column_config.NumberColumn(format='dollar',step=0.01)
            }
            )
    st.divider()
    
def histograma_frecuencia(df):
    st.header(f':material/circles_ext: {l.phrase[110]}')

    # Creo una copia del DF para poder graficar un boxplot
    df_box = df.copy()

    # Filtro el DF por anhos
    df_2023 = (df_box[df_box['Year']=='2023'])
    df_2024 = (df_box[df_box['Year']=='2024'])
    df_2025 = (df_box[df_box['Year']=='2025'])

    # Calculo los estimados de locacion por anho y los uno en un nuevo DF
    mean_2023 = np.mean(df_2023['Total'])
    mean_2024 = np.mean(df_2024['Total'])
    mean_2025 = np.mean(df_2025['Total'])

    median_1 = np.median(df_2023['Total'])
    median_2 = np.median(df_2024['Total'])
    median_3 = np.median(df_2025['Total'])

    df_estimates = pd.DataFrame(data={'Year':['2023','2024','2025'],'Media':[mean_2023,mean_2024,mean_2025],'Mediana':[median_1,median_2,median_3]})
    
    # Creo un DF para el histograma que comparara los anhos 2024 y 2025
    df_histo = df[df['Year'].isin(['2024', '2025'])].copy()
    
    # Creación del Histograma con Plotly Express
    fig = px.histogram(
        df_histo, # Data
        x='Total', # La linea que contiene los valores
        color='Year', # Dado que queremos graficar dos anhos, usamos la caracteristica "year" ya que esta contiene 2024 y 2025
        title='Distribución de Ventas para los Años 2024 y 2025',
        labels={'Total': 'Venta en $MXN'},
        nbins=4500,
        opacity=0.6,
        barmode='overlay' # Con este parametro los superpongo al momento de mostrar.
    )
    
    # Con el metodo .update_xaxes determino el rango de ventas que sera mostrado y el titulo para el eje "y":
    fig.update_xaxes(range=[0, 500])
    fig.update_yaxes(title='Frecuencia (Conteo de Evento)')

    # Muestro el histograma y la tabla de estimaciones:
    st.plotly_chart(fig, width='stretch')
    st.dataframe(
            df_estimates,
            hide_index=1,
            column_config={
                'Media':st.column_config.NumberColumn(format='dollar',step=0.01),
                'Mediana':st.column_config.NumberColumn(format='dollar',step=0.01)
            }
            )
    
    # Aqui creo el grafico de caja:
    fig = px.box(
        df_box,
        x='Year', # Eje x, separa las tres muestras
        y='Total', # Evalua la distribucion numerica en el eje "y"
        color='Year', # Asigna un color único a cada caja segun el anho.
        title='Distribución de Venta por Año',
        labels={'Total': 'Venta Total ($MXN)', 'Year': 'Año'},
        hover_data=['Month', 'Total'] # Muestra el Mes y Total al pasar el ratón
    )
    
    # Edito como se mostraran las cantidades grandes:
    fig.update_yaxes(
        tickformat = ',.0f', # Formato sin notación científica y separador de miles
    )
    
    fig.update_layout(
        showlegend=False # Aqui oculto la legenda de X dado que el grafico ya muestra bien todas las cajas por color.
    )

    # Creo dos columnas que tendran un toggle que permite las opciones de ver la estadisticas y el boxplot:
    col1,col2 = st.columns(2)
    prueba_aumento = col1.toggle( 
        label='RESULTADOS DE LA PRUEBA DE AUMENTO',
        key='prueba_aumento',
        width='stretch'
    )

    distribucion_box = col2.toggle( 
        label='MOSTRAR VALORES ATIPICOS ANUALES',
        key='distribucion_box',
        width='stretch'
    )

    if prueba_aumento:
        st.divider()
        st.subheader(':material/bar_chart: Resultado: Normalidad, Varianza y Aumento')

        alpha = 0.05

        # Resultado de la prueba Anderson-Darling (El calculo esta en "MyDrive/colab/Providencia"):
        st.info("**Prueba de Normalidad (Anderson-Darling):** Se **RECHAZA** la hipótesis nula ($H_0$) para ambos años (2024 y 2025). Esto indica que la distribución de ventas **NO es normal**.")

        # PRUEBA DE LEVENE (VARIANZA)
        stats_levene, p_value_levene = stat.levene(df_2024['Total'], df_2025['Total'])
        
        st.markdown("#### Prueba de Homogeneidad de Varianza (Levene)")
        st.markdown(f"**Valor $p$ (Levene):** `{p_value_levene:.4f}`")

        if p_value_levene > alpha:
            st.success('**Resultado:** Las varianzas son iguales (No se rechaza $H_0$)')
        else:
            st.info('**Resultado:** Las varianzas son **diferentes** (Se rechaza $H_0$)')


        # PRUEBA DE AUMENTO (MANN-WHITNEY U)
        resultados_mw = stat.mannwhitneyu(df_2025['Total'], df_2024['Total'], alternative='greater')
        
        st.markdown("#### Prueba de Aumento de Mediana (Mann-Whitney U)")
        st.markdown(f"**Hipótesis $H_0$:** Las distribuciones de ventas son iguales (`2025 - 2024`).")
        st.markdown(f"**Hipótesis $H_1$:** Las ventas de 2025 son mayores que las ventas de 2024.")
        st.markdown(f"**Valor $p$ (Mann-Whitney U):** `{resultados_mw.pvalue:.4f}`")

        if resultados_mw.pvalue < alpha:
            st.success('**Resultado:** Las ventas de 2025 son mayores que las ventas de 2024 (Se rechaza $H_0$)')
        else:
            st.info('**Resultado:** La distribuciones de las ventas del 2025 y 2024 son **iguales** (No se rechaza $H_0$)')
    
    if distribucion_box:
        st.divider()
        # Muestro el gráfico en Streamlit
        st.plotly_chart(fig, width='stretch')

        # Muestro información de outliers/resumen
        st.write('**Los valores atipicos altos son mas concurrentes para el :blue[2025], lo cual podria explicar el aumento de venta.**')
        st.write('**Los valores atipicos del :blue[2025] se realizaron dentro de los Meses :blue[(Enero - Mayo)], esto no sucede para el :red[2023] y :red[2024]**')
    st.divider()

def proporcion_marcas(df):
    st.header(f':material/hardware: {l.phrase[111]}')
    
    # Widget que determina el criterio de filtro
    umbral = st.number_input(
        label='Especifica El Umbral de Filtro de Proporcion',
        step=0.1,
        min_value=0.1,
        max_value=100.0,
        value=3.0
    )

    umbral /= 100

    # 1. Copia y Agrupación
    df_copia_2 = df.copy()

    # Sumas Totales (para calcular el "resto" correctamente)
    total_cantidad_absoluto = np.sum(df_copia_2['Cantidad'])
    criterio_de_total = np.sum(df_copia_2['Total'])
    
    # Agrupacion por Marcas
    df_marcas = df_copia_2.groupby(by='Categoría 1',observed=False)[['Cantidad','Total']].sum()
    df_marcas.sort_values(by='Total',ascending=False,inplace=True)
    df_marcas.reset_index(inplace=True)

    # 2. Cálculo de Porcentaje
    # Creo una columna que representa la proporcion por marcas:
    df_marcas['Porcentaje'] = df_marcas['Total'] / criterio_de_total 
    df_marcas.set_index('Categoría 1',inplace=True)

    # 3. Filtrado y Copia
    df_marcas_filtrado = df_marcas[df_marcas['Porcentaje'] > umbral].copy()
    
    # Los valores filtrados son la suma de las filas en el DataFrame filtrado
    porcentaje_filtrado = np.sum(df_marcas_filtrado['Porcentaje'])
    cantitdad_filtrada = np.sum(df_marcas_filtrado['Cantidad'])
    total_filtrado = np.sum(df_marcas_filtrado['Total'])

    # Cálculo del RESTO
    porcentaje_resto = 1 - porcentaje_filtrado 
    cantidad_resto = total_cantidad_absoluto - cantitdad_filtrada
    total_resto = criterio_de_total - total_filtrado

    # 5. Asigno la nueva linea 'Otras Marcas':
    df_marcas_filtrado.loc['Otras Marcas',['Cantidad','Total','Porcentaje']] = [cantidad_resto, total_resto, porcentaje_resto]
    df_marcas_filtrado = df_marcas_filtrado.sort_values(by='Porcentaje',ascending=False)
    df_marcas_filtrado['Total'] = df_marcas_filtrado['Total'].round(2)

    st.info('**:red[SIN MARCA]** son los articulos del inventario que no estan categorizados apropiadamente en la base de datos.')
    fig = px.pie(
        df_marcas_filtrado,
        values='Porcentaje',
        names=df_marcas_filtrado.index,
        title='Proporcion De Marcas',
        color_discrete_sequence=px.colors.sequential.RdBu,
        hover_data=['Total'],
        labels={'Total':'Total MXN'}
        )
    st.plotly_chart(fig)

    # 6. Mostrar Tabla
    st.dataframe(
        df_marcas_filtrado,
        column_config={
            # Se usa el formato 'percent' para el porcentaje que es un valor de 0 a 1
            'Cantidad':st.column_config.NumberColumn(step=1), # Cantidades son números enteros
            'Total':st.column_config.NumberColumn(format='$%0.2f',step=0.01),
            'Porcentaje':st.column_config.NumberColumn(format='percent') # Muestra el valor de 0.xx como porcentaje
        }
    )
    st.divider()

def top_productos(df):
    """Esta seccion calcula y regresa el top productos, escala valores y los pondera"""
    st.header(f':material/format_list_numbered: {l.phrase[112]}')

    cantidad = st.number_input(
        label='Determinar Cantidad De Muestras',
        key='Determinar_Cantidad_De_Muestras',
        step=1,
        min_value=1,
        max_value=30,
        value=10
    )

    pivot_productos = pd.pivot_table(df,index='Producto',values=['Cantidad','Total'],aggfunc='sum')

    # Escalando los datos para poder ser ponderados eventualmente y evaluados de mayor a menor
    scaler = MinMaxScaler()
    pivot_array_escalado = scaler.fit_transform(pivot_productos)
    pivot_escalada = pd.DataFrame(pivot_array_escalado,index=pivot_productos.index,columns=pivot_productos.columns)

    # Ponderando el ranking y ordenando sobre la nueva columna:
    pivot_escalada['Rank'] = ((pivot_escalada['Cantidad']*0.3) + (pivot_escalada['Total']*0.7))
    pivot_escalada['Cantidad Real'] = pivot_productos['Cantidad'].round()
    pivot_escalada['Total Real'] = pivot_productos['Total'].round(1)
    copia = pivot_escalada.copy()
    pivot_escalada = pivot_escalada.sort_values(by='Rank',ascending=False).head(cantidad)

    # Generacion del grafico
    fig = px.bar(
        data_frame=pivot_escalada,
        x='Total Real',
        y=pivot_escalada.index,
        orientation='h',
        title='Top Productos',
        text_auto='.1s'
        )
    
    st.plotly_chart(fig)
    
    st.dataframe(
        pivot_escalada,
        column_order=['Cantidad Real','Total Real','Rank'],
        column_config={
            'Total Real':st.column_config.NumberColumn(format='dollar',step=0.1),
            'Rank':st.column_config.NumberColumn(step=0.0001)
        }
        )

    productos_menos_vendidos = st.toggle(
        label='Productos menos vendidos',
        key='productos_menos_vendidos'
    )
    if productos_menos_vendidos:
        st.divider()
        st.dataframe(
            data=copia.sort_values(by='Rank',ascending=False).tail(20),
            column_order=['Cantidad Real','Total Real','Rank'],
            column_config={
            'Total Real':st.column_config.NumberColumn(format='dollar',step=0.1)
            }
            )
    st.divider()

def correlacion(df):
    
    st.header(f':material/calendar_month: {l.phrase[113]}')
    
    # Muestro un mapa de calor para las ventas a traves de los anhos:
    pivot_calor = pd.pivot_table(data=df,aggfunc='sum',values='Total',columns='Year',index='Month')
    meses= {'01':'Enero','02':'Febrero','03':'Marzo','04':'Abril','05':'Mayo','06':'Junio','07':'Julio','08':'Agosto','09':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre'}
    pivot_calor = pivot_calor.rename(index = meses)
    
    # Heatmap plot
    fig0 = px.imshow(
        pivot_calor,
        x=pivot_calor.columns,
        y=pivot_calor.index,
        text_auto=True,
        aspect='auto',
        color_continuous_scale='YlGn'
        )
    st.markdown('**Meses mas calientes representados por un :green[verde] intenso**')
    st.plotly_chart(fig0)
    st.divider()

    # Muestro a traves de una linea de tiempo las ventas, tanto general como en comparacion directa
    pivot_line = pd.pivot_table(df,index=['Year','Month'],values='Total',aggfunc='sum')
    pivot_line = pivot_line.reset_index()
    
    # Esta seccion prepara los datos para el calculo de ACF, y el uso de type(datetime)
    ACF_tab = pivot_line.copy()
    ACF_tab['Fecha'] = pd.to_datetime(ACF_tab['Year'].astype('str')+'-'+ACF_tab['Month'].astype('str'))
    ACF_tab = ACF_tab.set_index('Fecha')
    ACF_Serie = ACF_tab['Total']

    # Linea de tiempo plot
    pivot_line['Month'] = pivot_line['Month'].replace(to_replace=meses)
    fig2 = px.line(
        pivot_line,
        x='Month',
        color='Year',
        y='Total',
        markers=True,
        labels={'Total':'Total (MXN)','Month':'Meses'}
        )
    
    # Linea de tiempo comparacion directa
    pivot_line['Eje X'] = pivot_line['Year']+' - '+pivot_line['Month']
    fig = px.line(
        pivot_line,
        x='Eje X',
        y='Total',
        markers=True,
        labels={'Eje X':'Linea de Tiempo 2023 - 2025','Total':'Total (MXN)'})
    
    st.markdown('**Tendencia a lo largo del tiempo :blue[2023 - 2025]**')
    st.plotly_chart(fig)
    st.divider()
    st.markdown('**Comparacion directa: Años :red[2023 - 2024 - 2025]**')
    st.plotly_chart(fig2)

    ACF = st.toggle(
        label='Grafica del Valor ACF',
        key='Calculo_Y_Grafica_del_Valor_ACF'
    )
    if ACF:
        lags_max = 32

        fig, ax = plt.subplots()
        plot_acf(ACF_Serie,lags=lags_max,ax=ax)
        plt.title('Función de Autocorrelación (ACF) de las Ventas Mensuales')
        plt.grid(True,alpha=0.5,linestyle='--')
        plt.xlabel('Rezagos (Lags) en meses')
        plt.ylabel('Coeficiente de Autocorrelación')
        st.pyplot(fig)
    
    st.divider()

# Aqui empieza la interfaz de usuario:
st.title(f':material/analytics: {l.phrase[5]}')
df = acceso_datos_ventas()

seleccion = st.pills(
    label=l.phrase[108],
    options=[
        f':material/analytics: {l.phrase[109]}',
        f':material/circles_ext: {l.phrase[110]}',
        f':material/hardware: {l.phrase[111]}',
        f':material/format_list_numbered: {l.phrase[112]}',
        f':material/calendar_month: {l.phrase[113]}'
        ],
    key='Opciones_Estadisticas',
    width='stretch',
    default=f':material/calendar_month: {l.phrase[113]}'
    )

if seleccion == f':material/analytics: {l.phrase[109]}':
    ventas_mensuales(df)
if seleccion == f':material/circles_ext: {l.phrase[110]}':
    histograma_frecuencia(df)
if seleccion == f':material/hardware: {l.phrase[111]}':
    proporcion_marcas(df)
if seleccion == f':material/format_list_numbered: {l.phrase[112]}':
    top_productos(df)
if seleccion == f':material/calendar_month: {l.phrase[113]}':
    correlacion(df)