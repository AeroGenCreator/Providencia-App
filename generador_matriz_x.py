# Interfaz de usuario
import streamlit as st

# Manejo de datos
import pandas as pd
import numpy as np

# lectura de datos
import json

# Modulo de lenguaje
import lenguaje

# Para lacreacion de todas las combinaciones (fecha, producto)
from itertools import product

# Interfaz de usuario:
l = lenguaje.tu_idioma()

def obtener_dataframe(csv):
    try:
        df = pd.read_csv(csv,delimiter=';', encoding='utf8')
        return df
    except Exception as e:
        st.warning(e)
        return None

def revision_de_columnas(data):
    try:
        data = data[['Fecha','Descripción','Cantidad']]
        data = data.rename(columns={'Descripción':'Producto'})
        data['Cantidad'] = pd.to_numeric(data['Cantidad'],errors='coerce')
        return data
    except Exception as e:
        st.warning(e)

def obtener_meses(data):
    data['Fecha'] = pd.to_datetime(data['Fecha'],errors='coerce',yearfirst=True)
    data['Mes'] = data['Fecha'].dt.month
    data.dropna(subset=['Fecha'], inplace=True)
    return data

def combinaciones_mes_producto(meses,productos):
    esqueleto_completo = list(product(meses, productos))
    df_esqueleto = pd.DataFrame(esqueleto_completo, columns=['Mes', 'Producto'])
    return df_esqueleto

def pivotear_df(data):
    grupo = data.groupby(by=['Mes','Producto'])['Cantidad'].sum()
    df_grupo = pd.DataFrame(grupo)
    df_grupo = df_grupo.reset_index()
    return df_grupo

def aplicar_lags_y_media_movil(data):
    
    # 1. Aplicar Lag por grupo de Producto:
    rolling_window = 3
    lags = 3
    for lag in range(1, lags + 1):
        data[f'Cantidad_lag_{lag}'] = (data.groupby('Producto')['Cantidad'].shift(lag))

    # 2. Aplicar Media Móvil por grupo de Producto:
    # 1. Elimina el índice 'Producto' temporalmente, Aplicar el desplazamiento al resultado de la media móvil
    data['Rolling_mean'] = (data.groupby('Producto')['Cantidad'].rolling(window=rolling_window).mean().shift(1).reset_index(level=0, drop=True))

    return data

def codificar_meses(data):
    # Sen/Cos para codificar los meses de manera ciclica
    P = 12 # <- El periodo son los 12 meses del anho
    # Crear las dos columnas ciclicas:
    data['Mes_seno'] = np.sin((2 * np.pi * data['Mes'])/ P)
    data['Mes_coseno'] = np.cos((2 * np.pi * data['Mes']) / P)
    return data

def limpieza(df):

    df = revision_de_columnas(data=df)
    df = obtener_meses(data=df)

    meses = df['Mes'].unique()
    productos = df['Producto'].unique()

    esqueleto = combinaciones_mes_producto(meses=meses,productos=productos)
    df = pivotear_df(data=df)

    df = pd.merge(esqueleto,df,on=['Mes','Producto'],how='left')
    df['Cantidad'] = df['Cantidad'].fillna(0)

    df = aplicar_lags_y_media_movil(data=df)
    df = codificar_meses(data=df)

    df = df.dropna()
    return df

# Aqui comienza la interfaz superficial de usuario:
st.title(f':material/graph_2: {l.phrase[126]}')
st.subheader(l.phrase[127])
st.info(f'**:blue[{l.phrase[128]}]**')

csv = st.file_uploader(
    label='Nada',
    label_visibility='hidden',
    type=['csv','txt'],
    key='funcion_de_limpieza_creacion_matriz_de_caracteristicas')

if csv:
    try:
        df = obtener_dataframe(csv)
        if df is not None:
            df_limpio = limpieza(df)
            # orden correcto y columnas necesarias:
            df_limpio = df_limpio[['Producto','Cantidad_lag_1','Cantidad_lag_2','Cantidad_lag_3','Rolling_mean','Mes_seno','Mes_coseno']]
            df_limpio = df_limpio.reset_index(drop=1)
            st.dataframe(df_limpio,hide_index=True)
            st.write(f'{l.phrase[129]}: {df_limpio.shape[0]}')
        else:
            st.warning('1')
    except Exception as e:
        st.warning(e)