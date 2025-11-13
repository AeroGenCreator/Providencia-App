"""En este archivo se accede a las opciones de configuracion
y se editan las mismas para posteriormente ser almacenadas en 
el archivo configuraciones_file.json"""
import os
import json
# Mis modulos
import lenguaje
# Terceros librerias
import streamlit as st

RUTA_CONFIG = 'configuracion_file.json'

def acceso_a_provedores():
    RUTA_PROVEDORES = 'provedores.json'
    try:
        if os.path.exists(RUTA_PROVEDORES) and os.path.getsize(RUTA_PROVEDORES) > 0:
            with open(RUTA_PROVEDORES,'r',encoding='utf-8') as f:
                datos = json.load(f)
                return datos
        else:
            return st.warning(l.phrase[73])
    except (FileNotFoundError, FileExistsError, json.JSONDecodeError):
        return st.warning(l.phrase[73])

def agregar_provedor(provedor):
    RUTA_PROVEDORES = 'provedores.json'
    try:
        if os.path.exists(RUTA_PROVEDORES) and os.path.getsize(RUTA_PROVEDORES) > 0:
            with open(RUTA_PROVEDORES,'r',encoding='utf-8') as f:
                datos = json.load(f)
                datos = set(datos)
                if provedor not in datos:
                    datos = list(datos)
                    datos = datos.append(provedor)
                    with open(RUTA_PROVEDORES,'r',encoding='utf-8') as e:
                        json.dump(datos,e,indent=2,ensure_ascii=False)
                else:
                    return st.info(f'{provedor} {l.phrase[90]}')
        else:
            return st.warning(l.phrase[73])
    except (FileNotFoundError, FileExistsError, json.JSONDecodeError):
        return st.warning(l.phrase[73])

def acceso_a_iva():
    RUTA_CONFI = 'configuracion_file.json'
    try:
        if os.path.exists(RUTA_CONFI) and os.path.getsize(RUTA_CONFI) > 0:
            with open(RUTA_CONFI,'r',encoding='utf-8') as f:
                datos = json.load(f)
                iva = datos['configuracion']['mejor_precio']['iva']
                return iva
        else:
            st.warning(l.phrase[80])
    except (FileExistsError, KeyError, json.JSONDecodeError):
        st.warning(l.phrase[80])

def cambiar_iva(nueva_iva):
    RUTA_CONFI = 'configuracion_file.json'
    try:  
        if os.path.exists(RUTA_CONFI) and os.path.getsize(RUTA_CONFI) > 0:
            with open(RUTA_CONFI,'r',encoding='utf-8') as f:
                datos = json.load(f)
                datos['configuracion']['mejor_precio']['iva'] = nueva_iva
            with open(RUTA_CONFI,'w',encoding='utf-8') as e:
                json.dump(datos,e,indent=2,ensure_ascii=False)
        else:
            st.warning(l.phrase[80])
    except (FileExistsError, KeyError, json.JSONDecodeError):
        st.warning(l.phrase[80])

def acceso_a_descuento():
    try:
        RUTA_CONFI = 'configuracion_file.json'
        if os.path.exists(RUTA_CONFI) and os.path.getsize(RUTA_CONFI) > 0:
            with open(RUTA_CONFI,'r',encoding='utf-8') as f:
                datos = json.load(f)
                descuento = datos['configuracion']['mejor_precio']['descuento']
                return descuento
        else:
            st.warning([80])
    except (FileExistsError, KeyError, json.JSONDecodeError):
        st.warning(l.phrase[80])

def cambiar_descuento(nuevo_descuento):
    RUTA_CONFI = 'configuracion_file.json'
    try:  
        if os.path.exists(RUTA_CONFI) and os.path.getsize(RUTA_CONFI) > 0:
            with open(RUTA_CONFI,'r',encoding='utf-8') as f:
                datos = json.load(f)
                datos['configuracion']['mejor_precio']['descuento'] = nuevo_descuento
            with open(RUTA_CONFI,'w',encoding='utf-8') as e:
                json.dump(datos,e,indent=2,ensure_ascii=False)
        else:
            st.warning(l.phrase[80])
    except (FileExistsError, KeyError, json.JSONDecodeError):
        st.warning(l.phrase[80])

def folio_por_facturar():
    try:
        if os.path.exists(RUTA_CONFIG) and os.path.getsize(RUTA_CONFIG) > 0:
            with open(RUTA_CONFIG,'r',encoding='utf-8') as por_folio:
                datos = json.load(por_folio)
                folio = datos['configuracion']['folio factura']
                return folio
        else:
            return
    except TypeError:
        return

def cambiar_folio(numero):
    try:
        if os.path.exists(RUTA_CONFIG) and os.path.getsize(RUTA_CONFIG) > 0:
            with open(RUTA_CONFIG,'r',encoding='utf-8') as cambio_folio:
                datos = json.load(cambio_folio)   
                datos['configuracion']['folio factura'] = numero
            with open(RUTA_CONFIG,'w',encoding='utf-8') as escritura:
                json.dump(datos,escritura,indent=4,ensure_ascii=False)
        else:
            st.warning(f'1. No se encuentra o se altero el archivo {RUTA_CONFIG}. Pedir ayuda con el soporte')
    except (FileNotFoundError,FileExistsError,json.JSONDecodeError):
        st.warning(f'2. No se encuentra o se altero el archivo <{RUTA_CONFIG}> Pedir ayuda con el soporte')

