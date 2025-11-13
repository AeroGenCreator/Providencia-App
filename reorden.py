# modulos python
import json

# mis modulos
import lenguaje

# librerias 3eros
import streamlit as st
import pandas as pd
import numpy as np

l = lenguaje.tu_idioma()
st.title(f':material/local_shipping: {l.phrase[114]}')

# Factor de corrección para convertir el MAD Estándar a Desviación Estándar (Sigma Robusta)
# Asume una distribución normal y es necesario para usar el factor Z.
FACTOR_CORRECCION_MAD = 1.4826

# Carga de datos
@st.cache_resource
def acceso_a_ventas():
    try:
        with open('ventas_limpias_providencia.json','r',encoding='utf-8')as f:
            df = pd.DataFrame(json.load(f))
            return df
    except FileNotFoundError:
        return None

df = acceso_a_ventas()
if df is None:
    st.error("Error: Archivo 'ventas_limpias_providencia.json' no encontrado.")

# Aislo marca y producto.
marcas = df[['Producto','Categoría 1','Categoría 2']]
marcas = marcas.drop_duplicates(subset=['Producto'])

# Corrección manual de outliers, ya revisados.
df.loc[52153,['Cantidad']] = 4
df.loc[52153,['Total']] = 44.9
df.loc[2487,['Cantidad']] = 2
df.loc[2487,['Total']] = 12.068

col1, col2 = st.columns([2.5,1.5])
# Parámetros editables
dias_de_entrega = col1.slider(label='Dias Entrega',key='Dias Entrega',min_value=1,max_value=20,step=1,value=8)
factor_z = col2.selectbox(label='**:red[RIESGO]**',options=[0.84,1.3],key='probabilidad_riesgo')
st.markdown('**:blue[INFO. RIESGO:]** $(0.84 = 80\\%)$ inventario seguro, $(1.3 = 90\\%)$ de inventario seguro.')

st.subheader(':material/data_table: Tabla De Minimos y Punto De Reorden')
col3, col4 = st.columns([1.5,2.5])
filtro_marca = col3.multiselect(label=':red[**Filtrar por marca**]',key='filtro_marca',options=marcas['Categoría 1'].unique())
filtro_producto = col4.multiselect(label=':red[**Filtrar por producto**]',key='filtro_producto',options=marcas['Producto'].unique())

# Agrupación de la venta diaria por producto.
grupo_1 = df.groupby(['Year','Month','Day','Producto'])['Cantidad'].sum()
grupo_1 = pd.DataFrame(data=grupo_1,columns=['Cantidad'],index=grupo_1.index)


# MAD Estándar = Mediana de las desviaciones absolutas desde la mediana
def calcular_mad_estandar(x):
    """Calcula el Desvío Absoluto Mediana (MAD estándar)."""
    # 1. Encuentra la mediana del grupo
    mediana = x.median()
    # 2. Calcula la mediana de la diferencia absoluta entre cada punto y la mediana
    return np.median(np.abs(x - mediana))

# Cálculo de la Mediana Diaria y el MAD Estándar por producto
pivot_1 = pd.pivot_table(
    data=grupo_1,
    values='Cantidad',
    index='Producto',
    aggfunc=['median', calcular_mad_estandar] # Usamos la nueva función MAD Estándar
    )

pivot_1 = pivot_1.reset_index()
pivot_1 = pivot_1.fillna(0) # Rellenar NaN (productos sin ventas) con 0
pivot_1.columns = ['Producto','Mediana Diaria','MAD Estándar']

# 1. Estimar la Desviación Estándar (Sigma Robusta) usando el MAD Estándar
# Esto hace que el cálculo sea compatible con el factor Z
pivot_1['Sigma Robusta'] = pivot_1['MAD Estándar'] * FACTOR_CORRECCION_MAD

# 2. Calcular el Stock de Seguridad (SS)
# SS = Z * Sigma_Robusta * sqrt(LT)
pivot_1['Stock Seguro'] = (pivot_1['Sigma Robusta'] * (np.sqrt(dias_de_entrega))) * factor_z

pivot_1['Stock Seguro'] = pivot_1['Stock Seguro'].round().astype(int) # Redondeo para unidades
pivot_1['ss/6'] = round(pivot_1['Stock Seguro']/6)
pivot_1['ss/20'] = round(pivot_1['Stock Seguro']/20)
pivot_1['ss/100'] = round(pivot_1['Stock Seguro']/100)
pivot_1['ss/200'] = round(pivot_1['Stock Seguro']/200)

# 3. Calcular el Punto de Reorden (ROP)
# ROP = (Demanda_Robusta * LT) + SS
pivot_1['Punto Reorden'] = (pivot_1['Mediana Diaria'] * dias_de_entrega) + pivot_1['Stock Seguro']
pivot_1['Punto Reorden'] = pivot_1['Punto Reorden'].astype(int)

# Cálculo de fracciones
pivot_1['rop/6'] = round(pivot_1['Punto Reorden']/6)
pivot_1['rop/20'] = round(pivot_1['Punto Reorden']/20)
pivot_1['rop/100'] = round(pivot_1['Punto Reorden']/100)
pivot_1['rop/200'] = round(pivot_1['Punto Reorden']/200)

# Agrego las marcas
tabla_rop = pd.merge(pivot_1,marcas,on='Producto',how='left')

# Selección y ordenamiento de columnas
tabla_rop = tabla_rop[[
    'Producto',
    'Categoría 1',
    'Categoría 2',
    'Mediana Diaria',
    'Sigma Robusta',
    'Stock Seguro',
    'ss/6',
    'ss/20',
    'ss/100',
    'ss/200',
    'Punto Reorden',
    'rop/6',
    'rop/20',
    'rop/100',
    'rop/200'
    ]].sort_values(by='Punto Reorden',ascending=False).reset_index(drop=1).copy()

# renombro columnas a un formato mas limpio
tabla_rop = tabla_rop.rename(
    columns={
        'Producto':'producto',
        'Categoría 1':'marca',
        'Categoría 2':'material',
        'Mediana Diaria':'mediana_diaria',
        'Sigma Robusta':'sigma_robusta',
        'Stock Seguro':'stock_seguro',
        'Punto Reorden':'punto_reorden'
        })

# Agrego las opciones del filtro
if filtro_marca:
    st.dataframe(tabla_rop[tabla_rop['marca'].isin(filtro_marca)],hide_index=1)
elif filtro_producto:
    st.dataframe(tabla_rop[tabla_rop['producto'].isin(filtro_producto)],hide_index=1)
else:
    st.dataframe(tabla_rop,hide_index=1)
