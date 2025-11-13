'''Toda esta seccion maneja el modelo de prediccion y su salida final para el usuario'''
# Para ler archivos json
import json
# Para guardar modelos y metadatos de modelo
import joblib
# Para Medir Tiempos
import time

# Manejo de datos
import pandas as pd
import numpy as np

# Para producir tuplas con diferentes combinaciones
from itertools import product

# Metricas de evaluacion de modelos
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Classes para buscar mejores hiperparametros en un SeriesTiempo
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

# LightGBM Regression Model
from lightgbm import LGBMRegressor
# Para la interfaz de usuario
import streamlit as st
# Manejo de PDFs
from fpdf import FPDF
from fpdf import XPos,YPos
# Para fechas
import datetime
# Mi modulo de lenguajes
import lenguaje

l=lenguaje.tu_idioma()

# Usar este decorador para cargar una sola vez
@st.cache_resource 
def acceso_modelo():
    modelo = joblib.load('lgbm_model.joblib')
    return modelo

# Usa este decorador para cargar una sola vez
@st.cache_resource
def acceso_rop():
    ruta = 'df_rop_final_dias_8_riesgo_90.csv'
    df = pd.read_csv(ruta)
    if 'Unnamed: 0' in df.columns:
        df = df.rename(columns={'Unnamed: 0':'index'})
        df = df.set_index('index')
        df = df.drop(labels=['material','mediana_diaria','sigma_robusta','ss/20','ss/200','rop/20','rop/200'],axis=1)
        df = df.rename(columns={'producto':'Producto','marca':'Marca','stock_seguro':'Stock_Seguro','punto_reorden':'Punto_Reorden'})
        return df
    
    df = df.drop(labels=['material','mediana_diaria','sigma_robusta','ss/20','ss/200','rop/20','rop/200'],axis=1)
    df = df.rename(columns={'producto':'Producto','marca':'Marca','stock_seguro':'Stock_Seguro','punto_reorden':'Punto_Reorden'})
    return df

def limpiar_columnas(df):
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns='Unnamed: 0',axis=1)
        df = df.reset_index()
    
    orden_esperado = ['Producto','Cantidad_lag_1','Cantidad_lag_2','Cantidad_lag_3','Rolling_mean','Mes_seno','Mes_coseno']
    if list(df.columns) != orden_esperado:
        st.info(f'{l.phrase[122]} `{orden_esperado}`')
        return None
    return df

def predecir(modelo,df):
    productos_temporales = df['Producto'].copy()
    df = df.drop(columns=['Producto'])
    prediccion_array = modelo.predict(df)
    prediccion_df = pd.DataFrame(data=prediccion_array,index=df.index,columns=['Prediccion'])
    prediccion_df = pd.concat([productos_temporales,prediccion_df],axis=1)
    return prediccion_df

def unir_clasificar(prediccion,tabla_rop):
    union = pd.merge(prediccion,tabla_rop,on='Producto',how='left')
    union = union.dropna()
    union['Revision'] = np.where(union['Punto_Reorden']*0.95 < union['Prediccion'],'Riesgo','Estable')
    
    df_completo = union.copy()
    df_final = union[union['Revision']=='Riesgo']
    return (df_final,df_completo)

# A partir de aqui se maneja la interfaz superficial
st.title(f':material/neurology: {l.phrase[118]}')
st.subheader(l.phrase[119])

tab1, tab2 = st.tabs([
    f':material/batch_prediction: LGBMRegressor',
    f':material/book_3: Docs.'],
    default=f':material/batch_prediction: LGBMRegressor')

with tab1:
    modelo = acceso_modelo()
    df_rop = acceso_rop()

    st.info(f'**:blue[{l.phrase[120]}]:**')
    csv = st.file_uploader(
        label=l.phrase[121],
        type='csv',
        key='matri_x_para_prediccion'
    )
    if csv:
        try:
            df = pd.read_csv(csv)
            df = limpiar_columnas(df)
            if df is not None:
                prediccion_en_df = predecir(modelo=modelo,df=df)
                prediccion_clasificada_lenguaje_humano = unir_clasificar(prediccion=prediccion_en_df,tabla_rop=df_rop)
                st.markdown(f'**:red[{l.phrase[124]}:] ${prediccion_clasificada_lenguaje_humano[0].shape[0]}$**')
                st.dataframe(prediccion_clasificada_lenguaje_humano[0])
                st.divider()
                mostrar_prediccion_completa = st.toggle(label=f'**:blue[{l.phrase[125]}:]**')
                if mostrar_prediccion_completa:
                    st.markdown(f'**:blue[{l.phrase[130]}:] ${prediccion_clasificada_lenguaje_humano[1].shape[0]}$**')
                    st.dataframe(prediccion_clasificada_lenguaje_humano[1])
            else:
                st.warning(l.phrase[123])
        except Exception as e:
            st.warning(e)

with tab2:
    st.subheader(l.phrase[131])
    st.markdown(
        f'{l.phrase[132]}: :material/book_3: [Git-Hub](https://github.com/AeroGenCreator/LGBMRegressor-Providencia/blob/main/SeriesTiempo_Prediccion.ipynb)')
    st.markdown(f'{l.phrase[133]}: :material/folder_data: [Git-Hub Providencia](https://github.com/AeroGenCreator/Providencia-App)')