import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import json
import altair as alt
from supabase import create_client
import base64

# Configuración inicial de la página
st.set_page_config(page_title="Gestión Corporativa", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 ESTÉTICA "DARK LUXURY / BOUTIQUE" (CSS AVANZADO)
# ==========================================
st.markdown("""
<style>
/* ---> IMPORTAR FUENTES DE ALTA COSTURA <--- */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;800&family=Manrope:wght@300;400;500;600&display=swap');

/* ---> RESET Y MODO OSCURO FORZADO <--- */
.stApp { background-color: #050505 !important; color: #E5E4E2 !important; }
[data-testid="stToolbar"] { display: none !important; }
.viewerBadge_container { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ---> TIPOGRAFÍA GLOBAL (Sin romper los iconos nativos de Streamlit) <--- */
p, label, li, h1, h2, h3, h4, h5, h6 { font-family: 'Manrope', sans-serif; color: #E5E4E2; }
h1, h2, h3, .main-title { font-family: 'Cinzel', serif !important; text-transform: uppercase; letter-spacing: 3px; font-weight: 400; color: #D4AF37 !important;}

/* ---> PESTAÑAS (TABS) ESTILO EDITORIAL <--- */
.stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding-bottom: 5px; background: transparent; }
.stTabs [data-baseweb="tab"] { 
    background-color: transparent !important; 
    border: none !important; 
    padding: 10px 5px !important; 
    color: #737373 !important; 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-size: 0.85rem; 
    font-weight: 600;
}
.stTabs [aria-selected="true"] { 
    color: #D4AF37 !important; 
    border-bottom: 2px solid #D4AF37 !important; 
    box-shadow: none !important;
}

/* ---> BOTONES ESTILO HIGH-END <--- */
button[data-testid="baseButton-primary"] {
    min-height: 70px !important;
    font-size: 1.2rem !important;
    font-family: 'Cinzel', serif !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 4px;
    background: rgba(212, 175, 55, 0.05) !important;
    color: #D4AF37 !important;
    border: 1px solid #D4AF37 !important;
    transition: all 0.4s ease !important;
}
button[data-testid="baseButton-primary"]:hover {
    background: #D4AF37 !important;
    color: #050505 !important;
    box-shadow: 0 10px 30px -10px rgba(212, 175, 55, 0.4) !important;
}
.stButton>button:not([data-testid="baseButton-primary"]) { 
    border-radius: 4px !important; 
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important; 
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease; 
    border: 1px solid #444 !important; 
    background-color: #111 !important;
    color: #E5E4E2 !important;
}
.stButton>button:not([data-testid="baseButton-primary"]):hover { 
    border-color: #D4AF37 !important;
    color: #D4AF37 !important;
    background-color: #1a1a1a !important;
}

/* ---> INPUTS Y SELECTBOX <--- */
.stTextInput input, .stDateInput input, .stTimeInput input, .stNumberInput input, .stTextArea textarea {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
    font-family: 'Manrope', sans-serif !important;
    padding: 12px 15px !important;
    font-weight: 500 !important;
}
.stTextInput input:focus, .stDateInput input:focus, .stTimeInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { 
    border-color: #D4AF37 !important; 
    box-shadow: 0 0 5px rgba(212, 175, 55, 0.5) !important; 
}
div[data-baseweb="select"] > div {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
}

/* ---> METRICAS Y TARJETAS <--- */
div[data-testid="metric-container"] { 
    background: rgba(15, 15, 15, 0.8) !important; 
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05); 
    padding: 20px; 
    border-radius: 4px; 
    border-top: none;
    border-left: 2px solid #D4AF37;
}
div[data-testid="stMetricValue"] { font-size: 2.2rem; font-family: 'Cinzel', serif; font-weight: 400; color: #D4AF37; }

/* ---> ALERTAS Y AVISOS <--- */
.alert-box { padding: 15px; border-radius: 4px; border-left: 3px solid #EF4444; background-color: rgba(239, 68, 68, 0.1); margin-bottom: 15px; color: #E5E4E2; font-size: 0.9rem;}
.task-box { padding: 15px; border-radius: 4px; border-left: 3px solid #10B981; background-color: rgba(16, 185, 129, 0.1); margin-bottom: 15px; color: #E5E4E2; font-size: 0.9rem;}
.task-pend { padding: 15px; border-radius: 4px; border-left: 3px solid #D4AF37; background-color: rgba(212, 175, 55, 0.1); margin-bottom: 15px; color: #E5E4E2; font-size: 0.9rem;}
.task-rej { padding: 15px; border-radius: 4px; border-left: 3px solid #EF4444; background-color: rgba(239, 68, 68, 0.1); margin-bottom: 15px; color: #E5E4E2; font-size: 0.9rem;}
.report-box { padding: 15px; border-radius: 4px; border-left: 3px solid #8B5CF6; background-color: rgba(139, 92, 246, 0.1); margin-bottom: 15px; color: #E5E4E2; font-size: 0.9rem;}
.super-box { padding: 20px; border: 1px solid rgba(212, 175, 55, 0.3); background: #0a0a0a; margin-bottom: 15px; color: #D4AF37; text-align: center; font-family: 'Cinzel', serif; letter-spacing: 1px; border-radius: 4px;}
.validation-box { padding: 15px; border-radius: 4px; border: 1px solid #333; background-color: #0a0a0a; margin-bottom: 10px; color: #A0A0A0; font-size: 0.9rem;}

/* ---> CREDENCIAL EMPLEADO <--- */
.credencial { 
    background: linear-gradient(135deg, #151515 0%, #050505 100%); 
    color: #E5E4E2; 
    padding: 30px 25px; 
    border-radius: 8px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.9); 
    margin-bottom: 30px; 
    border: 1px solid rgba(212, 175, 55, 0.2);
    position: relative;
    overflow: hidden;
}
.credencial::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(212, 175, 55, 0.05) 0%, transparent 60%);
    pointer-events: none;
}
.cred-nombre { font-family: 'Cinzel', serif; font-size: 2.2rem; font-weight: 600; margin: 0; color: #D4AF37; letter-spacing: 2px; text-transform: uppercase;}
.cred-rol { font-size: 0.9rem; color: #A0A0A0; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 4px; font-weight: 400;}
.cred-nivel { font-family: 'Manrope', sans-serif; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; color: #E5E4E2; border-top: 1px solid #333; padding-top: 15px;}

/* ---> NUEVO: MATRIZ DE DESVIACIONES Y ROSTER <--- */
.roster-wrapper { display: flex; flex-direction: column; gap: 8px; margin-top: 20px;}
.roster-row { display: flex; background: #050505; border: 1px solid #111; border-radius: 4px; overflow: hidden; align-items: stretch;}
.roster-emp { width: 150px; min-width: 150px; padding: 15px 10px; background: #0A0A0A; display: flex; align-items: center; justify-content: flex-start; font-family: 'Cinzel', serif; font-size: 0.85rem; font-weight: bold; color: #D4AF37; border-right: 1px solid #222;}
.roster-days { display: flex; flex: 1; overflow-x: auto;}
.roster-cell { flex: 1; min-width: 130px; padding: 12px 10px; border-right: 1px solid #0f0f0f; display: flex; flex-direction: column; justify-content: center;}
.roster-cell:last-child { border-right: none; }

/* STEALTH MODE (Todo Perfecto) */
.c-ok { background: #030303; }
.c-ok .main-txt { color: #10B981; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 5px; opacity: 0.5;}

/* HIGHLIGHTING (Anomalías) */
.c-falta { background: rgba(239, 68, 68, 0.05); border-bottom: 2px solid #EF4444;}
.c-falta .sub-txt { color: #737373; font-size: 0.65rem; margin-bottom: 3px; font-family: 'Manrope', sans-serif;}
.c-falta .main-txt { color: #EF4444; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;}

.c-tarde { background: rgba(212, 175, 55, 0.05); border-bottom: 2px solid #D4AF37;}
.c-tarde .sub-txt { color: #737373; font-size: 0.65rem; margin-bottom: 3px; font-family: 'Manrope', sans-serif;}
.c-tarde .main-txt { color: #D4AF37; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;}

.c-cambio { background: rgba(212, 175, 55, 0.02); border-bottom: 2px dashed #D4AF37;}
.c-cambio .sub-txt { color: #737373; font-size: 0.65rem; margin-bottom: 3px; font-family: 'Manrope', sans-serif;}
.c-cambio .main-txt { color: #E5E4E2; font-size: 0.75rem; font-weight: bold;}

.c-extra { background: rgba(139, 92, 246, 0.05); border-bottom: 2px solid #8B5CF6;}
.c-extra .sub-txt { color: #A0A0A0; font-size: 0.65rem; margin-bottom: 3px; font-family: 'Manrope', sans-serif;}
.c-extra .main-txt { color: #8B5CF6; font-size: 0.75rem; font-weight: bold;}

.c-pend { background: #0A0A0A;}
.c-pend .main-txt { color: #444; font-size: 0.7rem; font-weight: 500;}

.c-libre { background: #050505;}
.c-libre .main-txt { color: #222; font-size: 0.7rem; font-style: italic;}

/* Escáner Modal de Conflictos */
.conflict-box { background: rgba(239, 68, 68, 0.05); border: 1px solid #EF4444; border-radius: 4px; padding: 20px; margin-bottom: 20px; border-left: 4px solid #EF4444;}
.conflict-title { color: #EF4444; font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; letter-spacing: 1px;}
.conflict-item { color: #E5E4E2; font-size: 0.9rem; margin-bottom: 5px; font-family: 'Manrope', sans-serif; display: flex; align-items: center; gap: 8px;}

/* ---> TABLAS DE DATOS Y BLOQUEO <--- */
[data-testid="stDataFrame"] { background: #0a0a0a; border: 1px solid #333; border-radius: 4px;}
.bloqueo-pantalla { padding: 60px 40px; background: #050505; border: 1px solid #EF4444; text-align: center; margin-top: 50px; border-radius: 4px;}
.bloqueo-titulo { font-family: 'Cinzel', serif; font-size: 3rem; color: #EF4444; letter-spacing: 5px; margin-bottom: 20px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚡ FUNCIÓN MAESTRA DE RECARGA Y LIMPIEZA
# ==========================================
def recargar_app():
    st.cache_data.clear()
    st.rerun()

# ==========================================
# ☁️ 1. CONEXIÓN A SUPABASE (LA NUBE)
# ==========================================
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Error: No se encontraron los secretos de Supabase en Streamlit.")
        st.stop()

supabase = init_connection()

def show_db_error(e, context="base de datos"):
    error_details = str(e)
    if hasattr(e, 'args') and len(e.args) > 0 and isinstance(e.args[0], dict):
        error_details = e.args[0].get('message', str(e))
        hint = e.args[0].get('hint', '')
        if hint: error_details += f" | Pista: {hint}"
    st.error(f"Error de Supabase al guardar en {context}: {error_details}")

@st.cache_data(ttl=60, show_spinner=False)
def get_all_settings():
    try:
        res = supabase.table('app_data').select('id, data').execute()
        if res.data:
            return {row['id']: row['data'] for row in res.data}
        return {}
    except Exception as e:
        return None 

def load_json(key_name, default_data):
    settings = get_all_settings()
    if settings is None:
        st.error("Aguardá un momento. Reconectando de forma segura con la base de datos...")
        st.stop()
        
    if key_name in settings:
        data = settings[key_name]
        if isinstance(data, dict) and isinstance(default_data, dict) and key_name in ["config", "owner_config"]:
            for k, v in default_data.items():
                if k not in data:
                    data[k] = v
        return data
    else:
        try:
            supabase.table('app_data').insert({'id': key_name, 'data': default_data}).execute()
            get_all_settings.clear()
            return default_data
        except:
            return default_data

def save_json(key_name, data):
    try:
        settings = get_all_settings()
        if settings is None:
            st.error("No se pudo guardar ahora mismo por un error de conexión.")
            return
        if key_name in settings:
            supabase.table('app_data').update({'data': data}).eq('id', key_name).execute()
        else:
            supabase.table('app_data').insert({'id': key_name, 'data': data}).execute()
        get_all_settings.clear()
    except Exception as e:
        show_db_error(e, f"guardando '{key_name}'")

@st.cache_data(ttl=15, show_spinner=False)
def load_df(table_name):
    try:
        res = supabase.table(table_name).select('*').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df.columns = df.columns.str.lower()
            df = df.loc[:, ~df.columns.duplicated()]
            if table_name == "asistencia":
                df = df.rename(columns={"empleado": "Empleado", "fecha": "Fecha", "hora": "Hora", "sucursal": "Sucursal", "turno": "Turno", "tipo": "Tipo", "estado": "Estado", "distancia_m": "Distancia_m", "nota": "Nota"})
            elif table_name == "tareas_log":
                df = df.rename(columns={"fecha": "Fecha", "hora": "Hora", "empleado": "Empleado", "tarea": "Tarea", "puntos": "Puntos", "estado": "Estado"})
            return df.reset_index(drop=True)
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=15, show_spinner=False)
def load_table_list(table_name):
    try:
        res = supabase.table(table_name).select('*').execute()
        if not res.data:
            return []
        
        mapped_data = []
        for row in res.data:
            r = row.copy()
            def map_key(target_key, possible_lower):
                if possible_lower in r and possible_lower != target_key:
                    r[target_key] = r.pop(possible_lower)
                    
            if table_name == "sueldos_historico":
                map_key("Empleado", "empleado")
                map_key("Fecha_Desde", "fecha_desde")
                map_key("Fecha_Hasta", "fecha_hasta")
                map_key("Valor_Hora", "valor_hora")
            elif table_name == "cierres_caja":
                map_key("Fecha", "fecha")
                map_key("Hora", "hora")
                map_key("Cajero", "cajero")
                map_key("Sucursal", "sucursal")
                map_key("Turno", "turno")
                map_key("Efectivo", "efectivo")
                map_key("Tarjeta", "tarjeta")
                map_key("Transferencia", "transferencia")
                map_key("Total_Ventas", "total_ventas")
                map_key("Nota", "nota")
            elif table_name == "salidas_pendientes":
                map_key("Fecha", "fecha")
                map_key("Hora", "hora")
                map_key("Empleado", "empleado")
                map_key("Sucursal", "sucursal")
                map_key("Turno", "turno")
                map_key("Nota", "nota")
                map_key("Autor", "autor")
            elif table_name == "correcciones_pendientes":
                map_key("Empleado", "empleado")
                map_key("Fecha", "fecha")
                map_key("Hora_Real", "hora_real")
                map_key("Sucursal", "sucursal")
                map_key("Turno", "turno")
                map_key("Motivo", "motivo")
            elif table_name == "ajustes_puntos":
                map_key("Fecha", "fecha")
                map_key("Empleado", "empleado")
                map_key("Puntos", "puntos")
                map_key("Motivo", "motivo")
                map_key("Autor", "autor")
                map_key("Estado", "estado")
            elif table_name == "puntos_cajero_pendientes":
                map_key("Fecha", "fecha")
                map_key("Hora", "hora")
                map_key("Emisor", "emisor")
                map_key("Compañero", "compañero")
                map_key("Puntos_Sugeridos", "puntos_sugeridos")
                map_key("Motivo", "motivo")
                map_key("Estado", "estado")
            elif table_name == "reportes":
                map_key("Fecha", "fecha")
                map_key("Hora", "hora")
                map_key("Emisor", "emisor")
                map_key("Tipo", "tipo")
                map_key("Implicado", "implicado")
                map_key("Detalle", "detalle")
                map_key("Estado", "estado")
            elif table_name == "intentos_seguridad":
                map_key("Fecha", "fecha")
                map_key("Hora", "hora")
                map_key("Usuario", "usuario")
                map_key("Clave", "clave")
                map_key("Resultado", "resultado")
            
            mapped_data.append(r)
        return mapped_data
    except:
        return []

def insert_row(table_name, row_dict):
    try:
        row_dict_lower = {k.lower(): v for k, v in row_dict.items()}
        supabase.table(table_name).insert(row_dict_lower).execute()
        return True
    except Exception as e:
        show_db_error(e, f"la tabla '{table_name}'")
        return False

# ==========================================
# 2. CARGA DE DATOS CENTRALIZADA DESDE TABLAS SQL
# ==========================================
zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%I:%M:%S %p")

config_defecto = {
    "titulo_portal": "Portal Corporativo",
    "admin_password": "1234", "tolerancia_minutos": 10,
    "mensaje_llegada_tarde": "Llegada fuera del margen de tolerancia.", "verificar_gps": True,
    "verificar_wifi": False, "salida_estricta": False, "exigir_salida_manual": False, "autoregistro": False,
    "ip_wifi_oficial": "", "radio_metros": 150, "fecha_inicio_puntos": ahora.date().replace(day=1).strftime("%Y-%m-%d"),
    "desc_tarde": True, "desc_temp": True, "perdonar_tolerancia": True,
    "mostrar_horas_empleado": False, "dia_inicio_semana": "Lunes", "fichaje_estricto_plan": False,
    "recompensa_auditoria_cajero": 10,
    "rankings_muro": [{"nombre": "Ranking Global", "competidores": ["Todos"], "espectadores": ["Todos"], "mostrar_puntos": True}],
    "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0, "Olvido Fichaje": -10}
}
config_app = load_json("config", config_defecto)

def get_bool_config(key, default=True):
    val = config_app.get(key, default)
    if isinstance(val, str): return val.lower() in ['true', '1', 'yes', 't']
    return bool(val)

owner_config_defecto = {
    "estado_licencia": "Activo", "plan_pago": "Mensual", "fecha_vencimiento": "2030-12-31",
    "mensaje_bloqueo": "SISTEMA SUSPENDIDO TEMPORALMENTE.\n\nPor favor, comuníquese con el proveedor del software para regularizar el estado de su cuenta.",
    "mostrar_membresia": False, "dias_aviso": 5,
    "mensaje_aviso": "Tu suscripción está próxima a vencer. Por favor, renová tu plan para evitar interrupciones en el servicio.",
    "empresa_nombre": "SyncroRetail Solutions",
    "quienes_somos": "Nacimos con una misión clara: revolucionar la gestión del personal...",
    "contactos": "Oficina Central: Salta Capital\nSoporte: soporte@syncroretail.com",
    "nombre_tab_dueno": "Owner"
}
owner_config = load_json("owner_config", owner_config_defecto)

# ---> EXTRACCIÓN RELACIONAL SQL <---
roles_data = load_table_list("roles_disponibles")
lista_roles_disponibles = [r["rol"] for r in roles_data] if roles_data else ["Vendedor", "Cajero", "Encargado", "Depósito", "Planchero", "Otro"]

emp_data = load_table_list("empleados")
lista_empleados = [r["nombre"] for r in emp_data] if emp_data else []
roles_empleados = {r["nombre"]: r["rol"] for r in emp_data} if emp_data else {}
dispositivos_vinculados = {r["nombre"]: r["dispositivo_id"] for r in emp_data if r.get("dispositivo_id")} if emp_data else {}

tr_data = load_table_list("tareas_roles")
tareas_roles = {}
for r in tr_data:
    tareas_roles.setdefault(r["rol"], []).append({"id": r.get("id"), "tarea": r["tarea"], "puntos": r["puntos"]})

ti_data = load_table_list("tareas_individuales")
tareas_individuales = {}
for r in ti_data:
    tareas_individuales.setdefault(r["empleado"], []).append({"id": r.get("id"), "tarea": r["tarea"], "puntos": r["puntos"]})

locales_data = load_table_list("locales")
lista_locales = {r["nombre"]: {"lat": float(r["lat"]), "lon": float(r["lon"]), "ip": str(r.get("ip", ""))} for r in locales_data} if locales_data else {}

turnos_data = load_table_list("turnos")
lista_turnos = {r["nombre"]: {"ingreso": str(r["ingreso"]), "salida": str(r["salida"])} for r in turnos_data} if turnos_data else {}

lista_mensajes = load_table_list("mensajes")
alertas_ingreso = load_table_list("alertas_ingreso")
lista_intentos = load_table_list("intentos_seguridad")
lista_puntos = load_table_list("ajustes_puntos")
reportes_log = load_table_list("reportes")
salidas_pendientes = load_table_list("salidas_pendientes")
correcciones_pendientes = load_table_list("correcciones_pendientes")
sueldos_historico = load_table_list("sueldos_historico")
cierres_caja = load_table_list("cierres_caja")
puntos_cajero_pendientes = load_table_list("puntos_cajero_pendientes")

plan_data = load_table_list("planificacion_turnos")
planificacion_turnos = {}
for r in plan_data:
    f = r.get("fecha"); s = r.get("sucursal"); t = r.get("turno"); e = r.get("empleado")
    if f and s and t and e:
        if f not in planificacion_turnos: planificacion_turnos[f] = {}
        if s not in planificacion_turnos[f]: planificacion_turnos[f][s] = {}
        if t not in planificacion_turnos[f][s]: planificacion_turnos[f][s][t] = []
        planificacion_turnos[f][s][t].append(e)

ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida Automática", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A", "Retiro Temprano", "Salida (Cambio Local)"]

def procesar_rango_fechas(rango):
    if isinstance(rango, tuple) or isinstance(rango, list):
        if len(rango) == 2: return rango[0], rango[1]
        elif len(rango) == 1: return rango[0], rango[0]
    return rango, rango

def get_fechas_filtro(opcion, custom_rango=None):
    hoy = ahora.date()
    if opcion == "Hoy": return hoy, hoy
    elif opcion == "Esta Semana": 
        inicio_semana_int = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}.get(config_app.get("dia_inicio_semana", "Lunes"), 0)
        dias_desde_inicio = (hoy.weekday() - inicio_semana_int) % 7
        return hoy - datetime.timedelta(days=dias_desde_inicio), hoy
    elif opcion == "Este Mes": return hoy.replace(day=1), hoy
    elif opcion == "Mes Anterior":
        u_dia = hoy.replace(day=1) - datetime.timedelta(days=1)
        return u_dia.replace(day=1), u_dia
    elif opcion == "Todo el Historial": return datetime.date(2020, 1, 1), hoy
    elif opcion == "Personalizado": return procesar_rango_fechas(custom_rango)
    return hoy, hoy

def calcular_nivel(puntos):
    if puntos < 80: return "Observación"
    elif puntos < 100: return "Bronce"
    elif puntos < 130: return "Plata"
    elif puntos < 160: return "Oro"
    elif puntos < 200: return "Platino"
    else: return "Élite"

def formato_horas_texto(h_decimal):
    try:
        h_decimal = float(h_decimal)
        horas = int(h_decimal)
        minutos = int(round((h_decimal - horas) * 60))
        if minutos == 60:
            horas += 1
            minutos = 0
        return f"{horas}:{minutos:02d}h"
    except:
        return str(h_decimal)

def generate_html_download(df, filename, label):
    csv_b64 = base64.b64encode(df.to_csv(index=False).encode('utf-8')).decode()
    return f'<a href="data:file/csv;base64,{csv_b64}" download="{filename}" style="display: block; width: 100%; text-align: center; padding: 0.8rem 1rem; background-color: transparent; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 0; text-decoration: none; font-family: \'Cinzel\', serif; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-top: 15px; transition: all 0.3s ease;">{label}</a>'

# ==========================================
# 3. IDENTIFICACIÓN Y MODO INCÓGNITO (ESPÍA)
# ==========================================
empleado_en_celu = None
es_incognito = st.session_state.get('incognito', False)
usuario_incognito = st.session_state.get('incognito_user', None)

if es_incognito and usuario_incognito in lista_empleados:
    empleado_en_celu = usuario_incognito
elif 'device_id' in st.session_state:
    for emp, dev in dispositivos_vinculados.items():
        if dev == st.session_state['device_id']:
            empleado_en_celu = emp
            break

# ==========================================
# LÓGICA CORE DE MOTOR DE TIEMPO (FILTRO DINÁMICO)
# ==========================================
turnos_disponibles_ahora = []
nombres_turnos_todos = list(lista_turnos.keys())

for t_name, t_data in lista_turnos.items():
    try:
        h_in_obj = datetime.datetime.strptime(t_data["ingreso"], "%I:%M %p").time()
        h_out_obj = datetime.datetime.strptime(t_data["salida"], "%I:%M %p").time()
        
        dt_in = datetime.datetime.combine(ahora.date(), h_in_obj).replace(tzinfo=zona_arg)
        dt_out = datetime.datetime.combine(ahora.date(), h_out_obj).replace(tzinfo=zona_arg)
        
        if dt_out < dt_in:
            dt_out += datetime.timedelta(days=1)
        
        dt_habilitacion = dt_in - datetime.timedelta(minutes=30)
        if dt_habilitacion <= ahora <= dt_out:
            turnos_disponibles_ahora.append(t_name)
    except Exception as e:
        turnos_disponibles_ahora.append(t_name)

# ==========================================
# CERRADO AUTOMÁTICO DE TURNOS VENCIDOS
# ==========================================
df_punt_check = load_df("asistencia")
if not df_punt_check.empty:
    df_punt_check['Timestamp'] = pd.to_datetime(df_punt_check['Fecha'].astype(str) + ' ' + df_punt_check['Hora'].astype(str), errors='coerce')
    df_punt_check = df_punt_check.dropna(subset=['Timestamp']).sort_values(by="Timestamp").reset_index(drop=True)
    
    for emp_check in lista_empleados:
        df_e_check = df_punt_check[df_punt_check["Empleado"] == emp_check].reset_index(drop=True)
        if not df_e_check.empty:
            ultimo_fichaje = df_e_check.iloc[-1]
            tipo_uf = ultimo_fichaje["Tipo"]
            if isinstance(tipo_uf, pd.Series):
                tipo_uf = tipo_uf.iloc[0]
            if tipo_uf == "Entrada":
                turno_activo = str(ultimo_fichaje["Turno"])
                if turno_activo in lista_turnos:
                    try:
                        hora_salida_str = lista_turnos[turno_activo]["salida"]
                        hora_salida_obj = datetime.datetime.strptime(hora_salida_str, "%I:%M %p").time()
                        
                        fecha_entrada = pd.to_datetime(ultimo_fichaje["Fecha"]).date()
                        dt_salida = datetime.datetime.combine(fecha_entrada, hora_salida_obj).replace(tzinfo=zona_arg)
                        
                        if ahora > dt_salida:
                            insert_row("asistencia", {
                                "fecha": str(fecha_entrada),
                                "hora": hora_salida_obj.strftime("%I:%M:%S %p"),
                                "empleado": str(emp_check),
                                "sucursal": str(ultimo_fichaje["Sucursal"]),
                                "turno": turno_activo,
                                "tipo": "Salida",
                                "estado": "Salida Automática",
                                "distancia_m": 0.0,
                                "nota": "Cierre automático del sistema."
                            })
                    except Exception as e:
                        pass

# ==========================================
# 4. NAVEGACIÓN FRONTAL
# ==========================================
titulo_app_personalizado = config_app.get("titulo_portal", "PORTAL CORPORATIVO")
nombre_tab_dueno = owner_config.get("nombre_tab_dueno", "OWNER")

st.markdown(f'<div class="main-title" style="text-align: center;">{titulo_app_personalizado}</div>', unsafe_allow_html=True)
pestaña = st.selectbox("NAVEGACIÓN", ["Portal del Empleado", "Panel de Gerencia", nombre_tab_dueno], label_visibility="collapsed")
st.write("---")

# ==========================================
# 🚨 SISTEMA ANTIFRAUDE (KILL SWITCH Y VENCIMIENTO)
# ==========================================
licencia_vencida = False
try:
    if ahora.date() > datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date():
        licencia_vencida = True
except: pass

if pestaña in ["Portal del Empleado", "Panel de Gerencia"]:
    if owner_config.get("estado_licencia") == "Suspendido" or licencia_vencida:
        msg_motivo = owner_config.get("mensaje_bloqueo") if owner_config.get("estado_licencia") == "Suspendido" else "LICENCIA VENCIDA. Contacte a soporte."
        st.markdown(f"""
        <div class="bloqueo-pantalla">
        <div class="bloqueo-titulo">SISTEMA BLOQUEADO</div>
        <p style="font-size: 1.2rem; color: #E5E4E2; letter-spacing: 1px;">{msg_motivo}</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
# ==========================================
# 5. INTERFAZ: PORTAL DEL EMPLEADO
# ==========================================
if pestaña == "Portal del Empleado":
    if es_incognito and usuario_incognito in lista_empleados:
        device_id = "incognito_device"
        st.warning(f"MODO INCÓGNITO: Visualizando como {usuario_incognito}. Los registros impactarán en la base real.")
        if st.button("SALIR DEL MODO INCÓGNITO", key="btn_exit_inc_emp"):
            st.session_state['incognito'] = False
            st.session_state['incognito_user'] = None
            recargar_app()
    else:
        if 'device_id' not in st.session_state:
            js_get_device = "(function() { let id = localStorage.getItem('tienda_app_device_id'); if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); } return id; })();"
            did = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")
            if did:
                st.session_state['device_id'] = did
                recargar_app()
        device_id = st.session_state.get('device_id')

    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"COMUNICADO INSTITUCIONAL: {config_app['mensaje_dia']}")

    if not device_id:
        st.info("Autenticando terminal...")
    else:
        if empleado_en_celu:
            if 'fichaje_exitoso' in st.session_state:
                st.success(st.session_state['fichaje_exitoso'])
                del st.session_state['fichaje_exitoso']

            puntos_actuales = config_app["reglas_puntos"]["base"]
            f_inicio_str = config_app.get("fecha_inicio_puntos", ahora.date().replace(day=1).strftime("%Y-%m-%d"))
            d_inicio_puntos = datetime.datetime.strptime(f_inicio_str, "%Y-%m-%d").date()
            df_punt = load_df("asistencia")
            if not df_punt.empty:
                df_punt = df_punt.reset_index(drop=True)
            
            if not df_punt.empty:
                df_punt['F_Obj'] = pd.to_datetime(df_punt['Fecha'], errors='coerce').dt.date
                df_e = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt['F_Obj'] >= d_inicio_puntos)].reset_index(drop=True)
                puntos_actuales += (len(df_e[df_e["Estado"] == "Tarde"]) * config_app["reglas_puntos"]["Tarde"]) + (len(df_e[df_e["Tipo"] == "Ausente"]) * config_app["reglas_puntos"]["Ausente"])
                
            df_tl = load_df("tareas_log")
            if not df_tl.empty:
                df_tl = df_tl.reset_index(drop=True)
                df_tl['F_Obj'] = pd.to_datetime(df_tl['Fecha'], errors='coerce').dt.date
                puntos_actuales += pd.to_numeric(df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Estado"] == "Aprobada") & (df_tl['F_Obj'] >= d_inicio_puntos)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
                
            puntos_actuales += sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == empleado_en_celu and p.get('Estado') == "Aprobada" and datetime.datetime.strptime(p.get('Fecha', p.get('fecha')), "%Y-%m-%d").date() >= d_inicio_puntos])
            
            df_hoy = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["Fecha"] == fecha_hoy)].copy().reset_index(drop=True) if not df_punt.empty else pd.DataFrame()
            estado_laboral = "Fuera"
            datos_turno_activo = {}
            
            if not df_hoy.empty:
                if 'id' in df_hoy.columns:
                    df_hoy['id_num'] = pd.to_numeric(df_hoy['id'], errors='coerce')
                    df_hoy = df_hoy.sort_values(by="id_num").reset_index(drop=True)
                else:
                    df_hoy = df_hoy.reset_index(drop=True)
                ultimo_reg = df_hoy.iloc[-1]
                tipo_ur = ultimo_reg["Tipo"]
                if isinstance(tipo_ur, pd.Series):
                    tipo_ur = tipo_ur.iloc[0]
                if tipo_ur == "Entrada":
                    estado_laboral = "Adentro"
                    try: dist_guardada = float(ultimo_reg.get("Distancia_m", 0.0))
                    except: dist_guardada = 0.0
                    datos_turno_activo = {"Sucursal": str(ultimo_reg["Sucursal"]), "Turno": str(ultimo_reg["Turno"]), "Distancia_m": dist_guardada}
                    
            rol_empleado = roles_empleados.get(empleado_en_celu, 'Staff')
            st.markdown(f"<div class='credencial'><p class='cred-nombre'>{empleado_en_celu}</p><p class='cred-rol'>{rol_empleado}</p><div class='cred-nivel'>STATUS: {calcular_nivel(puntos_actuales)} &nbsp;|&nbsp; {puntos_actuales} PTS</div></div>", unsafe_allow_html=True)
            
            with st.expander("SMART CHECK-IN", expanded=True):
                st.markdown("### RADAR DE POSICIÓN")
                local_detectado = None
                distancia_real = 0.0
                metodo_det = ""
                client_ip_local = None
                
                if get_bool_config("verificar_wifi", False):
                    if 'client_ip' not in st.session_state:
                        js_get_ip = "fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')"
                        cip = streamlit_js_eval(js_expressions=js_get_ip, want_output=True, key="get_client_ip")
                        if cip: st.session_state['client_ip'] = cip
                    client_ip_local = st.session_state.get('client_ip')
                    
                ubicacion = None
                if get_bool_config("verificar_gps", True):
                    ubicacion = get_geolocation()
                    
                if get_bool_config("verificar_wifi", False) and client_ip_local and client_ip_local != 'Error':
                    for loc, d_loc in lista_locales.items():
                        if d_loc.get("ip", "").strip() == client_ip_local:
                            local_detectado = loc
                            metodo_det = "Red Oficial"
                            break
                            
                if not local_detectado and get_bool_config("verificar_gps", True):
                    if ubicacion and 'coords' in ubicacion:
                        coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                        for loc, d_loc in lista_locales.items():
                            coord_local = (d_loc["lat"], d_loc["lon"])
                            dist = geodesic(coord_usuario, coord_local).meters
                            if dist <= int(config_app.get("radio_metros", 50)):
                                local_detectado = loc
                                distancia_real = float(dist)
                                metodo_det = f"Satelital ({dist:.1f} m)"
                                break
                                
                if estado_laboral == "Fuera":
                    if local_detectado:
                        turno_planificado = "Libre"
                        dia_plan = planificacion_turnos.get(fecha_hoy, {})
                        loc_plan_actual = dia_plan.get(local_detectado, {})
                        if isinstance(loc_plan_actual, dict):
                            for t_name, emps_asignados in loc_plan_actual.items():
                                if isinstance(emps_asignados, list) and empleado_en_celu in emps_asignados:
                                    turno_planificado = t_name
                                    break
                                    
                        st.markdown(f"<div class='task-box'>SUCURSAL DETECTADA: <b>{local_detectado}</b><br><small>Verificado por: {metodo_det}</small></div>", unsafe_allow_html=True)
                        
                        mostrar_boton_entrada = False
                        turno_seleccionado = None
                        
                        if get_bool_config("fichaje_estricto_plan", False):
                            if turno_planificado == "Libre":
                                st.error(f"Ingreso bloqueado. No posee turnos asignados en {local_detectado}.")
                            else:
                                st.markdown(f"TURNO ASIGNADO: **{turno_planificado}**")
                                if turno_planificado in turnos_disponibles_ahora:
                                    turno_seleccionado = turno_planificado
                                    mostrar_boton_entrada = True
                                else:
                                    try:
                                        h_in_str = lista_turnos[turno_planificado]["ingreso"]
                                        h_out_str = lista_turnos[turno_planificado]["salida"]
                                        st.warning(f"Su turno ({turno_planificado}) es de {h_in_str} a {h_out_str}. No está activo.")
                                    except:
                                        st.warning("Fuera del horario de turno asignado.")
                                        
                        else:
                            if not turnos_disponibles_ahora:
                                st.error("No hay turnos programados en este horario.")
                            else:
                                idx_sel = turnos_disponibles_ahora.index(turno_planificado) if turno_planificado in turnos_disponibles_ahora else 0
                                turno_seleccionado = st.selectbox("SELECCIONAR TURNO:", turnos_disponibles_ahora, index=idx_sel, key="sel_turno_in")
                                mostrar_boton_entrada = True
                                
                                if turno_planificado != "Libre" and turno_planificado != turno_seleccionado:
                                    st.info(f"Nota: Su planificación original indicaba el turno {turno_planificado}.")

                        if mostrar_boton_entrada and turno_seleccionado:
                            nota_empleado = st.text_input("NOVEDADES (OPCIONAL):", placeholder="Escriba aquí...", key="nota_in")
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            if st.button("REGISTRAR ENTRADA", use_container_width=True, type="primary"):
                                estado_llegada = "A tiempo"
                                try:
                                    hora_t_str = lista_turnos[turno_seleccionado]["ingreso"]
                                    hora_t_obj = datetime.datetime.strptime(hora_t_str, "%I:%M %p").time()
                                    dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                    if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))):
                                        estado_llegada = "Tarde"
                                except: pass
                                
                                exito = insert_row("asistencia", {"fecha": str(fecha_hoy), "hora": str(hora_hoy), "empleado": str(empleado_en_celu), "sucursal": str(local_detectado), "turno": str(turno_seleccionado), "tipo": "Entrada", "estado": str(estado_llegada), "distancia_m": round(float(distancia_real), 1), "nota": str(nota_empleado)})
                                
                                if exito:
                                    msg_final = f"Entrada registrada a las {hora_hoy}."
                                    if estado_llegada == "Tarde": msg_final += f" | {config_app.get('mensaje_llegada_tarde')}"
                                    for a in alertas_ingreso:
                                        if a['destinatario'] in ['Todos', empleado_en_celu, rol_empleado]:
                                            msg_final += f" | AVISO: {a['texto']}"
                                    st.session_state['fichaje_exitoso'] = msg_final
                                    recargar_app()
                    else:
                        if get_bool_config("verificar_gps", True) and (not ubicacion or 'coords' not in ubicacion):
                            st.info("Detectando satélite... Permita acceso al GPS.")
                        else:
                            st.error("Fuera de rango de las sucursales autorizadas.")
                            
                elif estado_laboral == "Adentro":
                    local_actual = datos_turno_activo.get("Sucursal", "N/A")
                    turno_actual = datos_turno_activo.get("Turno", "N/A")
                    
                    if local_detectado and local_detectado != local_actual:
                        st.warning(f"CAMBIO DE LOCACIÓN: Fichado en {local_actual}, detectado en {local_detectado}.")
                        nuevo_turno_planificado = "Libre"
                        dia_plan = planificacion_turnos.get(fecha_hoy, {})
                        loc_plan_actual = dia_plan.get(local_detectado, {})
                        if isinstance(loc_plan_actual, dict):
                            for t_name, emps_asignados in loc_plan_actual.items():
                                if isinstance(emps_asignados, list) and empleado_en_celu in emps_asignados:
                                    nuevo_turno_planificado = t_name
                                    break
                                    
                        mostrar_btn_cambio = False
                        turno_seleccionado = None
                        
                        if get_bool_config("fichaje_estricto_plan", False):
                            if nuevo_turno_planificado == "Libre":
                                st.error(f"Ingreso bloqueado. Sin turnos en {local_detectado}.")
                            else:
                                if nuevo_turno_planificado in turnos_disponibles_ahora:
                                    turno_seleccionado = nuevo_turno_planificado
                                    mostrar_btn_cambio = True
                                else:
                                    st.warning(f"El turno {nuevo_turno_planificado} no está activo.")
                        else:
                            if not turnos_disponibles_ahora:
                                st.error("No hay turnos disponibles en esta sucursal.")
                            else:
                                idx_sel = turnos_disponibles_ahora.index(nuevo_turno_planificado) if nuevo_turno_planificado in turnos_disponibles_ahora else 0
                                turno_seleccionado = st.selectbox("TURNO A REGISTRAR:", turnos_disponibles_ahora, index=idx_sel, key="sel_turno_cambio")
                                mostrar_btn_cambio = True

                        if mostrar_btn_cambio and turno_seleccionado:
                            if st.button("CERRAR ANTERIOR E INGRESAR AQUÍ", use_container_width=True):
                                insert_row("asistencia", {"fecha": str(fecha_hoy), "hora": str(hora_hoy), "empleado": str(empleado_en_celu), "sucursal": str(local_actual), "turno": str(turno_actual), "tipo": "Salida", "estado": "Salida (Cambio Local)", "distancia_m": 0.0, "nota": "Cierre por cambio."})
                                
                                estado_llegada = "A tiempo"
                                if turno_seleccionado in lista_turnos:
                                    try:
                                        hora_t_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado]["ingreso"], "%I:%M %p").time()
                                        dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                        estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                                    except: pass
                                
                                exito = insert_row("asistencia", {"fecha": str(fecha_hoy), "hora": str(hora_hoy), "empleado": str(empleado_en_celu), "sucursal": str(local_detectado), "turno": str(turno_seleccionado), "tipo": "Entrada", "estado": str(estado_llegada), "distancia_m": round(float(distancia_real), 1), "nota": "Cambio de local."})
                                
                                if exito:
                                    st.session_state['fichaje_exitoso'] = "Transferencia de sucursal exitosa."
                                    recargar_app()
                    else:
                        st.markdown("### FINALIZAR JORNADA")
                        st.success(f"OPERATIVO EN: {local_actual} ({turno_actual}).")
                        
                        if not get_bool_config("exigir_salida_manual", False):
                            st.info("Salida automática activa. Cierre procesado por el sistema al finalizar horario.")
                        else:
                            puede_salir = True
                            distancia_salida = datos_turno_activo.get("Distancia_m", 0.0)
                            if get_bool_config("salida_estricta", False) and local_actual in lista_locales:
                                st.markdown("VERIFICACIÓN DE SEGURIDAD REQUERIDA:")
                                ubicacion_sal = get_geolocation() if get_bool_config("verificar_gps", True) else None
                                en_rango_sal = True
                                wifi_aprobado_sal = True
                                radio_permitido = int(config_app.get("radio_metros", 50))
                                
                                if get_bool_config("verificar_gps", True):
                                    if ubicacion_sal and 'coords' in ubicacion_sal:
                                        coord_us = (ubicacion_sal['coords']['latitude'], ubicacion_sal['coords']['longitude'])
                                        coord_loc = (lista_locales[local_actual]["lat"], lista_locales[local_actual]["lon"])
                                        distancia_salida = geodesic(coord_us, coord_loc).meters
                                        if distancia_salida <= radio_permitido:
                                            st.markdown(f"<div class='validation-box'>SEÑAL GPS: APROBADA ({distancia_salida:.1f} m)</div>", unsafe_allow_html=True)
                                        else:
                                            en_rango_sal = False
                                            st.markdown(f"<div class='validation-box' style='border: 1px solid #991B1B;'>SEÑAL GPS: FUERA DE RANGO. Requerido para salir.</div>", unsafe_allow_html=True)
                                    else:
                                        en_rango_sal = False
                                        st.markdown("<div class='validation-box'>SEÑAL GPS: DETECTANDO...</div>", unsafe_allow_html=True)
                                        
                                client_ip_local = None
                                if get_bool_config("verificar_wifi", False):
                                    if 'client_ip' not in st.session_state:
                                        js_get_ip = "fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')"
                                        cip = streamlit_js_eval(js_expressions=js_get_ip, want_output=True, key="get_client_ip")
                                        if cip: st.session_state['client_ip'] = cip
                                    client_ip_local = st.session_state.get('client_ip')
                                    ip_tienda = lista_locales[local_actual].get("ip", "").strip()
                                    if not ip_tienda: wifi_aprobado_sal = False
                                    elif client_ip_local and client_ip_local == ip_tienda: st.markdown("<div class='validation-box'>RED OFICIAL: APROBADA</div>", unsafe_allow_html=True)
                                    else: wifi_aprobado_sal = False
                                    
                                if get_bool_config("verificar_wifi", False) and not wifi_aprobado_sal: puede_salir = False
                                if get_bool_config("verificar_gps", True) and not en_rango_sal: puede_salir = False
                                
                            if puede_salir:
                                nota_empleado = st.text_input("NOVEDAD AL SALIR (OPCIONAL):", key="nota_out")
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("REGISTRAR SALIDA", use_container_width=True, type="primary"):
                                    exito = insert_row("asistencia", {"fecha": str(fecha_hoy), "hora": str(hora_hoy), "empleado": str(empleado_en_celu), "sucursal": str(local_actual), "turno": str(turno_actual), "tipo": "Salida", "estado": "Salida", "distancia_m": round(float(distancia_salida), 1), "nota": str(nota_empleado)})
                                    if exito:
                                        st.session_state['fichaje_exitoso'] = "Salida registrada."
                                        recargar_app()
                            else:
                                st.error("Sistema estricto: Debe encontrarse físicamente en la sucursal para finalizar.")

            # --- CORRECCIÓN OLVIDO DE FICHAJE ---
            st.markdown("---")
            with st.expander("SOLICITUD DE CORRECCIÓN (OLVIDO)", expanded=False):
                st.markdown("""
                <div class='alert-box' style='background-color: #171105; border-color: #D4AF37; color: #D4AF37;'>
                <b>AVISO:</b> Enviar corrección restará puntos de ranking por falta de atención, pero resguardará las horas operativas. Limitado a uno por día.
                </div>
                """, unsafe_allow_html=True)
                
                ya_pidio = False
                for cp in correcciones_pendientes:
                    if cp.get('Empleado', cp.get('empleado')) == empleado_en_celu and cp.get('Fecha', cp.get('fecha')) == str(fecha_hoy):
                        ya_pidio = True
                        break
                        
                if ya_pidio:
                    st.info("Solicitud diaria ya enviada a Gerencia.")
                else:
                    with st.form("form_olvido_ingreso"):
                        c_olv1, c_olv2 = st.columns(2)
                        suc_olv = c_olv1.selectbox("SUCURSAL:", ["Seleccionar..."] + list(lista_locales.keys()), key="olv_suc")
                        turno_olv = c_olv2.selectbox("TURNO A CORREGIR:", ["Seleccionar..."] + list(lista_turnos.keys()), key="olv_tur")
                        
                        c_olv3, c_olv4 = st.columns(2)
                        fecha_olvido = c_olv3.date_input("FECHA:", value=ahora.date(), key="olv_fec")
                        hora_real = c_olv4.time_input("HORA REAL DE INGRESO:", value=ahora.time(), key="olv_hor")
                        
                        motivo_olv = st.text_input("MOTIVO:", key="olv_mot")
                        
                        if st.form_submit_button("ENVIAR A AUDITORÍA"):
                            if suc_olv == "Seleccionar..." or turno_olv == "Seleccionar..." or not motivo_olv.strip():
                                st.warning("Complete todos los campos de auditoría.")
                            else:
                                exito = insert_row("correcciones_pendientes", {
                                    "empleado": empleado_en_celu,
                                    "fecha": str(fecha_olvido),
                                    "hora_real": hora_real.strftime("%I:%M:%S %p"),
                                    "sucursal": suc_olv,
                                    "turno": turno_olv,
                                    "motivo": motivo_olv.strip()
                                })
                                if exito:
                                    st.session_state['fichaje_exitoso'] = "Solicitud de corrección enviada."
                                    recargar_app()

            # 3. AVISOS
            st.markdown("---")
            mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu, rol_empleado]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='super-box' style='border-color: #A0A0A0; color: #E5E4E2;'>COMUNICADO GENERAL: {m['texto']}</div>", unsafe_allow_html=True)
                    elif m['destinatario'] == rol_empleado: st.markdown(f"<div class='task-pend'>MENSAJE DE ROL: {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='report-box'>MENSAJE PRIVADO: {m['texto']}</div>", unsafe_allow_html=True)

            # 4. LIGAS DE PUNTOS
            rankings_actuales = config_app.get("rankings_muro", [{"nombre": "RANKING GLOBAL", "competidores": ["Todos"], "espectadores": ["Todos"], "mostrar_puntos": True}])
            
            inicio_semana_int = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}.get(config_app.get("dia_inicio_semana", "Lunes"), 0)
            hoy_dt_top = ahora.date()
            dias_desde_inicio_top = (hoy_dt_top.weekday() - inicio_semana_int) % 7
            fecha_inicio_sem_actual = hoy_dt_top - datetime.timedelta(days=dias_desde_inicio_top)
            p_in_top = fecha_inicio_sem_actual - datetime.timedelta(days=7)
            p_fi_top = fecha_inicio_sem_actual - datetime.timedelta(days=1)
            
            df_p_top = df_punt[(df_punt['F_Obj'] >= p_in_top) & (df_punt['F_Obj'] <= p_fi_top)] if not df_punt.empty else pd.DataFrame()
            df_t_top = df_tl[(df_tl['F_Obj'] >= p_in_top) & (df_tl['F_Obj'] <= p_fi_top)] if not df_tl.empty else pd.DataFrame()
            ajustes_top = [p for p in lista_puntos if p_in_top <= datetime.datetime.strptime(p.get('Fecha', p.get('fecha')), "%Y-%m-%d").date() <= p_fi_top]
            reg_top = config_app.get("reglas_puntos", {})
            
            for rank in rankings_actuales:
                espectadores = rank.get("espectadores", [])
                puede_ver = False
                if "Todos" in espectadores or rol_empleado in espectadores or empleado_en_celu in espectadores:
                    puede_ver = True
                    
                if puede_ver:
                    with st.expander(f"{rank['nombre']} (SEMANA ANTERIOR)", expanded=True):
                        competidores = rank.get("competidores", ["Todos"])
                        emps_compitiendo = []
                        for e in lista_empleados:
                            e_rol = roles_empleados.get(e, "Staff")
                            if "Todos" in competidores or e_rol in competidores or e in competidores:
                                emps_compitiendo.append(e)
                                
                        ranking_sp = []
                        for emp_r in emps_compitiendo:
                            df_e_p_top = df_p_top[df_p_top["Empleado"] == emp_r].reset_index(drop=True) if not df_p_top.empty else pd.DataFrame()
                            e_aj_top = sum([int(p.get('Puntos', p.get('puntos', 0))) for p in ajustes_top if p.get('Empleado', p.get('empleado')) == emp_r and p.get('Estado', p.get('estado', 'Aprobada')) == 'Aprobada'])
                            e_tp_top = pd.to_numeric(df_t_top[(df_t_top["Empleado"] == emp_r) & (df_t_top["Estado"] == "Aprobada")]["Puntos"], errors='coerce').fillna(0).astype(int).sum() if not df_t_top.empty else 0
                            e_ok_top = len(df_e_p_top[df_e_p_top["Estado"] == "A tiempo"]) if not df_e_p_top.empty else 0
                            e_tar_top = len(df_e_p_top[df_e_p_top["Estado"] == "Tarde"]) if not df_e_p_top.empty else 0
                            e_au_top = len(df_e_p_top[df_e_p_top["Tipo"] == "Ausente"]) if not df_e_p_top.empty else 0
                            
                            puntaje_semana = (e_ok_top * reg_top.get('A tiempo', 0)) + (e_tar_top * reg_top.get('Tarde', -5)) + (e_au_top * reg_top.get('Ausente', -15)) + e_aj_top + e_tp_top
                            
                            if not df_e_p_top.empty or e_tp_top > 0 or e_aj_top != 0:
                                ranking_sp.append({"Empleado": emp_r, "Puntos": puntaje_semana})
                        
                        ranking_sp = sorted(ranking_sp, key=lambda x: x["Puntos"], reverse=True)
                        st.markdown(f"<p style='text-align: center; color: #737373; font-size: 0.8rem; letter-spacing: 1px;'>PERÍODO: {p_in_top.strftime('%d/%m')} - {p_fi_top.strftime('%d/%m')}</p>", unsafe_allow_html=True)
                        
                        if not ranking_sp:
                            st.info("Sin registros de actividad en la liga.")
                        else:
                            mostrar_pts_liga = rank.get("mostrar_puntos", True)
                            c1, c2, c3 = st.columns(3)
                            
                            if len(ranking_sp) > 0: 
                                txt_p1 = f"<br><span style='font-size: 0.8rem; color: #A0A0A0;'>{ranking_sp[0]['Puntos']} PTS</span>" if mostrar_pts_liga else ""
                                c2.markdown(f"<div style='text-align:center; padding:15px; background:#111; border:1px solid #D4AF37; color:#D4AF37; border-radius:4px;'><b>1. {ranking_sp[0]['Empleado']}</b>{txt_p1}</div>", unsafe_allow_html=True)
                            if len(ranking_sp) > 1: 
                                txt_p2 = f"<br><span style='font-size: 0.8rem; color: #737373;'>{ranking_sp[1]['Puntos']} PTS</span>" if mostrar_pts_liga else ""
                                c1.markdown(f"<div style='text-align:center; padding:15px; background:#0a0a0a; border:1px solid #A0A0A0; color:#E5E4E2; border-radius:4px; margin-top:20px;'><b>2. {ranking_sp[1]['Empleado']}</b>{txt_p2}</div>", unsafe_allow_html=True)
                            if len(ranking_sp) > 2: 
                                txt_p3 = f"<br><span style='font-size: 0.8rem; color: #737373;'>{ranking_sp[2]['Puntos']} PTS</span>" if mostrar_pts_liga else ""
                                c3.markdown(f"<div style='text-align:center; padding:15px; background:#0a0a0a; border:1px solid #8c7853; color:#E5E4E2; border-radius:4px; margin-top:40px;'><b>3. {ranking_sp[2]['Empleado']}</b>{txt_p3}</div>", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)

            # 5. HORAS SEMANALES
            if get_bool_config("mostrar_horas_empleado", False):
                inicio_semana_int = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}.get(config_app.get("dia_inicio_semana", "Lunes"), 0)
                hoy_dt = ahora.date()
                dias_desde_inicio = (hoy_dt.weekday() - inicio_semana_int) % 7
                fecha_inicio_sem = hoy_dt - datetime.timedelta(days=dias_desde_inicio)
                fecha_fin_sem = fecha_inicio_sem + datetime.timedelta(days=6)
                
                df_horas_emp = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt['F_Obj'] >= fecha_inicio_sem) & (df_punt['F_Obj'] <= fecha_fin_sem)].copy().reset_index(drop=True)
                horas_semanales_acumuladas = 0.0
                
                if not df_horas_emp.empty:
                    df_horas_emp['Timestamp'] = pd.to_datetime(df_horas_emp['Fecha'].astype(str) + ' ' + df_horas_emp['Hora'].astype(str), errors='coerce')
                    df_horas_emp = df_horas_emp.dropna(subset=['Timestamp']).sort_values(by="Timestamp")
                    
                    def procesar_tramo_emp(entrada_row, salida_row):
                        h_in = entrada_row["Timestamp"]
                        h_out_real = salida_row["Timestamp"] if salida_row is not None else None
                        t_eval = str(entrada_row["Turno"]).strip()
                        
                        if not h_out_real:
                            if t_eval in lista_turnos:
                                try:
                                    t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                    h_out_real = datetime.datetime.combine(h_in.date(), t_out_obj)
                                    if h_out_real < h_in: h_out_real += datetime.timedelta(days=1)
                                except: h_out_real = h_in
                            else: h_out_real = h_in
                        
                        if t_eval in lista_turnos:
                            try:
                                t_in_obj = pd.to_datetime(lista_turnos[t_eval].get("ingreso")).time()
                                t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                h_in_ofi = datetime.datetime.combine(h_in.date(), t_in_obj)
                                h_out_ofi = datetime.datetime.combine(h_in.date(), t_out_obj)
                                if h_out_ofi < h_in_ofi: h_out_ofi += datetime.timedelta(days=1)
                                
                                if (h_in_ofi - h_in).total_seconds() > 43200:
                                    h_in_ofi -= datetime.timedelta(days=1); h_out_ofi -= datetime.timedelta(days=1)
                                elif (h_in - h_in_ofi).total_seconds() > 43200:
                                    h_in_ofi += datetime.timedelta(days=1); h_out_ofi += datetime.timedelta(days=1)
                                    
                                h_tramo_oficial = (h_out_ofi - h_in_ofi).total_seconds() / 3600.0
                                
                                minutos_tarde = (h_in - h_in_ofi).total_seconds() / 60.0
                                if get_bool_config("desc_tarde", True):
                                    tolerancia_m = int(config_app.get("tolerancia_minutos", 10))
                                    if get_bool_config("perdonar_tolerancia", True) and (minutos_tarde <= tolerancia_m):
                                        desc_in = 0.0
                                    else:
                                        desc_in = max(0.0, minutos_tarde / 60.0)
                                else:
                                    desc_in = 0.0
                                    
                                desc_out = (h_out_ofi - h_out_real).total_seconds() / 3600.0 if get_bool_config("desc_temp", True) else 0.0
                                desc_in = max(0.0, desc_in)
                                desc_out = max(0.0, desc_out)
                                
                                h_tramo = h_tramo_oficial - desc_in - desc_out
                            except:
                                h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                        else:
                            h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                        return max(0.0, h_tramo)

                    ent_act = None
                    for _, rf in df_horas_emp.iterrows():
                        tr = str(rf["Tipo"]).strip()
                        if tr == "Entrada":
                            if ent_act is not None: horas_semanales_acumuladas += procesar_tramo_emp(ent_act, None)
                            ent_act = rf
                        elif tr in ["Salida", "Salida Automática", "Salida (Cambio Local)", "Retiro Temprano"] and ent_act is not None:
                            horas_semanales_acumuladas += procesar_tramo_emp(ent_act, rf)
                            ent_act = None
                    if ent_act is not None:
                        horas_semanales_acumuladas += procesar_tramo_emp(ent_act, None)
                        
                st.markdown(f"<div class='super-box'>CÓMPUTO SEMANAL: {formato_horas_texto(horas_semanales_acumuladas)} <br><span style='color: #737373; font-size: 0.8rem; font-family: Manrope, sans-serif;'>({fecha_inicio_sem.strftime('%d/%m')} - {fecha_fin_sem.strftime('%d/%m')})</span></div>", unsafe_allow_html=True)

            # 6. PANEL SUPERVISOR
            if rol_empleado in ["Cajero", "Encargado"]:
                with st.expander("PANEL DE AUDITORÍA (SUPERVISOR)", expanded=False):
                    st.markdown("<div class='super-box' style='font-size:0.9rem;'>HABILITADO PARA AUDITORÍA Y ASIGNACIÓN DE PUNTOS</div>", unsafe_allow_html=True)
                    st.markdown("#### AUDITAR SALIDA DE COMPAÑERO")
                    if estado_laboral == "Adentro":
                        suc_cajero = datos_turno_activo.get("Sucursal")
                        st.write(f"ZONA DE AUDITORÍA: {suc_cajero}")
                        auditables = []
                        df_hoy_todos = df_punt[df_punt["Fecha"] == fecha_hoy].reset_index(drop=True) if not df_punt.empty else pd.DataFrame()
                        
                        if not df_hoy_todos.empty:
                            if 'id' in df_hoy_todos.columns:
                                df_hoy_todos['id_num'] = pd.to_numeric(df_hoy_todos['id'], errors='coerce')
                                df_hoy_todos = df_hoy_todos.sort_values(by="id_num").reset_index(drop=True)
                            else:
                                df_hoy_todos = df_hoy_todos.reset_index(drop=True)
                            for e_comp in lista_empleados:
                                if e_comp != empleado_en_celu:
                                    df_c = df_hoy_todos[df_hoy_todos["Empleado"] == e_comp].reset_index(drop=True)
                                    if not df_c.empty:
                                        ult_c = df_c.iloc[-1]
                                        tipo_uc = ult_c["Tipo"]
                                        if isinstance(tipo_uc, pd.Series):
                                            tipo_uc = tipo_uc.iloc[0]
                                        suc_uc = ult_c["Sucursal"]
                                        if isinstance(suc_uc, pd.Series):
                                            suc_uc = suc_uc.iloc[0]
                                        if tipo_uc == "Entrada" and str(suc_uc) == str(suc_cajero):
                                            auditables.append(e_comp)
                                            
                        if auditables:
                            with st.form("form_sup_salida"):
                                c_s1, c_s2 = st.columns(2)
                                s_emp_salida = c_s1.selectbox("COMPAÑERO:", ["Seleccionar..."] + auditables, key="sup_emp")
                                s_hora_salida = c_s2.time_input("HORA DE SALIDA:", ahora.time(), key="sup_hor")
                                s_motivo_salida = st.text_input("NOTA DE AUDITORÍA:", key="sup_not")
                                if st.form_submit_button("FICHAR SALIDA AUDITADA"):
                                    if s_emp_salida == "Seleccionar...":
                                        st.warning("Seleccione empleado.")
                                    elif not s_motivo_salida.strip():
                                        st.warning("Ingrese el motivo de auditoría.")
                                    else:
                                        ya_pedido = False
                                        ya_salio = not df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Salida")].empty
                                        for sp in salidas_pendientes:
                                            if sp.get("Empleado", sp.get("empleado")) == s_emp_salida and sp.get("Fecha", sp.get("fecha")) == str(fecha_hoy):
                                                ya_pedido = True
                                                break
                                        if ya_salio:
                                            st.error("Salida ya registrada en el sistema.")
                                        elif ya_pedido:
                                            st.error("Solicitud en revisión por Gerencia.")
                                        else:
                                            hora_str_salida = s_hora_salida.strftime("%I:%M:%S %p")
                                            nota_final = f"[Auditor: {empleado_en_celu}] {s_motivo_salida}"
                                            turno_del_auditado = "Manual"
                                            df_aud_turno = df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Entrada")].reset_index(drop=True)
                                            if not df_aud_turno.empty:
                                                turno_del_auditado = df_aud_turno.iloc[-1]["Turno"]
                                                if isinstance(turno_del_auditado, pd.Series):
                                                    turno_del_auditado = turno_del_auditado.iloc[0]
                                            
                                            exito = insert_row("salidas_pendientes", {
                                                "fecha": str(fecha_hoy), "hora": str(hora_str_salida), "empleado": str(s_emp_salida),
                                                "sucursal": str(suc_cajero), "turno": str(turno_del_auditado),
                                                "nota": str(nota_final), "autor": str(empleado_en_celu)
                                            })
                                            if exito:
                                                st.success("Enviado a Gerencia para revisión.")
                                                recargar_app()
                        else:
                            st.info("Sin operarios en esta zona.")
                    else:
                        st.warning("Requiere registro de entrada en sucursal para auditar.")
                        
            # 7. BUZÓN 
            with st.expander("BUZÓN DE REPORTES", expanded=False):
                opciones_reporte = ["Falla técnica", "Incumplimiento de políticas", "Observación gerencial"]
                
                if rol_empleado in ["Cajero", "Encargado"]:
                    opciones_reporte.append("Sugerir Ajuste de Puntos a Operario")
                    
                tipo_rep = st.selectbox("CATEGORÍA:", opciones_reporte, key="rep_cat")
                
                if tipo_rep in ["Incumplimiento de políticas", "Sugerir Ajuste de Puntos a Operario"]:
                    implicado = st.selectbox("IMPLICADO:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu], key="rep_imp")
                else:
                    implicado = "N/A"
                    
                pts_sugeridos = 0
                if tipo_rep == "Sugerir Ajuste de Puntos a Operario":
                    pts_recompensa_info = config_app.get("recompensa_auditoria_cajero", 10)
                    if rol_empleado == "Cajero":
                        st.info(f"Recompensa de auditoría por aprobación: +{pts_recompensa_info} pts.")
                    pts_sugeridos = st.number_input("PUNTOS PROPUESTOS:", value=0, step=1, key="rep_pts")
                    
                detalle_rep = st.text_area("DETALLE DEL REPORTE:", key="rep_det")
                
                if st.button("ENVIAR REPORTE", key="btn_enviar_rep"):
                    if not detalle_rep.strip(): 
                        st.warning("Detalle requerido.")
                    elif implicado == "Seleccionar...": 
                        st.warning("Seleccione empleado implicado.")
                    elif tipo_rep == "Sugerir Ajuste de Puntos a Operario" and pts_sugeridos == 0:
                        st.warning("Puntos propuestos inválidos (0).")
                    else:
                        if tipo_rep == "Sugerir Ajuste de Puntos a Operario":
                            exito = insert_row("puntos_cajero_pendientes", {
                                "fecha": fecha_hoy, "hora": hora_hoy, "emisor": empleado_en_celu,
                                "compañero": implicado, "puntos_sugeridos": pts_sugeridos,
                                "motivo": detalle_rep.strip(), "estado": "Pendiente de auditoría"
                            })
                            if exito:
                                st.session_state['fichaje_exitoso'] = "Auditoría de puntos enviada."
                                recargar_app()
                        else:
                            exito = insert_row("reportes", {
                                "fecha": fecha_hoy, "hora": hora_hoy, "emisor": empleado_en_celu,
                                "tipo": tipo_rep, "implicado": implicado, "detalle": detalle_rep.strip(), "estado": "Pendiente de lectura"
                            })
                            if exito:
                                st.session_state['fichaje_exitoso'] = "Reporte procesado."
                                recargar_app()
                        
            # 8. MIS TAREAS
            tareas_totales = tareas_roles.get(rol_empleado, []) + tareas_individuales.get(empleado_en_celu, [])
            if tareas_totales:
                with st.expander("TAREAS OPERATIVAS", expanded=True):
                    tareas_hoy_df = df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Fecha"] == fecha_hoy)].reset_index(drop=True) if not df_tl.empty else pd.DataFrame()
                    for t in tareas_totales:
                        t_nombre, t_puntos = t.get('tarea'), t.get('puntos')
                        t_reg = tareas_hoy_df[tareas_hoy_df["Tarea"] == t_nombre].reset_index(drop=True) if not tareas_hoy_df.empty else pd.DataFrame()
                        if not t_reg.empty:
                            est_t = t_reg.iloc[-1]["Estado"]
                            if isinstance(est_t, pd.Series):
                                est_t = est_t.iloc[0]
                            if est_t == "Aprobada": st.markdown(f"<div class='task-box'>VERIFICADO: {t_nombre} | +{t_puntos} pts</div>", unsafe_allow_html=True)
                            elif est_t == "Rechazada": st.markdown(f"<div class='task-rej'>DENEGADA: {t_nombre}</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='task-pend'>EN REVISIÓN: {t_nombre}</div>", unsafe_allow_html=True)
                        else:
                            c_t1, c_t2 = st.columns([3, 1])
                            c_t1.write(f"- {t_nombre} ({t_puntos} pts)")
                            if c_t2.button("FINALIZAR", key=f"btn_t_{t_nombre}"):
                                exito = insert_row("tareas_log", {"fecha": str(fecha_hoy), "hora": str(hora_hoy), "empleado": str(empleado_en_celu), "tarea": str(t_nombre), "puntos": str(t_puntos), "estado": "Pendiente"})
                                if exito:
                                    recargar_app()
                                
            # 9. HISTORIAL RECIENTE
            with st.expander("HISTORIAL DE JORNADAS"):
                if not df_punt.empty:
                    df_emp = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["F_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].copy().reset_index(drop=True)
                    if not df_emp.empty:
                        if 'id' in df_emp.columns:
                            df_emp['id_num'] = pd.to_numeric(df_emp['id'], errors='coerce')
                            df_emp = df_emp.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                    else: st.write("Sin registros en el período.")
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # 10. QUIÉNES SOMOS
            with st.expander("SOPORTE Y ASISTENCIA", expanded=False):
                st.markdown(f"### {owner_config.get('empresa_nombre', 'Corporación')}")
                st.write(owner_config.get('quienes_somos', ''))
                st.markdown("---")
                st.markdown("**INFORMACIÓN DE CONTACTO:**")
                st.write(owner_config.get('contactos', ''))
        else:
            if get_bool_config("autoregistro", False):
                st.info("PROCESO DE VINCULACIÓN DE TERMINAL ACTIVO.")
                nuevo_nombre_emp = st.text_input("NOMBRE OPERARIO:", key="reg_nom")
                rol_elegido_auto = st.selectbox("DESIGNACIÓN:", lista_roles_disponibles, key="reg_rol")
                if st.button("SINCRONIZAR TERMINAL", key="reg_btn") and nuevo_nombre_emp.strip():
                    n_emp = nuevo_nombre_emp.strip()
                    match = next((e for e in lista_empleados if e.lower() == n_emp.lower()), None)
                    
                    if device_id in dispositivos_vinculados.values():
                        st.error("Terminal previamente asignada.")
                    elif match and match in dispositivos_vinculados:
                        st.error(f"El operario '{match}' ya posee una terminal vinculada.")
                    else:
                        try:
                            if not match:
                                insert_row("empleados", {"nombre": n_emp, "rol": rol_elegido_auto, "dispositivo_id": device_id})
                            else:
                                supabase.table("empleados").update({"rol": rol_elegido_auto, "dispositivo_id": device_id}).eq("nombre", match).execute()
                            recargar_app()
                        except Exception as e:
                            show_db_error(e, "vinculando dispositivo")
            else:
                st.info("AUTO-REGISTRO INACTIVO. Seleccione credencial emitida por Gerencia.")
                emp_vincular = st.selectbox("CREDENCIAL:", ["Seleccionar..."] + sorted(lista_empleados), key="vinc_emp")
                if st.button("SINCRONIZAR TERMINAL", key="vinc_btn") and emp_vincular != "Seleccionar...":
                    if emp_vincular in dispositivos_vinculados:
                        st.error("Credencial en uso en otra terminal.")
                    elif device_id in dispositivos_vinculados.values():
                        st.error("Terminal asignada a otra credencial.")
                    else:
                        try:
                            supabase.table("empleados").update({"dispositivo_id": device_id}).eq("nombre", emp_vincular).execute()
                            recargar_app()
                        except Exception as e:
                            show_db_error(e, "vinculando cuenta existente")
# ==========================================
# 6. PANEL DE GERENCIA (BUSINESS INTELLIGENCE)
# ==========================================
elif pestaña == "Panel de Gerencia":
    es_incognito_gerencia = (es_incognito and usuario_incognito == "Gerencia")

    if not es_incognito_gerencia:
        password_ingresada = st.text_input("CLAVE DE ACCESO GERENCIAL:", type="password", key="login_gerencia")
        
        if password_ingresada and password_ingresada != "doremifasol":
            if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
                st.session_state['last_pw_attempt'] = password_ingresada
                res = "Acceso Permitido" if password_ingresada == config_app.get("admin_password", "1234") else "Acceso Denegado"
                insert_row("intentos_seguridad", {"fecha": fecha_hoy, "hora": hora_hoy, "usuario": empleado_en_celu if empleado_en_celu else "Desconocido", "clave": password_ingresada, "resultado": res})
                
        acceso_concedido = (password_ingresada == config_app.get("admin_password", "1234") or password_ingresada == "doremifasol")
    else:
        st.warning("MODO INCÓGNITO ACTIVO: Visualizando como Gerencia. Sistema de seguridad en pausa.")
        if st.button("SALIR DEL MODO INCÓGNITO", key="btn_exit_inc_ger"):
            st.session_state['incognito'] = False
            st.session_state['incognito_user'] = None
            recargar_app()
        acceso_concedido = True

    if acceso_concedido:
        try:
            f_venc = datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date()
            dias_restantes = (f_venc - ahora.date()).days
            if 0 <= dias_restantes <= owner_config.get("dias_aviso", 5) and owner_config.get("estado_licencia", "Activo") == "Activo":
                st.markdown(f"<div class='task-pend'><b>AVISO DEL PROVEEDOR:</b><br>{owner_config.get('mensaje_aviso', '')} (Vence en {dias_restantes} días)</div>", unsafe_allow_html=True)
        except: pass

        if owner_config.get("mostrar_membresia", False):
            st.markdown(f"<div style='background-color: #111; color: #D4AF37; padding: 15px; border-radius: 4px; margin-bottom: 15px; font-family: Cinzel, serif; letter-spacing: 2px; border: 1px solid #D4AF37;'>PLAN CONTRATADO: <b>{owner_config.get('plan_pago', 'MENSUAL').upper()}</b></div>", unsafe_allow_html=True)
        
        tab_analytics, tab_caja, tab_sueldos, tab_horarios, tab_puntos, tab_tareas, tab_perfil, tab_staff, tab_tiendas, tab_comunicados, tab_config, tab_limpieza = st.tabs([
            "ANALYTICS", "CAJAS", "SUELDOS", "HORARIOS", "RANKING", "TAREAS", "PERFILES", "STAFF", "TIENDAS", "COMUNICADOS", "AJUSTES", "LIMPIEZA"
        ])
        
        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">ANALYTICS GLOBALES</div>', unsafe_allow_html=True)
            c_alrt1, c_alrt2 = st.columns([2, 1])
            c_alrt1.markdown(f"### ALERTAS DEL DÍA ({fecha_hoy})")
            suc_alerta = c_alrt2.selectbox("FILTRAR POR SUCURSAL:", ["Todas las sucursales"] + list(lista_locales.keys()), key="filtro_alertas_dia")
            df_activos = load_df("asistencia")
            if not df_activos.empty:
                df_activos = df_activos.reset_index(drop=True)
            if df_activos.empty:
                st.info("Base de datos limpia.")
            else:
                df_activos = df_activos[df_activos["Empleado"].isin(lista_empleados)].copy().reset_index(drop=True)
                df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                df_hoy_alertas = df_activos[df_activos["Fecha"] == fecha_hoy].copy().reset_index(drop=True)
                
                if suc_alerta != "Todas las sucursales":
                    df_hoy_filtrado = df_hoy_alertas[df_hoy_alertas["Sucursal"] == suc_alerta].reset_index(drop=True)
                else:
                    df_hoy_filtrado = df_hoy_alertas
                    
                ult_suc_hoy = {}
                if not df_hoy_filtrado.empty:
                    if 'id' in df_hoy_filtrado.columns:
                        df_hoy_filtrado['id_num'] = pd.to_numeric(df_hoy_filtrado['id'], errors='coerce')
                        df_hoy_filtrado = df_hoy_filtrado.sort_values(by="id_num")
                    for idx, row in df_hoy_filtrado.iterrows():
                        ult_suc_hoy[row["Empleado"]] = row["Sucursal"]
                        
                entradas_hoy = df_hoy_filtrado[df_hoy_filtrado["Tipo"] == "Entrada"]["Empleado"].unique().tolist()
                ausentes = df_hoy_filtrado[df_hoy_filtrado["Tipo"] == "Ausente"]["Empleado"].unique().tolist()
                llegadas_tarde = df_hoy_filtrado[(df_hoy_filtrado["Tipo"] == "Entrada") & (df_hoy_filtrado["Estado"] == "Tarde")]["Empleado"].unique().tolist()
                
                entradas_hoy_global = df_hoy_alertas[df_hoy_alertas["Tipo"] == "Entrada"]["Empleado"].unique().tolist()
                ausentes_global = df_hoy_alertas[df_hoy_alertas["Tipo"] == "Ausente"]["Empleado"].unique().tolist()
                sin_fichar = [e for e in lista_empleados if e not in entradas_hoy_global and e not in ausentes_global]
                
                def format_nombres(lista_emps):
                    if not lista_emps: return "NINGUNO"
                    if suc_alerta == "Todas las sucursales": return "<br>".join([f"• {e} <small style='color:#737373;'>({ult_suc_hoy.get(e, 'Desconocida')})</small>" for e in lista_emps])
                    else: return "<br>".join([f"• {e}" for e in lista_emps])
                    
                txt_presentes = format_nombres(entradas_hoy)
                txt_tardes = format_nombres(llegadas_tarde)
                txt_ausentes = format_nombres(ausentes)
                txt_sinfichar = "<br>".join([f"• {e}" for e in sin_fichar]) if sin_fichar else "TODOS OK"
                
                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                c_h1.markdown(f"<div class='task-box'><b>PRESENTES</b><br>{txt_presentes}</div>", unsafe_allow_html=True)
                c_h2.markdown(f"<div class='task-pend'><b>LLEGADAS TARDE</b><br>{txt_tardes}</div>", unsafe_allow_html=True)
                c_h3.markdown(f"<div class='alert-box'><b>AUSENTES</b><br>{txt_ausentes}</div>", unsafe_allow_html=True)
                c_h4.markdown(f"<div class='validation-box'><b>SIN FICHAR</b><br>{txt_sinfichar}</div>", unsafe_allow_html=True)
                
                st.write("---")
                c_fil1_2, c_fil2_2 = st.columns([1,3])
                filtro_a = c_fil1_2.selectbox("KPI DASHBOARD:", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_a")
                rango_stats = c_fil2_2.date_input("FECHAS DEL DASHBOARD:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date()), key="rango_stats") if filtro_a == "Personalizado" else None
                s_in, s_fi = get_fechas_filtro(filtro_a, rango_stats)
                
                df_per = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_in) & (df_activos['Fecha_Obj'].dt.date <= s_fi)].reset_index(drop=True)
                if not df_per.empty:
                    atiempo = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "A tiempo")])
                    tardes = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "Tarde")])
                    ausencias_tot = len(df_per[df_per["Tipo"] == "Ausente"])
                    tot_ingresos = atiempo + tardes
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("PUNTUALIDAD PROMEDIO", f"{round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0}%")
                    c2.metric("INGRESOS A TIEMPO", atiempo)
                    c3.metric("LLEGADAS TARDE", tardes)
                    c4.metric("INASISTENCIAS", ausencias_tot)
                    
                st.write("---")
                st.markdown("### RECUENTO DE HORAS Y EXPORTACIÓN")
                
                inicio_semana_int = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}.get(config_app.get("dia_inicio_semana", "Lunes"), 0)
                dias_desde_inicio_def = (ahora.date().weekday() - inicio_semana_int) % 7
                fecha_inicio_semana_def = ahora.date() - datetime.timedelta(days=dias_desde_inicio_def)
                
                tipo_vista_rrhh = st.radio("FILTRO DE SUCURSAL:", ["Ver todas las sucursales juntas", "Ver una sucursal en particular"], horizontal=True, key="filtro_rrhh_loc")

                c_dl1, c_dl2, c_dl3 = st.columns(3)
                if tipo_vista_rrhh == "Ver una sucursal en particular":
                    local_descarga = c_dl1.selectbox("SELECCIONAR SUCURSAL:", list(lista_locales.keys()), key="dl_loc")
                else:
                    local_descarga = "Todas las sucursales"
                    c_dl1.write("<br><span style='color:#D4AF37;'>MODO GLOBAL SELECCIONADO</span>", unsafe_allow_html=True)
                
                fecha_in_dl = c_dl2.date_input("DESDE EL DÍA:", value=fecha_inicio_semana_def, key="dl_in")
                fecha_fi_dl = c_dl3.date_input("HASTA EL DÍA:", value=ahora.date(), key="dl_fi")
                
                df_dl = df_activos.copy()
                df_dl = df_dl[(df_dl['Fecha_Obj'].dt.date >= fecha_in_dl) & (df_dl['Fecha_Obj'].dt.date <= fecha_fi_dl)].reset_index(drop=True)
                
                if local_descarga != "Todas las sucursales":
                    st.info(f"MODO FILTRADO: Mostrando datos exclusivos de la sucursal {local_descarga}.")
                
                df_dl['Timestamp'] = pd.to_datetime(df_dl['Fecha'].astype(str) + ' ' + df_dl['Hora'].astype(str), errors='coerce')
                df_dl = df_dl.dropna(subset=['Timestamp']).sort_values(by="Timestamp")
                
                datos_horas_dict = {}
                
                if not df_dl.empty:
                    for emp in df_dl["Empleado"].unique():
                        df_e = df_dl[df_dl["Empleado"] == emp].reset_index(drop=True)
                        entrada_actual = None
                        
                        def procesar_tramo_estricto(entrada_row, salida_row):
                            h_in = entrada_row["Timestamp"]
                            h_out_real = salida_row["Timestamp"] if salida_row is not None else None
                            
                            t_eval = str(entrada_row["Turno"]).strip()
                            s_eval = str(entrada_row["Sucursal"]).strip()
                            
                            if local_descarga != "Todas las sucursales" and s_eval != local_descarga:
                                return
                                
                            h_tramo = 0.0
                            
                            if not h_out_real:
                                if t_eval in lista_turnos:
                                    try:
                                        t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                        h_out_real = datetime.datetime.combine(h_in.date(), t_out_obj)
                                        if h_out_real < h_in: h_out_real += datetime.timedelta(days=1)
                                    except:
                                        h_out_real = h_in
                                else:
                                    h_out_real = h_in
                            
                            if t_eval in lista_turnos:
                                try:
                                    t_in_obj = pd.to_datetime(lista_turnos[t_eval].get("ingreso")).time()
                                    t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                    h_in_ofi = datetime.datetime.combine(h_in.date(), t_in_obj)
                                    h_out_ofi = datetime.datetime.combine(h_in.date(), t_out_obj)
                                    if h_out_ofi < h_in_ofi: h_out_ofi += datetime.timedelta(days=1)
                                    
                                    if (h_in_ofi - h_in).total_seconds() > 43200:
                                        h_in_ofi -= datetime.timedelta(days=1); h_out_ofi -= datetime.timedelta(days=1)
                                    elif (h_in - h_in_ofi).total_seconds() > 43200:
                                        h_in_ofi += datetime.timedelta(days=1); h_out_ofi += datetime.timedelta(days=1)
                                    
                                    h_tramo_oficial = (h_out_ofi - h_in_ofi).total_seconds() / 3600.0
                                    
                                    minutos_tarde = (h_in - h_in_ofi).total_seconds() / 60.0
                                    if get_bool_config("desc_tarde", True):
                                        tolerancia_m = int(config_app.get("tolerancia_minutos", 10))
                                        if get_bool_config("perdonar_tolerancia", True) and (minutos_tarde <= tolerancia_m):
                                            desc_in = 0.0
                                        else:
                                            desc_in = max(0.0, minutos_tarde / 60.0)
                                    else:
                                        desc_in = 0.0

                                    desc_out = (h_out_ofi - h_out_real).total_seconds() / 3600.0 if get_bool_config("desc_temp", True) else 0.0
                                    desc_out = max(0.0, desc_out)
                                    
                                    h_tramo = h_tramo_oficial - desc_in - desc_out
                                except Exception as e:
                                    h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                            else:
                                h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                                
                            h_tramo = max(0.0, h_tramo)
                            
                            if h_tramo > 0:
                                sueldo_h = 0.0
                                f_str = h_in.strftime("%Y-%m-%d")
                                for s in sueldos_historico:
                                    emp_hist = s.get("Empleado", s.get("empleado", ""))
                                    f_desde = s.get("Fecha_Desde", s.get("fecha_desde", ""))
                                    f_hasta = s.get("Fecha_Hasta", s.get("fecha_hasta", ""))
                                    if emp_hist == emp and f_desde <= f_str <= f_hasta:
                                        sueldo_h = float(s.get("Valor_Hora", s.get("valor_hora", 0.0)))
                                        break
                                        
                                k = (emp, s_eval)
                                if k not in datos_horas_dict: datos_horas_dict[k] = {"Horas": 0.0, "Pago": 0.0}
                                datos_horas_dict[k]["Horas"] += h_tramo
                                datos_horas_dict[k]["Pago"] += (h_tramo * sueldo_h)

                        for _, row_f in df_e.iterrows():
                            tipo_reg = str(row_f["Tipo"]).strip()
                            if tipo_reg == "Entrada":
                                if entrada_actual is not None:
                                    procesar_tramo_estricto(entrada_actual, None)
                                entrada_actual = row_f
                            elif tipo_reg in ["Salida", "Salida Automática", "Salida (Cambio Local)", "Retiro Temprano"] and entrada_actual is not None:
                                procesar_tramo_estricto(entrada_actual, row_f)
                                entrada_actual = None
                                
                        if entrada_actual is not None:
                            procesar_tramo_estricto(entrada_actual, None)
                
                    datos_horas = []
                    for (emp, loc), vals in datos_horas_dict.items():
                        if vals["Horas"] > 0:
                            datos_horas.append({"Personal": emp, "Rol": roles_empleados.get(emp, "Staff"), "Sucursal": loc, "Horas Computadas": round(vals["Horas"], 2), "Pago Est.": round(vals["Pago"], 2)})
                            
                    if datos_horas:
                        df_horas_final = pd.DataFrame(datos_horas).sort_values(by=["Personal", "Horas Computadas"], ascending=[True, False])
                        
                        st.write("### CUADRO DE LIQUIDACIÓN")
                        
                        total_horas_num = df_horas_final["Horas Computadas"].sum()
                        total_pago_num = df_horas_final["Pago Est."].sum()
                        st.markdown(f"<div class='super-box'><b>TOTALES DEL PERÍODO:</b><br><span style='font-size: 1.5rem;'>Horas: <b>{total_horas_num:.2f} hrs</b> &nbsp; | &nbsp; Pago: <b>${total_pago_num:,.2f}</b></span></div>", unsafe_allow_html=True)
                        
                        df_vista = df_horas_final.copy()
                        df_vista["Horas Computadas"] = df_vista["Horas Computadas"].apply(lambda x: formato_horas_texto(x))
                        df_vista["Pago Est."] = df_vista["Pago Est."].apply(lambda x: f"${x:,.2f}")
                        
                        st.dataframe(df_vista, use_container_width=True, hide_index=True)

                        st.write("---")
                        st.write("### DESCARGAS (RRHH)")
                        c_btn1, c_btn2 = st.columns(2)
                        
                        nombre_export_sucursal = local_descarga.replace(" ", "_")
                        
                        total_row = pd.DataFrame([{"Personal": "TOTAL GENERAL", "Rol": "-", "Sucursal": "-", "Horas Computadas": total_horas_num, "Pago Est.": total_pago_num}])
                        df_export = pd.concat([df_horas_final, total_row], ignore_index=True)
                        
                        c_btn1.markdown(generate_html_download(df_export, f"Horas_y_Sueldos_{nombre_export_sucursal}_{fecha_in_dl}.csv", "DESCARGAR LIQUIDACIÓN GENERAL"), unsafe_allow_html=True)
                        
                        df_asist_dl = df_dl[["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]]
                        if local_descarga != "Todas las sucursales":
                            df_asist_dl = df_asist_dl[df_asist_dl["Sucursal"] == local_descarga].reset_index(drop=True)
                        
                        c_btn2.markdown(generate_html_download(df_asist_dl, f"Fichajes_{nombre_export_sucursal}_{fecha_in_dl}.csv", "DESCARGAR FICHAJES CRUDOS"), unsafe_allow_html=True)
                else:
                    st.info("Sin registros para liquidar en las fechas seleccionadas.")

        with tab_caja:
            st.markdown('<div class="main-title" style="font-size: 2rem;">CONTROL DE CAJA</div>', unsafe_allow_html=True)
            
            empleados_cajeros = [e for e in lista_empleados if roles_empleados.get(e) in ["Cajero", "Encargado"]]
            if not empleados_cajeros:
                empleados_cajeros = lista_empleados
            
            with st.expander("CARGAR CIERRE DE CAJA", expanded=True):
                with st.form("form_cierre_caja"):
                    c_caj1, c_caj2 = st.columns(2)
                    caj_emp = c_caj1.selectbox("Responsable de Caja:", ["Seleccionar..."] + sorted(empleados_cajeros), key="caja_emp")
                    caj_suc = c_caj2.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()), key="caja_suc")
                    
                    c_caj3, c_caj4 = st.columns(2)
                    val_efectivo = c_caj3.number_input("Efectivo ($):", min_value=0.0, step=1000.0, key="caja_efv")
                    val_tarjeta = c_caj4.number_input("Tarjeta ($):", min_value=0.0, step=1000.0, key="caja_tar")
                    
                    c_caj5, c_caj6 = st.columns(2)
                    val_transf = c_caj5.number_input("Transferencia ($):", min_value=0.0, step=1000.0, key="caja_tra")
                    val_total = c_caj6.number_input("Total Declarado ($):", min_value=0.0, step=1000.0, key="caja_tot")
                    
                    c_caj7, c_caj8 = st.columns(2)
                    caj_fecha = c_caj7.date_input("Fecha:", value=ahora.date(), key="caja_fec")
                    nota_caja = c_caj8.text_input("Novedades / Notas:", key="caja_not")
                    
                    if st.form_submit_button("GUARDAR CIERRE"):
                        if caj_emp == "Seleccionar..." or caj_suc == "Seleccionar...":
                            st.warning("Seleccione Responsable y Sucursal.")
                        else:
                            exito = insert_row("cierres_caja", {"fecha": caj_fecha.strftime("%Y-%m-%d"), "hora": hora_hoy, "cajero": caj_emp, "sucursal": caj_suc, "turno": "N/A", "efectivo": val_efectivo, "tarjeta": val_tarjeta, "transferencia": val_transf, "total_ventas": val_total, "nota": nota_caja.strip()})
                            if exito:
                                st.success("Cierre de caja guardado correctamente.")
                                recargar_app()

            with st.expander("MODIFICAR O ELIMINAR CIERRES", expanded=False):
                if cierres_caja:
                    for cc in reversed(cierres_caja):
                        cc_id = cc.get("id")
                        c_fecha = cc.get("Fecha", cc.get("fecha", ""))
                        c_suc = cc.get("Sucursal", cc.get("sucursal", ""))
                        c_caj = cc.get("Cajero", cc.get("cajero", ""))
                        c_tot = float(cc.get('Total_Ventas', cc.get('total_ventas', 0)))
                        
                        with st.expander(f"{c_fecha} | {c_suc} | {c_caj} | TOTAL: ${c_tot:,.2f}"):
                            c_edc1, c_edc2 = st.columns(2)
                            
                            idx_emp = (sorted(empleados_cajeros).index(c_caj) + 1) if c_caj in empleados_cajeros else 0
                            n_emp_caja = c_edc1.selectbox("Responsable:", ["Seleccionar..."] + sorted(empleados_cajeros), index=idx_emp, key=f"ecaj_{cc_id}")
                            
                            idx_suc = (list(lista_locales.keys()).index(c_suc) + 1) if c_suc in lista_locales else 0
                            n_suc_caja = c_edc2.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()), index=idx_suc, key=f"esuc_{cc_id}")
                            
                            c_edc3, c_edc4 = st.columns(2)
                            n_efvo = c_edc3.number_input("Efectivo ($):", value=float(cc.get('Efectivo', cc.get('efectivo', 0))), step=1000.0, key=f"eefvo_{cc_id}")
                            n_tarj = c_edc4.number_input("Tarjeta ($):", value=float(cc.get('Tarjeta', cc.get('tarjeta', 0))), step=1000.0, key=f"etarj_{cc_id}")
                            
                            c_edc5, c_edc6 = st.columns(2)
                            n_transf = c_edc5.number_input("Transferencia ($):", value=float(cc.get('Transferencia', cc.get('transferencia', 0))), step=1000.0, key=f"etransf_{cc_id}")
                            n_tot = c_edc6.number_input("Total Declarado ($):", value=c_tot, step=1000.0, key=f"etot_{cc_id}")
                            
                            c_edc7, c_edc8 = st.columns(2)
                            try: 
                                fecha_def = datetime.datetime.strptime(c_fecha, "%Y-%m-%d").date()
                            except: 
                                fecha_def = ahora.date()
                            n_fecha = c_edc7.date_input("Fecha:", value=fecha_def, key=f"efec_{cc_id}")
                            n_nota = c_edc8.text_input("Nota:", value=cc.get('Nota', cc.get('nota', '')), key=f"enot_{cc_id}")

                            c_edcb1, c_edcb2 = st.columns(2)
                            if c_edcb1.button("GUARDAR CAMBIOS", key=f"btn_s_c_{cc_id}"):
                                if n_emp_caja != "Seleccionar..." and n_suc_caja != "Seleccionar...":
                                    try:
                                        supabase.table("cierres_caja").update({
                                            "fecha": n_fecha.strftime("%Y-%m-%d"), 
                                            "hora": cc.get("Hora", hora_hoy), 
                                            "cajero": n_emp_caja, 
                                            "sucursal": n_suc_caja, 
                                            "turno": cc.get("Turno", "N/A"), 
                                            "efectivo": n_efvo, 
                                            "tarjeta": n_tarj, 
                                            "transferencia": n_transf, 
                                            "total_ventas": n_tot, 
                                            "nota": n_nota.strip()
                                        }).eq("id", cc_id).execute()
                                        st.success("Cierre actualizado.")
                                        recargar_app()
                                    except Exception as e: show_db_error(e, "actualizando caja")
                                else:
                                    st.warning("Faltan datos de Responsable o Sucursal.")
                                    
                            if c_edcb2.button("ELIMINAR CIERRE", key=f"btn_d_c_{cc_id}"):
                                try:
                                    supabase.table("cierres_caja").delete().eq("id", cc_id).execute()
                                    st.success("Cierre eliminado.")
                                    recargar_app()
                                except Exception as e: show_db_error(e, "eliminando caja")
                else:
                    st.info("No hay cierres registrados.")
                    
            st.write("---")
            st.subheader("ESTADÍSTICAS DE RECAUDACIÓN")
            c_fc1, c_fc2 = st.columns([1,3])
            filtro_caja = c_fc1.selectbox("FILTRAR POR:", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_caja")
            rango_caja = c_fc2.date_input("RANGO DE FECHAS:", value=(ahora.date() - datetime.timedelta(days=30), ahora.date()), key="rango_caja") if filtro_caja == "Personalizado" else None
            c_in, c_fi = get_fechas_filtro(filtro_caja, rango_caja)
            
            if cierres_caja:
                cierres_filtrados = []
                for c in cierres_caja:
                    try:
                        d_obj = datetime.datetime.strptime(c.get("Fecha", c.get("fecha")), "%Y-%m-%d").date()
                        if c_in <= d_obj <= c_fi: cierres_filtrados.append(c)
                    except: pass
                
                if cierres_filtrados:
                    df_caja = pd.DataFrame(cierres_filtrados)
                    df_caja['Efectivo'] = pd.to_numeric(df_caja['Efectivo'], errors='coerce').fillna(0)
                    df_caja['Tarjeta'] = pd.to_numeric(df_caja['Tarjeta'], errors='coerce').fillna(0)
                    df_caja['Transferencia'] = pd.to_numeric(df_caja['Transferencia'], errors='coerce').fillna(0)
                    df_caja['Total_Ventas'] = pd.to_numeric(df_caja['Total_Ventas'], errors='coerce').fillna(0)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("EFECTIVO", f"${df_caja['Efectivo'].sum():,.2f}")
                    col2.metric("TARJETA", f"${df_caja['Tarjeta'].sum():,.2f}")
                    col3.metric("TRANSFERENCIA", f"${df_caja['Transferencia'].sum():,.2f}")
                    col4.metric("TOTAL VENTAS", f"${df_caja['Total_Ventas'].sum():,.2f}")
                    
                    st.markdown("#### GRÁFICOS DE RENDIMIENTO")
                    tab_g1, tab_g2 = st.tabs(["EVOLUCIÓN EN EL TIEMPO", "COMPARATIVA POR SUCURSAL"])
                    
                    with tab_g1:
                        df_caja['Fecha_DT'] = pd.to_datetime(df_caja['Fecha'])
                        ventas_por_dia = df_caja.groupby("Fecha_DT")["Total_Ventas"].sum().reset_index()
                        grafico_lineas = alt.Chart(ventas_por_dia).mark_line(point=True, color='#D4AF37', strokeWidth=3).encode(
                            x=alt.X('Fecha_DT:T', title='Fecha'),
                            y=alt.Y('Total_Ventas:Q', title='Total Ventas ($)'),
                            tooltip=[alt.Tooltip('Fecha_DT:T', title='Fecha'), alt.Tooltip('Total_Ventas:Q', title='Recaudación ($)', format=',.2f')]
                        ).properties(height=350).interactive()
                        st.altair_chart(grafico_lineas, use_container_width=True)
                        
                    with tab_g2:
                        ventas_por_sucursal = df_caja.groupby("Sucursal")["Total_Ventas"].sum().reset_index()
                        grafico_barras = alt.Chart(ventas_por_sucursal).mark_bar(color='#D4AF37').encode(
                            x=alt.X('Sucursal:N', title='Sucursal', sort='-y'),
                            y=alt.Y('Total_Ventas:Q', title='Total Ventas ($)'),
                            tooltip=[alt.Tooltip('Sucursal:N', title='Sucursal'), alt.Tooltip('Total_Ventas:Q', title='Recaudación ($)', format=',.2f')]
                        ).properties(height=350).interactive()
                        st.altair_chart(grafico_barras, use_container_width=True)

                    st.markdown("#### REGISTRO DETALLADO")
                    df_mostrar_caja = df_caja.copy()
                    df_mostrar_caja["Efectivo"] = df_mostrar_caja["Efectivo"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Tarjeta"] = df_mostrar_caja["Tarjeta"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Transferencia"] = df_mostrar_caja["Transferencia"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Total_Ventas"] = df_mostrar_caja["Total_Ventas"].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_mostrar_caja.sort_values(by=["Fecha", "Hora"], ascending=[False, False])[["Fecha", "Hora", "Sucursal", "Cajero", "Efectivo", "Tarjeta", "Transferencia", "Total_Ventas", "Nota"]], use_container_width=True, hide_index=True)
                    
                    st.markdown(generate_html_download(df_caja, f"Reporte_Cajas_{c_in}_al_{c_fi}.csv", "DESCARGAR REPORTE COMPLETO"), unsafe_allow_html=True)
                else:
                    st.info("Sin registros de caja en las fechas seleccionadas.")

        with tab_sueldos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">LIQUIDACIÓN DE SUELDOS</div>', unsafe_allow_html=True)
            c_su1, c_su2 = st.columns([1, 2])
            with c_su1:
                with st.form("form_nuevo_sueldo"):
                    st.subheader("ASIGNAR NUEVA TARIFA")
                    emp_s = st.selectbox("Empleado:", ["Seleccionar..."] + sorted(lista_empleados), key="sue_emp")
                    val_s = st.number_input("Valor por Hora ($):", min_value=0.0, step=100.0, key="sue_val")
                    f_ini = st.date_input("Vigente Desde:", value=ahora.date(), key="sue_ini")
                    es_actual = st.checkbox("Tarifa actual (Sin fecha de cierre)", value=True, key="sue_act")
                    f_fin = datetime.date(2099, 12, 31) if es_actual else st.date_input("Vigente Hasta:", value=ahora.date(), key="sue_fin")
                    
                    if st.form_submit_button("GUARDAR TARIFA"):
                        if emp_s == "Seleccionar...":
                            st.warning("Seleccione un empleado.")
                        elif val_s <= 0:
                            st.warning("Ingrese un valor mayor a $0.")
                        elif f_ini > f_fin:
                            st.warning("La fecha 'Desde' no puede ser mayor a 'Hasta'.")
                        else:
                            exito = insert_row("sueldos_historico", {"empleado": emp_s, "fecha_desde": f_ini.strftime("%Y-%m-%d"), "fecha_hasta": f_fin.strftime("%Y-%m-%d"), "valor_hora": val_s})
                            if exito:
                                st.success(f"Tarifa de ${val_s}/h asignada a {emp_s}.")
                                recargar_app()
            with c_su2:
                st.subheader("HISTORIAL DE TARIFAS")
                if sueldos_historico:
                    c_fsu1, c_fsu2 = st.columns(2)
                    f_s_in = c_fsu1.date_input("Filtrar vista desde:", value=ahora.date() - datetime.timedelta(days=30), key="f_s_in")
                    f_s_fi = c_fsu2.date_input("Filtrar vista hasta:", value=ahora.date() + datetime.timedelta(days=365), key="f_s_fi")
                    
                    sueldos_filtrados = []
                    for s in sueldos_historico:
                        try:
                            d_desde = datetime.datetime.strptime(s.get("Fecha_Desde", s.get("fecha_desde")), "%Y-%m-%d").date()
                            d_hasta = datetime.datetime.strptime(s.get("Fecha_Hasta", s.get("fecha_hasta")), "%Y-%m-%d").date() if s.get("Fecha_Hasta", s.get("fecha_hasta")) != "2099-12-31" else datetime.date(2099, 12, 31)
                            if d_desde <= f_s_fi and d_hasta >= f_s_in:
                                sueldos_filtrados.append(s)
                        except:
                            sueldos_filtrados.append(s)

                    if sueldos_filtrados:
                        df_sueldos = pd.DataFrame(sueldos_filtrados).sort_values(by=["Empleado", "Fecha_Desde"], ascending=[True, False])
                        df_mostrar = df_sueldos.copy()
                        if 'id' in df_mostrar.columns:
                            df_mostrar = df_mostrar.drop(columns=['id'])
                        df_mostrar["Fecha_Hasta"] = df_mostrar["Fecha_Hasta"].replace("2099-12-31", "Actualidad")
                        df_mostrar["Valor_Hora"] = df_mostrar["Valor_Hora"].apply(lambda x: f"${float(x):,.2f}")
                        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                        
                        st.write("---")
                        st.write("**CORREGIR O ELIMINAR TARIFAS:**")
                        for s in sueldos_filtrados:
                            s_id = s.get("id")
                            emp_hist = s.get("Empleado", s.get("empleado", ""))
                            v_hora = s.get("Valor_Hora", s.get("valor_hora", 0))
                            f_desde = s.get("Fecha_Desde", s.get("fecha_desde", ""))
                            f_hasta = s.get("Fecha_Hasta", s.get("fecha_hasta", ""))
                            
                            txt_hasta = "Actualidad" if f_hasta == "2099-12-31" else f_hasta
                            with st.expander(f"{emp_hist} | ${float(v_hora):,.2f}/h | {f_desde} - {txt_hasta}"):
                                c_ed1, c_ed2, c_ed3 = st.columns(3)
                                n_val = c_ed1.number_input("Valor ($):", value=float(v_hora), step=100.0, key=f"nval_{s_id}")
                                n_ini = c_ed2.date_input("Desde:", value=datetime.datetime.strptime(f_desde, "%Y-%m-%d").date(), key=f"nini_{s_id}")
                                is_2099 = f_hasta == "2099-12-31"
                                n_fin = c_ed3.date_input("Hasta:", value=datetime.datetime.strptime(f_hasta, "%Y-%m-%d").date() if not is_2099 else ahora.date(), key=f"nfin_{s_id}")
                                n_actual = c_ed3.checkbox("Dejar sin fecha de fin", value=is_2099, key=f"nact_{s_id}")
                                n_fin_str = "2099-12-31" if n_actual else n_fin.strftime("%Y-%m-%d")
                                c_b1, c_b2 = st.columns(2)
                                if c_b1.button("GUARDAR CAMBIOS", key=f"save_s_{s_id}"):
                                    try:
                                        supabase.table("sueldos_historico").update({
                                            'valor_hora': n_val,
                                            'fecha_desde': n_ini.strftime("%Y-%m-%d"),
                                            'fecha_hasta': n_fin_str
                                        }).eq("id", s_id).execute()
                                        recargar_app()
                                    except Exception as e: show_db_error(e, "actualizando tarifa")
                                if c_b2.button("ELIMINAR TARIFA", key=f"del_s_{s_id}"):
                                    try:
                                        supabase.table("sueldos_historico").delete().eq("id", s_id).execute()
                                        recargar_app()
                                    except Exception as e: show_db_error(e, "eliminando tarifa")
                else: 
                    st.info("Sin sueldos configurados. Valor defecto: $0.")

        with tab_horarios:
            st.markdown('<div class="main-title" style="font-size: 2rem;">PLANIFICACIÓN Y HORARIOS</div>', unsafe_allow_html=True)
            
            st.markdown("### AGREGAR FICHAJE MANUAL")
            with st.form("form_add_fichaje"):
                c_add1, c_add2, c_add3 = st.columns(3)
                add_emp = c_add1.selectbox("Empleado:", ["Seleccionar..."] + sorted(lista_empleados), key="add_emp")
                add_fecha = c_add2.date_input("Fecha:", value=ahora.date(), key="add_fec")
                add_hora = c_add3.time_input("Hora:", value=ahora.time(), key="add_hor")

                c_add4, c_add5, c_add6 = st.columns(3)
                add_suc = c_add4.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()), key="add_suc")
                add_turno = c_add5.selectbox("Turno:", ["Seleccionar..."] + list(lista_turnos.keys()) + ["Manual"], key="add_tur")
                add_tipo = c_add6.selectbox("Tipo:", ["Entrada", "Salida"], key="add_tip")

                c_add7, c_add8 = st.columns([1, 2])
                add_estado = c_add7.selectbox("Estado:", ["Automático (Calculado)"] + ESTADOS_POSIBLES, key="add_est")
                add_nota = c_add8.text_input("Nota / Motivo:", key="add_not")

                if st.form_submit_button("GUARDAR FICHAJE"):
                    if "Seleccionar..." in [add_emp, add_suc, add_turno]:
                        st.warning("Seleccione Empleado, Sucursal y Turno.")
                    else:
                        str_hora = add_hora.strftime("%I:%M:%S %p")
                        str_fecha = add_fecha.strftime("%Y-%m-%d")
                        dt_fichaje = datetime.datetime.combine(add_fecha, add_hora)
                        
                        estado_final = add_estado
                        if add_estado == "Automático (Calculado)":
                            if add_turno in lista_turnos:
                                try:
                                    t_ing_obj = datetime.datetime.strptime(lista_turnos[add_turno]["ingreso"], "%I:%M %p").time()
                                    t_sal_obj = datetime.datetime.strptime(lista_turnos[add_turno]["salida"], "%I:%M %p").time()
                                    
                                    dt_ing_ofi = datetime.datetime.combine(add_fecha, t_ing_obj)
                                    dt_sal_ofi = datetime.datetime.combine(add_fecha, t_sal_obj)
                                    
                                    if dt_sal_ofi < dt_ing_ofi:
                                        if add_tipo == "Salida" and add_hora < datetime.time(12, 0): 
                                            dt_ing_ofi -= datetime.timedelta(days=1)
                                        else:
                                            dt_sal_ofi += datetime.timedelta(days=1)

                                    if add_tipo == "Entrada":
                                        tolerancia = int(config_app.get("tolerancia_minutos", 10))
                                        limite_tarde = dt_ing_ofi + datetime.timedelta(minutes=tolerancia)
                                        estado_final = "Tarde" if dt_fichaje > limite_tarde else "A tiempo"
                                    
                                    elif add_tipo == "Salida":
                                        estado_final = "Retiro Temprano" if dt_fichaje < dt_sal_ofi else "Salida"
                                        
                                except Exception as e:
                                    estado_final = "A tiempo" if add_tipo == "Entrada" else "Salida"
                            else:
                                estado_final = "A tiempo" if add_tipo == "Entrada" else "Salida"
                                
                        exito = insert_row("asistencia", {
                            "fecha": str_fecha,
                            "hora": str_hora,
                            "empleado": add_emp,
                            "sucursal": add_suc,
                            "turno": add_turno,
                            "tipo": add_tipo,
                            "estado": estado_final,
                            "distancia_m": 0.0,
                            "nota": f"[Carga Manual] {add_nota}".strip()
                        })
                        if exito:
                            st.success(f"Fichaje guardado. (Estado: {estado_final})")
                            recargar_app()
                            
            st.markdown("---")
            
            st.markdown("### EDITAR FICHAJES EXISTENTES")
            c_edh1, c_edh2 = st.columns(2)
            emp_mod_horario = c_edh1.selectbox("Seleccionar Empleado:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_mod_hor")
            fecha_mod_horario = c_edh2.date_input("Fecha a buscar:", value=ahora.date(), key="f_mod_hor")
            
            if emp_mod_horario != "Seleccionar...":
                df_asist_mod = load_df("asistencia")
                if not df_asist_mod.empty:
                    df_asist_mod = df_asist_mod.reset_index(drop=True)
                    df_fil = df_asist_mod[(df_asist_mod["Empleado"] == emp_mod_horario) & (df_asist_mod["Fecha"] == str(fecha_mod_horario))].reset_index(drop=True)
                    if not df_fil.empty:
                        turnos_del_dia = df_fil["Turno"].unique()
                        for turno_str in turnos_del_dia:
                            st.markdown(f"#### {turno_str}")
                            df_t = df_fil[df_fil["Turno"] == turno_str].reset_index(drop=True)
                            
                            for idx, row in df_t.iterrows():
                                with st.expander(f"{row['Tipo']} - {row['Sucursal']} ({row['Hora']})", expanded=False):
                                    c_m1, c_m2, c_m3 = st.columns(3)
                                    
                                    pd_t = pd.to_datetime(row['Hora'], errors='coerce')
                                    time_val = pd_t.time() if not pd.isna(pd_t) else ahora.time()
                                    pd_f = pd.to_datetime(row['Fecha'], errors='coerce')
                                    date_val = pd_f.date() if not pd.isna(pd_f) else ahora.date()
                                    
                                    nueva_fecha = c_m1.date_input("Fecha:", value=date_val, key=f"fec_{row['id']}")
                                    nueva_hora = c_m2.time_input("Hora:", value=time_val, key=f"time_{row['id']}")
                                    nuevo_tipo = c_m3.selectbox("Tipo:", ["Entrada", "Salida"], index=0 if row['Tipo']=="Entrada" else 1, key=f"tip_{row['id']}")
                                    
                                    c_m4, c_m5, c_m6 = st.columns(3)
                                    
                                    suc_ops = list(lista_locales.keys())
                                    if row['Sucursal'] not in suc_ops: suc_ops.append(row['Sucursal'])
                                    idx_suc = suc_ops.index(row['Sucursal'])
                                    nueva_sucursal = c_m4.selectbox("Sucursal:", suc_ops, index=idx_suc, key=f"suc_{row['id']}")
                                    
                                    turnos_ops = list(lista_turnos.keys()) + ["Manual", "N/A"]
                                    if row['Turno'] not in turnos_ops: turnos_ops.append(row['Turno'])
                                    idx_tur = turnos_ops.index(row['Turno'])
                                    nuevo_turno = c_m5.selectbox("Turno:", turnos_ops, index=idx_tur, key=f"tur_{row['id']}")
                                    
                                    est_ops = ESTADOS_POSIBLES.copy()
                                    if row['Estado'] not in est_ops: est_ops.append(row['Estado'])
                                    idx_est = est_ops.index(row['Estado'])
                                    nuevo_estado = c_m6.selectbox("Estado:", est_ops, index=idx_est, key=f"est_{row['id']}")
                                    
                                    nueva_nota = st.text_input("Nota:", value=row.get('Nota', ''), key=f"not_{row['id']}")
                                    
                                    c_btn1, c_btn2 = st.columns(2)
                                    if c_btn1.button("GUARDAR CAMBIOS", key=f"btn_upd_{row['id']}"):
                                        try:
                                            supabase.table("asistencia").update({
                                                "fecha": nueva_fecha.strftime("%Y-%m-%d"),
                                                "hora": nueva_hora.strftime("%I:%M:%S %p"),
                                                "tipo": nuevo_tipo,
                                                "sucursal": nueva_sucursal,
                                                "turno": nuevo_turno,
                                                "estado": nuevo_estado,
                                                "nota": nueva_nota
                                            }).eq("id", int(row['id'])).execute()
                                            st.success("Fichaje actualizado.")
                                            recargar_app()
                                        except Exception as e: show_db_error(e, "actualizando fichaje")
                                    if c_btn2.button("ELIMINAR FICHAJE", key=f"btn_del_{row['id']}"):
                                        try:
                                            supabase.table("asistencia").delete().eq("id", int(row['id'])).execute()
                                            st.success("Fichaje eliminado.")
                                            recargar_app()
                                        except Exception as e: show_db_error(e, "eliminando fichaje")
                    else:
                        st.info("Sin registros para esta fecha y empleado.")
                        
            st.markdown("---")
            st.subheader("PLANILLA SEMANAL (ROSTER)")
            today_date = ahora.date()
            
            inicio_semana_int = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}.get(config_app.get("dia_inicio_semana", "Lunes"), 0)
            dia_inicio_actual = today_date - datetime.timedelta(days=(today_date.weekday() - inicio_semana_int) % 7)
            
            c_plan1, c_plan2 = st.columns([1,3])
            semana_sel = c_plan1.selectbox("SELECCIONAR SEMANA:", ["Esta Semana", "Semana Próxima", "Semana Anterior", "Elegir Fecha"], key="sel_sem_rost")
            
            if semana_sel == "Esta Semana": start_date_plan = dia_inicio_actual
            elif semana_sel == "Semana Próxima": start_date_plan = dia_inicio_actual + datetime.timedelta(days=7)
            elif semana_sel == "Semana Anterior": start_date_plan = dia_inicio_actual - datetime.timedelta(days=7)
            else:
                start_date_plan = c_plan2.date_input("Elegir Inicio de semana:", value=dia_inicio_actual, key="fec_sem_rost")
                
            if (start_date_plan.weekday() - inicio_semana_int) % 7 != 0: 
                start_date_plan = start_date_plan - datetime.timedelta(days=(start_date_plan.weekday() - inicio_semana_int) % 7)
                
            fechas_semana = [start_date_plan + datetime.timedelta(days=i) for i in range(7)]
            nombres_dias_todos = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            nombres_dias = nombres_dias_todos[inicio_semana_int:] + nombres_dias_todos[:inicio_semana_int]
            cols_fechas = [f"{nombres_dias[i]} {fechas_semana[i].strftime('%d/%m')}" for i in range(7)]
            str_fechas = [f.strftime("%Y-%m-%d") for f in fechas_semana]
            
            nuevos_datos_plan = {}
            opciones_emps = ["Nadie"] + sorted(lista_empleados)
            
            for loc in lista_locales.keys():
                with st.expander(f"SUCURSAL: {loc}", expanded=False):
                    for turno, datos_turno in lista_turnos.items():
                        st.markdown(f"**{turno.upper()}** ({datos_turno.get('ingreso')} - {datos_turno.get('salida')})")
                        data_t = []
                        for i in range(3):
                            row_t = {"Cupo": f"CUPO {i+1}"}
                            for j, f_str in enumerate(str_fechas):
                                try:
                                    emps_asignados = planificacion_turnos.get(f_str, {}).get(loc, {}).get(turno, [])
                                    emp_name = emps_asignados[i] if i < len(emps_asignados) else "Nadie"
                                except: emp_name = "Nadie"
                                row_t[cols_fechas[j]] = emp_name
                            data_t.append(row_t)
                            
                        df_plan_t = pd.DataFrame(data_t)
                        config_cols_t = {"Cupo": st.column_config.TextColumn("Cupo", disabled=True)}
                        for c in cols_fechas: config_cols_t[c] = st.column_config.SelectboxColumn(c, options=opciones_emps, default="Nadie")
                        df_editado_t = st.data_editor(df_plan_t, column_config=config_cols_t, hide_index=True, use_container_width=True, key=f"ed_{loc}_{turno}", num_rows="dynamic")
                        nuevos_datos_plan[(loc, turno)] = df_editado_t
                        st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("GUARDAR PLANIFICACIÓN", use_container_width=True, key="btn_save_rost"):
                errores_duplicados = []
                for f_str in str_fechas:
                    for turno in lista_turnos.keys():
                        control_empleados = {}
                        for loc in lista_locales.keys():
                            df_e = nuevos_datos_plan[(loc, turno)]
                            day_col = cols_fechas[str_fechas.index(f_str)]
                            emps = df_e[day_col].dropna().tolist()
                            emps = [e for e in emps if e != "Nadie" and str(e).strip() != ""]
                            
                            for e in emps:
                                if e in control_empleados:
                                    errores_duplicados.append(f"⚠️ <b>{e}</b> fue asignado a <b>{control_empleados[e]}</b> y a <b>{loc}</b> simultáneamente. (Día: {day_col}, Turno: {turno}).")
                                else:
                                    control_empleados[e] = loc

                if errores_duplicados:
                    conflict_html = "<div class='conflict-box'><div class='conflict-title'>🛑 CONFLICTO DETECTADO</div>"
                    conflict_html += "".join([f"<div class='conflict-item'>{err}</div>" for err in errores_duplicados])
                    conflict_html += "</div>"
                    st.markdown(conflict_html, unsafe_allow_html=True)
                else:
                    try:
                        inserts = []
                        for f_str in str_fechas:
                            supabase.table("planificacion_turnos").delete().eq("fecha", f_str).execute()
                            for loc in lista_locales.keys():
                                for turno in lista_turnos.keys():
                                    df_e = nuevos_datos_plan[(loc, turno)]
                                    day_col = cols_fechas[str_fechas.index(f_str)]
                                    emps = df_e[day_col].dropna().tolist()
                                    emps = list(dict.fromkeys([e for e in emps if e != "Nadie" and str(e).strip() != ""]))
                                    for e in emps:
                                        inserts.append({"fecha": f_str, "sucursal": loc, "turno": turno, "empleado": e})
                        if inserts:
                            supabase.table("planificacion_turnos").insert(inserts).execute()
                        st.success("Planificación semanal validada y guardada con éxito.")
                        recargar_app()
                    except Exception as e: show_db_error(e, "guardando planificación")
                
            st.markdown("---")
            st.subheader("MATRIZ DE DESVIACIONES (PLAN VS. REAL)")
            
            c_comp1, c_comp2 = st.columns(2)
            filtro_suc_comp = c_comp1.selectbox("FILTRAR POR SUCURSAL:", ["Todas las sucursales"] + list(lista_locales.keys()), key="filtro_suc_comp")
            filtro_tur_comp = c_comp2.selectbox("FILTRAR POR TURNO:", ["Todos los turnos"] + list(lista_turnos.keys()), key="filtro_tur_comp")

            df_asist_comp = load_df("asistencia")
            if not df_asist_comp.empty:
                df_asist_comp = df_asist_comp.reset_index(drop=True)

            html_content = "<div class='roster-wrapper'>"
            hay_datos_para_mostrar = False

            for emp in sorted(lista_empleados):
                dias_html = ""
                emp_tiene_turnos_visibles = False
                
                for j, f_str in enumerate(str_fechas):
                    f_date = datetime.datetime.strptime(f_str, "%Y-%m-%d").date()
                    es_futuro = f_date > today_date
                    es_hoy = f_date == today_date
                    
                    planificados = []
                    for loc, turnos_dict in planificacion_turnos.get(f_str, {}).items():
                        for t_name, emps in turnos_dict.items():
                            if emp in emps:
                                planificados.append({"turno": t_name, "sucursal": loc})
                    
                    reales_hoy = df_asist_comp[(df_asist_comp["Empleado"] == emp) & (df_asist_comp["Fecha"] == f_str)] if not df_asist_comp.empty else pd.DataFrame()
                    reales_entradas = reales_hoy[reales_hoy["Tipo"] == "Entrada"] if not reales_hoy.empty else pd.DataFrame()
                    reales_ausencias = reales_hoy[reales_hoy["Tipo"] == "Ausente"] if not reales_hoy.empty else pd.DataFrame()

                    celdas_html = ""
                    turnos_procesados = set()

                    for plan in planificados:
                        p_tur = plan["turno"]
                        p_loc = plan["sucursal"]
                        turnos_procesados.add(p_tur)
                        
                        if filtro_suc_comp != "Todas las sucursales" and p_loc != filtro_suc_comp: continue
                        if filtro_tur_comp != "Todos los turnos" and p_tur != filtro_tur_comp: continue
                        
                        emp_tiene_turnos_visibles = True
                        
                        if es_futuro:
                            celdas_html += f"<div class='roster-cell c-pend'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>PENDIENTE</div></div>"
                        else:
                            asist = reales_entradas[reales_entradas["Turno"] == p_tur] if not reales_entradas.empty else pd.DataFrame()
                            ausencia = reales_ausencias[reales_ausencias["Turno"] == p_tur] if not reales_ausencias.empty else pd.DataFrame()
                            
                            if not asist.empty:
                                estado_real = asist.iloc[-1]["Estado"]
                                suc_real = asist.iloc[-1]["Sucursal"]
                                if isinstance(estado_real, pd.Series): estado_real = estado_real.iloc[0]
                                if isinstance(suc_real, pd.Series): suc_real = suc_real.iloc[0]
                                
                                if suc_real != p_loc:
                                    celdas_html += f"<div class='roster-cell c-cambio'><div class='sub-txt'>Plan: {p_loc} ({p_tur})</div><div class='main-txt'>🔄 Fichó en: {suc_real}</div></div>"
                                else:
                                    if estado_real == "A tiempo":
                                        celdas_html += f"<div class='roster-cell c-ok'><div class='main-txt'>✓ Cumplido</div></div>"
                                    elif estado_real == "Tarde":
                                        celdas_html += f"<div class='roster-cell c-tarde'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>⚠️ TARDE</div></div>"
                                    else:
                                        celdas_html += f"<div class='roster-cell c-ok'><div class='main-txt'>✓ Cumplido</div></div>"
                            elif not ausencia.empty:
                                celdas_html += f"<div class='roster-cell c-falta'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>❌ AUSENTE REP.</div></div>"
                            else:
                                if es_hoy:
                                    turno_ya_termino = False
                                    try:
                                        hora_salida_str = lista_turnos[p_tur]["salida"]
                                        hora_salida_obj = datetime.datetime.strptime(hora_salida_str, "%I:%M %p").time()
                                        dt_salida = datetime.datetime.combine(today_date, hora_salida_obj).replace(tzinfo=zona_arg)
                                        
                                        if ahora > dt_salida:
                                            turno_ya_termino = True
                                    except:
                                        pass
                                    
                                    if turno_ya_termino:
                                        celdas_html += f"<div class='roster-cell c-falta'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>❌ NO FICHÓ</div></div>"
                                    else:
                                        celdas_html += f"<div class='roster-cell c-pend'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>EN ESPERA</div></div>"
                                else:
                                    celdas_html += f"<div class='roster-cell c-falta'><div class='sub-txt'>Plan: {p_loc} - {p_tur}</div><div class='main-txt'>❌ NO FICHÓ</div></div>"

                    if not es_futuro and not reales_entradas.empty:
                        for idx, row in reales_entradas.iterrows():
                            r_tur = row["Turno"]
                            if isinstance(r_tur, pd.Series): r_tur = r_tur.iloc[0]
                            if r_tur not in turnos_procesados and r_tur != "Manual" and str(r_tur) != "nan":
                                r_suc = row["Sucursal"]
                                if isinstance(r_suc, pd.Series): r_suc = r_suc.iloc[0]
                                
                                if filtro_suc_comp != "Todas las sucursales" and r_suc != filtro_suc_comp: continue
                                if filtro_tur_comp != "Todos los turnos" and r_tur != filtro_tur_comp: continue
                                
                                emp_tiene_turnos_visibles = True
                                celdas_html += f"<div class='roster-cell c-extra'><div class='sub-txt'>🔵 TURNO EXTRA</div><div class='main-txt'>En: {r_suc} - {r_tur}</div></div>"

                    if not celdas_html:
                        if filtro_suc_comp == "Todas las sucursales" and filtro_tur_comp == "Todos los turnos":
                            celdas_html = "<div class='roster-cell c-libre'><div class='main-txt'>Libre</div></div>"
                        else:
                            celdas_html = "<div class='roster-cell c-libre'><div class='main-txt'>-</div></div>"

                    dias_html += f"<div style='display:flex; flex-direction:column; flex:1; border-right: 1px solid #1A1A1A;'><div style='font-size:0.7rem; color:#737373; text-align:center; padding:5px 0; border-bottom:1px solid #1A1A1A; font-weight: 600; letter-spacing: 1px;'>{cols_fechas[j]}</div><div style='display:flex; flex-direction:column; height:100%;'>{celdas_html}</div></div>"

                if emp_tiene_turnos_visibles or (filtro_suc_comp == "Todas las sucursales" and filtro_tur_comp == "Todos los turnos"):
                    hay_datos_para_mostrar = True
                    html_content += f"<div class='roster-row'><div class='roster-emp'>{emp}</div><div class='roster-days'>{dias_html}</div></div>"
                    
            html_content += "</div>"

            if hay_datos_para_mostrar:
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("No hay planificaciones que coincidan con los filtros seleccionados.")

            st.markdown("<br>", unsafe_allow_html=True)
            df_export_roster = pd.DataFrame([{"Info": "Para ver la data cruda, descárguela desde la sección Analytics."}])
            st.markdown(generate_html_download(df_export_roster, f"Comparativa_Horarios_Resumen.csv", "DESCARGAR DATA PLANA (CSV)"), unsafe_allow_html=True)

        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">RANKING CORPORATIVO</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns([1,3])
            filtro_p = c_fil1.selectbox("FILTRAR RANKING:", ["Período Activo (Desde Reseteo)", "Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_p_gr")
            rango_punt = c_fil2.date_input("FECHAS:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date()), key="rango_p_gr") if filtro_p == "Personalizado" else None
            
            if filtro_p == "Período Activo (Desde Reseteo)":
                f_ini_pts = config_app.get("fecha_inicio_puntos", ahora.date().replace(day=1).strftime("%Y-%m-%d"))
                p_in, p_fi = datetime.datetime.strptime(f_ini_pts, "%Y-%m-%d").date(), ahora.date()
            else: p_in, p_fi = get_fechas_filtro(filtro_p, rango_punt)
            
            df_p, df_t = load_df("asistencia"), load_df("tareas_log")
            if not df_p.empty:
                df_p['F_Obj'] = pd.to_datetime(df_p['Fecha'], errors='coerce').dt.date
                df_p = df_p[(df_p['F_Obj'] >= p_in) & (df_p['F_Obj'] <= p_fi)]
            if not df_t.empty:
                df_t['F_Obj'] = pd.to_datetime(df_t['Fecha'], errors='coerce').dt.date
                df_t = df_t[(df_t['F_Obj'] >= p_in) & (df_t['F_Obj'] <= p_fi)]
                
            reg = config_app.get("reglas_puntos", {})
            ajustes_per = [p for p in lista_puntos if p_in <= datetime.datetime.strptime(p.get('Fecha', p.get('fecha')), "%Y-%m-%d").date() <= p_fi]
            ranking_data = []
            
            for emp in lista_empleados:
                e_aj = sum([int(p.get('Puntos', p.get('puntos', 0))) for p in ajustes_per if p.get('Empleado', p.get('empleado')) == emp and p.get('Estado', p.get('estado', 'Aprobada')) == 'Aprobada'])
                e_tp = pd.to_numeric(df_t[(df_t["Empleado"] == emp) & (df_t["Estado"] == "Aprobada")]["Puntos"], errors='coerce').fillna(0).astype(int).sum() if not df_t.empty else 0
                df_e = df_p[df_p["Empleado"] == emp] if not df_p.empty else pd.DataFrame()
                e_ok = len(df_e[df_e["Estado"] == "A tiempo"]) if not df_e.empty else 0
                e_tar = len(df_e[df_e["Estado"] == "Tarde"]) if not df_e.empty else 0
                e_au = len(df_e[df_e["Tipo"] == "Ausente"]) if not df_e.empty else 0
                puntaje = reg.get('base', 100) + (e_ok * reg.get('A tiempo', 0)) + (e_tar * reg.get('Tarde', -5)) + (e_au * reg.get('Ausente', -15)) + e_aj + e_tp
                ranking_data.append({"Personal": emp, "Nivel": calcular_nivel(puntaje), "PUNTOS": puntaje, "Pts Tareas": e_tp, "Ajustes": e_aj, "Tardes": e_tar, "Faltas": e_au})
                
            st.dataframe(pd.DataFrame(ranking_data).sort_values(by="PUNTOS", ascending=False), use_container_width=True, hide_index=True)
            st.markdown("---")
            
            st.subheader("AUDITORÍA DE PUNTUACIÓN")
            if puntos_cajero_pendientes:
                for pt in puntos_cajero_pendientes:
                    if pt.get("Estado", pt.get("estado")) == "Pendiente de auditoría":
                        pt_id = pt.get("id")
                        pt_sug = pt.get("Puntos_Sugeridos", pt.get("puntos_sugeridos", 0))
                        st.markdown(f"<div class='task-pend'><b>{pt.get('Emisor', pt.get('emisor'))}</b> sugiere {'sumar' if pt_sug > 0 else 'restar'} <b>{abs(pt_sug)} pts</b> a <b>{pt.get('Compañero', pt.get('compañero'))}</b><br>Motivo: <i>{pt.get('Motivo', pt.get('motivo'))}</i></div>", unsafe_allow_html=True)
                        
                        recompensa_cajero = st.number_input(f"Bono para el auditor '{pt.get('Emisor', pt.get('emisor'))}':", value=int(config_app.get("recompensa_auditoria_cajero", 10)), step=1, key=f"rec_cajero_{pt_id}")
                        
                        c1, c2, c3 = st.columns([1,1,2])
                        if c1.button("APROBAR", key=f"apr_caj_{pt_id}"):
                            try:
                                insert_row("ajustes_puntos", {
                                    "fecha": pt.get("Fecha", pt.get("fecha")), 
                                    "empleado": pt.get("Compañero", pt.get("compañero")), 
                                    "puntos": pt_sug, 
                                    "motivo": f"[{pt.get('Emisor', pt.get('emisor'))}] {pt.get('Motivo', pt.get('motivo'))}", 
                                    "autor": "Gerencia", 
                                    "estado": "Aprobada"
                                })
                                
                                emisor_actual = pt.get("Emisor", pt.get("emisor"))
                                rol_emisor = roles_empleados.get(emisor_actual, "")
                                if recompensa_cajero > 0 and rol_emisor == "Cajero":
                                    insert_row("ajustes_puntos", {
                                        "fecha": fecha_hoy, 
                                        "empleado": emisor_actual, 
                                        "puntos": recompensa_cajero, 
                                        "motivo": "Bono por auditoría de personal.", 
                                        "autor": "Gerencia", 
                                        "estado": "Aprobada"
                                    })
                                
                                supabase.table("puntos_cajero_pendientes").update({"estado": "Aprobado"}).eq("id", pt_id).execute()
                                st.success("Procesado.")
                                recargar_app()
                            except Exception as e: show_db_error(e, "aprobando sugerencia")
                            
                        if c2.button("DENEGAR", key=f"den_caj_{pt_id}"):
                            try:
                                supabase.table("puntos_cajero_pendientes").update({"estado": "Rechazado"}).eq("id", pt_id).execute()
                                st.info("Descartado.")
                                recargar_app()
                            except Exception as e: show_db_error(e, "denegando sugerencia")
            else:
                st.info("Sin auditorías pendientes.")
            
            st.markdown("---")
            st.subheader("APLICAR BONO O MULTA")
            with st.form("form_bonos"):
                c_b1, c_b2, c_b3, c_b4 = st.columns([2,1,1,2])
                ap_emp = c_b1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados), key="ab_emp")
                ap_fecha = c_b2.date_input("Fecha:", ahora.date(), key="ab_fec")
                ap_puntos = c_b3.number_input("Puntos (+/-):", value=0, step=1, key="ab_pts")
                ap_motivo = c_b4.text_input("Motivo:", key="ab_mot")
                if st.form_submit_button("APLICAR AJUSTE"):
                    if ap_emp == "Seleccionar...":
                        st.warning("Datos incompletos.")
                    else:
                        exito = insert_row("ajustes_puntos", {"fecha": ap_fecha.strftime("%Y-%m-%d"), "empleado": ap_emp, "puntos": ap_puntos, "motivo": ap_motivo.strip(), "autor": "Gerencia", "estado": "Aprobada"})
                        if exito:
                            st.success("Ajuste aplicado.")
                            recargar_app()

        with tab_tareas:
            st.subheader("SOLICITUDES DE RETIRO TEMPRANO")
            if salidas_pendientes:
                for sp in salidas_pendientes:
                    sp_id = sp.get("id")
                    emp_sp = sp.get('Empleado', sp.get('empleado'))
                    hor_sp = sp.get('Hora', sp.get('hora'))
                    aut_sp = sp.get('Autor', sp.get('autor'))
                    not_sp = sp.get('Nota', sp.get('nota'))
                    st.markdown(f"<div class='task-pend'><b>{emp_sp}</b> solicitó retiro: <b>{hor_sp}</b> (Auditor: {aut_sp})<br>Motivo: <i>{not_sp}</i></div>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if c1.button("APROBAR", key=f"apr_sal_{sp_id}"):
                        try:
                            insert_row("asistencia", {"fecha": sp.get("Fecha", sp.get("fecha")), "hora": hor_sp, "empleado": emp_sp, "sucursal": sp.get("Sucursal", sp.get("sucursal")), "turno": sp.get("Turno", sp.get("turno")), "tipo": "Salida", "estado": "Retiro Temprano", "nota": not_sp})
                            supabase.table("salidas_pendientes").delete().eq("id", sp_id).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "aprobando salida")
                    if c2.button("DENEGAR", key=f"den_sal_{sp_id}"):
                        try:
                            supabase.table("salidas_pendientes").delete().eq("id", sp_id).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "denegando salida")
            else:
                st.info("Sin solicitudes pendientes.")
                
            st.markdown("---")
            st.subheader("CORRECCIONES DE INGRESO (OLVIDOS)")
            if correcciones_pendientes:
                for cp in correcciones_pendientes:
                    cp_id = cp.get("id")
                    emp_cp = cp.get('Empleado', cp.get('empleado'))
                    fec_cp = cp.get('Fecha', cp.get('fecha'))
                    hor_cp = cp.get('Hora_Real', cp.get('hora_real'))
                    suc_cp = cp.get('Sucursal', cp.get('sucursal'))
                    tur_cp = cp.get('Turno', cp.get('turno'))
                    mot_cp = cp.get('Motivo', cp.get('motivo'))
                    st.markdown(f"<div class='task-pend'><b>{emp_cp}</b> declaró ingreso: <b>{hor_cp}</b> el {fec_cp} en {suc_cp} ({tur_cp}).<br>Motivo: <i>{mot_cp}</i></div>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    
                    pts_penalidad = config_app.get("reglas_puntos", {}).get("Olvido Fichaje", -10)
                    
                    if c1.button(f"APROBAR E IMPUTAR ({pts_penalidad} PTS)", key=f"apr_olv_{cp_id}"):
                        try:
                            df_asist_olv = load_df("asistencia")
                            if not df_asist_olv.empty:
                                df_asist_olv = df_asist_olv.reset_index(drop=True)
                            ya_existe = False
                            id_modificar = None
                            
                            if not df_asist_olv.empty:
                                filtro = df_asist_olv[(df_asist_olv["Empleado"] == emp_cp) & (df_asist_olv["Fecha"] == fec_cp) & (df_asist_olv["Tipo"] == "Entrada") & (df_asist_olv["Turno"] == tur_cp)].reset_index(drop=True)
                                if not filtro.empty:
                                    id_modificar = filtro.iloc[-1]["id"]
                                    if isinstance(id_modificar, pd.Series):
                                        id_modificar = id_modificar.iloc[0]
                                    ya_existe = True
                            
                            estado_final = "A tiempo"
                            try:
                                t_ing_obj = datetime.datetime.strptime(lista_turnos[tur_cp]["ingreso"], "%I:%M %p").time()
                                dt_ing_ofi = datetime.datetime.combine(datetime.datetime.strptime(fec_cp, "%Y-%m-%d").date(), t_ing_obj)
                                dt_fichaje_real = datetime.datetime.combine(datetime.datetime.strptime(fec_cp, "%Y-%m-%d").date(), datetime.datetime.strptime(hor_cp, "%I:%M:%S %p").time())
                                
                                tolerancia = int(config_app.get("tolerancia_minutos", 10))
                                if dt_fichaje_real > (dt_ing_ofi + datetime.timedelta(minutes=tolerancia)):
                                    estado_final = "Tarde"
                            except: pass
                            
                            nota_final = f"[Corregido por Gerencia] {mot_cp}"
                            
                            if ya_existe:
                                supabase.table("asistencia").update({
                                    "hora": hor_cp,
                                    "estado": estado_final,
                                    "nota": nota_final
                                }).eq("id", int(id_modificar)).execute()
                            else:
                                insert_row("asistencia", {
                                    "fecha": fec_cp,
                                    "hora": hor_cp,
                                    "empleado": emp_cp,
                                    "sucursal": suc_cp,
                                    "turno": tur_cp,
                                    "tipo": "Entrada",
                                    "estado": estado_final,
                                    "distancia_m": 0.0,
                                    "nota": nota_final
                                })
                            
                            insert_row("ajustes_puntos", {
                                "fecha": str(fecha_hoy),
                                "empleado": emp_cp,
                                "puntos": pts_penalidad,
                                "motivo": "Penalidad automática: Omisión de registro operativo.",
                                "autor": "Gerencia",
                                "estado": "Aprobada"
                            })
                            
                            supabase.table("correcciones_pendientes").delete().eq("id", cp_id).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "corrigiendo ingreso")
                        
                    if c2.button("DENEGAR", key=f"den_olv_{cp_id}"):
                        try:
                            supabase.table("correcciones_pendientes").delete().eq("id", cp_id).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "denegando corrección")
            else:
                st.info("Sin correcciones pendientes.")

            st.markdown("---")
            st.subheader("TAREAS OPERATIVAS PENDIENTES")
            df_tl_all = load_df("tareas_log")
            if not df_tl_all.empty:
                pend_tareas = df_tl_all[df_tl_all["Estado"] == "Pendiente"]
                for idx, row in pend_tareas.iterrows():
                    c_p1, c_p2, c_p3 = st.columns([4, 1, 1])
                    c_p1.markdown(f"**{row['Empleado']}** reportó: '{row['Tarea']}' (+{row['Puntos']} pts)")
                    if c_p2.button("APROBAR", key=f"apr_t_{row['id']}"):
                        try:
                            supabase.table("tareas_log").update({"estado": "Aprobada"}).eq("id", int(row['id'])).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "aprobando tarea")
                    if c_p3.button("RECHAZAR", key=f"rec_t_{row['id']}"):
                        try:
                            supabase.table("tareas_log").update({"estado": "Rechazada"}).eq("id", int(row['id'])).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "rechazando tarea")
                        
            puntos_pendientes = [p for p in lista_puntos if p.get("Estado", p.get("estado")) == "Pendiente"]
            if puntos_pendientes:
                st.write("**EVALUACIONES PENDIENTES:**")
                for p in lista_puntos:
                    if p.get("Estado", p.get("estado")) == "Pendiente":
                        p_id = p.get("id")
                        c_pp1, c_pp2, c_pp3 = st.columns([4, 1, 1])
                        c_pp1.markdown(f"**{p.get('Autor', p.get('autor'))}** sugiere **{p.get('Puntos', p.get('puntos'))} pts** a **{p.get('Empleado', p.get('empleado'))}** (Motivo: {p.get('Motivo', p.get('motivo'))})")
                        if c_pp2.button("APROBAR", key=f"apr_p_{p_id}"):
                            try:
                                supabase.table("ajustes_puntos").update({"estado": "Aprobada"}).eq("id", p_id).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "aprobando puntos")
                        if c_pp3.button("RECHAZAR", key=f"rec_p_{p_id}"):
                            try:
                                supabase.table("ajustes_puntos").update({"estado": "Rechazada"}).eq("id", p_id).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "rechazando puntos")
                            
            st.subheader("BUZÓN DE REPORTES")
            for r in reportes_log:
                if r.get("Estado", r.get("estado")) == "Pendiente de lectura":
                    r_id = r.get("id")
                    st.markdown(f"<div class='report-box'><b>REPORTE RECIBIDO</b> | {r.get('Fecha', r.get('fecha'))} {r.get('Hora', r.get('hora'))}<br><b>Emisor:</b> {r.get('Emisor', r.get('emisor'))} | <b>Categoría:</b> {r.get('Tipo', r.get('tipo'))}<br><b>Detalle:</b> <i>'{r.get('Detalle', r.get('detalle'))}'</i></div>", unsafe_allow_html=True)
                    if st.button("MARCAR COMO VISTO", key=f"visto_rep_{r_id}"):
                        try:
                            supabase.table("reportes").update({"estado": "Visto"}).eq("id", r_id).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "marcando reporte")

        with tab_perfil:
            st.markdown('<div class="main-title" style="font-size: 2rem;">DOSSIER INDIVIDUAL 360°</div>', unsafe_allow_html=True)
            col_pf1, col_pf2 = st.columns([1,3])
            emp_perfil = col_pf1.selectbox("SELECCIONAR EMPLEADO:", ["Seleccionar..."] + sorted(lista_empleados), key="sel_perf_emp")
            filtro_pf = col_pf2.selectbox("PERÍODO A EVALUAR:", ["Este Mes", "Mes Anterior", "Esta Semana", "Todo el Historial"], key="filtro_perf")
            pf_in, pf_fi = get_fechas_filtro(filtro_pf)
            
            if emp_perfil != "Seleccionar...":
                st.write(f"**ROL:** `{roles_empleados.get(emp_perfil, 'N/A')}` | **ESTADO:** {'Conectado' if emp_perfil in dispositivos_vinculados else 'Desconectado'}")
                df_act_p, df_tar_p = load_df("asistencia"), load_df("tareas_log")
                if not df_act_p.empty:
                    df_act_p = df_act_p.reset_index(drop=True)
                if not df_tar_p.empty:
                    df_tar_p = df_tar_p.reset_index(drop=True)
                if not df_act_p.empty:
                    df_act_p['F_Obj'] = pd.to_datetime(df_act_p['Fecha'], errors='coerce').dt.date
                    df_e_p = df_act_p[(df_act_p["Empleado"] == emp_perfil) & (df_act_p['F_Obj'] >= pf_in) & (df_act_p['F_Obj'] <= pf_fi)].copy().reset_index(drop=True)
                    e_atiempo = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "A tiempo")])
                    e_tardes = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "Tarde")])
                    e_ausencias = len(df_e_p[df_e_p["Tipo"] == "Ausente"])
                    
                    df_e_p['Timestamp'] = pd.to_datetime(df_e_p['Fecha'].astype(str) + ' ' + df_e_p['Hora'].astype(str), errors='coerce')
                    df_e_p = df_e_p.dropna(subset=['Timestamp']).sort_values(by="Timestamp")
                    
                    entrada_actual = None
                    horas_totales = 0.0
                    
                    def procesar_tramo_perfil(entrada_row, salida_row):
                        h_in = entrada_row["Timestamp"]
                        t_eval = str(entrada_row["Turno"]).strip()
                        h_tramo = 0.0
                        h_out_real = salida_row["Timestamp"] if salida_row is not None else None
                        
                        if not h_out_real:
                            if t_eval in lista_turnos:
                                try:
                                    t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                    h_out_real = datetime.datetime.combine(h_in.date(), t_out_obj)
                                    if h_out_real < h_in: h_out_real += datetime.timedelta(days=1)
                                except: h_out_real = h_in
                            else:
                                h_out_real = h_in
                        
                        if t_eval in lista_turnos:
                            try:
                                t_in_obj = pd.to_datetime(lista_turnos[t_eval].get("ingreso")).time()
                                t_out_obj = pd.to_datetime(lista_turnos[t_eval].get("salida")).time()
                                h_in_ofi = datetime.datetime.combine(h_in.date(), t_in_obj)
                                h_out_ofi = datetime.datetime.combine(h_in.date(), t_out_obj)
                                if h_out_ofi < h_in_ofi: h_out_ofi += datetime.timedelta(days=1)
                                
                                if (h_in_ofi - h_in).total_seconds() > 43200:
                                    h_in_ofi -= datetime.timedelta(days=1); h_out_ofi -= datetime.timedelta(days=1)
                                elif (h_in - h_in_ofi).total_seconds() > 43200:
                                    h_in_ofi += datetime.timedelta(days=1); h_out_ofi += datetime.timedelta(days=1)
                                    
                                h_tramo_oficial = (h_out_ofi - h_in_ofi).total_seconds() / 3600.0
                                
                                minutos_tarde = (h_in - h_in_ofi).total_seconds() / 60.0
                                if get_bool_config("desc_tarde", True):
                                    tolerancia_m = int(config_app.get("tolerancia_minutos", 10))
                                    if get_bool_config("perdonar_tolerancia", True) and (minutos_tarde <= tolerancia_m):
                                        desc_in = 0.0
                                    else:
                                        desc_in = max(0.0, minutos_tarde / 60.0)
                                else:
                                    desc_in = 0.0
                                    
                                desc_out = (h_out_ofi - h_out_real).total_seconds() / 3600.0 if get_bool_config("desc_temp", True) else 0.0
                                
                                desc_in = max(0.0, desc_in)
                                desc_out = max(0.0, desc_out)
                                
                                h_tramo = h_tramo_oficial - desc_in - desc_out
                            except:
                                h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                        else:
                            h_tramo = (h_out_real - h_in).total_seconds() / 3600.0
                            
                        return max(0.0, h_tramo)

                    for _, row_f in df_e_p.iterrows():
                        tipo_reg = str(row_f["Tipo"]).strip()
                        if tipo_reg == "Entrada":
                            if entrada_actual is not None:
                                horas_totales += procesar_tramo_perfil(entrada_actual, None)
                            entrada_actual = row_f
                        elif tipo_reg in ["Salida", "Salida Automática", "Salida (Cambio Local)", "Retiro Temprano"] and entrada_actual is not None:
                            horas_totales += procesar_tramo_perfil(entrada_actual, row_f)
                            entrada_actual = None
                            
                    if entrada_actual is not None:
                        horas_totales += procesar_tramo_perfil(entrada_actual, None)
                        
                    e_aj = sum([int(p.get('Puntos', p.get('puntos', 0))) for p in lista_puntos if p.get('Empleado', p.get('empleado')) == emp_perfil and p.get('Estado', p.get('estado', 'Aprobada')) == 'Aprobada' and pf_in <= datetime.datetime.strptime(p.get('Fecha', p.get('fecha')), "%Y-%m-%d").date() <= pf_fi])
                    e_tp = 0
                    if not df_tar_p.empty:
                        df_tar_p['F_Obj'] = pd.to_datetime(df_tar_p['Fecha'], errors='coerce').dt.date
                        e_tp = pd.to_numeric(df_tar_p[(df_tar_p["Empleado"] == emp_perfil) & (df_tar_p["Estado"] == "Aprobada") & (df_tar_p['F_Obj'] >= pf_in) & (df_tar_p['F_Obj'] <= pf_fi)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
                        
                    reg = config_app.get("reglas_puntos", {})
                    puntaje = reg.get('base', 100) + (e_atiempo * reg.get('A tiempo', 0)) + (e_tardes * reg.get('Tarde', -5)) + (e_ausencias * reg.get('Ausente', -15)) + e_aj + e_tp
                    c_pf1, c_pf2, c_pf3, c_pf4 = st.columns(4)
                    
                    c_pf1.metric("HORAS TRABAJADAS", formato_horas_texto(horas_totales))
                    c_pf2.metric("STATUS", f"{puntaje} PTS")
                    c_pf3.metric("TARDANZAS", e_tardes)
                    c_pf4.metric("AUSENCIAS", e_ausencias)
                    
                    with st.expander("FICHA DETALLADA"):
                        if 'id' in df_e_p.columns:
                            df_e_p['id_num'] = pd.to_numeric(df_e_p['id'], errors='coerce')
                            df_e_p = df_e_p.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_e_p[["Fecha", "Hora", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]], use_container_width=True, hide_index=True)

        with tab_staff:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader("ESTADO DE TERMINALES")
                datos_conexion = []
                for emp in sorted(lista_empleados):
                    estado_cel = "CONECTADO" if emp in dispositivos_vinculados else "DESCONECTADO"
                    datos_conexion.append({"Empleado": emp, "Estado": estado_cel})
                st.dataframe(pd.DataFrame(datos_conexion), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("ALTA DE PERSONAL")
                with st.form("form_alta_emp"):
                    nuevo_emp = st.text_input("Nombre Operario:", key="alta_n_emp")
                    rol_asignar = st.selectbox("Designación:", lista_roles_disponibles, key="alta_r_emp")
                    if st.form_submit_button("REGISTRAR") and nuevo_emp:
                        n_emp = nuevo_emp.strip()
                        if any(e.lower() == n_emp.lower() for e in lista_empleados):
                            st.error("Registro duplicado.")
                        else:
                            try:
                                supabase.table("empleados").insert({"nombre": n_emp, "rol": rol_asignar, "dispositivo_id": ""}).execute()
                                st.success("Registrado correctamente.")
                                recargar_app()
                            except Exception as e: show_db_error(e, "agregando empleado")
                        
                if lista_empleados:
                    st.markdown("---")
                    st.markdown("**EDICIÓN DE PERSONAL**")
                    emp_mod = st.selectbox("Seleccionar:", sorted(lista_empleados), key="mod_sel_emp")
                    nuevo_nombre_mod = st.text_input("Corregir Nombre:", value=emp_mod, key="mod_nom_emp")
                    nuevo_rol = st.selectbox("Modificar Rol:", lista_roles_disponibles, index=lista_roles_disponibles.index(roles_empleados.get(emp_mod, lista_roles_disponibles[0])) if roles_empleados.get(emp_mod) in lista_roles_disponibles else 0, key="mod_rol_emp")
                    c_mod1, c_mod2, c_mod3 = st.columns(3)
                    
                    if c_mod1.button("GUARDAR", key="btn_save_emp"):
                        nn = nuevo_nombre_mod.strip()
                        if nn and nn != emp_mod:
                            if any(e.lower() == nn.lower() for e in lista_empleados):
                                st.error("Nombre en uso.")
                            else:
                                try:
                                    supabase.table("empleados").update({"nombre": nn, "rol": nuevo_rol}).eq("nombre", emp_mod).execute()
                                    try: supabase.table("ajustes_puntos").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("ajustes_puntos").update({"autor": nn}).eq("autor", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("salidas_pendientes").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("salidas_pendientes").update({"autor": nn}).eq("autor", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("correcciones_pendientes").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("reportes").update({"emisor": nn}).eq("emisor", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("reportes").update({"implicado": nn}).eq("implicado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("alertas_ingreso").update({"destinatario": nn}).eq("destinatario", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("mensajes").update({"destinatario": nn}).eq("destinatario", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("sueldos_historico").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("cierres_caja").update({"cajero": nn}).eq("cajero", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("planificacion_turnos").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("asistencia").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("tareas_log").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    try: supabase.table("tareas_individuales").update({"empleado": nn}).eq("empleado", emp_mod).execute()
                                    except: pass
                                    
                                    st.success(f"Nombre actualizado a {nn} en toda la base de datos.")
                                    recargar_app()
                                except Exception as e: show_db_error(e, "actualizando empleado")
                        else:
                            try:
                                supabase.table("empleados").update({"rol": nuevo_rol}).eq("nombre", emp_mod).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "actualizando rol")
                        
                    if c_mod2.button("LIBERAR TERMINAL", key="btn_lib_term") and emp_mod in dispositivos_vinculados:
                        try:
                            supabase.table("empleados").update({"dispositivo_id": ""}).eq("nombre", emp_mod).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "liberando celular")
                    if c_mod3.button("BORRAR PERFIL", key="btn_del_emp"):
                        try:
                            supabase.table("empleados").delete().eq("nombre", emp_mod).execute()
                            try: supabase.table("tareas_individuales").delete().eq("empleado", emp_mod).execute()
                            except: pass
                            recargar_app()
                        except Exception as e: show_db_error(e, "borrando empleado")
                        
            with col_s2:
                st.subheader("ASIGNACIÓN OPERATIVA")
                tipo_asig = st.radio("Destino:", ["Rol General", "Personal"], key="radio_tipo_asig")
                obj_tarea = st.selectbox("Elegir:", lista_roles_disponibles if tipo_asig == "Rol General" else sorted(lista_empleados), key="sel_obj_tarea")
                n_tarea, p_tarea = st.text_input("Operación:", key="input_n_tarea"), st.number_input("Puntos:", value=5, min_value=1, key="input_p_tarea")
                
                if st.button("ASIGNAR", key="btn_asignar_t") and n_tarea:
                    try:
                        if tipo_asig == "Rol General":
                            supabase.table("tareas_roles").insert({"rol": obj_tarea, "tarea": n_tarea, "puntos": p_tarea}).execute()
                        else:
                            supabase.table("tareas_individuales").insert({"empleado": obj_tarea, "tarea": n_tarea, "puntos": p_tarea}).execute()
                        recargar_app()
                    except Exception as e: show_db_error(e, "asignando tarea")
                    
                ver_t_tipo = st.radio("Ver operativas de:", ["Roles", "Personales"], key="radio_ver_t")
                diccionario_ver = tareas_roles if ver_t_tipo == "Roles" else tareas_individuales
                for clave, tareas in diccionario_ver.items():
                    if tareas:
                        with st.expander(f"{clave}"):
                            for t in tareas:
                                t_id = t.get("id")
                                c_t1, c_t2 = st.columns([3,1])
                                c_t1.write(f"- {t.get('tarea')} (+{t.get('puntos')})")
                                if c_t2.button("ELIMINAR", key=f"del_t_mod_{t_id}"):
                                    try:
                                        supabase.table("tareas_roles" if ver_t_tipo == "Roles" else "tareas_individuales").delete().eq("id", t_id).execute()
                                        recargar_app()
                                    except Exception as e: show_db_error(e, "eliminando tarea")

        with tab_tiendas:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("LOCACIONES")
                for loc, d_loc in lista_locales.items(): 
                    st.write(f"- **{loc}** | IP: `{d_loc.get('ip', 'Ninguna')}` | Lat: {d_loc.get('lat')} | Lon: {d_loc.get('lon')}")
                st.markdown("---")
                ip_gerencia = st.session_state.get('client_ip')
                if not ip_gerencia:
                    ip_eval = streamlit_js_eval(js_expressions="fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')", want_output=True, key="ip_manager_tiendas")
                    if ip_eval:
                        st.session_state['client_ip'] = ip_eval
                        ip_gerencia = ip_eval
                if ip_gerencia and ip_gerencia != 'Error':
                    st.info(f"IP LOCAL ACTUAL: `{ip_gerencia}`")
                else: st.info("Sondeando IP local...")
                
                with st.expander("ALTA DE LOCACIÓN", expanded=False):
                    n_loc = st.text_input("Designación:", key="input_alta_loc")
                    lat_loc = st.number_input("Latitud:", format="%.6f", key="input_lat_loc")
                    lon_loc = st.number_input("Longitud:", format="%.6f", key="input_lon_loc")
                    ip_loc = st.text_input("IP (Red Oficial):", key="input_ip_loc")
                    if st.button("REGISTRAR LOCACIÓN", key="btn_reg_loc") and n_loc:
                        try:
                            supabase.table("locales").insert({"nombre": n_loc, "lat": lat_loc, "lon": lon_loc, "ip": ip_loc.strip()}).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "creando tienda")
                        
                st.markdown("---")
                st.markdown("**EDICIÓN DE LOCACIÓN**")
                loc_mod = st.selectbox("Seleccionar:", ["Seleccionar..."] + list(lista_locales.keys()), key="sel_mod_loc")
                if loc_mod != "Seleccionar...":
                    n_loc_mod = st.text_input("Modificar Designación:", value=loc_mod, key="mod_n_loc")
                    lat_mod = st.number_input("Modificar Lat:", value=float(lista_locales[loc_mod].get("lat", 0.0)), format="%.6f", key="mod_lat_loc")
                    lon_mod = st.number_input("Modificar Lon:", value=float(lista_locales[loc_mod].get("lon", 0.0)), format="%.6f", key="mod_lon_loc")
                    ip_mod = st.text_input("Modificar IP:", value=lista_locales[loc_mod].get("ip", ""), key="mod_ip_loc")
                    
                    if st.button("GUARDAR CAMBIOS", key="btn_save_loc"):
                        nuevo_nombre = n_loc_mod.strip()
                        if nuevo_nombre and nuevo_nombre != loc_mod:
                            if nuevo_nombre not in lista_locales:
                                try:
                                    supabase.table("locales").update({"nombre": nuevo_nombre, "lat": lat_mod, "lon": lon_mod, "ip": ip_mod.strip()}).eq("nombre", loc_mod).execute()
                                    try: supabase.table("planificacion_turnos").update({"sucursal": nuevo_nombre}).eq("sucursal", loc_mod).execute()
                                    except: pass
                                    try: supabase.table("asistencia").update({"sucursal": nuevo_nombre}).eq("sucursal", loc_mod).execute()
                                    except: pass
                                    try: supabase.table("cierres_caja").update({"sucursal": nuevo_nombre}).eq("sucursal", loc_mod).execute()
                                    except: pass
                                    recargar_app()
                                except Exception as e: show_db_error(e, "actualizando tienda")
                            else:
                                st.warning("Designación en uso.")
                        else:
                            try:
                                supabase.table("locales").update({"lat": lat_mod, "lon": lon_mod, "ip": ip_mod.strip()}).eq("nombre", loc_mod).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "actualizando tienda")

                st.markdown("---")
                borrar_loc = st.selectbox("Dar de baja locación:", ["Seleccionar..."] + list(lista_locales.keys()), key="sel_del_loc")
                if st.button("ELIMINAR", key="btn_del_loc") and borrar_loc != "Seleccionar...":
                    try:
                        supabase.table("locales").delete().eq("nombre", borrar_loc).execute()
                        recargar_app()
                    except Exception as e: show_db_error(e, "eliminando tienda")
                    
            with col_l2:
                st.subheader("BLOQUES HORARIOS")
                for turno, horas in lista_turnos.items(): st.write(f"- **{turno}** | {horas.get('ingreso')} - {horas.get('salida')}")
                
                with st.expander("NUEVO BLOQUE", expanded=False):
                    n_turno = st.text_input("Designación:", key="alta_n_turno")
                    c_h1, c_h2 = st.columns(2)
                    h_ingreso, h_salida = c_h1.time_input("Ingreso:", key="alta_h_ing"), c_h2.time_input("Salida:", key="alta_h_sal")
                    if st.button("CREAR", key="btn_crear_tur") and n_turno:
                        try:
                            supabase.table("turnos").insert({"nombre": n_turno, "ingreso": h_ingreso.strftime("%I:%M %p"), "salida": h_salida.strftime("%I:%M %p")}).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "creando horario")
                        
                st.markdown("---")
                st.markdown("**EDICIÓN DE BLOQUES**")
                turno_mod = st.selectbox("Seleccionar:", ["Seleccionar..."] + list(lista_turnos.keys()), key="sel_mod_tur")
                if turno_mod != "Seleccionar...":
                    n_turno_mod = st.text_input("Renombrar:", value=turno_mod, key="mod_n_tur")
                    try:
                        time_ing_def = datetime.datetime.strptime(lista_turnos[turno_mod].get('ingreso'), "%I:%M %p").time()
                        time_sal_def = datetime.datetime.strptime(lista_turnos[turno_mod].get('salida'), "%I:%M %p").time()
                    except:
                        time_ing_def, time_sal_def = ahora.time(), ahora.time()
                        
                    c_hm1, c_hm2 = st.columns(2)
                    hm_ingreso = c_hm1.time_input("Ajustar Ingreso:", value=time_ing_def, key="mod_h_ing")
                    hm_salida = c_hm2.time_input("Ajustar Salida:", value=time_sal_def, key="mod_h_sal")
                    
                    if st.button("GUARDAR", key="btn_save_tur"):
                        nuevo_nombre_t = n_turno_mod.strip()
                        if nuevo_nombre_t and nuevo_nombre_t != turno_mod:
                            if nuevo_nombre_t not in lista_turnos:
                                try:
                                    supabase.table("turnos").update({"nombre": nuevo_nombre_t, "ingreso": hm_ingreso.strftime("%I:%M %p"), "salida": hm_salida.strftime("%I:%M %p")}).eq("nombre", turno_mod).execute()
                                    try: supabase.table("planificacion_turnos").update({"turno": nuevo_nombre_t}).eq("turno", turno_mod).execute()
                                    except: pass
                                    recargar_app()
                                except Exception as e: show_db_error(e, "actualizando horario")
                            else:
                                st.warning("Designación en uso.")
                        else:
                            try:
                                supabase.table("turnos").update({"ingreso": hm_ingreso.strftime("%I:%M %p"), "salida": hm_salida.strftime("%I:%M %p")}).eq("nombre", turno_mod).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "actualizando horario")

                st.markdown("---")
                borrar_turno = st.selectbox("Dar de baja bloque:", ["Seleccionar..."] + list(lista_turnos.keys()), key="sel_del_tur")
                if st.button("ELIMINAR BLOQUE", key="btn_del_tur") and borrar_turno != "Seleccionar...":
                    try:
                        supabase.table("turnos").delete().eq("nombre", borrar_turno).execute()
                        recargar_app()
                    except Exception as e: show_db_error(e, "eliminando turno")

        with tab_comunicados:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.subheader("ALERTA DE RECEPCIÓN")
                with st.form("form_alertas"):
                    dest_ing = st.selectbox("Destino:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados), key="al_dest")
                    txt_alerta = st.text_area("Contenido:", key="al_txt")
                    if st.form_submit_button("EMITIR ALERTA") and txt_alerta:
                        try:
                            supabase.table("alertas_ingreso").insert({"destinatario": dest_ing, "texto": txt_alerta}).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "creando alerta")
                for a in alertas_ingreso:
                    a_id = a.get("id")
                    with st.expander(f"PARA {a.get('destinatario', a.get('Destinatario')).upper()}: {a.get('texto', a.get('Texto'))[:20]}..."):
                        if st.button("ELIMINAR", key=f"del_al_{a_id}"):
                            try:
                                supabase.table("alertas_ingreso").delete().eq("id", a_id).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "eliminando alerta")
                            
            with col_m2:
                st.subheader("ANUNCIO PERMANENTE")
                with st.form("form_fijo"):
                    dest_fijo = st.selectbox("Destino:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados), key="fijo_dest")
                    txt_fijo = st.text_area("Contenido:", key="fijo_txt")
                    if st.form_submit_button("FIJAR ANUNCIO") and txt_fijo:
                        try:
                            supabase.table("mensajes").insert({"destinatario": dest_fijo, "texto": txt_fijo}).execute()
                            recargar_app()
                        except Exception as e: show_db_error(e, "creando anuncio")
                for m in lista_mensajes:
                    m_id = m.get("id")
                    with st.expander(f"PARA {m.get('destinatario', 'Todos').upper()}: {m.get('texto', '')[:20]}..."):
                        st.write(m.get('texto', ''))
                        if st.button("ELIMINAR", key=f"del_msg_{m_id}"):
                            try:
                                supabase.table("mensajes").delete().eq("id", m_id).execute()
                                recargar_app()
                            except Exception as e: show_db_error(e, "eliminando anuncio")

        with tab_config:
            st.subheader("PARÁMETROS DEL SISTEMA")
            with st.form("form_config"):
                st.markdown("### FUNDAMENTOS")
                c_conf1, c_conf2 = st.columns(2)
                nuevo_titulo = c_conf1.text_input("IDENTIFICADOR DEL PORTAL", value=config_app.get("titulo_portal", "PORTAL CORPORATIVO"), key="cfg_tit")
                nueva_pass = c_conf2.text_input("CLAVE GERENCIAL", value=config_app.get("admin_password", "1234"), type="password", key="cfg_pass")
                
                c_conf3, c_conf4 = st.columns(2)
                nueva_tol = c_conf3.number_input("TOLERANCIA (MIN)", value=int(config_app.get("tolerancia_minutos", 10)), key="cfg_tol")
                rad_metros = c_conf4.number_input("RANGO GPS (M)", value=int(config_app.get("radio_metros", 150)), key="cfg_rad")
                
                nuevo_msg_dia = st.text_area("MANTRA / MENSAJE DEL DÍA", value=config_app.get("mensaje_dia", ""), key="cfg_msg")
                msg_tarde = st.text_input("ADVERTENCIA DE TARDANZA", value=config_app.get("mensaje_llegada_tarde", "Llegada fuera de parámetro."), key="cfg_tar")
                
                c_conf5, c_conf6 = st.columns(2)
                rec_cajero = c_conf5.number_input("BONO AUDITORÍA (PTS)", value=int(config_app.get("recompensa_auditoria_cajero", 10)), key="cfg_rec")
                d_semana = c_conf6.selectbox("INICIO DE CICLO", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], index=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].index(config_app.get("dia_inicio_semana", "Lunes")), key="cfg_dia")
                
                try:
                    f_pts_def = datetime.datetime.strptime(config_app.get("fecha_inicio_puntos", ahora.date().replace(day=1).strftime("%Y-%m-%d")), "%Y-%m-%d").date()
                except:
                    f_pts_def = ahora.date().replace(day=1)
                n_fecha_pts = st.date_input("INICIO DE LIGA ACTUAL", value=f_pts_def, key="cfg_fpts")

                st.markdown("### PROTOCOLOS DE SEGURIDAD")
                col_op1, col_op2 = st.columns(2)
                with col_op1:
                    n_gps = st.checkbox("AUTORIZACIÓN SATELITAL (GPS)", value=get_bool_config("verificar_gps", True), key="cfg_gps")
                    n_wifi = st.checkbox("AUTORIZACIÓN RED LOCAL (WI-FI)", value=get_bool_config("verificar_wifi", False), key="cfg_wifi")
                    n_auto = st.checkbox("PERMITIR ONBOARDING MANUAL DE PERSONAL", value=get_bool_config("autoregistro", False), key="cfg_aut")
                    n_sal_estricta = st.checkbox("CIERRE ESTRICTO (EXIGE RED/GPS PARA SALIR)", value=get_bool_config("salida_estricta", False), key="cfg_se")
                    n_sal_manual = st.checkbox("INHABILITAR CIERRE AUTOMÁTICO", value=get_bool_config("exigir_salida_manual", False), key="cfg_sm")
                with col_op2:
                    n_desc_tarde = st.checkbox("COMPUTAR DESCUENTO POR TARDANZA", value=get_bool_config("desc_tarde", True), key="cfg_dt")
                    n_desc_temp = st.checkbox("COMPUTAR DESCUENTO POR RETIRO ANTICIPADO", value=get_bool_config("desc_temp", True), key="cfg_dtemp")
                    n_perdon_tol = st.checkbox("ABSORBER TOLERANCIA EN CÓMPUTO", value=get_bool_config("perdonar_tolerancia", True), key="cfg_pt")
                    n_mostrar_hs = st.checkbox("VISIBILIDAD DE HORAS PARA EL OPERARIO", value=get_bool_config("mostrar_horas_empleado", False), key="cfg_mh")
                    n_estricto_plan = st.checkbox("BLOQUEO DE INGRESO FUERA DE PLANIFICACIÓN", value=get_bool_config("fichaje_estricto_plan", False), key="cfg_fep")
                
                if st.form_submit_button("APLICAR CONFIGURACIÓN"):
                    config_app["titulo_portal"] = nuevo_titulo
                    config_app["admin_password"] = nueva_pass
                    config_app["tolerancia_minutos"] = nueva_tol
                    config_app["mensaje_dia"] = nuevo_msg_dia
                    config_app["mensaje_llegada_tarde"] = msg_tarde
                    config_app["radio_metros"] = rad_metros
                    config_app["recompensa_auditoria_cajero"] = rec_cajero
                    config_app["dia_inicio_semana"] = d_semana
                    config_app["fecha_inicio_puntos"] = n_fecha_pts.strftime("%Y-%m-%d")
                    config_app["verificar_gps"] = n_gps
                    config_app["verificar_wifi"] = n_wifi
                    config_app["autoregistro"] = n_auto
                    config_app["salida_estricta"] = n_sal_estricta
                    config_app["exigir_salida_manual"] = n_sal_manual
                    config_app["desc_tarde"] = n_desc_tarde
                    config_app["desc_temp"] = n_desc_temp
                    config_app["perdonar_tolerancia"] = n_perdon_tol
                    config_app["mostrar_horas_empleado"] = n_mostrar_hs
                    config_app["fichaje_estricto_plan"] = n_estricto_plan
                    save_json("config", config_app)
                    st.success("Configuración del sistema actualizada.")
                    recargar_app()
                    
            with st.form("form_rankings"):
                st.markdown("### LIGAS DE RENDIMIENTO")
                rankings = config_app.get("rankings_muro", [])
                edited_rankings = []
                for i, r in enumerate(rankings):
                    st.markdown(f"**LIGA: {r['nombre']}**")
                    c1, c2 = st.columns(2)
                    r_nom = c1.text_input("DESIGNACIÓN", value=r['nombre'], key=f"rn_{i}")
                    r_mp = c2.checkbox("VISIBILIDAD DE PUNTUACIÓN", value=r.get("mostrar_puntos", True), key=f"rmp_{i}")
                    
                    c3, c4 = st.columns(2)
                    r_comp = c3.multiselect("COMPETIDORES:", ["Todos"] + lista_roles_disponibles + lista_empleados, default=r.get('competidores', ["Todos"]), key=f"rc_{i}")
                    r_esp = c4.multiselect("ESPECTADORES:", ["Todos"] + lista_roles_disponibles + lista_empleados, default=r.get('espectadores', ["Todos"]), key=f"re_{i}")
                    
                    borrar = st.checkbox(f"ELIMINAR LIGA", key=f"rdel_{i}")
                    if not borrar:
                        edited_rankings.append({"nombre": r_nom, "competidores": r_comp, "espectadores": r_esp, "mostrar_puntos": r_mp})
                    st.write("---")
                
                st.markdown("**NUEVA LIGA DE RENDIMIENTO**")
                n_nom = st.text_input("Designación:", key="new_rn")
                c_n1, c_n2 = st.columns(2)
                n_mp = c_n1.checkbox("Visibilidad de Puntuación", value=True, key="new_rmp")
                c_n3, c_n4 = st.columns(2)
                n_comp = c_n3.multiselect("Competidores:", ["Todos"] + lista_roles_disponibles + lista_empleados, default=["Todos"], key="new_rc")
                n_esp = c_n4.multiselect("Espectadores:", ["Todos"] + lista_roles_disponibles + lista_empleados, default=["Todos"], key="new_re")
                
                if st.form_submit_button("ACTUALIZAR LIGAS"):
                    if n_nom.strip():
                        edited_rankings.append({"nombre": n_nom.strip(), "competidores": n_comp, "espectadores": n_esp, "mostrar_puntos": n_mp})
                    config_app["rankings_muro"] = edited_rankings
                    save_json("config", config_app)
                    st.success("Ligas procesadas.")
                    recargar_app()
                    
        with tab_limpieza:
            st.subheader("PURGA DE DATOS")
            
            c_limp1, c_limp2, c_limp3 = st.columns(3)
            tabla_a_limpiar = c_limp1.selectbox("TABLA:", ["Asistencia (Fichajes)", "Cierres de Caja", "Tareas y Puntos", "Reportes y Avisos"], key="limp_tab")
            fecha_in_limp = c_limp2.date_input("DESDE:", value=ahora.date() - datetime.timedelta(days=365), key="limp_in")
            fecha_fi_limp = c_limp3.date_input("HASTA:", value=ahora.date() - datetime.timedelta(days=30), key="limp_fi")
            
            st.warning("ACCIÓN DEPURATIVA: Los registros eliminados no podrán ser recuperados.")
            confirmar_borrado = st.checkbox("AUTORIZO LA ELIMINACIÓN PERMANENTE.", key="limp_chk")
            
            if st.button("PURGAR REGISTROS", type="primary", key="limp_btn"):
                if not confirmar_borrado:
                    st.error("Requiere autorización.")
                else:
                    try:
                        f_in_str = fecha_in_limp.strftime("%Y-%m-%d")
                        f_fi_str = fecha_fi_limp.strftime("%Y-%m-%d")
                        
                        if tabla_a_limpiar == "Asistencia (Fichajes)":
                            try: supabase.table("asistencia").delete().gte("fecha", f_in_str).lte("fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("asistencia").delete().gte("Fecha", f_in_str).lte("Fecha", f_fi_str).execute()
                            except: pass
                        elif tabla_a_limpiar == "Cierres de Caja":
                            try: supabase.table("cierres_caja").delete().gte("fecha", f_in_str).lte("fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("cierres_caja").delete().gte("Fecha", f_in_str).lte("Fecha", f_fi_str).execute()
                            except: pass
                        elif tabla_a_limpiar == "Tareas y Puntos":
                            try: supabase.table("tareas_log").delete().gte("fecha", f_in_str).lte("fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("tareas_log").delete().gte("Fecha", f_in_str).lte("Fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("ajustes_puntos").delete().gte("fecha", f_in_str).lte("fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("ajustes_puntos").delete().gte("Fecha", f_in_str).lte("Fecha", f_fi_str).execute()
                            except: pass
                        elif tabla_a_limpiar == "Reportes y Avisos":
                            try: supabase.table("reportes").delete().gte("fecha", f_in_str).lte("fecha", f_fi_str).execute()
                            except: pass
                            try: supabase.table("reportes").delete().gte("Fecha", f_in_str).lte("Fecha", f_fi_str).execute()
                            except: pass

                        st.success(f"Purga ejecutada en la tabla {tabla_a_limpiar}.")
                        recargar_app()
                    except Exception as e:
                        show_db_error(e, "eliminando datos históricos")

elif pestaña == nombre_tab_dueno:
    st.markdown('<div class="main-title" style="font-size: 2rem;">PANEL DEL PROPIETARIO</div>', unsafe_allow_html=True)
    
    pass_owner = st.text_input("CLAVE DE ACCESO ROOT:", type="password", key="login_root")
    
    if pass_owner == "master123":
        t_esp, t_lic = st.tabs(["MODO INCÓGNITO", "GESTIÓN DE LICENCIA"])
        
        with t_esp:
            st.subheader("AUDITORÍA DE SESIONES (INCÓGNITO)")
            emp_espia = st.selectbox("SIMULAR TERMINAL DE:", ["Seleccionar..."] + sorted(lista_empleados), key="espia_emp")
            if st.button("INICIAR INSTANCIA DE OPERARIO", key="btn_espia_emp") and emp_espia != "Seleccionar...":
                st.session_state['incognito'] = True
                st.session_state['incognito_user'] = emp_espia
                recargar_app()
                
            st.write("---")
            if st.button("INICIAR INSTANCIA GERENCIAL", key="btn_espia_ger"):
                st.session_state['incognito'] = True
                st.session_state['incognito_user'] = "Gerencia"
                recargar_app()

        with t_lic:
            st.subheader("PARÁMETROS DE CONTRATO Y MARCA")
            with st.form("form_owner"):
                n_empresa = st.text_input("ENTIDAD PROVEEDORA", value=owner_config.get("empresa_nombre", ""), key="ow_emp")
                n_tab = st.text_input("DESIGNACIÓN DE PESTAÑA ROOT", value=owner_config.get("nombre_tab_dueno", "OWNER"), key="ow_tab")
                n_estado = st.selectbox("ESTADO DE LICENCIA", ["Activo", "Suspendido"], index=0 if owner_config.get("estado_licencia") == "Activo" else 1, key="ow_est")
                
                try: 
                    fv = datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date()
                except: 
                    fv = ahora.date()
                n_venc = st.date_input("VENCIMIENTO DE CONTRATO", value=fv, key="ow_fec")
                
                n_plan = st.text_input("PLAN ACTUAL", value=owner_config.get("plan_pago", "Mensual"), key="ow_pla")
                n_mostrar_plan = st.checkbox("VISIBILIDAD DEL PLAN EN GERENCIA", value=owner_config.get("mostrar_membresia", False), key="ow_chk")
                
                n_bloqueo = st.text_area("MENSAJE DE BLOQUEO", value=owner_config.get("mensaje_bloqueo", ""), key="ow_blo")
                n_aviso = st.text_area("AVISO PREVENCIMIENTO", value=owner_config.get("mensaje_aviso", ""), key="ow_avi")
                d_aviso = st.number_input("DÍAS DE GRACIA", value=int(owner_config.get("dias_aviso", 5)), key="ow_dia")
                
                n_somos = st.text_area("MANIFIESTO CORPORATIVO", value=owner_config.get("quienes_somos", ""), key="ow_som")
                n_contacto = st.text_area("CANALES DE ASISTENCIA", value=owner_config.get("contactos", ""), key="ow_con")

                if st.form_submit_button("APLICAR PROTOCOLO"):
                    owner_config["empresa_nombre"] = n_empresa
                    owner_config["nombre_tab_dueno"] = n_tab
                    owner_config["estado_licencia"] = n_estado
                    owner_config["fecha_vencimiento"] = n_venc.strftime("%Y-%m-%d")
                    owner_config["plan_pago"] = n_plan
                    owner_config["mostrar_membresia"] = n_mostrar_plan
                    owner_config["mensaje_bloqueo"] = n_bloqueo
                    owner_config["mensaje_aviso"] = n_aviso
                    owner_config["dias_aviso"] = d_aviso
                    owner_config["quienes_somos"] = n_somos
                    owner_config["contactos"] = n_contacto
                    save_json("owner_config", owner_config)
                    st.success("Protocolos del Propietario actualizados.")
                    recargar_app()
                    
    elif pass_owner != "":
        st.error("CREDENCIALES INVÁLIDAS.")