def acceso_fondo_caja():
    
    try:
        if os.path.exists(RUTA_CONFIG) and os.path.getsize(RUTA_CONFIG) > 0:
            with open(RUTA_CONFIG,'r',encoding='utf-8') as f:
                datos = json.load(f)   
                return datos['configuracion']['caja fondo']
        else:
            st.warning(f'1. No se encuentra o se altero el archivo {RUTA_CONFIG}. Pedir ayuda con el soporte')
    except (FileNotFoundError,FileExistsError,json.JSONDecodeError):
        st.warning(f'2. No se encuentra o se altero el archivo <{RUTA_CONFIG}> Pedir ayuda con el soporte')

def cambiar_fondo(cantidad):
    try:
        if os.path.exists(RUTA_CONFIG) and os.path.getsize(RUTA_CONFIG) > 0:
            with open(RUTA_CONFIG,'r',encoding='utf-8') as f:
                datos = json.load(f)   
                datos['configuracion']['caja fondo'] = cantidad
            with open(RUTA_CONFIG,'w',encoding='utf-8') as e:
                json.dump(datos,e,indent=4,ensure_ascii=False)
        else:
            st.warning(f'1. No se encuentra o se altero el archivo {RUTA_CONFIG}. Pedir ayuda con el soporte')
    except (FileNotFoundError,FileExistsError,json.JSONDecodeError):
        st.warning(f'2. No se encuentra o se altero el archivo <{RUTA_CONFIG}> Pedir ayuda con el soporte')

l=lenguaje.tu_idioma()
st.title(f':material/settings: {l.phrase[6]}')

# AQUI COMIENZA LA INTERFAZ --------------------------------------------------------------------------------------------------------

# Aqui accedo a los archivos de lenguaje.py, creo un widget de seleccion de idioma
# El selector, guarda los cambio en configuracion_file.json
# Para conocer el proceso, estudiar el codigo del archivo lenguaje.py
seleccion_idioma = lenguaje.escojer_idioma(llave='seleccion_configuracion')
# Aqui se leen los datos de configuracion_file.json/configuracion/idioma
# Y se leen los datos de configuracion_file.json/configuracion/traducciones
# Se crea un objeto con las traducciones disponibles y accedo a cada frase guardada
# utilizando el atributo .phrase[] y un indice dentro de los corchetes de barra.
l = lenguaje.tu_idioma()

col1,col2 = st.columns(2)
with col1:
    st.write(f'{l.phrase[12]}: :red[{acceso_fondo_caja()}]')
    fondo = st.number_input(
        label=l.phrase[58],
        step=1,
        min_value=0
        )
    if fondo:
        cambiar_fondo(fondo)
with col2:
    st.write(f'{l.phrase[22]}: :red[{folio_por_facturar()}]')
    folio = st.number_input(
    label=l.phrase[65],
    step=1,
    value=folio_por_facturar(),
    min_value=0
)
    if folio:
        cambiar_folio(folio)
    if not folio:
        cambiar_folio(0)

st.divider()

col3, col4 = st.columns(2)
with col3:
    st.write(f'{l.phrase[82]}: :red[% {int(acceso_a_iva()*100)}]')
    nueva_iva = st.number_input(
        label=l.phrase[85],
        step=1,
        min_value=0,
        max_value=100,
        key='iva_mejores_precios',
        value=int(acceso_a_iva()*100)
    )
    if nueva_iva:
        nueva_iva = float(nueva_iva/100)
        cambiar_iva(nueva_iva)
    else:
        nueva_iva = float(0/100)
        cambiar_iva(nueva_iva)
with col4:
    st.write(f'{l.phrase[86]}: :red[% {int(acceso_a_descuento()*100)}]')
    nuevo_descuento = st.number_input(
        label=l.phrase[87],
        step=1,
        min_value=0,
        max_value=100,
        key='nuevo_descuento_mejores_precios',
        value=int(acceso_a_descuento()*100)
    )
    if nuevo_descuento:
        nuevo_descuento = float(nuevo_descuento/100)
        cambiar_descuento(nuevo_descuento)
    else:
        nuevo_descuento = float(0/100)
        cambiar_descuento(nuevo_descuento)
col5,col6 = st.columns(2)
with col5:
    nuevo_provedor=st.selectbox(
        label=l.phrase[88],
        key='agregar_nuevo_provedor_a_la_base',
        accept_new_options=True,
        options=set(acceso_a_provedores()),
    )
    agregar = st.button(
        label=l.phrase[89],
        key='boton_agregar_provedor',
        width='stretch',
        type='primary'
    )
    if agregar:
        if len(nuevo_provedor) > 26:
            st.info(l.phrase[91])
        else:
            nuevo_provedor = str(nuevo_provedor)
            nuevo_provedor = nuevo_provedor.strip().upper()
            agregar_provedor(nuevo_provedor)

st.divider()
guardar_cambios = st.button(
    label=l.phrase[59],
    key='guardar_cambios',
    type='primary',
    width='stretch'
    )
if guardar_cambios:
    st.toast(body=l.phrase[116],duration='short',icon='⚙️')
    st.success(f':material/settings: {l.phrase[116]}')