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
st.set_page_config(page_title="Gestión Corporativa", page_icon="🏢", layout="wide")

# ==========================================
# 🎨 ESTÉTICA PREMIUM COMERCIAL (CSS) Y MARCA BLANCA
# ==========================================
st.markdown("""
<style>
/* ---> MODO MARCA BLANCA TOTAL <--- */
[data-testid="stToolbar"] { display: none !important; }
.viewerBadge_container { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ---> DISEÑO DE PESTAÑAS (TABS) ESTILO APP MODERNA <--- */
.stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 10px; }
.stTabs [data-baseweb="tab"] { 
    background-color: #f8f9fa; 
    border-radius: 10px 10px 0 0;
    padding: 12px 24px; 
    border: 1px solid #e9ecef; 
    border-bottom: none; 
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
    color: #495057;
}
.stTabs [aria-selected="true"] { 
    background: linear-gradient(135deg, #1e3a8a, #3b82f6) !important; 
    color: white !important; 
    font-weight: 800 !important; 
    box-shadow: 0 -4px 15px -3px rgba(59, 130, 246, 0.3); 
    border: none;
}
.stTabs [data-baseweb="tab"]:hover { background-color: #e2e8f0; }

/* ---> DISEÑO GENERAL DE LA APP <--- */
.main-title { 
    font-size: 2.5rem; 
    font-weight: 900; 
    background: -webkit-linear-gradient(45deg, #0f172a, #3b82f6); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    margin-bottom: 1rem; 
    text-transform: uppercase; 
    letter-spacing: -0.5px; 
}
div[data-testid="metric-container"] { 
    background: white; 
    border: 1px solid #f1f5f9; 
    padding: 24px; 
    border-radius: 16px; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); 
    border-top: 5px solid #3b82f6; 
    transition: all 0.3s ease;
}
div[data-testid="metric-container"]:hover { 
    transform: translateY(-5px); 
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 900; color: #0f172a; }
.stButton>button { 
    border-radius: 12px; 
    font-weight: 700; 
    transition: all 0.2s ease; 
    border: 1px solid #e2e8f0; 
    padding: 0.6rem 1rem; 
    width: 100%; 
    background-color: white;
    color: #1e293b;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}
.stButton>button:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); 
    border-color: #cbd5e1;
    background-color: #f8fafc;
}

/* ---> CAJAS DE AVISOS Y ALERTAS <--- */
.alert-box { padding: 18px; border-radius: 12px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #991B1B;}
.task-box { padding: 18px; border-radius: 12px; border-left: 6px solid #10B981; background-color: #ECFDF5; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #065F46;}
.task-pend { padding: 18px; border-radius: 12px; border-left: 6px solid #F59E0B; background-color: #FFFBEB; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #92400E;}
.task-rej { padding: 18px; border-radius: 12px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #991B1B;}
.report-box { padding: 18px; border-radius: 12px; border-left: 6px solid #8B5CF6; background-color: #F5F3FF; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #5B21B6;}
.super-box { padding: 20px; border-radius: 16px; border-left: 6px solid #3B82F6; background-color: #EFF6FF; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); color: #1E40AF;}
.validation-box { padding: 18px; border-radius: 12px; border: 1px solid #E5E7EB; background-color: #F9FAFB; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); color: #374151;}

/* ---> CREDENCIAL EMPLEADO <--- */
.credencial { 
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
    color: white; 
    padding: 25px; 
    border-radius: 20px; 
    box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4); 
    margin-bottom: 25px; 
    border: 1px solid rgba(255,255,255,0.1);
}
.cred-nombre { font-size: 2.2rem; font-weight: 900; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);}
.cred-rol { font-size: 1.2rem; opacity: 0.95; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;}
.cred-nivel { font-size: 1.4rem; font-weight: 800; background-color: rgba(255,255,255,0.25); padding: 8px 20px; border-radius: 25px; display: inline-block; backdrop-filter: blur(5px);}

/* ---> BLOQUEO PANTALLA <--- */
.bloqueo-pantalla { padding: 40px; background: linear-gradient(180deg, #FEF2F2 0%, #ffffff 100%); border: 4px solid #EF4444; border-radius: 20px; text-align: center; margin-top: 50px; box-shadow: 0 25px 50px -12px rgba(239, 68, 68, 0.25);}
.bloqueo-titulo { font-size: 3.5rem; color: #B91C1C; font-weight: 900; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

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
        st.error("🚨 Error: No se encontraron los secretos de Supabase en Streamlit.")
        st.stop()

supabase = init_connection()

@st.cache_data(ttl=60)
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
        st.error("⏳ Aguardá un momento. Reconectando de forma segura con la base de datos...")
        st.stop()
        
    if key_name in settings:
        return settings[key_name]
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
            st.error("🚨 No se pudo guardar ahora mismo por un error de conexión.")
            return
        if key_name in settings:
            supabase.table('app_data').update({'data': data}).eq('id', key_name).execute()
        else:
            supabase.table('app_data').insert({'id': key_name, 'data': data}).execute()
        get_all_settings.clear()
    except Exception as e:
        st.error(f"❌ Error guardando '{key_name}': {e}")

def load_df(table_name):
    try:
        res = supabase.table(table_name).select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def insert_row(table_name, row_dict):
    try:
        supabase.table(table_name).insert(row_dict).execute()
    except Exception as e:
        st.error(f"❌ Error guardando en la tabla '{table_name}': {e}")

# ==========================================
# 2. CARGA DE DATOS CENTRALIZADA
# ==========================================
zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%I:%M:%S %p")

config_defecto = {
    "admin_password": "1234", "tolerancia_minutos": 10,
    "mensaje_llegada_tarde": "🚨 Llegada fuera del margen de tolerancia.", "verificar_gps": True,
    "verificar_wifi": False, "salida_estricta": False, "exigir_salida_manual": False, "autoregistro": False,
    "ip_wifi_oficial": "", "radio_metros": 150, "fecha_inicio_puntos": ahora.date().replace(day=1).strftime("%Y-%m-%d"),
    "desc_tarde": True, "desc_temp": True,
    "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}
}
config_app = load_json("config", config_defecto)

owner_config_defecto = {
    "estado_licencia": "Activo", "plan_pago": "Mensual", "fecha_vencimiento": "2030-12-31",
    "mensaje_bloqueo": "🚨 SISTEMA SUSPENDIDO TEMPORALMENTE.\n\nPor favor, comuníquese con el proveedor del software para regularizar el estado de su cuenta.",
    "mostrar_membresia": False, "dias_aviso": 5,
    "mensaje_aviso": "🚨 Tu suscripción está próxima a vencer. Por favor, renová tu plan para evitar interrupciones en el servicio.",
    "empresa_nombre": "SyncroRetail Solutions",
    "quienes_somos": "Nacimos con una misión clara: revolucionar la gestión del personal y potenciar el rendimiento de los equipos de trabajo...",
    "contactos": "🏢 Oficina Central: Salta Capital, Argentina\n📧 Soporte y Soluciones: soporte@syncroretail.com\n💡 Sugerencias y Nuevas Funciones: desarrollo@syncroretail.com"
}
owner_config = load_json("owner_config", owner_config_defecto)

lista_roles_disponibles = load_json("lista_roles", ["Vendedor", "Cajero", "Encargado", "Depósito", "Otro"])
lista_empleados = load_json("empleados", ["Abril Gonzalez", "Agustina Lopez", "Daniela Perez", "Macarena Silva"])
roles_empleados = load_json("roles", {e: "Vendedor" for e in lista_empleados})
tareas_roles = load_json("tareas_roles", {"Vendedor": [{"tarea": "Acomodar Sector", "puntos": 5}]})
tareas_individuales = load_json("tareas_individuales", {e: [] for e in lista_empleados})
dispositivos_vinculados = load_json("dispositivos", {})
lista_locales = load_json("locales", {"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}})
lista_turnos = load_json("turnos", {"Apertura": {"ingreso": "09:00 AM", "salida": "05:00 PM"}})
lista_mensajes = load_json("mensajes", [])
alertas_ingreso = load_json("alertas_ingreso", [])
lista_intentos = load_json("intentos_seguridad", [])
lista_puntos = load_json("ajustes_puntos", [])
reportes_log = load_json("reportes", [])
salidas_pendientes = load_json("salidas_pendientes", [])
sueldos_historico = load_json("sueldos_historico", [])
cierres_caja = load_json("cierres_caja", [])
planificacion_turnos = load_json("planificacion_turnos", {})

ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A", "Retiro Temprano", "Salida (Cambio Local)"]

def procesar_rango_fechas(rango):
    if isinstance(rango, tuple) or isinstance(rango, list):
        if len(rango) == 2: return rango[0], rango[1]
        elif len(rango) == 1: return rango[0], rango[0]
    return rango, rango

def get_fechas_filtro(opcion, custom_rango=None):
    hoy = ahora.date()
    if opcion == "Hoy": return hoy, hoy
    elif opcion == "Esta Semana": return hoy - datetime.timedelta(days=hoy.weekday()), hoy
    elif opcion == "Este Mes": return hoy.replace(day=1), hoy
    elif opcion == "Mes Anterior":
        u_dia = hoy.replace(day=1) - datetime.timedelta(days=1)
        return u_dia.replace(day=1), u_dia
    elif opcion == "Todo el Historial": return datetime.date(2020, 1, 1), hoy
    elif opcion == "Personalizado": return procesar_rango_fechas(custom_rango)
    return hoy, hoy

def calcular_nivel(puntos):
    if puntos < 80: return "🔴 Observación"
    elif puntos < 100: return "🥉 Bronce"
    elif puntos < 130: return "🥈 Plata"
    elif puntos < 160: return "🥇 Oro"
    elif puntos < 200: return "💎 Platino"
    else: return "👑 Leyenda"

def formato_horas_texto(h_decimal):
    try:
        h_decimal = float(h_decimal)
        horas = int(h_decimal)
        minutos = int(round((h_decimal - horas) * 60))
        if minutos == 60:
            horas += 1
            minutos = 0
        nums = {0: "cero", 1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce", 15: "quince", 16: "dieciséis", 17: "diecisiete", 18: "dieciocho", 19: "diecinueve", 20: "veinte", 21: "veintiuna", 22: "veintidós", 23: "veintitrés", 24: "veinticuatro"}
        h_str = nums.get(horas, str(horas))
        txt_h = "hora" if horas == 1 else "horas"
        return f"{horas}:{minutos:02d} ({h_str} {txt_h} y {minutos} min)"
    except:
        return str(h_decimal)

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
# 4. NAVEGACIÓN FRONTAL PARA CELULARES
# ==========================================
st.markdown('<div class="main-title" style="text-align: center;">🏢 Portal Corporativo</div>', unsafe_allow_html=True)
pestaña = st.selectbox("Navegación:", ["📱 Portal del Empleado", "💼 Panel de Gerencia", "⚙️ Dueño del Software"], label_visibility="collapsed")
st.write("---")

# ==========================================
# 🚨 SISTEMA ANTIFRAUDE (KILL SWITCH Y VENCIMIENTO)
# ==========================================
licencia_vencida = False
try:
    if ahora.date() > datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date():
        licencia_vencida = True
except: pass

if pestaña in ["📱 Portal del Empleado", "💼 Panel de Gerencia"]:
    if owner_config.get("estado_licencia") == "Suspendido" or licencia_vencida:
        msg_motivo = owner_config.get("mensaje_bloqueo") if owner_config.get("estado_licencia") == "Suspendido" else "🚨 EL PERÍODO DE LICENCIA HA VENCIDO.\n\nPor favor, contacte a soporte para renovar su suscripción."
        st.markdown(f"""
        <div class="bloqueo-pantalla">
        <div class="bloqueo-titulo">⛔ ACCESO BLOQUEADO</div>
        <p style="font-size: 1.5rem; color: #7F1D1D;">{msg_motivo}</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# ==========================================
# 5. INTERFAZ: PORTAL DEL EMPLEADO
# ==========================================
if pestaña == "📱 Portal del Empleado":
    if es_incognito and usuario_incognito in lista_empleados:
        device_id = "incognito_device"
        st.warning(f"🕵️ **MODO INCÓGNITO ACTIVO:** Estás viendo la app como **{usuario_incognito}**. Tu celular personal no quedó vinculado en el sistema.\n\n*Nota: Podés usar la app libremente, pero si hacés clic en 'Registrar Entrada' o guardás datos, SÍ impactarán en la base de datos real.*")
        if st.button("❌ Salir del Modo Incógnito", key="btn_exit_inc_emp"):
            st.session_state['incognito'] = False
            st.session_state['incognito_user'] = None
            st.rerun()
    else:
        if 'device_id' not in st.session_state:
            js_get_device = "(function() { let id = localStorage.getItem('tienda_app_device_id'); if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); } return id; })();"
            did = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")
            if did:
                st.session_state['device_id'] = did
                st.rerun()
        device_id = st.session_state.get('device_id')

    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")

    if not device_id:
        st.info("⏳ Autenticando tu equipo...")
    else:
        if empleado_en_celu:
            if 'fichaje_exitoso' in st.session_state:
                if "🚨" in st.session_state['fichaje_exitoso'] or "❌" in st.session_state['fichaje_exitoso']:
                    st.warning(st.session_state['fichaje_exitoso'])
                else:
                    st.success(st.session_state['fichaje_exitoso'])
                    st.balloons()
                del st.session_state['fichaje_exitoso']

            puntos_actuales = config_app["reglas_puntos"]["base"]
            f_inicio_str = config_app.get("fecha_inicio_puntos", ahora.date().replace(day=1).strftime("%Y-%m-%d"))
            d_inicio_puntos = datetime.datetime.strptime(f_inicio_str, "%Y-%m-%d").date()
            df_punt = load_df("asistencia")
            
            if not df_punt.empty:
                df_punt['F_Obj'] = pd.to_datetime(df_punt['Fecha'], errors='coerce').dt.date
                df_e = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt['F_Obj'] >= d_inicio_puntos)]
                puntos_actuales += (len(df_e[df_e["Estado"] == "Tarde"]) * config_app["reglas_puntos"]["Tarde"]) + (len(df_e[df_e["Tipo"] == "Ausente"]) * config_app["reglas_puntos"]["Ausente"])
                
            df_tl = load_df("tareas_log")
            if not df_tl.empty:
                df_tl['F_Obj'] = pd.to_datetime(df_tl['Fecha'], errors='coerce').dt.date
                puntos_actuales += pd.to_numeric(df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Estado"] == "Aprobada") & (df_tl['F_Obj'] >= d_inicio_puntos)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
                
            puntos_actuales += sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == empleado_en_celu and p.get('Estado') == "Aprobada" and datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() >= d_inicio_puntos])
            
            df_hoy = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["Fecha"] == fecha_hoy)].copy() if not df_punt.empty else pd.DataFrame()
            estado_laboral = "Fuera"
            datos_turno_activo = {}
            
            if not df_hoy.empty:
                if 'id' in df_hoy.columns:
                    df_hoy['id_num'] = pd.to_numeric(df_hoy['id'], errors='coerce')
                    df_hoy = df_hoy.sort_values(by="id_num")
                ultimo_reg = df_hoy.iloc[-1]
                if ultimo_reg["Tipo"] == "Entrada":
                    estado_laboral = "Adentro"
                    try: dist_guardada = float(ultimo_reg.get("Distancia_m", 0.0))
                    except: dist_guardada = 0.0
                    datos_turno_activo = {"Sucursal": str(ultimo_reg["Sucursal"]), "Turno": str(ultimo_reg["Turno"]), "Distancia_m": dist_guardada}
                    
            rol_empleado = roles_empleados.get(empleado_en_celu, 'Staff')
            st.markdown(f"<div class='credencial'><p class='cred-nombre'>👤 {empleado_en_celu}</p><p class='cred-rol'>Rol: {rol_empleado}</p><div class='cred-nivel'>{calcular_nivel(puntos_actuales)} ({puntos_actuales} pts)</div></div>", unsafe_allow_html=True)
            
            if rol_empleado in ["Cajero", "Encargado"]:
                with st.expander("🛡️ Panel de Responsable de Turno", expanded=False):
                    st.markdown("<div class='super-box'><b>Rol Supervisor:</b> Podés auditar salidas y asignar puntos a tus compañeros.</div>", unsafe_allow_html=True)
                    st.markdown("#### 🚪 Auditar Salida de Compañero")
                    if estado_laboral == "Adentro":
                        suc_cajero = datos_turno_activo.get("Sucursal")
                        st.write(f"📍 Estás auditando la sucursal: **{suc_cajero}**")
                        auditables = []
                        df_hoy_todos = df_punt[df_punt["Fecha"] == fecha_hoy] if not df_punt.empty else pd.DataFrame()
                        
                        if not df_hoy_todos.empty:
                            if 'id' in df_hoy_todos.columns:
                                df_hoy_todos['id_num'] = pd.to_numeric(df_hoy_todos['id'], errors='coerce')
                                df_hoy_todos = df_hoy_todos.sort_values(by="id_num")
                            for e_comp in lista_empleados:
                                if e_comp != empleado_en_celu:
                                    df_c = df_hoy_todos[df_hoy_todos["Empleado"] == e_comp]
                                    if not df_c.empty:
                                        ult_c = df_c.iloc[-1]
                                        if ult_c["Tipo"] == "Entrada" and str(ult_c["Sucursal"]) == str(suc_cajero):
                                            auditables.append(e_comp)
                                            
                        if auditables:
                            with st.form("form_sup_salida"):
                                c_s1, c_s2 = st.columns(2)
                                s_emp_salida = c_s1.selectbox("Compañero a retirar:", ["Seleccionar..."] + auditables)
                                s_hora_salida = c_s2.time_input("Hora exacta de salida:", ahora.time())
                                s_motivo_salida = st.text_input("Nota de Auditoría (Ej: 'Se fue temprano por el médico'):")
                                if st.form_submit_button("Fichar Salida"):
                                    if s_emp_salida == "Seleccionar...":
                                        st.warning("🚨 Elegí un compañero de la lista.")
                                    elif not s_motivo_salida.strip():
                                        st.warning("🚨 Escribí el motivo en la nota (Obligatorio para la auditoría).")
                                    else:
                                        ya_pedido = False
                                        ya_salio = not df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Salida")].empty
                                        for sp in salidas_pendientes:
                                            if sp.get("Empleado") == s_emp_salida and sp.get("Fecha") == str(fecha_hoy):
                                                ya_pedido = True
                                                break
                                        if ya_salio:
                                            st.error(f"🚨 El empleado {s_emp_salida} ya tiene una salida registrada en este turno.")
                                        elif ya_pedido:
                                            st.error(f"🚨 Ya enviaste una solicitud de salida para {s_emp_salida} hoy. Gerencia la está revisando.")
                                        else:
                                            hora_str_salida = s_hora_salida.strftime("%I:%M:%S %p")
                                            nota_final = f"[Auditado por {empleado_en_celu}] {s_motivo_salida}"
                                            turno_del_auditado = "Manual"
                                            df_aud_turno = df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Entrada")]
                                            if not df_aud_turno.empty:
                                                turno_del_auditado = df_aud_turno.iloc[-1]["Turno"]
                                            salidas_pendientes.append({
                                                "Fecha": str(fecha_hoy), "Hora": str(hora_str_salida), "Empleado": str(s_emp_salida),
                                                "Sucursal": str(suc_cajero), "Turno": str(turno_del_auditado),
                                                "Nota": str(nota_final), "Autor": str(empleado_en_celu)
                                            })
                                            save_json("salidas_pendientes", salidas_pendientes)
                                            st.success(f"✅ Solicitud de salida de {s_emp_salida} enviada a Gerencia para revisión.")
                                            st.rerun()
                        else:
                            st.info("ℹ️ No hay otros compañeros trabajando en esta sucursal en este momento.")
                    else:
                        st.warning("🚨 Para auditar la salida de un compañero, primero tenés que registrar tu propia ENTRADA en la sucursal.")
                        
                    st.markdown("---")
                    st.markdown("#### ⭐ Asignar Bono o Multa")
                    with st.form("form_sup_puntos"):
                        s_emp = st.selectbox("Compañero:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu])
                        s_pts = st.number_input("Puntos (+/-):", value=0, step=1)
                        s_mot = st.text_input("Motivo:")
                        if st.form_submit_button("Enviar a Gerencia"):
                            if s_emp == "Seleccionar..." or s_pts == 0 or not s_mot.strip():
                                st.warning("🚨 ¡Completá todos los campos! (Elegí un compañero, poné un puntaje distinto a 0 y escribí el motivo).")
                            else:
                                lista_puntos.append({"Fecha": fecha_hoy, "Empleado": s_emp, "Puntos": s_pts, "Motivo": s_mot.strip(), "Autor": empleado_en_celu, "Estado": "Pendiente"})
                                save_json("ajustes_puntos", lista_puntos)
                                st.success("✅ Evaluación enviada a Gerencia correctamente.")
                                
            mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu, rol_empleado]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='alert-box' style='border-color: #3B82F6; background-color: #EFF6FF; color: #1E40AF;'>📢 <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    elif m['destinatario'] == rol_empleado: st.markdown(f"<div class='task-pend'>📢 <b>Para el equipo de {rol_empleado}s:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='report-box'>✉️ <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    
            with st.expander("📍 Smart Check-In", expanded=True):
                st.markdown("### 📡 Radar Automático")
                local_detectado = None
                distancia_real = 0.0
                metodo_det = ""
                client_ip_local = None
                
                if config_app.get("verificar_wifi", False):
                    if 'client_ip' not in st.session_state:
                        js_get_ip = "fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')"
                        cip = streamlit_js_eval(js_expressions=js_get_ip, want_output=True, key="get_client_ip")
                        if cip: st.session_state['client_ip'] = cip
                    client_ip_local = st.session_state.get('client_ip')
                    
                ubicacion = None
                if config_app.get("verificar_gps", True):
                    ubicacion = get_geolocation()
                    
                if config_app.get("verificar_wifi", False) and client_ip_local and client_ip_local != 'Error':
                    for loc, d_loc in lista_locales.items():
                        if d_loc.get("ip", "").strip() == client_ip_local:
                            local_detectado = loc
                            metodo_det = "📶 Red Wi-Fi de la tienda"
                            break
                            
                if not local_detectado and config_app.get("verificar_gps", True):
                    if ubicacion and 'coords' in ubicacion:
                        coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                        for loc, d_loc in lista_locales.items():
                            coord_local = (d_loc["lat"], d_loc["lon"])
                            dist = geodesic(coord_usuario, coord_local).meters
                            if dist <= int(config_app.get("radio_metros", 50)):
                                local_detectado = loc
                                distancia_real = float(dist)
                                metodo_det = f"📍 GPS Satelital ({dist:.1f} metros)"
                                break
                                
                if estado_laboral == "Fuera":
                    if local_detectado:
                        nombres_turnos = list(lista_turnos.keys())
                        idx_defecto = 0
                        turno_planificado = "Libre"
                        dia_plan = planificacion_turnos.get(fecha_hoy, {})
                        loc_plan_actual = dia_plan.get(local_detectado, {})
                        if isinstance(loc_plan_actual, dict):
                            for t_name, emps_asignados in loc_plan_actual.items():
                                if isinstance(emps_asignados, list) and empleado_en_celu in emps_asignados:
                                    turno_planificado = t_name
                                    break
                        if turno_planificado in nombres_turnos:
                            idx_defecto = nombres_turnos.index(turno_planificado)
                        elif nombres_turnos:
                            min_diff = float('inf')
                            for idx, t_name in enumerate(nombres_turnos):
                                try:
                                    h_ing_str = lista_turnos[t_name]["ingreso"]
                                    h_ing_obj = datetime.datetime.strptime(h_ing_str, "%I:%M %p").time()
                                    dt_ing = datetime.datetime.combine(ahora.date(), h_ing_obj).replace(tzinfo=zona_arg)
                                    diff = abs((ahora - dt_ing).total_seconds())
                                    if diff < min_diff:
                                        min_diff = diff
                                        idx_defecto = idx
                                except: pass
                                
                        st.markdown(f"<div class='task-box'>✅ <b>Sucursal Detectada:</b> {local_detectado}<br><small>Verificado por: {metodo_det}</small></div>", unsafe_allow_html=True)
                        if nombres_turnos:
                            st.markdown("📋 **Verificá y confirmá tu turno:**")
                            if turno_planificado != "Libre" and turno_planificado in nombres_turnos:
                                st.markdown(f"*(Turno planificado por Gerencia: **{turno_planificado}**)*")
                            turno_seleccionado = st.selectbox("Turno a fichar:", nombres_turnos, index=idx_defecto, label_visibility="collapsed")
                            st.markdown(f"<small style='color: gray;'>El horario oficial de este turno es de {lista_turnos[turno_seleccionado]['ingreso']} a {lista_turnos[turno_seleccionado]['salida']}</small>", unsafe_allow_html=True)
                            nota_empleado = st.text_input("✍️ Novedades (Opcional):", placeholder="¿Llegaste tarde por el colectivo? Dejá tu nota acá...")
                            
                            if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                estado_llegada = "A tiempo"
                                try:
                                    hora_t_str = lista_turnos[turno_seleccionado]["ingreso"]
                                    hora_t_obj = datetime.datetime.strptime(hora_t_str, "%I:%M %p").time()
                                    dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                    estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                                except: pass
                                
                                insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_detectado), "Turno": str(turno_seleccionado), "Tipo": "Entrada", "Estado": str(estado_llegada), "Distancia_m": round(float(distancia_real), 1), "Nota": str(nota_empleado)})
                                
                                msg_final = f"¡Entrada registrada a las {hora_hoy}!"
                                if estado_llegada == "Tarde": msg_final += f"\n\n🚨 {config_app.get('mensaje_llegada_tarde')}"
                                for a in alertas_ingreso:
                                    if a['destinatario'] in ['Todos', empleado_en_celu, rol_empleado]:
                                        msg_final += f"\n\n📢 {a['texto']}"
                                st.session_state['fichaje_exitoso'] = msg_final
                                st.rerun()
                        else:
                            st.warning("No hay turnos configurados en el sistema. Avisale a Gerencia.")
                    else:
                        if config_app.get("verificar_gps", True) and (not ubicacion or 'coords' not in ubicacion):
                            st.info("⏳ Detectando ubicación satelital... Por favor, permití el acceso al GPS en tu celular.")
                        else:
                            st.error(f"❌ Estás fuera del rango de todas las sucursales. Acercate al local para habilitar el fichaje.")
                            
                elif estado_laboral == "Adentro":
                    local_actual = datos_turno_activo.get("Sucursal", "N/A")
                    turno_actual = datos_turno_activo.get("Turno", "N/A")
                    
                    if local_detectado and local_detectado != local_actual:
                        st.warning(f"🔄 **Cambio de Sucursal Detectado:** Tenías un turno abierto en **{local_actual}**, pero detectamos que llegaste a **{local_detectado}**.")
                        st.write("Podés cerrar automáticamente el turno anterior y registrar tu ingreso en esta nueva sucursal con un solo botón.")
                        
                        nombres_turnos = list(lista_turnos.keys())
                        turno_seleccionado = st.selectbox("Turno a fichar acá:", nombres_turnos) if nombres_turnos else "Manual"
                        
                        if st.button("🔄 Cambiar de Sucursal (Cerrar anterior e Ingresar acá)", use_container_width=True):
                            insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_actual), "Turno": str(turno_actual), "Tipo": "Salida", "Estado": "Salida (Cambio Local)", "Distancia_m": 0.0, "Nota": "Cierre automático al cambiar de local."})
                            
                            estado_llegada = "A tiempo"
                            if turno_seleccionado in lista_turnos:
                                try:
                                    hora_t_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado]["ingreso"], "%I:%M %p").time()
                                    dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                    estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                                except: pass
                            
                            insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_detectado), "Turno": str(turno_seleccionado), "Tipo": "Entrada", "Estado": str(estado_llegada), "Distancia_m": round(float(distancia_real), 1), "Nota": "Ingreso por cambio de local."})
                            
                            st.session_state['fichaje_exitoso'] = f"¡Saliste de {local_actual} e ingresaste a {local_detectado} a las {hora_hoy}!"
                            st.rerun()
                    else:
                        st.markdown("### 🏃‍♂️ Finalizar Turno")
                        st.success(f"🏢 Actualmente trabajando en **{local_actual}** (Horario: {turno_actual}).")
                        
                        if not config_app.get("exigir_salida_manual", False):
                            st.info("🟢 **Salida Automática Activada:** No necesitás registrar tu salida. El sistema computará tu turno automáticamente.")
                        else:
                            puede_salir = True
                            distancia_salida = datos_turno_activo.get("Distancia_m", 0.0)
                            if config_app.get("salida_estricta", False) and local_actual in lista_locales:
                                st.markdown("🔒 **Verificación requerida para finalizar turno:**")
                                ubicacion_sal = get_geolocation() if config_app.get("verificar_gps", True) else None
                                en_rango_sal = True
                                wifi_aprobado_sal = True
                                radio_permitido = int(config_app.get("radio_metros", 50))
                                
                                if config_app.get("verificar_gps", True):
                                    if ubicacion_sal and 'coords' in ubicacion_sal:
                                        coord_us = (ubicacion_sal['coords']['latitude'], ubicacion_sal['coords']['longitude'])
                                        coord_loc = (lista_locales[local_actual]["lat"], lista_locales[local_actual]["lon"])
                                        distancia_salida = geodesic(coord_us, coord_loc).meters
                                        if distancia_salida <= radio_permitido:
                                            st.markdown(f"<div class='validation-box'>✅ <b>GPS Aprobado:</b> Estás en el local ({distancia_salida:.1f} m).</div>", unsafe_allow_html=True)
                                        else:
                                            en_rango_sal = False
                                            st.markdown(f"<div class='validation-box' style='border-left: 5px solid #EF4444;'>❌ <b>Fuera de rango:</b> Estás a {distancia_salida:.1f} m. (Límite: {radio_permitido}m). <b>No podés finalizar el turno desde acá.</b></div>", unsafe_allow_html=True)
                                    else:
                                        en_rango_sal = False
                                        st.markdown("<div class='validation-box' style='border-left: 5px solid #F59E0B;'>⏳ <b>Obteniendo GPS...</b></div>", unsafe_allow_html=True)
                                        
                                client_ip_local = None
                                if config_app.get("verificar_wifi", False):
                                    if 'client_ip' not in st.session_state:
                                        js_get_ip = "fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')"
                                        cip = streamlit_js_eval(js_expressions=js_get_ip, want_output=True, key="get_client_ip")
                                        if cip: st.session_state['client_ip'] = cip
                                    client_ip_local = st.session_state.get('client_ip')
                                    ip_tienda = lista_locales[local_actual].get("ip", "").strip()
                                    if not ip_tienda: wifi_aprobado_sal = False
                                    elif client_ip_local and client_ip_local == ip_tienda: st.markdown("<div class='validation-box'>✅ <b>Red Aprobada.</b></div>", unsafe_allow_html=True)
                                    else: wifi_aprobado_sal = False
                                    
                                if config_app.get("verificar_wifi", False) and not wifi_aprobado_sal: puede_salir = False
                                if config_app.get("verificar_gps", True) and not en_rango_sal: puede_salir = False
                                
                            if puede_salir:
                                nota_empleado = st.text_input("✍️ Novedad al salir (Opcional):")
                                if st.button("🔴 REGISTRAR SALIDA", use_container_width=True):
                                    insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_actual), "Turno": str(turno_actual), "Tipo": "Salida", "Estado": "Salida", "Distancia_m": round(float(distancia_salida), 1), "Nota": str(nota_empleado)})
                                    st.session_state['fichaje_exitoso'] = f"¡Salida registrada a las {hora_hoy}! Buen descanso."
                                    st.rerun()
                            else:
                                st.error("🚨 El sistema exige que finalices tu turno físicamente dentro de la sucursal.")
                                
            with st.expander("📬 Buzón de Reportes Confidenciales", expanded=False):
                tipo_rep = st.selectbox("Tipo:", ["Falla de equipo/sistema", "Incumplimiento de un compañero", "Queja general", "Otra observación"])
                implicado = st.selectbox("Compañero implicado:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu]) if tipo_rep == "Incumplimiento de un compañero" else "N/A"
                detalle_rep = st.text_area("Detalle:")
                if st.button("📤 Enviar a Gerencia"):
                    if not detalle_rep.strip(): st.warning("🚨 Error: Tenés que escribir el detalle del reporte para poder enviarlo.")
                    elif tipo_rep == "Incumplimiento de un compañero" and implicado == "Seleccionar...": st.warning("🚨 Error: Tenés que seleccionar al compañero implicado.")
                    else:
                        reportes_log.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Emisor": empleado_en_celu, "Tipo": tipo_rep, "Implicado": implicado, "Detalle": detalle_rep.strip(), "Estado": "Pendiente de lectura"})
                        save_json("reportes", reportes_log)
                        st.success("✅ ¡Reporte enviado confidencialmente a Gerencia!")
                        
            tareas_totales = tareas_roles.get(rol_empleado, []) + tareas_individuales.get(empleado_en_celu, [])
            if tareas_totales:
                with st.expander("📝 Mis Tareas del Día", expanded=True):
                    tareas_hoy_df = df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Fecha"] == fecha_hoy)] if not df_tl.empty else pd.DataFrame()
                    for t in tareas_totales:
                        t_nombre, t_puntos = t.get('tarea'), t.get('puntos')
                        t_reg = tareas_hoy_df[tareas_hoy_df["Tarea"] == t_nombre] if not tareas_hoy_df.empty else pd.DataFrame()
                        if not t_reg.empty:
                            est_t = t_reg.iloc[-1]["Estado"]
                            if est_t == "Aprobada": st.markdown(f"<div class='task-box'>✅ <b>{t_nombre}</b> (+{t_puntos} pts) - <b>Aprobada</b></div>", unsafe_allow_html=True)
                            elif est_t == "Rechazada": st.markdown(f"<div class='task-rej'>❌ <b>{t_nombre}</b> - Rechazada</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='task-pend'>⏳ <b>{t_nombre}</b> - Esperando auditoría...</div>", unsafe_allow_html=True)
                        else:
                            c_t1, c_t2 = st.columns([3, 1])
                            c_t1.write(f"📌 {t_nombre} (+{t_puntos} pts)")
                            if c_t2.button("✔️ Listo", key=f"btn_t_{t_nombre}"):
                                insert_row("tareas_log", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Tarea": str(t_nombre), "Puntos": str(t_puntos), "Estado": "Pendiente"})
                                st.rerun()
                                
            with st.expander("🕒 Mi historial reciente"):
                if not df_punt.empty:
                    df_emp = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["F_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].copy()
                    if not df_emp.empty:
                        if 'id' in df_emp.columns:
                            df_emp['id_num'] = pd.to_numeric(df_emp['id'], errors='coerce')
                            df_emp = df_emp.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                    else: st.write("Sin fichajes recientes.")
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            with st.expander("ℹ️ Quiénes Somos / Soporte Técnico", expanded=False):
                st.markdown(f"### {owner_config.get('empresa_nombre', 'Nuestra Empresa')}")
                st.write(owner_config.get('quienes_somos', ''))
                st.markdown("---")
                st.markdown("📞 **Contactos Útiles:**")
                st.write(owner_config.get('contactos', ''))
        else:
            if config_app.get("autoregistro", False):
                st.info("📝 **El Auto-registro está habilitado.** Escribí tu nombre, elegí tu rol y vinculá tu celular.")
                nuevo_nombre_emp = st.text_input("Tu Nombre Completo:")
                rol_elegido_auto = st.selectbox("Tu Rol / Puesto:", lista_roles_disponibles)
                if st.button("🔗 Registrar y Enlazar mi teléfono") and nuevo_nombre_emp.strip():
                    n_emp = nuevo_nombre_emp.strip()
                    match = next((e for e in lista_empleados if e.lower() == n_emp.lower()), None)
                    
                    if device_id in dispositivos_vinculados.values():
                        st.error("❌ Este celular ya está vinculado a otra persona. No se permite compartir dispositivos.")
                    elif match and match in dispositivos_vinculados:
                        st.error(f"❌ '{match}' ya tiene un celular vinculado. No puedes ingresar desde otro celular ni usar el Modo Incógnito.")
                    else:
                        if not match:
                            lista_empleados.append(n_emp)
                            roles_empleados[n_emp] = rol_elegido_auto
                            tareas_individuales[n_emp] = []
                            save_json("empleados", lista_empleados)
                            save_json("roles", roles_empleados)
                            save_json("tareas_individuales", tareas_individuales)
                            dispositivos_vinculados[n_emp] = device_id
                            save_json("dispositivos", dispositivos_vinculados)
                        else:
                            roles_empleados[match] = rol_elegido_auto
                            save_json("roles", roles_empleados)
                            dispositivos_vinculados[match] = device_id
                            save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()
            else:
                st.info("🔒 **Auto-registro deshabilitado.** Pedile a gerencia que te dé de alta en la lista o seleccioná tu nombre si ya existís.")
                emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + sorted(lista_empleados))
                if st.button("🔗 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
                    if emp_vincular in dispositivos_vinculados:
                        st.error(f"❌ La cuenta de '{emp_vincular}' ya está vinculada a otro celular. No puedes ingresar desde otro equipo ni usar el Navegador en Modo Incógnito. Si cambiaste tu teléfono, pedile a Gerencia que libere tu usuario.")
                    elif device_id in dispositivos_vinculados.values():
                        st.error("❌ Este celular ya está vinculado a otra persona. No se permite prestar el celular a otro compañero.")
                    else:
                        dispositivos_vinculados[emp_vincular] = device_id
                        save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()

# ==========================================
# 6. PANEL DE GERENCIA (BUSINESS INTELLIGENCE)
# ==========================================
elif pestaña == "💼 Panel de Gerencia":
    es_incognito_gerencia = (es_incognito and usuario_incognito == "Gerencia")

    if not es_incognito_gerencia:
        password_ingresada = st.text_input("Clave de acceso de Gerencia:", type="password")
        
        if password_ingresada and password_ingresada != "doremifasol":
            if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
                st.session_state['last_pw_attempt'] = password_ingresada
                res = "✅ Acceso Permitido" if password_ingresada == config_app.get("admin_password", "1234") else "❌ Acceso Denegado"
                lista_intentos.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Usuario": empleado_en_celu if empleado_en_celu else "Desconocido", "Clave": password_ingresada, "Resultado": res})
                save_json("intentos_seguridad", lista_intentos)
                
        acceso_concedido = (password_ingresada == config_app.get("admin_password", "1234") or password_ingresada == "doremifasol")
    else:
        st.warning("🕵️ **MODO INCÓGNITO ACTIVO:** Estás viendo el panel como Gerente. Has ingresado sin contraseña y sin dejar registro de tu acceso en el historial de seguridad.")
        if st.button("❌ Salir del Modo Incógnito", key="btn_exit_inc_ger"):
            st.session_state['incognito'] = False
            st.session_state['incognito_user'] = None
            st.rerun()
        acceso_concedido = True

    if acceso_concedido:
        try:
            f_venc = datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date()
            dias_restantes = (f_venc - ahora.date()).days
            if 0 <= dias_restantes <= owner_config.get("dias_aviso", 5) and owner_config.get("estado_licencia", "Activo") == "Activo":
                st.markdown(f"<div class='task-pend' style='border-color: #F59E0B;'><b>⚠️ Aviso del Proveedor de Software:</b><br>{owner_config.get('mensaje_aviso', '')} (Vence en {dias_restantes} días)</div>", unsafe_allow_html=True)
        except: pass
        
        tab_analytics, tab_caja, tab_sueldos, tab_horarios, tab_puntos, tab_tareas, tab_perfil, tab_staff, tab_tiendas, tab_comunicados, tab_config, tab_espia = st.tabs([
            "📊 Analytics", "💰 Cajas", "💵 Sueldos", "📅 Horarios", "🏆 Ranking", "📋 Tareas", "👤 Perfiles", "👥 Staff", "🏢 Tiendas", "📢 Avisos", "⚙️ Ajustes", "🕵️ Espía"
        ])
        
        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📊 Analytics Globales</div>', unsafe_allow_html=True)
            c_alrt1, c_alrt2 = st.columns([2, 1])
            c_alrt1.markdown(f"### 🔔 Alertas del Día ({fecha_hoy})")
            suc_alerta = c_alrt2.selectbox("🏢 Filtrar por Sucursal:", ["Todas las sucursales"] + list(lista_locales.keys()), key="filtro_alertas_dia")
            df_activos = load_df("asistencia")
            if df_activos.empty:
                st.info("📭 Base de datos limpia.")
            else:
                df_activos = df_activos[df_activos["Empleado"].isin(lista_empleados)].copy()
                df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                df_hoy_alertas = df_activos[df_activos["Fecha"] == fecha_hoy].copy()
                
                if suc_alerta != "Todas las sucursales":
                    df_hoy_filtrado = df_hoy_alertas[df_hoy_alertas["Sucursal"] == suc_alerta]
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
                    if not lista_emps: return "Ninguno"
                    if suc_alerta == "Todas las sucursales": return "<br>".join([f"• {e} <small style='color:gray;'>({ult_suc_hoy.get(e, 'Desconocida')})</small>" for e in lista_emps])
                    else: return "<br>".join([f"• {e}" for e in lista_emps])
                    
                txt_presentes = format_nombres(entradas_hoy)
                txt_tardes = format_nombres(llegadas_tarde)
                txt_ausentes = format_nombres(ausentes)
                txt_sinfichar = "<br>".join([f"• {e}" for e in sin_fichar]) if sin_fichar else "Todos OK"
                
                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                c_h1.markdown(f"<div class='task-box'><b>✅ Presentes</b><br>{txt_presentes}</div>", unsafe_allow_html=True)
                c_h2.markdown(f"<div class='alert-box' style='border-color: #F59E0B; background-color: #FFFBEB; color: #B45309;'><b>🚨 Tarde</b><br>{txt_tardes}</div>", unsafe_allow_html=True)
                c_h3.markdown(f"<div class='alert-box'><b>❌ Ausentes</b><br>{txt_ausentes}</div>", unsafe_allow_html=True)
                c_h4.markdown(f"<div class='validation-box'><b>⚪ Sin Fichar (Global)</b><br>{txt_sinfichar}</div>", unsafe_allow_html=True)
                
                st.write("---")
                c_fil1_2, c_fil2_2 = st.columns([1,3])
                filtro_a = c_fil1_2.selectbox("⏳ KPI Dashboard (Métricas Rápidas):", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_a")
                rango_stats = c_fil2_2.date_input("📅 Fechas del Dashboard:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_a == "Personalizado" else None
                s_in, s_fi = get_fechas_filtro(filtro_a, rango_stats)
                
                df_per = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_in) & (df_activos['Fecha_Obj'].dt.date <= s_fi)]
                if not df_per.empty:
                    atiempo = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "A tiempo")])
                    tardes = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "Tarde")])
                    ausencias_tot = len(df_per[df_per["Tipo"] == "Ausente"])
                    tot_ingresos = atiempo + tardes
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("⏱️ Puntualidad Promedio", f"{round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0}%")
                    c2.metric("✅ Ingresos A Tiempo", atiempo)
                    c3.metric("🚨 Llegadas Tarde", tardes)
                    c4.metric("❌ Inasistencias", ausencias_tot)
                    
                st.write("---")
                st.markdown("### 🧮 Recuento de Horas y Exportaciones")
                st.write("Configurá los filtros acá abajo para calcular las horas de tu equipo y descargar las planillas para liquidación.")
                c_dl1, c_dl2, c_dl3 = st.columns(3)
                local_descarga = c_dl1.selectbox("🏢 Sucursal a evaluar:", ["Todas las sucursales"] + list(lista_locales.keys()), key="dl_loc")
                fecha_in_dl = c_dl2.date_input("📅 Desde el día:", value=ahora.date() - datetime.timedelta(days=7), key="dl_in")
                fecha_fi_dl = c_dl3.date_input("📅 Hasta el día:", value=ahora.date(), key="dl_fi")
                
                df_dl = df_activos.copy()
                df_dl = df_dl[(df_dl['Fecha_Obj'].dt.date >= fecha_in_dl) & (df_dl['Fecha_Obj'].dt.date <= fecha_fi_dl)]
                
                # ---> SOLUCIÓN FILTRO DE SUCURSAL <---
                # Filtramos la tabla general ANTES de exportar, así las descargas y el loop respetan la sucursal.
                if local_descarga != "Todas las sucursales":
                    df_dl = df_dl[df_dl['Sucursal'] == local_descarga]
                    st.info(f"📍 **Modo filtrado activo:** Mostrando y exportando únicamente datos de la sucursal **{local_descarga}**.")
                
                # ---> SOLUCIÓN CÁLCULO DE HORAS (CRUCE DE MEDIANOCHE Y PARSEO DE FECHAS) <---
                # Aseguramos que el Timestamp se procese bien aunque el horario sea AM/PM.
                try:
                    df_dl['Timestamp'] = pd.to_datetime(df_dl['Fecha'] + ' ' + df_dl['Hora'], errors='coerce')
                except:
                    pass # Fallback nativo
                
                df_dl = df_dl.dropna(subset=['Timestamp']).sort_values(by="Timestamp")
                
                datos_horas_dict = {}
                
                if not df_dl.empty:
                    for emp in df_dl["Empleado"].unique():
                        df_e = df_dl[df_dl["Empleado"] == emp]
                        entrada_actual = None
                        
                        for _, row_f in df_e.iterrows():
                            if row_f["Tipo"] == "Entrada":
                                entrada_actual = row_f
                            elif row_f["Tipo"] == "Salida" and entrada_actual is not None:
                                h_in = entrada_actual["Timestamp"]
                                h_out = row_f["Timestamp"]
                                turno_eval = entrada_actual["Turno"]
                                suc_eval = entrada_actual["Sucursal"]
                                
                                # Doble chequeo por las dudas (ya filtramos el df entero arriba)
                                if local_descarga != "Todas las sucursales" and suc_eval != local_descarga:
                                    entrada_actual = None
                                    continue
                                
                                horas_tramo = 0.0
                                if turno_eval in lista_turnos:
                                    h_ofi_in_str = lista_turnos[turno_eval].get("ingreso")
                                    h_ofi_out_str = lista_turnos[turno_eval].get("salida")
                                    if h_ofi_in_str and h_ofi_out_str:
                                        try:
                                            # Parseo súper seguro de horas usando datetime nativo
                                            t_in_obj = datetime.datetime.strptime(h_ofi_in_str, "%I:%M %p").time()
                                            t_out_obj = datetime.datetime.strptime(h_ofi_out_str, "%I:%M %p").time()
                                            
                                            h_in_oficial = datetime.datetime.combine(h_in.date(), t_in_obj)
                                            h_out_oficial = datetime.datetime.combine(h_in.date(), t_out_obj)
                                            
                                            if h_out_oficial < h_in_oficial: 
                                                h_out_oficial += datetime.timedelta(days=1)
                                            
                                            horas_tramo = (h_out_oficial - h_in_oficial).total_seconds() / 3600.0
                                            
                                            if config_app.get("desc_tarde", True):
                                                diff_tarde = (h_in - h_in_oficial).total_seconds() / 3600.0
                                                if diff_tarde > 0: horas_tramo -= diff_tarde
                                                
                                            if config_app.get("desc_temp", True):
                                                diff_temp = (h_out_oficial - h_out).total_seconds() / 3600.0
                                                if diff_temp > 0: horas_tramo -= diff_temp
                                        except Exception as e:
                                            # Si falla el parseo, caemos directo a la hora real
                                            horas_tramo = (h_out - h_in).total_seconds() / 3600.0
                                else:
                                    # Para turnos manuales o no definidos, cuenta el tiempo exacto que estuvo
                                    horas_tramo = (h_out - h_in).total_seconds() / 3600.0
                                
                                if horas_tramo < 0: horas_tramo += 24.0
                                horas_tramo = max(0.0, horas_tramo)
                                
                                sueldo_hora = 0.0
                                fecha_in_str = h_in.strftime("%Y-%m-%d")
                                for s in sueldos_historico:
                                    if s["Empleado"] == emp and s["Fecha_Desde"] <= fecha_in_str <= s["Fecha_Hasta"]:
                                        sueldo_hora = float(s["Valor_Hora"])
                                        break
                                
                                key_datos = (emp, suc_eval)
                                if key_datos not in datos_horas_dict: datos_horas_dict[key_datos] = {"Horas": 0.0, "Pago": 0.0}
                                datos_horas_dict[key_datos]["Horas"] += horas_tramo
                                datos_horas_dict[key_datos]["Pago"] += (horas_tramo * sueldo_hora)
                                
                                entrada_actual = None
                
                    datos_horas = []
                    for (emp, loc), vals in datos_horas_dict.items():
                        if vals["Horas"] > 0:
                            datos_horas.append({"Personal": emp, "Rol": roles_empleados.get(emp, "Staff"), "Sucursal": loc, "⏱️ Horas Computadas": round(vals["Horas"], 2), "💰 Pago Est.": round(vals["Pago"], 2)})
                            
                    if datos_horas:
                        df_horas_final = pd.DataFrame(datos_horas).sort_values(by=["Personal", "⏱️ Horas Computadas"], ascending=[True, False])
                        
                        st.write("### 🪪 Fichas de Liquidación Individuales")
                        st.write("Acá tenés el desglose exacto y corregido. Podés descargar el CSV individual de cada empleado.")
                        
                        # --- NUEVO DISEÑO VISUAL PARA FICHAS ---
                        c_cards = st.columns(3)
                        col_idx = 0
                        for idx, row in df_horas_final.iterrows():
                            with c_cards[col_idx]:
                                with st.container():
                                    st.markdown(f"""
                                    <div class='super-box' style='padding: 20px; margin-bottom: 15px; border-radius: 12px;'>
                                        <h4 style='margin:0; font-size: 1.3rem;'>👤 {row['Personal']}</h4>
                                        <small style='color:gray;'>{row['Rol']} | {row['Sucursal']}</small>
                                        <hr style='margin: 12px 0; border: 0; border-top: 1px solid #E5E7EB;'>
                                        <p style='margin:0; font-size: 1.1rem; color: #4B5563;'>{formato_horas_texto(row["⏱️ Horas Computadas"])}</p>
                                        <h2 style='margin: 5px 0 0 0; color:#059669; font-weight: 900;'>${row['💰 Pago Est.']:,.2f}</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Generar CSV individual nativo
                                    csv_ind = pd.DataFrame([row]).to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        label="📥 Descargar Ficha",
                                        data=csv_ind,
                                        file_name=f"Ficha_{row['Personal'].replace(' ', '_')}.csv",
                                        mime="text/csv",
                                        key=f"dl_btn_{idx}",
                                        use_container_width=True
                                    )
                                    st.write("")
                            col_idx = (col_idx + 1) % 3

                        st.write("---")
                        st.write("### ⬇️ Descargas Generales (Para RRHH)")
                        c_btn1, c_btn2 = st.columns(2)
                        
                        # BOTÓN NATIVO PARA LIQUIDACIÓN GLOBAL (AHORA RESPETA EL FILTRO)
                        csv_horas = df_horas_final.to_csv(index=False).encode('utf-8')
                        c_btn1.download_button(
                            label="📥 Liquidación General de Sueldos (CSV)",
                            data=csv_horas,
                            file_name=f"Horas_y_Sueldos_{local_descarga}_{fecha_in_dl}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # BOTÓN NATIVO PARA ASISTENCIA CRUDO (AHORA RESPETA EL FILTRO)
                        df_asist_dl = df_dl[["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]]
                        csv_asist = df_asist_dl.to_csv(index=False).encode('utf-8')
                        c_btn2.download_button(
                            label="📥 Todos los Fichajes Crudos (CSV)",
                            data=csv_asist,
                            file_name=f"Fichajes_{local_descarga}_{fecha_in_dl}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.info("📭 Sin registros de horas completados (Entrada + Salida) para la sucursal y fechas seleccionadas.")

        with tab_caja:
            st.markdown('<div class="main-title" style="font-size: 2rem;">💰 Control de Caja y Estadísticas</div>', unsafe_allow_html=True)
            
            empleados_cajeros = [e for e in lista_empleados if roles_empleados.get(e) in ["Cajero", "Encargado"]]
            if not empleados_cajeros:
                empleados_cajeros = lista_empleados
            
            with st.expander("➕ Cargar Cierre de Caja (Actual o Histórico)", expanded=True):
                st.write("Registrá los montos recaudados al finalizar el turno. **Podés elegir fechas anteriores** para cargar tu historial en el sistema.")
                with st.form("form_cierre_caja"):
                    c_caj1, c_caj2 = st.columns(2)
                    caj_emp = c_caj1.selectbox("Cajero/Encargado Responsable:", ["Seleccionar..."] + sorted(empleados_cajeros))
                    caj_suc = c_caj2.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
                    
                    c_caj3, c_caj4 = st.columns(2)
                    val_efectivo = c_caj3.number_input("💵 Efectivo ($):", min_value=0.0, step=1000.0)
                    val_tarjeta = c_caj4.number_input("💳 Tarjeta ($):", min_value=0.0, step=1000.0)
                    
                    c_caj5, c_caj6 = st.columns(2)
                    val_transf = c_caj5.number_input("🏦 Transferencia ($):", min_value=0.0, step=1000.0)
                    val_total = c_caj6.number_input("🧾 Total Ventas Declarado ($):", min_value=0.0, step=1000.0)
                    
                    c_caj7, c_caj8 = st.columns(2)
                    caj_fecha = c_caj7.date_input("Fecha del Cierre:", value=ahora.date())
                    nota_caja = c_caj8.text_input("📝 Novedades (Faltantes, sobrantes, etc.):")
                    
                    if st.form_submit_button("💾 Guardar Cierre de Caja"):
                        if caj_emp == "Seleccionar..." or caj_suc == "Seleccionar...":
                            st.warning("🚨 Seleccioná un empleado y una sucursal para guardar el reporte.")
                        else:
                            cierres_caja.append({"Fecha": caj_fecha.strftime("%Y-%m-%d"), "Hora": hora_hoy, "Cajero": caj_emp, "Sucursal": caj_suc, "Turno": "N/A", "Efectivo": val_efectivo, "Tarjeta": val_tarjeta, "Transferencia": val_transf, "Total_Ventas": val_total, "Nota": nota_caja.strip()})
                            save_json("cierres_caja", cierres_caja)
                            st.success("✅ ¡Cierre de caja guardado correctamente!")
                            st.rerun()

            with st.expander("✏️ Modificar o Eliminar Cierres Existentes", expanded=False):
                if cierres_caja:
                    st.write("Acá podés corregir montos o borrar cierres mal cargados (se muestran de más nuevo a más viejo).")
                    for idx, cc in reversed(list(enumerate(cierres_caja))):
                        with st.expander(f"🛒 {cc.get('Fecha')} - {cc.get('Sucursal')} | {cc.get('Cajero')} | Total: ${float(cc.get('Total_Ventas', 0)):,.2f}"):
                            c_edc1, c_edc2 = st.columns(2)
                            
                            idx_emp = (sorted(empleados_cajeros).index(cc['Cajero']) + 1) if cc['Cajero'] in empleados_cajeros else 0
                            n_emp_caja = c_edc1.selectbox("Cajero/Encargado:", ["Seleccionar..."] + sorted(empleados_cajeros), index=idx_emp, key=f"ecaj_{idx}")
                            
                            idx_suc = (list(lista_locales.keys()).index(cc['Sucursal']) + 1) if cc['Sucursal'] in lista_locales else 0
                            n_suc_caja = c_edc2.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()), index=idx_suc, key=f"esuc_{idx}")
                            
                            c_edc3, c_edc4 = st.columns(2)
                            n_efvo = c_edc3.number_input("Efectivo ($):", value=float(cc.get('Efectivo', 0)), step=1000.0, key=f"eefvo_{idx}")
                            n_tarj = c_edc4.number_input("Tarjeta ($):", value=float(cc.get('Tarjeta', 0)), step=1000.0, key=f"etarj_{idx}")
                            
                            c_edc5, c_edc6 = st.columns(2)
                            n_transf = c_edc5.number_input("Transferencia ($):", value=float(cc.get('Transferencia', 0)), step=1000.0, key=f"etransf_{idx}")
                            n_tot = c_edc6.number_input("Total Declarado ($):", value=float(cc.get('Total_Ventas', 0)), step=1000.0, key=f"etot_{idx}")
                            
                            c_edc7, c_edc8 = st.columns(2)
                            try: 
                                fecha_def = datetime.datetime.strptime(cc['Fecha'], "%Y-%m-%d").date()
                            except: 
                                fecha_def = ahora.date()
                            n_fecha = c_edc7.date_input("Fecha:", value=fecha_def, key=f"efec_{idx}")
                            n_nota = c_edc8.text_input("Nota:", value=cc.get('Nota', ''), key=f"enot_{idx}")

                            c_edcb1, c_edcb2 = st.columns(2)
                            if c_edcb1.button("💾 Guardar Cambios", key=f"btn_s_c_{idx}"):
                                if n_emp_caja != "Seleccionar..." and n_suc_caja != "Seleccionar...":
                                    cierres_caja[idx] = {
                                        "Fecha": n_fecha.strftime("%Y-%m-%d"), 
                                        "Hora": cc.get("Hora", hora_hoy), 
                                        "Cajero": n_emp_caja, 
                                        "Sucursal": n_suc_caja, 
                                        "Turno": cc.get("Turno", "N/A"), 
                                        "Efectivo": n_efvo, 
                                        "Tarjeta": n_tarj, 
                                        "Transferencia": n_transf, 
                                        "Total_Ventas": n_tot, 
                                        "Nota": n_nota.strip()
                                    }
                                    save_json("cierres_caja", cierres_caja)
                                    st.success("✅ Cierre actualizado.")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Faltan seleccionar Empleado o Sucursal.")
                                    
                            if c_edcb2.button("🗑️ Eliminar Cierre", key=f"btn_d_c_{idx}"):
                                cierres_caja.pop(idx)
                                save_json("cierres_caja", cierres_caja)
                                st.success("🗑️ Cierre eliminado.")
                                st.rerun()
                else:
                    st.info("No hay cierres registrados todavía.")
                    
            st.write("---")
            st.subheader("📊 Estadísticas y Comparativas de Recaudación")
            c_fc1, c_fc2 = st.columns([1,3])
            filtro_caja = c_fc1.selectbox("⏳ Filtrar por:", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_caja")
            rango_caja = c_fc2.date_input("📅 Rango de Fechas:", value=(ahora.date() - datetime.timedelta(days=30), ahora.date())) if filtro_caja == "Personalizado" else None
            c_in, c_fi = get_fechas_filtro(filtro_caja, rango_caja)
            
            if cierres_caja:
                cierres_filtrados = []
                for c in cierres_caja:
                    try:
                        d_obj = datetime.datetime.strptime(c["Fecha"], "%Y-%m-%d").date()
                        if c_in <= d_obj <= c_fi: cierres_filtrados.append(c)
                    except: pass
                
                if cierres_filtrados:
                    df_caja = pd.DataFrame(cierres_filtrados)
                    df_caja['Efectivo'] = pd.to_numeric(df_caja['Efectivo'], errors='coerce').fillna(0)
                    df_caja['Tarjeta'] = pd.to_numeric(df_caja['Tarjeta'], errors='coerce').fillna(0)
                    df_caja['Transferencia'] = pd.to_numeric(df_caja['Transferencia'], errors='coerce').fillna(0)
                    df_caja['Total_Ventas'] = pd.to_numeric(df_caja['Total_Ventas'], errors='coerce').fillna(0)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💵 Efectivo Total", f"${df_caja['Efectivo'].sum():,.2f}")
                    col2.metric("💳 Tarjeta Total", f"${df_caja['Tarjeta'].sum():,.2f}")
                    col3.metric("🏦 Transf. Total", f"${df_caja['Transferencia'].sum():,.2f}")
                    col4.metric("🧾 TOTAL VENTAS", f"${df_caja['Total_Ventas'].sum():,.2f}")
                    
                    st.markdown("#### 📈 Gráficos de Rendimiento")
                    tab_g1, tab_g2 = st.tabs(["📉 Evolución de Ventas (Tiempo)", "🏢 Comparativa por Sucursal"])
                    
                    with tab_g1:
                        df_caja['Fecha_DT'] = pd.to_datetime(df_caja['Fecha'])
                        ventas_por_dia = df_caja.groupby("Fecha_DT")["Total_Ventas"].sum().reset_index()
                        grafico_lineas = alt.Chart(ventas_por_dia).mark_line(point=True, color='#3b82f6', strokeWidth=3).encode(
                            x=alt.X('Fecha_DT:T', title='Fecha'),
                            y=alt.Y('Total_Ventas:Q', title='Total Ventas ($)'),
                            tooltip=[alt.Tooltip('Fecha_DT:T', title='Fecha'), alt.Tooltip('Total_Ventas:Q', title='Recaudación ($)', format=',.2f')]
                        ).properties(height=350).interactive()
                        st.altair_chart(grafico_lineas, use_container_width=True)
                        
                    with tab_g2:
                        ventas_por_sucursal = df_caja.groupby("Sucursal")["Total_Ventas"].sum().reset_index()
                        grafico_barras = alt.Chart(ventas_por_sucursal).mark_bar(color='#10B981', cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                            x=alt.X('Sucursal:N', title='Sucursal', sort='-y'),
                            y=alt.Y('Total_Ventas:Q', title='Total Ventas ($)'),
                            tooltip=[alt.Tooltip('Sucursal:N', title='Sucursal'), alt.Tooltip('Total_Ventas:Q', title='Recaudación ($)', format=',.2f')]
                        ).properties(height=350).interactive()
                        st.altair_chart(grafico_barras, use_container_width=True)

                    st.markdown("#### 📜 Registro Detallado")
                    df_mostrar_caja = df_caja.copy()
                    df_mostrar_caja["Efectivo"] = df_mostrar_caja["Efectivo"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Tarjeta"] = df_mostrar_caja["Tarjeta"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Transferencia"] = df_mostrar_caja["Transferencia"].apply(lambda x: f"${x:,.2f}")
                    df_mostrar_caja["Total_Ventas"] = df_mostrar_caja["Total_Ventas"].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_mostrar_caja.sort_values(by=["Fecha", "Hora"], ascending=[False, False])[["Fecha", "Hora", "Sucursal", "Cajero", "Efectivo", "Tarjeta", "Transferencia", "Total_Ventas", "Nota"]], use_container_width=True, hide_index=True)
                    
                    # BOTÓN NATIVO
                    csv_cajas = df_caja.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Reporte Completo en CSV",
                        data=csv_cajas,
                        file_name=f"Reporte_Cajas_{c_in}_al_{c_fi}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("📭 No hay registros de caja para las fechas seleccionadas.")

        with tab_sueldos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">💵 Liquidación de Sueldos</div>', unsafe_allow_html=True)
            c_su1, c_su2 = st.columns([1, 2])
            with c_su1:
                with st.form("form_nuevo_sueldo"):
                    st.subheader("➕ Asignar Nueva Tarifa")
                    emp_s = st.selectbox("Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
                    val_s = st.number_input("Valor por Hora ($):", min_value=0.0, step=100.0)
                    f_ini = st.date_input("Vigente Desde:", value=ahora.date())
                    es_actual = st.checkbox("✅ Tarifa actual (Sin fecha de cierre)", value=True)
                    f_fin = datetime.date(2099, 12, 31) if es_actual else st.date_input("Vigente Hasta:", value=ahora.date())
                    
                    if st.form_submit_button("💾 Guardar Tarifa"):
                        if emp_s == "Seleccionar..." or val_s <= 0: st.warning("🚨 Tenés que seleccionar un empleado y poner un valor mayor a $0.")
                        elif f_ini > f_fin: st.warning("🚨 La fecha 'Desde' no puede ser mayor a la fecha 'Hasta'.")
                        else:
                            sueldos_historico.append({"Empleado": emp_s, "Fecha_Desde": f_ini.strftime("%Y-%m-%d"), "Fecha_Hasta": f_fin.strftime("%Y-%m-%d"), "Valor_Hora": val_s})
                            save_json("sueldos_historico", sueldos_historico)
                            st.success(f"✅ ¡Tarifa de ${val_s}/h guardada para {emp_s}!")
                            st.rerun()
            with c_su2:
                st.subheader("📜 Historial y Edición de Tarifas")
                if sueldos_historico:
                    df_sueldos = pd.DataFrame(sueldos_historico).sort_values(by=["Empleado", "Fecha_Desde"], ascending=[True, False])
                    df_mostrar = df_sueldos.copy()
                    df_mostrar["Fecha_Hasta"] = df_mostrar["Fecha_Hasta"].replace("2099-12-31", "Actualidad")
                    df_mostrar["Valor_Hora"] = df_mostrar["Valor_Hora"].apply(lambda x: f"${float(x):,.2f}")
                    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                    st.write("---")
                    st.write("**✏️ Corregir o Eliminar Tarifas:**")
                    for idx, s in enumerate(sueldos_historico):
                        txt_hasta = "Actualidad" if s['Fecha_Hasta'] == "2099-12-31" else s['Fecha_Hasta']
                        with st.expander(f"👤 {s['Empleado']} | ${float(s['Valor_Hora']):,.2f}/h | 📅 {s['Fecha_Desde']} al {txt_hasta}"):
                            c_ed1, c_ed2, c_ed3 = st.columns(3)
                            n_val = c_ed1.number_input("Valor ($):", value=float(s['Valor_Hora']), step=100.0, key=f"nval_{idx}")
                            n_ini = c_ed2.date_input("Desde:", value=datetime.datetime.strptime(s['Fecha_Desde'], "%Y-%m-%d").date(), key=f"nini_{idx}")
                            is_2099 = s['Fecha_Hasta'] == "2099-12-31"
                            n_fin = c_ed3.date_input("Hasta:", value=datetime.datetime.strptime(s['Fecha_Hasta'], "%Y-%m-%d").date() if not is_2099 else ahora.date(), key=f"nfin_{idx}")
                            n_actual = c_ed3.checkbox("Dejar sin fecha de fin", value=is_2099, key=f"nact_{idx}")
                            n_fin_str = "2099-12-31" if n_actual else n_fin.strftime("%Y-%m-%d")
                            c_b1, c_b2 = st.columns(2)
                            if c_b1.button("💾 Guardar Cambios", key=f"save_s_{idx}"):
                                sueldos_historico[idx]['Valor_Hora'] = n_val
                                sueldos_historico[idx]['Fecha_Desde'] = n_ini.strftime("%Y-%m-%d")
                                sueldos_historico[idx]['Fecha_Hasta'] = n_fin_str
                                save_json("sueldos_historico", sueldos_historico)
                                st.rerun()
                            if c_b2.button("🗑️ Eliminar Tarifa", key=f"del_s_{idx}"):
                                sueldos_historico.pop(idx)
                                save_json("sueldos_historico", sueldos_historico)
                                st.rerun()
                else: st.info("ℹ️ Todavía no configuraste ningún sueldo. Las horas se calcularán con un valor de $0 por defecto.")

        with tab_horarios:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📅 Planificación y Horarios</div>', unsafe_allow_html=True)
            
            # --- AGREGAR FICHAJE MANUALMENTE ---
            st.markdown("### ➕ Agregar Fichaje Manualmente")
            st.write("Registrá una entrada o salida que un empleado olvidó marcar en la app.")
            with st.form("form_add_fichaje"):
                c_add1, c_add2, c_add3 = st.columns(3)
                add_emp = c_add1.selectbox("Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
                add_fecha = c_add2.date_input("Fecha:", value=ahora.date())
                add_hora = c_add3.time_input("Hora:", value=ahora.time())

                c_add4, c_add5, c_add6 = st.columns(3)
                add_suc = c_add4.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
                add_turno = c_add5.selectbox("Turno:", ["Seleccionar..."] + list(lista_turnos.keys()) + ["Manual"])
                add_tipo = c_add6.selectbox("Tipo:", ["Entrada", "Salida"])

                c_add7, c_add8 = st.columns([1, 2])
                add_estado = c_add7.selectbox("Estado:", ESTADOS_POSIBLES)
                add_nota = c_add8.text_input("Nota / Motivo:")

                if st.form_submit_button("💾 Guardar Fichaje Manual"):
                    if "Seleccionar..." in [add_emp, add_suc, add_turno]:
                        st.warning("🚨 Por favor seleccioná el Empleado, la Sucursal y el Turno.")
                    else:
                        str_hora = add_hora.strftime("%I:%M:%S %p")
                        str_fecha = add_fecha.strftime("%Y-%m-%d")
                        insert_row("asistencia", {
                            "Fecha": str_fecha,
                            "Hora": str_hora,
                            "Empleado": add_emp,
                            "Sucursal": add_suc,
                            "Turno": add_turno,
                            "Tipo": add_tipo,
                            "Estado": add_estado,
                            "Distancia_m": 0.0,
                            "Nota": f"[Carga Manual] {add_nota}".strip()
                        })
                        st.success("✅ Fichaje manual agregado correctamente a la nube.")
                        st.rerun()
            st.markdown("---")
            
            # --- MODIFICAR FICHAJES EXISTENTES ---
            st.markdown("### ✏️ Modificar Fichajes Existentes")
            st.write("Editá cualquier dato de un registro o eliminalo.")
            c_edh1, c_edh2 = st.columns(2)
            emp_mod_horario = c_edh1.selectbox("Seleccionar Empleado:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_mod_hor")
            fecha_mod_horario = c_edh2.date_input("Fecha a buscar:", value=ahora.date(), key="f_mod_hor")
            
            if emp_mod_horario != "Seleccionar...":
                df_asist_mod = load_df("asistencia")
                if not df_asist_mod.empty:
                    df_fil = df_asist_mod[(df_asist_mod["Empleado"] == emp_mod_horario) & (df_asist_mod["Fecha"] == str(fecha_mod_horario))]
                    if not df_fil.empty:
                        turnos_del_dia = df_fil["Turno"].unique()
                        for turno_str in turnos_del_dia:
                            st.markdown(f"#### ⏰ {turno_str}")
                            df_t = df_fil[df_fil["Turno"] == turno_str]
                            
                            for idx, row in df_t.iterrows():
                                with st.expander(f"📍 {row['Tipo']} - {row['Sucursal']} (Hora: {row['Hora']})", expanded=False):
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
                                    if c_btn1.button("💾 Guardar Cambios", key=f"btn_upd_{row['id']}"):
                                        supabase.table("asistencia").update({
                                            "Fecha": nueva_fecha.strftime("%Y-%m-%d"),
                                            "Hora": nueva_hora.strftime("%I:%M:%S %p"),
                                            "Tipo": nuevo_tipo,
                                            "Sucursal": nueva_sucursal,
                                            "Turno": nuevo_turno,
                                            "Estado": nuevo_estado,
                                            "Nota": nueva_nota
                                        }).eq("id", int(row['id'])).execute()
                                        st.success("¡Fichaje actualizado correctamente!")
                                        st.rerun()
                                    if c_btn2.button("🗑️ Eliminar Fichaje", key=f"btn_del_{row['id']}"):
                                        supabase.table("asistencia").delete().eq("id", int(row['id'])).execute()
                                        st.success("Fichaje eliminado.")
                                        st.rerun()
                    else:
                        st.info("No hay fichajes registrados para este día y este empleado.")
                        
            st.markdown("---")
            st.subheader("🗓️ Planilla Semanal de Turnos (Roster)")
            today_date = ahora.date()
            lunes_actual = today_date - datetime.timedelta(days=today_date.weekday())
            c_plan1, c_plan2 = st.columns([1,3])
            semana_sel = c_plan1.selectbox("Seleccionar Semana a organizar:", ["Esta Semana", "Semana Próxima", "Semana Anterior", "Elegir Fecha"])
            
            if semana_sel == "Esta Semana": start_date_plan = lunes_actual
            elif semana_sel == "Semana Próxima": start_date_plan = lunes_actual + datetime.timedelta(days=7)
            elif semana_sel == "Semana Anterior": start_date_plan = lunes_actual - datetime.timedelta(days=7)
            else:
                start_date_plan = c_plan2.date_input("Elegir Lunes de inicio:", value=lunes_actual)
                
            if start_date_plan.weekday() != 0: start_date_plan = start_date_plan - datetime.timedelta(days=start_date_plan.weekday())
            fechas_semana = [start_date_plan + datetime.timedelta(days=i) for i in range(7)]
            nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            cols_fechas = [f"{nombres_dias[i]} {fechas_semana[i].strftime('%d/%m')}" for i in range(7)]
            str_fechas = [f.strftime("%Y-%m-%d") for f in fechas_semana]
            
            st.info("💡 **Instrucciones:** Seleccioná a qué empleado le toca cubrir cada cupo. Si no necesitás llenar todos los cupos, dejalo en 'Nadie'.")
            nuevos_datos_plan = {}
            opciones_emps = ["Nadie"] + sorted(lista_empleados)
            
            for loc in lista_locales.keys():
                st.markdown(f"### 🏢 Sucursal: {loc}")
                for turno, datos_turno in lista_turnos.items():
                    st.markdown(f"**⏰ {turno}** ({datos_turno.get('ingreso')} a {datos_turno.get('salida')})")
                    data_t = []
                    for i in range(3):
                        row_t = {"Cupo": f"🧑‍💼 Cupo {i+1}"}
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
                    
            if st.button("💾 Guardar Planificación Semanal", use_container_width=True, type="primary"):
                for f_str in str_fechas:
                    if f_str not in planificacion_turnos: planificacion_turnos[f_str] = {}
                    for loc in lista_locales.keys():
                        if loc not in planificacion_turnos[f_str]: planificacion_turnos[f_str][loc] = {}
                        for turno in lista_turnos.keys():
                            df_e = nuevos_datos_plan[(loc, turno)]
                            day_col = cols_fechas[str_fechas.index(f_str)]
                            emps = df_e[day_col].dropna().tolist()
                            emps = list(dict.fromkeys([e for e in emps if e != "Nadie" and str(e).strip() != ""]))
                            planificacion_turnos[f_str][loc][turno] = emps
                save_json("planificacion_turnos", planificacion_turnos)
                st.success("✅ ¡Planificación semanal guardada con éxito!")
                st.rerun()
                
            st.markdown("---")
            st.subheader("⚖️ Comparativa: Planificado vs. Real")
            def get_plan_emp(fecha_s, empleado_s):
                for l_plan, turnos_dict in planificacion_turnos.get(fecha_s, {}).items():
                    if isinstance(turnos_dict, dict):
                        for t_plan, emps_list in turnos_dict.items():
                            if isinstance(emps_list, list) and empleado_s in emps_list:
                                return l_plan, t_plan
                return None, "Libre"
                
            df_asist_comp = load_df("asistencia")
            comp_data = []
            for emp in lista_empleados:
                row = {"Empleado": emp}
                for i, f_str in enumerate(str_fechas):
                    plan_loc, plan_turno = get_plan_emp(f_str, emp)
                    real_estado, real_turno, real_sucursal = "No Fichó", "", ""
                    if not df_asist_comp.empty:
                        f_asist = df_asist_comp[(df_asist_comp["Empleado"] == emp) & (df_asist_comp["Fecha"] == f_str) & (df_asist_comp["Tipo"] == "Entrada")]
                        if not f_asist.empty:
                            real_estado = f_asist.iloc[-1]["Estado"]
                            real_turno = f_asist.iloc[-1]["Turno"]
                            real_sucursal = f_asist.iloc[-1]["Sucursal"]
                        else:
                            if not df_asist_comp[(df_asist_comp["Empleado"] == emp) & (df_asist_comp["Fecha"] == f_str) & (df_asist_comp["Tipo"] == "Ausente")].empty:
                                real_estado = "Ausente Reportado"
                                
                    f_date = datetime.datetime.strptime(f_str, "%Y-%m-%d").date()
                    if f_date > today_date:
                        cell_val = f"⏳ {plan_turno}" if plan_turno != "Libre" else "Libre"
                    else:
                        if plan_turno == "Libre":
                            cell_val = "✅ Libre" if real_estado == "No Fichó" else f"🚨 Vino en su franco"
                        else:
                            if real_estado == "No Fichó": cell_val = f"⏳ Pendiente" if f_date == today_date else f"❌ Faltó sin aviso"
                            elif real_estado == "Ausente Reportado": cell_val = f"❌ Ausente reportado"
                            else:
                                if real_turno != plan_turno or real_sucursal != plan_loc: cell_val = f"🚨 Vino a {real_sucursal} ({real_turno})"
                                else:
                                    if real_estado == "A tiempo": cell_val = f"✅ A tiempo"
                                    elif real_estado == "Tarde": cell_val = f"🚨 Tarde"
                                    else: cell_val = f"✅ Vino"
                    row[cols_fechas[i]] = cell_val
                comp_data.append(row)
                
            def color_comparativa(val):
                if isinstance(val, str):
                    if '✅' in val: return 'background-color: #D1FAE5; color: #065F46; font-weight: 600;'
                    if '❌' in val: return 'background-color: #FEE2E2; color: #991B1B; font-weight: 600;'
                    if '🚨' in val: return 'background-color: #FEF3C7; color: #92400E; font-weight: 600;'
                    if '⏳' in val: return 'background-color: #DBEAFE; color: #1E40AF; font-weight: 600;'
                return ''
                
            df_comp = pd.DataFrame(comp_data)
            try: styled_comp = df_comp.style.map(color_comparativa)
            except: styled_comp = df_comp.style.applymap(color_comparativa)
            st.dataframe(styled_comp, hide_index=True, use_container_width=True)

        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Ranking de Puntos</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns([1,3])
            filtro_p = c_fil1.selectbox("⏳ Filtrar Ranking:", ["Período Activo (Desde Reseteo)", "Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_p")
            rango_punt = c_fil2.date_input("📅 Fechas:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_p == "Personalizado" else None
            
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
            ajustes_per = [p for p in lista_puntos if p_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= p_fi]
            ranking_data = []
            
            for emp in lista_empleados:
                e_aj = sum([int(p.get('Puntos', 0)) for p in ajustes_per if p.get('Empleado') == emp and p.get('Estado', 'Aprobada') == 'Aprobada'])
                e_tp = pd.to_numeric(df_t[(df_t["Empleado"] == emp) & (df_t["Estado"] == "Aprobada")]["Puntos"], errors='coerce').fillna(0).astype(int).sum() if not df_t.empty else 0
                df_e = df_p[df_p["Empleado"] == emp] if not df_p.empty else pd.DataFrame()
                e_ok = len(df_e[df_e["Estado"] == "A tiempo"]) if not df_e.empty else 0
                e_tar = len(df_e[df_e["Estado"] == "Tarde"]) if not df_e.empty else 0
                e_au = len(df_e[df_e["Tipo"] == "Ausente"]) if not df_e.empty else 0
                puntaje = reg.get('base', 100) + (e_ok * reg.get('A tiempo', 0)) + (e_tar * reg.get('Tarde', -5)) + (e_au * reg.get('Ausente', -15)) + e_aj + e_tp
                ranking_data.append({"Personal": emp, "Nivel": calcular_nivel(puntaje), "⭐ PUNTOS": puntaje, "📝 Pts Tareas": e_tp, "⚖️ Ajustes": e_aj, "🚨 Tardes": e_tar, "❌ Faltas": e_au})
                
            st.dataframe(pd.DataFrame(ranking_data).sort_values(by="⭐ PUNTOS", ascending=False), use_container_width=True, hide_index=True)
            st.markdown("---")
            st.subheader("✍️ Cargar Bono o Multa Manual")
            with st.form("form_bonos"):
                c_b1, c_b2, c_b3, c_b4 = st.columns([2,1,1,2])
                ap_emp = c_b1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                ap_fecha = c_b2.date_input("Fecha:", ahora.date())
                ap_puntos = c_b3.number_input("Puntos (+/-):", value=0, step=1)
                ap_motivo = c_b4.text_input("Motivo:")
                if st.form_submit_button("Aplicar a Puntuación"):
                    if ap_emp == "Seleccionar..." or ap_puntos == 0 or not ap_motivo.strip():
                        st.warning("⚠️ Faltan completar datos.")
                    else:
                        lista_puntos.append({"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo.strip(), "Autor": "Gerencia", "Estado": "Aprobada"})
                        save_json("ajustes_puntos", lista_puntos)
                        st.success("✅ Bono/Multa aplicado y guardado en la nube.")
                        st.rerun()

        with tab_tareas:
            st.subheader("🚪 Solicitudes de Retiro Temprano")
            if salidas_pendientes:
                for idx, sp in enumerate(salidas_pendientes):
                    st.markdown(f"<div class='task-pend'><b>{sp['Empleado']}</b> solicitó salir a las <b>{sp['Hora']}</b> (Auditor: {sp['Autor']})<br>Motivo: <i>{sp['Nota']}</i></div>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Aprobar Salida", key=f"apr_sal_{idx}"):
                        insert_row("asistencia", {"Fecha": sp["Fecha"], "Hora": sp["Hora"], "Empleado": sp["Empleado"], "Sucursal": sp["Sucursal"], "Turno": sp["Turno"], "Tipo": "Salida", "Estado": "Retiro Temprano", "Nota": sp["Nota"]})
                        salidas_pendientes.pop(idx)
                        save_json("salidas_pendientes", salidas_pendientes)
                        st.success("Salida aprobada y registrada en la asistencia.")
                        st.rerun()
                    if c2.button("❌ Denegar", key=f"den_sal_{idx}"):
                        salidas_pendientes.pop(idx)
                        save_json("salidas_pendientes", salidas_pendientes)
                        st.success("Solicitud denegada y eliminada.")
                        st.rerun()
            else:
                st.info("No hay solicitudes de retiro temprano pendientes.")
                
            st.markdown("---")
            st.subheader("📋 Tareas Pendientes de Aprobación")
            df_tl_all = load_df("tareas_log")
            if not df_tl_all.empty:
                pend_tareas = df_tl_all[df_tl_all["Estado"] == "Pendiente"]
                for idx, row in pend_tareas.iterrows():
                    c_p1, c_p2, c_p3 = st.columns([4, 1, 1])
                    c_p1.markdown(f"**{row['Empleado']}** reportó: '{row['Tarea']}' (+{row['Puntos']} pts)")
                    if c_p2.button("✅ Aprobar", key=f"apr_t_{row['id']}"):
                        supabase.table("tareas_log").update({"Estado": "Aprobada"}).eq("id", int(row['id'])).execute()
                        st.rerun()
                    if c_p3.button("❌ Rechazar", key=f"rec_t_{row['id']}"):
                        supabase.table("tareas_log").update({"Estado": "Rechazada"}).eq("id", int(row['id'])).execute()
                        st.rerun()
                        
            puntos_pendientes = [p for p in lista_puntos if p.get("Estado") == "Pendiente"]
            if puntos_pendientes:
                st.write("**Evaluaciones Pendientes (De Supervisores):**")
                for idx, p in enumerate(lista_puntos):
                    if p.get("Estado") == "Pendiente":
                        c_pp1, c_pp2, c_pp3 = st.columns([4, 1, 1])
                        c_pp1.markdown(f"**{p['Autor']}** sugiere **{p['Puntos']} pts** a **{p['Empleado']}** (Motivo: {p['Motivo']})")
                        if c_pp2.button("✅ Aprobar", key=f"apr_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Aprobada"; save_json("ajustes_puntos", lista_puntos); st.rerun()
                        if c_pp3.button("❌ Rechazar", key=f"rec_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Rechazada"; save_json("ajustes_puntos", lista_puntos); st.rerun()
                            
            st.subheader("📬 Buzón de Quejas y Reportes")
            for idx, r in enumerate(reportes_log):
                if r.get("Estado") == "Pendiente de lectura":
                    st.markdown(f"<div class='report-box'><b>📬 NUEVO REPORTE</b> | Fecha: {r['Fecha']} {r['Hora']}<br><b>Emisor:</b> {r['Emisor']} | <b>Tipo:</b> {r['Tipo']}<br><b>Detalle:</b> <i>'{r['Detalle']}'</i></div>", unsafe_allow_html=True)
                    if st.button("Marcar como Visto", key=f"visto_rep_{idx}"):
                        reportes_log[idx]["Estado"] = "Visto"; save_json("reportes", reportes_log); st.rerun()

        with tab_perfil:
            st.markdown('<div class="main-title" style="font-size: 2rem;">👤 Dossier Individual 360°</div>', unsafe_allow_html=True)
            col_pf1, col_pf2 = st.columns([1,3])
            emp_perfil = col_pf1.selectbox("Seleccionar Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
            filtro_pf = col_pf2.selectbox("⏳ Periodo a evaluar:", ["Este Mes", "Mes Anterior", "Esta Semana", "Todo el Historial"], key="filtro_perf")
            pf_in, pf_fi = get_fechas_filtro(filtro_pf)
            
            if emp_perfil != "Seleccionar...":
                st.write(f"**Rol:** `{roles_empleados.get(emp_perfil, 'N/A')}` | **Estado:** {'🔗 Enlazado' if emp_perfil in dispositivos_vinculados else '📱 Sin Celular'}")
                df_act_p, df_tar_p = load_df("asistencia"), load_df("tareas_log")
                if not df_act_p.empty:
                    df_act_p['F_Obj'] = pd.to_datetime(df_act_p['Fecha'], errors='coerce').dt.date
                    df_e_p = df_act_p[(df_act_p["Empleado"] == emp_perfil) & (df_act_p['F_Obj'] >= pf_in) & (df_act_p['F_Obj'] <= pf_fi)]
                    e_atiempo = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "A tiempo")])
                    e_tardes = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "Tarde")])
                    e_ausencias = len(df_e_p[df_e_p["Tipo"] == "Ausente"])
                    horas_totales = 0.0
                    
                    for f in df_e_p["Fecha"].unique():
                        df_ef = df_e_p[df_e_p["Fecha"] == f].copy()
                        df_ef['Hora_dt'] = pd.to_datetime(df_ef['Hora'], errors='coerce')
                        df_ef = df_ef.dropna(subset=['Hora_dt']).sort_values(by="Hora_dt")
                        
                        entrada_actual = None
                        
                        for _, row_f in df_ef.iterrows():
                            if row_f["Tipo"] == "Entrada":
                                entrada_actual = row_f
                            elif row_f["Tipo"] == "Salida" and entrada_actual is not None:
                                h_in = entrada_actual["Hora_dt"]
                                h_out = row_f["Hora_dt"]
                                turno_actual_eval = entrada_actual["Turno"]
                                
                                horas_tramo = 0.0
                                if turno_actual_eval in lista_turnos:
                                    h_ofi_in_str = lista_turnos[turno_actual_eval].get("ingreso")
                                    h_ofi_out_str = lista_turnos[turno_actual_eval].get("salida")
                                    if h_ofi_in_str and h_ofi_out_str:
                                        try:
                                            t_in_obj = datetime.datetime.strptime(h_ofi_in_str, "%I:%M %p").time()
                                            t_out_obj = datetime.datetime.strptime(h_ofi_out_str, "%I:%M %p").time()
                                            
                                            h_in_oficial = datetime.datetime.combine(h_in.date(), t_in_obj)
                                            h_out_oficial = datetime.datetime.combine(h_in.date(), t_out_obj)
                                            
                                            if h_out_oficial < h_in_oficial: h_out_oficial += datetime.timedelta(days=1)
                                            
                                            horas_tramo = (h_out_oficial - h_in_oficial).total_seconds() / 3600.0
                                            
                                            if config_app.get("desc_tarde", True):
                                                diff_tarde = (h_in - h_in_oficial).total_seconds() / 3600.0
                                                if diff_tarde > 0: horas_tramo -= diff_tarde
                                            if config_app.get("desc_temp", True):
                                                diff_temp = (h_out_oficial - h_out).total_seconds() / 3600.0
                                                if diff_temp > 0: horas_tramo -= diff_temp
                                        except:
                                            horas_tramo = (h_out - h_in).total_seconds() / 3600.0
                                else:
                                    horas_tramo = (h_out - h_in).total_seconds() / 3600.0
                                
                                if horas_tramo < 0: horas_tramo += 24.0
                                horas_totales += max(0.0, horas_tramo)
                                entrada_actual = None
                        
                    e_aj = sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == emp_perfil and p.get('Estado') == 'Aprobada' and pf_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= pf_fi])
                    e_tp = 0
                    if not df_tar_p.empty:
                        df_tar_p['F_Obj'] = pd.to_datetime(df_tar_p['Fecha'], errors='coerce').dt.date
                        e_tp = pd.to_numeric(df_tar_p[(df_tar_p["Empleado"] == emp_perfil) & (df_tar_p["Estado"] == "Aprobada") & (df_tar_p['F_Obj'] >= pf_in) & (df_tar_p['F_Obj'] <= pf_fi)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
                        
                    reg = config_app.get("reglas_puntos", {})
                    puntaje = reg.get('base', 100) + (e_atiempo * reg.get('A tiempo', 0)) + (e_tardes * reg.get('Tarde', -5)) + (e_ausencias * reg.get('Ausente', -15)) + e_aj + e_tp
                    c_pf1, c_pf2, c_pf3, c_pf4 = st.columns(4)
                    
                    c_pf1.metric("⏱️ Horas Trabajadas", formato_horas_texto(horas_totales))
                    c_pf2.metric("⭐ Puntos", f"{puntaje} pts")
                    c_pf3.metric("🚨 Tardes", e_tardes)
                    c_pf4.metric("❌ Ausencias", e_ausencias)
                    
                    with st.expander("Ficha Detallada"):
                        if 'id' in df_e_p.columns:
                            df_e_p['id_num'] = pd.to_numeric(df_e_p['id'], errors='coerce')
                            df_e_p = df_e_p.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_e_p[["Fecha", "Hora", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]], use_container_width=True, hide_index=True)

        with tab_staff:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader("📱 Estado de Celulares")
                datos_conexion = []
                for emp in sorted(lista_empleados):
                    estado_cel = "🟢 Enlazado" if emp in dispositivos_vinculados else "🔴 Sin Enlazar"
                    datos_conexion.append({"Empleado": emp, "Celular": estado_cel})
                st.dataframe(pd.DataFrame(datos_conexion), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("➕ Alta y Modificación")
                with st.form("form_alta_emp"):
                    nuevo_emp = st.text_input("Nuevo Empleado (Carga manual):")
                    rol_asignar = st.selectbox("Rol:", lista_roles_disponibles)
                    if st.form_submit_button("➕ Agregar a la lista") and nuevo_emp:
                        n_emp = nuevo_emp.strip()
                        if any(e.lower() == n_emp.lower() for e in lista_empleados):
                            st.error("🚨 Ese empleado ya existe. No se permiten nombres repetidos.")
                        else:
                            lista_empleados.append(n_emp)
                            roles_empleados[n_emp] = rol_asignar
                            tareas_individuales[n_emp] = []
                            save_json("empleados", lista_empleados)
                            save_json("roles", roles_empleados)
                            save_json("tareas_individuales", tareas_individuales)
                            st.success(f"✅ Empleado '{n_emp}' agregado correctamente.")
                            st.rerun()
                        
                if lista_empleados:
                    st.markdown("---")
                    st.markdown("**✏️ Editar Empleado Existente**")
                    emp_mod = st.selectbox("Seleccionar empleado:", sorted(lista_empleados))
                    nuevo_nombre_mod = st.text_input("Modificar Nombre (Si querés corregirlo):", value=emp_mod)
                    nuevo_rol = st.selectbox("Cambiar Rol a:", lista_roles_disponibles, index=lista_roles_disponibles.index(roles_empleados.get(emp_mod, lista_roles_disponibles[0])) if roles_empleados.get(emp_mod) in lista_roles_disponibles else 0)
                    c_mod1, c_mod2, c_mod3 = st.columns(3)
                    
                    if c_mod1.button("💾 Guardar Cambios"):
                        nn = nuevo_nombre_mod.strip()
                        if nn and nn != emp_mod:
                            if any(e.lower() == nn.lower() for e in lista_empleados):
                                st.error("🚨 Ese nombre ya está en uso por otro empleado.")
                            else:
                                lista_empleados.remove(emp_mod)
                                lista_empleados.append(nn)
                                roles_empleados[nn] = nuevo_rol
                                roles_empleados.pop(emp_mod, None) 
                                if emp_mod in tareas_individuales: tareas_individuales[nn] = tareas_individuales.pop(emp_mod)
                                if emp_mod in dispositivos_vinculados: dispositivos_vinculados[nn] = dispositivos_vinculados.pop(emp_mod)
                                save_json("empleados", lista_empleados)
                                save_json("roles", roles_empleados)
                                save_json("tareas_individuales", tareas_individuales)
                                save_json("dispositivos", dispositivos_vinculados)
                                
                                for p in lista_puntos:
                                    if p.get('Empleado') == emp_mod: p['Empleado'] = nn
                                    if p.get('Autor') == emp_mod: p['Autor'] = nn
                                save_json("ajustes_puntos", lista_puntos)
                                for sp in salidas_pendientes:
                                    if sp.get('Empleado') == emp_mod: sp['Empleado'] = nn
                                    if sp.get('Autor') == emp_mod: sp['Autor'] = nn
                                save_json("salidas_pendientes", salidas_pendientes)
                                for r in reportes_log:
                                    if r.get('Emisor') == emp_mod: r['Emisor'] = nn
                                    if r.get('Implicado') == emp_mod: r['Implicado'] = nn
                                save_json("reportes", reportes_log)
                                for a in alertas_ingreso:
                                    if a.get('destinatario') == emp_mod: a['destinatario'] = nn
                                save_json("alertas_ingreso", alertas_ingreso)
                                for m in lista_mensajes:
                                    if m.get('destinatario') == emp_mod: m['destinatario'] = nn
                                save_json("mensajes", lista_mensajes)
                                for sh in sueldos_historico:
                                    if sh.get('Empleado') == emp_mod: sh['Empleado'] = nn
                                save_json("sueldos_historico", sueldos_historico)
                                for cc in cierres_caja:
                                    if cc.get('Cajero') == emp_mod: cc['Cajero'] = nn
                                save_json("cierres_caja", cierres_caja)
                                if emp_mod in planificacion_turnos: planificacion_turnos[nn] = planificacion_turnos.pop(emp_mod)
                                for fecha_plan, emps in planificacion_turnos.items():
                                    for loc_p, turnos_p in emps.items():
                                        if isinstance(turnos_p, dict):
                                            for turno_p, list_emps in turnos_p.items():
                                                if emp_mod in list_emps:
                                                    list_emps[list_emps.index(emp_mod)] = nn
                                save_json("planificacion_turnos", planificacion_turnos)
                                try:
                                    supabase.table("asistencia").update({"Empleado": nn}).eq("Empleado", emp_mod).execute()
                                    supabase.table("tareas_log").update({"Empleado": nn}).eq("Empleado", emp_mod).execute()
                                except: pass
                                st.success(f"Nombre actualizado a {nn} en toda la base de datos.")
                                st.rerun()
                        else:
                            roles_empleados[emp_mod] = nuevo_rol
                            save_json("roles", roles_empleados)
                            st.success("Rol actualizado.")
                            st.rerun()
                        
                    if c_mod2.button("🔓 Liberar Celular") and emp_mod in dispositivos_vinculados:
                        del dispositivos_vinculados[emp_mod]
                        save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()
                    if c_mod3.button("🗑️ Borrar Empleado"):
                        lista_empleados.remove(emp_mod)
                        roles_empleados.pop(emp_mod, None)
                        tareas_individuales.pop(emp_mod, None)
                        dispositivos_vinculados.pop(emp_mod, None)
                        save_json("empleados", lista_empleados)
                        save_json("roles", roles_empleados)
                        save_json("tareas_individuales", tareas_individuales)
                        save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()
                        
            with col_s2:
                st.subheader("📋 Asignar Tareas Extra")
                tipo_asig = st.radio("Asignar a:", ["Rol General", "Personal"])
                obj_tarea = st.selectbox("Elegí el destino:", lista_roles_disponibles if tipo_asig == "Rol General" else sorted(lista_empleados))
                n_tarea, p_tarea = st.text_input("Nombre Tarea:"), st.number_input("Puntos:", value=5, min_value=1)
                
                if st.button("➕ Asignar Tarea") and n_tarea:
                    if tipo_asig == "Rol General":
                        tareas_roles.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json("tareas_roles", tareas_roles)
                    else:
                        tareas_individuales.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json("tareas_individuales", tareas_individuales)
                    st.rerun()
                    
                ver_t_tipo = st.radio("Ver tareas de:", ["Roles", "Personales"])
                diccionario_ver = tareas_roles if ver_t_tipo == "Roles" else tareas_individuales
                for clave, tareas in diccionario_ver.items():
                    if tareas:
                        with st.expander(f"{clave}"):
                            for idx, t in enumerate(tareas):
                                c_t1, c_t2 = st.columns([3,1])
                                c_t1.write(f"- {t.get('tarea')} (+{t.get('puntos')})")
                                if c_t2.button("🗑️", key=f"del_t_{clave}_{idx}"):
                                    diccionario_ver[clave].pop(idx)
                                    save_json("tareas_roles" if ver_t_tipo == "Roles" else "tareas_individuales", diccionario_ver)
                                    st.rerun()

        with tab_tiendas:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("🏢 Tiendas Físicas")
                for loc, d_loc in lista_locales.items(): 
                    st.write(f"- **{loc}** | IP: `{d_loc.get('ip', 'Ninguna')}` | Lat: {d_loc.get('lat')} | Lon: {d_loc.get('lon')}")
                st.markdown("---")
                ip_gerencia = st.session_state.get('client_ip')
                if not ip_gerencia:
                    ip_eval = streamlit_js_eval(js_expressions="fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')", want_output=True, key="ip_manager")
                    if ip_eval:
                        st.session_state['client_ip'] = ip_eval
                        ip_gerencia = ip_eval
                if ip_gerencia and ip_gerencia != 'Error':
                    st.info(f"ℹ️ **Ayuda de Configuración:** La IP actual de tu conexión es `{ip_gerencia}`. (Si estás físicamente en la sucursal nueva, podés copiar y pegar este número abajo).")
                else: st.info("🔍 Buscando tu IP actual para ayudarte a configurar...")
                
                with st.expander("➕ Crear Nueva Tienda", expanded=False):
                    n_loc = st.text_input("Nombre Nueva Tienda:")
                    lat_loc = st.number_input("Lat:", format="%.6f")
                    lon_loc = st.number_input("Lon:", format="%.6f")
                    ip_loc = st.text_input("IP Wi-Fi:")
                    if st.button("➕ Crear Tienda") and n_loc:
                        lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc, "ip": ip_loc.strip()}
                        save_json("locales", lista_locales)
                        st.rerun()
                        
                st.markdown("---")
                st.markdown("**✏️ Editar Tienda Existente**")
                loc_mod = st.selectbox("Seleccionar tienda a editar:", ["Seleccionar..."] + list(lista_locales.keys()))
                if loc_mod != "Seleccionar...":
                    n_loc_mod = st.text_input("Modificar Nombre:", value=loc_mod)
                    lat_mod = st.number_input("Modificar Lat:", value=float(lista_locales[loc_mod].get("lat", 0.0)), format="%.6f")
                    lon_mod = st.number_input("Modificar Lon:", value=float(lista_locales[loc_mod].get("lon", 0.0)), format="%.6f")
                    ip_mod = st.text_input("Modificar IP Wi-Fi:", value=lista_locales[loc_mod].get("ip", ""))
                    
                    if st.button("💾 Guardar Cambios de Tienda"):
                        nuevo_nombre = n_loc_mod.strip()
                        if nuevo_nombre and nuevo_nombre != loc_mod:
                            if nuevo_nombre not in lista_locales:
                                lista_locales[nuevo_nombre] = {"lat": lat_mod, "lon": lon_mod, "ip": ip_mod.strip()}
                                del lista_locales[loc_mod]
                                for f_str in planificacion_turnos:
                                    if loc_mod in planificacion_turnos[f_str]:
                                        planificacion_turnos[f_str][nuevo_nombre] = planificacion_turnos[f_str].pop(loc_mod)
                                save_json("planificacion_turnos", planificacion_turnos)
                                save_json("locales", lista_locales)
                                st.success(f"✅ Tienda actualizada a {nuevo_nombre}.")
                                st.rerun()
                            else:
                                st.warning("⚠️ Ese nombre de tienda ya existe.")
                        else:
                            lista_locales[loc_mod] = {"lat": lat_mod, "lon": lon_mod, "ip": ip_mod.strip()}
                            save_json("locales", lista_locales)
                            st.success("✅ Datos de la tienda actualizados.")
                            st.rerun()

                st.markdown("---")
                borrar_loc = st.selectbox("Eliminar Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Tienda") and borrar_loc != "Seleccionar...":
                    del lista_locales[borrar_loc]; save_json("locales", lista_locales); st.rerun()
                    
            with col_l2:
                st.subheader("⏰ Turnos / Horarios")
                for turno, horas in lista_turnos.items(): st.write(f"- **{turno}** | De {horas.get('ingreso')} a {horas.get('salida')}")
                
                with st.expander("➕ Crear Nuevo Horario", expanded=False):
                    n_turno = st.text_input("Nuevo Horario (Nombre):")
                    c_h1, c_h2 = st.columns(2)
                    h_ingreso, h_salida = c_h1.time_input("Ingreso:"), c_h2.time_input("Salida:")
                    if st.button("➕ Crear Horario") and n_turno:
                        lista_turnos[n_turno] = {"ingreso": h_ingreso.strftime("%I:%M %p"), "salida": h_salida.strftime("%I:%M %p")}
                        save_json("turnos", lista_turnos)
                        st.rerun()
                        
                st.markdown("---")
                st.markdown("**✏️ Editar Horario Existente**")
                turno_mod = st.selectbox("Seleccionar turno a editar:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if turno_mod != "Seleccionar...":
                    n_turno_mod = st.text_input("Modificar Nombre Turno:", value=turno_mod)
                    try:
                        time_ing_def = datetime.datetime.strptime(lista_turnos[turno_mod].get('ingreso'), "%I:%M %p").time()
                        time_sal_def = datetime.datetime.strptime(lista_turnos[turno_mod].get('salida'), "%I:%M %p").time()
                    except:
                        time_ing_def, time_sal_def = ahora.time(), ahora.time()
                        
                    c_hm1, c_hm2 = st.columns(2)
                    hm_ingreso = c_hm1.time_input("Modificar Ingreso:", value=time_ing_def)
                    hm_salida = c_hm2.time_input("Modificar Salida:", value=time_sal_def)
                    
                    if st.button("💾 Guardar Horario"):
                        nuevo_nombre_t = n_turno_mod.strip()
                        if nuevo_nombre_t and nuevo_nombre_t != turno_mod:
                            if nuevo_nombre_t not in lista_turnos:
                                lista_turnos[nuevo_nombre_t] = {"ingreso": hm_ingreso.strftime("%I:%M %p"), "salida": hm_salida.strftime("%I:%M %p")}
                                del lista_turnos[turno_mod]
                                save_json("turnos", lista_turnos)
                                st.success("✅ Turno actualizado.")
                                st.rerun()
                            else:
                                st.warning("⚠️ Ese nombre de turno ya existe.")
                        else:
                            lista_turnos[turno_mod] = {"ingreso": hm_ingreso.strftime("%I:%M %p"), "salida": hm_salida.strftime("%I:%M %p")}
                            save_json("turnos", lista_turnos)
                            st.success("✅ Horario actualizado.")
                            st.rerun()

                st.markdown("---")
                borrar_turno = st.selectbox("Eliminar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno") and borrar_turno != "Seleccionar...":
                    del lista_turnos[borrar_turno]; save_json("turnos", lista_turnos); st.rerun()

        with tab_comunicados:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.subheader("🔔 Alerta al Ingresar")
                with st.form("form_alertas"):
                    dest_ing = st.selectbox("Destinatario:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados))
                    txt_alerta = st.text_area("Mensaje:")
                    if st.form_submit_button("Crear Alerta") and txt_alerta:
                        alertas_ingreso.append({"destinatario": dest_ing, "texto": txt_alerta})
                        save_json("alertas_ingreso", alertas_ingreso); st.rerun()
                for idx, a in enumerate(alertas_ingreso):
                    with st.expander(f"A {a['destinatario']}: {a['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_al_{idx}"):
                            alertas_ingreso.pop(idx); save_json("alertas_ingreso", alertas_ingreso); st.rerun()
                            
            with col_m2:
                st.subheader("📢 Anuncio Fijo")
                with st.form("form_fijo"):
                    dest_fijo = st.selectbox("Destinatario:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados), key="fijo")
                    txt_fijo = st.text_area("Mensaje:")
                    if st.form_submit_button("Publicar") and txt_fijo:
                        lista_mensajes.append({"destinatario": dest_fijo, "texto": txt_fijo})
                        save_json("mensajes", lista_mensajes); st.rerun()
                for idx, m in enumerate(lista_mensajes):
                    with st.expander(f"A {m['destinatario']}: {m['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_m_{idx}"):
                            lista_mensajes.pop(idx); save_json("mensajes", lista_mensajes); st.rerun()

        with tab_config:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("👥 Roles de la Empresa")
                nuevo_rol_cat = st.text_input("Crear Nuevo Rol:")
                if st.button("➕ Agregar Rol") and nuevo_rol_cat and nuevo_rol_cat not in lista_roles_disponibles:
                    lista_roles_disponibles.append(nuevo_rol_cat); save_json("lista_roles", lista_roles_disponibles); st.rerun()
                borrar_rol_cat = st.selectbox("Eliminar Rol:", ["Seleccionar..."] + lista_roles_disponibles)
                if st.button("🗑️ Eliminar Rol") and borrar_rol_cat != "Seleccionar...":
                    lista_roles_disponibles.remove(borrar_rol_cat); save_json("lista_roles", lista_roles_disponibles); st.rerun()
                    
                st.subheader("⚖️ Reglas de Asistencia")
                with st.form("form_reglas"):
                    r_base = st.number_input("Puntaje Base:", value=config_app.get("reglas_puntos", {}).get("base", 100))
                    c_r1, c_r2 = st.columns(2)
                    r_ok, r_tar = c_r1.number_input("✔️ A Tiempo:", value=config_app.get("reglas_puntos", {}).get("A tiempo", 0)), c_r2.number_input("Tarde:", value=config_app.get("reglas_puntos", {}).get("Tarde", -5))
                    r_aus, r_fj = c_r1.number_input("❌ Ausente:", value=config_app.get("reglas_puntos", {}).get("Ausente", -15)), c_r2.number_input("📝 Justif:", value=config_app.get("reglas_puntos", {}).get("Falta Justificada", 0))
                    if st.form_submit_button("💾 Guardar Reglas"):
                        config_app["reglas_puntos"] = {"base": r_base, "A tiempo": r_ok, "Tarde": r_tar, "Ausente": r_aus, "Falta Justificada": r_fj}
                        save_json("config", config_app); st.rerun()
                        
            with col_aj2:
                st.subheader("🛡️ Seguridad de Red y Ajustes")
                with st.form("form_seguridad"):
                    v_autoregistro = st.checkbox("📝 Permitir Auto-registro de empleados", value=config_app.get("autoregistro", False), help="Los empleados podrán escribir su propio nombre al abrir la app por primera vez.")
                    v_gps = st.checkbox("🛰️ Requerir GPS para Entrada", value=config_app.get("verificar_gps", True))
                    radio_m = st.number_input("Radio en metros:", value=int(config_app.get("radio_metros", 50)))
                    v_wifi = st.checkbox("📶 Requerir Wi-Fi para Entrada", value=config_app.get("verificar_wifi", False))
                    nueva_tolerancia = st.number_input("Minutos tolerancia (llegada tarde):", value=int(config_app.get("tolerancia_minutos", 10)))
                    st.markdown("---")
                    st.markdown("#### Ajustes de Recuento de Horas")
                    v_exigir_salida_manual = st.checkbox("🚪 Exigir Fichaje de Salida Manual", value=config_app.get("exigir_salida_manual", False), help="Si se desactiva, la salida es automática y no se les pedirá fichar al irse.")
                    v_desc_tarde = st.checkbox("⏱️ Descontar Llegada Tarde del total de horas", value=config_app.get("desc_tarde", True))
                    v_desc_temp = st.checkbox("🏃‍♂️ Descontar Salida Temprano del total de horas", value=config_app.get("desc_temp", True))
                    if st.form_submit_button("💾 Guardar Ajustes"):
                        config_app.update({"autoregistro": v_autoregistro, "verificar_gps": v_gps, "verificar_wifi": v_wifi, "radio_metros": radio_m, "tolerancia_minutos": nueva_tolerancia, "exigir_salida_manual": v_exigir_salida_manual, "desc_tarde": v_desc_tarde, "desc_temp": v_desc_temp})
                        save_json("config", config_app); st.rerun()
                        
                st.write("🔑 **Cambiar Clave de Gerencia**")
                nc = st.text_input("Nueva clave:", type="password")
                if st.button("💾 Cambiar Clave") and nc:
                    config_app["admin_password"] = nc; save_json("config", config_app); st.success("Clave modificada.")
                    
                st.markdown("---")
                st.subheader("🔄 Reiniciar Sistema de Puntos")
                st.write("Fijá una nueva fecha de inicio. Los puntos se contarán de cero desde la fecha que elijas (Ideal para cortes semanales o mensuales).")
                nueva_fecha_puntos = st.date_input("Nueva fecha de inicio:", value=ahora.date())
                if st.button("🔄 Reiniciar Puntos Ahora", type="primary"):
                    config_app["fecha_inicio_puntos"] = nueva_fecha_puntos.strftime("%Y-%m-%d")
                    save_json("config", config_app)
                    st.success(f"✅ ¡Puntos reseteados! El contador arrancará desde el {nueva_fecha_puntos.strftime('%d/%m/%Y')}.")
                    st.rerun()
                    
                st.markdown("---")
                st.subheader("🧹 Reseteo Quirúrgico en Nube")
                c_cl1, c_cl2 = st.columns(2)
                with c_cl1:
                    del_asist = st.checkbox("Registros de Asistencia")
                    del_tareas = st.checkbox("Tareas Realizadas")
                    del_bonos = st.checkbox("Bonos/Multas Manuales")
                with c_cl2:
                    filtro_b = st.selectbox("⏳ Rango a borrar:", ["Hoy", "Esta Semana", "Este Mes", "Mes Anterior", "Todo el Historial", "Personalizado"], key="filtro_borrado")
                    rango_borrado = st.date_input("📅 Fechas a limpiar:", value=(ahora.date(), ahora.date())) if filtro_b == "Personalizado" else None
                if st.button("🗑️ CONFIRMAR BORRADO"):
                    b_in, b_fi = get_fechas_filtro(filtro_b, rango_borrado)
                    if del_asist: supabase.table("asistencia").delete().gte("Fecha", b_in.strftime("%Y-%m-%d")).lte("Fecha", b_fi.strftime("%Y-%m-%d")).execute()
                    if del_tareas: supabase.table("tareas_log").delete().gte("Fecha", b_in.strftime("%Y-%m-%d")).lte("Fecha", b_fi.strftime("%Y-%m-%d")).execute()
                    if del_bonos:
                        lista_puntos = [p for p in lista_puntos if not (b_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= b_fi)]
                        save_json("ajustes_puntos", lista_puntos)
                    st.success("¡Datos borrados de la nube exitosamente!")
                    st.rerun()

        with tab_espia:
            if lista_intentos:
                st.dataframe(pd.DataFrame(lista_intentos).sort_values(by=["Fecha", "Hora"], ascending=[False, False]), use_container_width=True, hide_index=True)
                if st.button("🗑️ Limpiar registro"): save_json("intentos_seguridad", []); st.rerun()
            else: st.info("Sin intentos de acceso.")

# ==========================================
# 7. PANEL EXCLUSIVO DEL DUEÑO DEL SOFTWARE
# ==========================================
elif pestaña == "⚙️ Dueño del Software":
    st.markdown('<div class="main-title">👨‍💻 Administrador del Sistema</div>', unsafe_allow_html=True)
    st.info("🔒 Área restringida exclusiva para el propietario y desarrollador del software.")
    pass_dueño = st.text_input("Ingrese la Clave Maestra:", type="password")
    
    if pass_dueño == "SantiMaster2026":
        st.success("✅ Acceso Maestro Concedido")
        tab_licencia, tab_equipos, tab_empresa, tab_reset, tab_incognito = st.tabs([
            "🔑 Control de Licencia", "📱 Gestión de Sesiones", "🏢 Empresa", "☢️ Botón Nuclear", "🕵️ Modo Incógnito"
        ])
        
        with tab_licencia:
            st.subheader("Estado de la Licencia del Cliente")
            with st.form("form_licencia"):
                estado_actual = st.selectbox("Estado del Sistema:", ["Activo", "Suspendido"], index=["Activo", "Suspendido"].index(owner_config.get("estado_licencia", "Activo")))
                plan_actual = st.selectbox("Plan de Pago contratado:", ["Mensual", "Anual", "Vitalicio"], index=["Mensual", "Anual", "Vitalicio"].index(owner_config.get("plan_pago", "Mensual")))
                v_mostrar_membresia = st.checkbox("🏷️ Mostrar etiqueta de membresía a los empleados", value=owner_config.get("mostrar_membresia", False), help="Si se activa, todos verán el plan contratado en el menú lateral.")
                fecha_venc = st.date_input("Fecha de Vencimiento Automático:", value=datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date(), min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2099, 12, 31))
                msg_bloqueo = st.text_area("Mensaje de Bloqueo (Se muestra al suspender o vencer):", value=owner_config.get("mensaje_bloqueo", ""))
                st.markdown("---")
                st.write("⏳ **Aviso de Vencimiento Próximo (Solo visible para Gerencia)**")
                dias_aviso = st.number_input("Mostrar aviso preventivo cuántos días antes:", value=owner_config.get("dias_aviso", 5), min_value=0)
                msg_aviso = st.text_area("Mensaje preventivo de vencimiento:", value=owner_config.get("mensaje_aviso", "🚨 Tu suscripción está por vencer. Contactate con soporte para renovar."))
                if st.form_submit_button("💾 Guardar Estado"):
                    owner_config.update({"estado_licencia": estado_actual, "plan_pago": plan_actual, "fecha_vencimiento": str(fecha_venc), "mensaje_bloqueo": msg_bloqueo, "mostrar_membresia": v_mostrar_membresia, "dias_aviso": dias_aviso, "mensaje_aviso": msg_aviso})
                    save_json("owner_config", owner_config)
                    st.success("¡Licencia y avisos actualizados! El sistema obedecerá automáticamente.")
                    st.rerun()
                    
        with tab_equipos:
            st.subheader("🔌 Desconectar Dispositivos Remotamente")
            st.write("Acá podés ver quién está logueado en la aplicación y forzar el cierre de sesión.")
            if dispositivos_vinculados:
                for emp, dev in dispositivos_vinculados.items(): st.markdown(f"- 👤 **{emp}** (ID Interno: `{dev[:10]}...`)")
                emp_desvincular = st.selectbox("Seleccionar empleado para cerrar sesión:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                c_eq1, c_eq2 = st.columns(2)
                if c_eq1.button("🔌 Desconectar a este empleado") and emp_desvincular != "Seleccionar...":
                    del dispositivos_vinculados[emp_desvincular]; save_json("dispositivos", dispositivos_vinculados); st.success(f"✅ Sesión cerrada para {emp_desvincular}."); st.rerun()
                if c_eq2.button("🚫 CERRAR TODAS LAS SESIONES"):
                    dispositivos_vinculados.clear(); save_json("dispositivos", {}); st.success("✅ ¡Todos los empleados han sido desconectados!"); st.rerun()
            else: st.info("No hay ningún empleado logueado en este momento.")
            
        with tab_empresa:
            st.subheader("Personalizar Información 'Quiénes Somos'")
            st.write("Esta información aparecerá en el menú inferior para que todos los empleados la vean.")
            with st.form("form_empresa"):
                nombre_empresa = st.text_input("Nombre de la Empresa o Cliente:", value=owner_config.get("empresa_nombre", ""))
                historia = st.text_area("Historia / Quiénes Somos:", value=owner_config.get("quienes_somos", ""))
                datos_contacto = st.text_area("Datos de Contacto (Teléfonos, mails, etc):", value=owner_config.get("contactos", ""))
                if st.form_submit_button("💾 Actualizar Pantalla Pública"):
                    owner_config.update({"empresa_nombre": nombre_empresa, "quienes_somos": historia, "contactos": datos_contacto})
                    save_json("owner_config", owner_config)
                    st.success("¡Información actualizada con éxito!")
                    st.rerun()
                    
        with tab_reset:
            st.subheader("☢️ Instalación 0KM para Nuevo Cliente")
            st.error("¡CUIDADO! Este botón borra ABSOLUTAMENTE TODO (Empleados, roles, tareas, mensajes, fichajes y tiendas). Deja la aplicación en blanco para instalarla en una empresa nueva.")
            check_seguridad = st.checkbox("Estoy seguro que quiero borrar toda la empresa actual.")
            if st.button("☢️ INICIAR DE FÁBRICA (FACTORY RESET)") and check_seguridad:
                save_json("empleados", []); save_json("roles", {}); save_json("tareas_roles", {}); save_json("tareas_individuales", {}); save_json("dispositivos", {})
                save_json("locales", {}); save_json("turnos", {}); save_json("mensajes", []); save_json("alertas_ingreso", []); save_json("intentos_seguridad", [])
                save_json("ajustes_puntos", []); save_json("reportes", []); save_json("salidas_pendientes", []); save_json("sueldos_historico", []); save_json("cierres_caja", [])
                save_json("planificacion_turnos", {})
                try:
                    supabase.table("asistencia").delete().neq("id", 0).execute()
                    supabase.table("tareas_log").delete().neq("id", 0).execute()
                except: pass
                st.success("¡SISTEMA BORRADO! La aplicación está lista para un nuevo cliente.")
                st.rerun()

        with tab_incognito:
            st.subheader("🕵️ Modo Espía / Incógnito")
            st.write("Activá este modo para navegar por la aplicación simulando ser la Gerencia o un Empleado específico sin dejar rastros en los registros de acceso y sin vincular tu propio celular.")
            st.info("💡 **Cómo funciona:** Elegí una identidad de la lista de abajo, hacé clic en 'Aplicar Identidad' y luego movete a la pestaña de 'Portal del Empleado' o 'Panel de Gerencia' en el menú principal de arriba de todo.")

            identidad_actual = st.session_state.get('incognito_user', "Desactivado")
            opciones_identidad = ["Desactivado", "Gerencia"] + sorted(lista_empleados)
            idx_actual = opciones_identidad.index(identidad_actual) if identidad_actual in opciones_identidad else 0

            simular_como = st.selectbox("Simular identidad de:", opciones_identidad, index=idx_actual)

            if st.button("🕵️ Aplicar Identidad", use_container_width=True):
                if simular_como == "Desactivado":
                    st.session_state['incognito'] = False
                    st.session_state['incognito_user'] = None
                    st.success("✅ Modo incógnito desactivado. Ahora navegás como un dispositivo de incógnito normal.")
                else:
                    st.session_state['incognito'] = True
                    st.session_state['incognito_user'] = simular_como
                    st.success(f"✅ ¡Identidad '{simular_como}' aplicada! Navegá por el menú principal para espiar.")
