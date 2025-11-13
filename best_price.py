import json
import os

import lenguaje

import numpy as np
from fpdf import FPDF
import pandas as pd
import streamlit as st
from fpdf.enums import XPos, YPos

l = lenguaje.tu_idioma()

def crear_pdf():

    df = pd.DataFrame(data=st.session_state.TABLA_FINAL)

    class PDF(FPDF):
        def __init__(self, orientation = "portrait", unit = "mm", format = "letter"):
            super().__init__(orientation, unit, format)
            self.add_font(family='ArialUnicodeMS',fname='arial-unicode-ms.ttf',style="")
        def header(self):
            self.set_text_color(64,64,64)
            self.set_font(family='ArialUnicodeMS',size=14)
            self.cell(0,12,text=l.phrase[101],align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)
            return super().header()
        def footer(self):
            self.set_y(-10)
            self.set_font(family='ArialUnicodeMS',size=8)
            self.cell(0,6,text=f'{l.phrase[15]} {self.page_no()}/{{nb}}',center=True)
            return super().footer()
    
    pdf = PDF(orientation='portrait',unit='mm',format='letter')
    
    pdf.add_page()
    pdf.set_font(family='ArialUnicodeMS',size=7)
    pdf.set_line_width(0.1)
    pdf.set_draw_color(192,192,192)
    pdf.set_fill_color(192,192,192)
    pdf.set_text_color(64,64,64)

    pdf.cell(0,1,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.cell(14,6,text='CANT',border=True,align='C')
    pdf.cell(96,6,text='PRODUCTO',border=True,align='L')
    pdf.cell(39,6,text='PROVEDOR',border=True,align='L')
    pdf.cell(7,6,text='DES',border=True,align='C')
    pdf.cell(7,6,text='IVA',border=True,align='C')
    pdf.cell(16,6,text='PRECIO F',border=True,align='C')
    pdf.cell(17,6,text='TOTAL',border=True,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    pdf.cell(0,1,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    for i,fila in df.iterrows():
        pdf.set_font(size=7)
        pdf.cell(14,6,text=f'{fila['Cantidad']:.2f}',border=False,align='C')
        pdf.cell(96,6,text=f'{fila['Producto']}',border=False,align='L')
        pdf.cell(39,6,text=f'{fila['Provedor']}',border=False,align='L')
        pdf.cell(7,6,text=f'%{round(fila['Descuento']*100)}',border=False,align='C')
        pdf.cell(7,6,text=f'%{round(fila['IVA']*100)}',border=False,align='C')
        pdf.cell(16,6,text=f'${fila['Precio F.']}',border=False,align='C')
        pdf.cell(17,6,text=f'${fila['Total']}',border=False,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    pdf.set_font(family='ArialUnicodeMS',size=8)
    pdf.cell(0,1,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.cell(0,6,text=f'TOTAL CON IVA: ${round(st.session_state.METRIC_TOTAL,2)}',border=True,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.cell(0,1,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    output = bytes(pdf.output())
    
    st.download_button(
        label=l.phrase[79],
        key='Descargar_PDF_Mejores_Precios',
        data=output,
        file_name=f'{l.phrase[101]}.pdf'
    )

def productos():
    RUTA_PRODUCTOS = '_inventario_providencia.json'
    try:
        if os.path.exists(RUTA_PRODUCTOS) and os.path.getsize(RUTA_PRODUCTOS) > 0:
            with open(RUTA_PRODUCTOS,'r',encoding='utf-8') as f:
                datos = json.load(f)
                return datos['Producto']
        else:
            return st.warning(l.phrase[93])
    except (KeyError, json.JSONDecodeError):
        st.error(l.phrase[94])

def provedores():
    RUTA_PROVEDORES = 'provedores.json'
    try:
        if os.path.exists(RUTA_PROVEDORES) and os.path.getsize(RUTA_PROVEDORES) > 0:
            with open(RUTA_PROVEDORES,'r',encoding='utf-8') as f:
                datos = json.load(f)
                return datos
        else:
            return st.warning(l.phrase[93])
    except (KeyError, json.JSONDecodeError):
        st.error(l.phrase[94])

def acceso_a_iva():
    RUTA_CONFIGURACION = 'configuracion_file.json'
    try:
        if os.path.exists(RUTA_CONFIGURACION) and os.path.getsize(RUTA_CONFIGURACION) > 0:
            with open(RUTA_CONFIGURACION,'r',encoding='utf-8') as f:
                datos = json.load(f)
                iva = datos['configuracion']['mejor_precio']['iva']
                return iva
        else:
            st.warning(l.phrase[93])
    except (KeyError, json.JSONDecodeError):
        st.error(l.phrase[94])

def acceso_a_descuento():
    RUTA_CONFIGURACION = 'configuracion_file.json'
    try:
        if os.path.exists(RUTA_CONFIGURACION) and os.path.getsize(RUTA_CONFIGURACION) > 0:
            with open(RUTA_CONFIGURACION,'r',encoding='utf-8') as f:
                datos = json.load(f)
                descuento = datos['configuracion']['mejor_precio']['descuento']
                return descuento
        else:
            st.warning(l.phrase[93])
    except (KeyError, json.JSONDecodeError):
        st.error(l.phrase[94])

def parametros():
    
    DF_VACIO = {
        'Cantidad':pd.Series([],dtype='float64'),
        'Productos':pd.Series([],dtype='object')
    }
    
    if 'best_price' not in st.session_state:
        st.session_state.best_price = DF_VACIO
    if 'TABLA_GENERADA' not in st.session_state:
        st.session_state.TABLA_GENERADA = {}
    if 'provedores' not in st.session_state:
        st.session_state.provedores = []
    if 'TABLA_CALCULADA' not in st.session_state:
        st.session_state.TABLA_CALCULADA = {}
    if 'METRIC_TOTAL' not in st.session_state:
        st.session_state.METRIC_TOTAL = 0

    IVA = acceso_a_iva()
    DESCUENTO = acceso_a_descuento()
    lista_productos = productos()
    lista_provedores = provedores()

    cantidad_estandar = 1.00
    cantidad_minima = 0.00

    provedores_seleccionados = st.multiselect(
        label=l.phrase[95],
        options=lista_provedores,
        key='Seleccion_Provedores_Tags',
        accept_new_options=False,
        placeholder=l.phrase[117],
        default= st.session_state.provedores
    )

    st.write(l.phrase[96])
    parametros = st.data_editor(
        data=st.session_state.best_price,
        num_rows='dynamic',
        hide_index=True,
        column_config={
            'Cantidad':st.column_config.NumberColumn(default=cantidad_estandar,min_value=cantidad_minima,step=0.01,width=30),
            'Productos':st.column_config.SelectboxColumn(options=lista_productos,width=300),
        }
        )

    if provedores_seleccionados:
        st.session_state.provedores = provedores_seleccionados

    parametros = pd.DataFrame(parametros)

    if not parametros.empty and len(provedores_seleccionados) > 0:
        
        crear_tabla = st.button(
            label=f':material/Table: {l.phrase[97]}',
            key='Crear_Tabla_Editable',
            type='secondary',
            width='stretch'
        )

        if crear_tabla:
            nulos = parametros['Productos'].isna().sum()
            parametros.drop_duplicates(subset=['Productos'],keep='first',inplace=True,ignore_index=True)
            
            st.session_state.best_price = parametros

            if nulos > 0:
                st.info(l.phrase[98])
                return

            cantidades_para_cotizar = parametros['Cantidad'].tolist()*len(provedores_seleccionados)
            productos_para_cotizar = parametros['Productos'].tolist()*len(provedores_seleccionados)
            provedores_para_cotizar = sorted(provedores_seleccionados*len(parametros))

            filas_cantidad = []
            filas_producto = []
            filas_provedor = []

            for e in zip(cantidades_para_cotizar,productos_para_cotizar,provedores_para_cotizar):
                filas_cantidad.append(e[0])
                filas_producto.append(e[1])
                filas_provedor.append(e[2])
            
            celdas_vacias = []
            celdas_descuento = []
            celdas_iva = []

            for i in range(0,len(filas_cantidad)):
                celdas_vacias.append(0)
                celdas_descuento.append(DESCUENTO)
                celdas_iva.append(IVA)
            
            pre_diccionario_editable = {
                'Cantidad':filas_cantidad,
                'Producto':filas_producto,
                'Provedor':filas_provedor,
                'Precio Uni.':celdas_vacias,
                'Descuento':celdas_descuento,
                'IVA':celdas_iva,
                'Precio F.':celdas_vacias,
                'Total':celdas_vacias
            }
            
            st.session_state.TABLA_GENERADA = pre_diccionario_editable
            pass
    return None

def edicion_tabla():
    
    if 'TABLA_EDITADA' not in st.session_state:
        st.session_state.TABLA_EDITADA = {}

    st.divider()
    st.header(f':blue[{l.phrase[99]} :material/table_edit:]')
    
    tabla_editable = st.data_editor(
        data=st.session_state.TABLA_GENERADA,
        hide_index=True,
        num_rows='fixed',
        column_config={
            'Cantidad':st.column_config.NumberColumn(width=50,disabled=True),
            'Producto':st.column_config.TextColumn(width=190,disabled=True),
            'Provedor':st.column_config.TextColumn(width=90,disabled=True),
            'Precio Uni.':st.column_config.NumberColumn(width=70,format='dollar',step=0.01),
            'Descuento':st.column_config.NumberColumn(width=50,format='percent',step=0.01),
            'IVA':st.column_config.NumberColumn(width=50,format='percent',disabled=True),
            'Precio F.':st.column_config.NumberColumn(width=70,format='dollar',disabled=True),
            'Total':st.column_config.NumberColumn(width=70,format='dollar',disabled=True),
        }
        )

    filtrar_mejor_precio = st.button(
        label=f':material/database_search: {l.phrase[74]}',
        key='Filtrar_Mejor_Precio',
        type='primary',
        width='stretch'
    )

    if filtrar_mejor_precio:
        st.session_state.TABLA_EDITADA = tabla_editable
        return
    
def tabla_final():
    
    if 'TABLA_FINAL' not in st.session_state:
        st.session_state.TABLA_FINAL = {}

    st.divider()

    df_f = st.session_state.TABLA_EDITADA
    
    df_f = pd.DataFrame(df_f)
    
    df_f['Precio F.'] = round((df_f['Precio Uni.']-(df_f['Precio Uni.']*df_f['Descuento'])) * (1 + df_f['IVA']),2)
    df_f['Total'] = round(df_f['Cantidad']*df_f['Precio F.'],2)
    df_copia = df_f.copy()

    st.session_state.TABLA_CALCULADA = df_copia
    st.info(l.phrase[100])
    st.dataframe(
        data=st.session_state.TABLA_CALCULADA, # <-- USAMOS LA TABLA COMPLETA
        hide_index=True,
        column_config={
            'Cantidad':st.column_config.NumberColumn(width=55,step=0.01),
            'Producto':st.column_config.TextColumn(width=190),
            'Provedor':st.column_config.TextColumn(width=100),
            'Precio Uni.':st.column_config.NumberColumn(width=70,format='dollar'),
            'Descuento':st.column_config.NumberColumn(width=45,format='percent'),
            'IVA':st.column_config.NumberColumn(width=45,format='percent'),
            'Precio F.':st.column_config.NumberColumn(format='dollar'),
            'Total':st.column_config.NumberColumn(format='dollar')
        }
    )
    df_f.sort_values(by='Precio F.', ascending=True, inplace=True)
    df_f = df_f[~(df_f['Precio Uni.'] == 0.00)]
    df_f.drop_duplicates(subset=['Producto'],keep='first',inplace=True)
    metrica_total = round(df_f['Total'].sum(),2)

    st.session_state.TABLA_FINAL = df_f
    st.session_state.METRIC_TOTAL = metrica_total

    st.success(f':material/price_check: {l.phrase[101]}')
    st.dataframe(
        data=st.session_state.TABLA_FINAL,
        hide_index=True,
        column_config={
            'Cantidad':st.column_config.NumberColumn(width=55,step=0.01),
            'Producto':st.column_config.TextColumn(width=190),
            'Provedor':st.column_config.TextColumn(width=100),
            'Precio Uni.':st.column_config.NumberColumn(width=70,format='dollar'),
            'Descuento':st.column_config.NumberColumn(width=45,format='percent'),
            'IVA':st.column_config.NumberColumn(width=45,format='percent'),
            'Precio F.':st.column_config.NumberColumn(format='dollar'),
            'Total':st.column_config.NumberColumn(format='dollar')
        }
        )
    st.metric(
        label=l.phrase[102],
        value=f'${st.session_state.METRIC_TOTAL}',
        border=True
    )
    if 'TABLA_FINAL' in st.session_state and dict(st.session_state.TABLA_FINAL):
        col1, col2 = st.columns([2,2])
        pdf = col1.button(
            label=':material/draft: PDF',
            key='Obtner_PDF',
            type='primary',
            width='stretch'
        )
        limpiar = col2.button(
            label=f':material/mop: {l.phrase[103]}',
            key='Limpiar_Tablas',
            type='secondary',
            width='stretch'
        )
        if limpiar:
            try:
                del st.session_state.best_price
                del st.session_state.TABLA_GENERADA
                del st.session_state.TABLA_CALCULADA
                del st.session_state.METRIC_TOTAL
                del st.session_state.TABLA_EDITADA
                del st.session_state.TABLA_FINAL

                st.rerun()

            except KeyError:
                st.error('Parece Que Las Tablas Ya Estan Vacias Intenta Refrescar La Pagina')
        if pdf:
            crear_pdf()

# Esto Es La Interfaz:
st.title(f':material/price_check: {l.phrase[72]}')
parametros()
if 'TABLA_GENERADA' in st.session_state and dict(st.session_state.TABLA_GENERADA):
    edicion_tabla()
    if 'TABLA_EDITADA' in st.session_state and dict(st.session_state.TABLA_EDITADA):
        tabla_final()