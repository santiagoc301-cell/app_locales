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
[data-testid="collapsedControl"] { display: none !important; }
/* ---> DISEÑO DE PESTAÑAS (TABS) ESTILO APP MODERNA <--- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; padding-bottom: 5px; }
.stTabs [data-baseweb="tab"] { background-color: #F3F4F6; border-radius: 8px 8px 0 0; padding: 10px 20px; border: 1px solid #E5E7EB; border-bottom: none; transition: all 0.3s ease; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1e3a8a, #3b82f6) !important; color: white !important; font-weight: 800 !important; box-shadow: 0 4px 10px - 2px rgba(0, 0, 0, 0.2); }
.stTabs [data-baseweb="tab"]:hover { background-color: #E0E7FF; }
/* ---> DISEÑO GENERAL DE LA APP <--- */
.main-title { font-size: 2.4rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #111827, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; text-align: center; text-transform: uppercase; letter-spacing: -0.5px; }
div[data-testid="metric-container"] { background: linear-gradient(180deg, #ffffff 0%, #F9FAFB 100%); border: 1px solid #E5E7EB; padding: 20px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-top: 5px solid #3b82f6; transition: transform 0.2s ease-in-out;}
div[data-testid="metric-container"]:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);}
div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 900; color: #111827; }
.stButton>button { border-radius: 12px; font-weight: 700; transition: all 0.3s; border: 1px solid #D1D5DB; padding: 0.6rem 1rem; width: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-color: #9CA3AF;}
.alert-box { padding: 18px; border-radius: 12px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.task-box { padding: 18px; border-radius: 12px; border-left: 6px solid #10B981; background-color: #ECFDF5; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.task-pend { padding: 18px; border-radius: 12px; border-left: 6px solid #F59E0B; background-color: #FFFBEB; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.task-rej { padding: 18px; border-radius: 12px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.report-box { padding: 18px; border-radius: 12px; border-left: 6px solid #8B5CF6; background-color: #F5F3FF; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.super-box { padding: 18px; border-radius: 12px; border-left: 6px solid #3B82F6; background-color: #EFF6FF; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.highlight-edit { padding: 20px; background-color: #EFF6FF; border-radius: 12px; border-left: 6px solid #3B82F6; margin-bottom: 20px; font-weight: bold;}
.credencial { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 25px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4); margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.1);}
.cred-nombre { font-size: 2rem; font-weight: 900; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);}
.cred-rol { font-size: 1.2rem; opacity: 0.95; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;}
.cred-nivel { font-size: 1.4rem; font-weight: 800; background-color: rgba(255,255,255,0.25); padding: 8px 20px; border-radius: 25px; display: inline-block; backdrop-filter: blur(5px);}
.validation-box { padding: 18px; border-radius: 12px; border: 1px solid #E5E7EB; background-color: #F9FAFB; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
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
        st.error("⚠️ Error: No se encontraron los secretos de Supabase en Streamlit.")
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
        # 🔴 FIX: Si hay error de red, devolvemos 'None' en lugar de '{}' para no sobreescribir datos.
        return None 

def load_json(key_name, default_data):
    settings = get_all_settings()
    
    # 🔴 FIX: Si Supabase falló temporalmente, frenamos la app para proteger tu base de datos.
    if settings is None:
        st.error("⏳ Aguardá un momento. Reconectando de forma segura con la base de datos para no perder tu información...")
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
    "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia.", "verificar_gps": True,
    "verificar_wifi": False, "salida_estricta": False, "exigir_salida_manual": False, "autoregistro": False,
    "ip_wifi_oficial": "", "radio_metros": 50, "fecha_inicio_puntos": ahora.date().replace(day=1).strftime("%Y-%m-%d"),
    "desc_tarde": True, "desc_temp": True,
    "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}
}
config_app = load_json("config", config_defecto)

owner_config_defecto = {
    "estado_licencia": "Activo", "plan_pago": "Mensual", "fecha_vencimiento": "2030-12-31",
    "mensaje_bloqueo": "⚠️ SISTEMA SUSPENDIDO TEMPORALMENTE.\\n\\nPor favor, comuníquese con el proveedor del software para regularizar el estado de su cuenta.",
    "mostrar_membresia": False, "dias_aviso": 5,
    "mensaje_aviso": "⚠️ Tu suscripción está próxima a vencer. Por favor, renová tu plan para evitar interrupciones en el servicio.",
    "empresa_nombre": "SyncroRetail Solutions",
    "quienes_somos": "Nacimos con una misión clara: revolucionar la gestión del personal y potenciar el rendimiento de los equipos de trabajo...",
    "contactos": "📍 Oficina Central: Salta Capital, Argentina\\n📩 Soporte y Soluciones: soporte@syncroretail.com\\n💻 Sugerencias y Nuevas Funciones: desarrollo@syncroretail.com"
}
owner_config = load_json("owner_config", owner_config_defecto)

lista_roles_disponibles = load_json("lista_roles", ["Vendedor", "Cajero", "Encargado", "Depósito", "Otro"])
# 🔴 ATENCIÓN: Solo modificá los nombres desde la app, no desde acá.
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

ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A"]

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
    elif puntos < 100: return "🟤 Bronce"
    elif puntos < 130: return "⚪ Plata"
    elif puntos < 160: return "🟡 Oro"
    elif puntos < 200: return "💠 Platino"
    else: return "👑 Leyenda"

# ==========================================
# 4. NAVEGACIÓN FRONTAL PARA CELULARES
# ==========================================
st.markdown('<div class="main-title">🌐 Portal Corporativo</div>', unsafe_allow_html=True)
pestaña = st.selectbox("Navegación:", ["📱 Portal del Empleado", "📊 Panel de Gerencia", "🛠️ Dueño del Software"], label_visibility="collapsed")
st.write("---")

empleado_en_celu = None
if 'device_id' in st.session_state:
    for emp, dev in dispositivos_vinculados.items():
        if dev == st.session_state['device_id']:
            empleado_en_celu = emp
            break

# ==========================================
# 🚨 SISTEMA ANTIFRAUDE (KILL SWITCH Y VENCIMIENTO)
# ==========================================
licencia_vencida = False
try:
    if ahora.date() > datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date():
        licencia_vencida = True
except: pass

if pestaña in ["📱 Portal del Empleado", "📊 Panel de Gerencia"]:
    if owner_config.get("estado_licencia") == "Suspendido" or licencia_vencida:
        msg_motivo = owner_config.get("mensaje_bloqueo") if owner_config.get("estado_licencia") == "Suspendido" else "⚠️ EL PERÍODO DE LICENCIA HA VENCIDO.\\n\\nPor favor, contacte a soporte para renovar su suscripción."
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
    if 'device_id' not in st.session_state:
        js_get_device = "(function() { let id = localStorage.getItem('tienda_app_device_id'); if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); } return id; })();"
        did = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")
        if did:
            st.session_state['device_id'] = did
            st.rerun()
            
    device_id = st.session_state.get('device_id')
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\\n\\n{config_app['mensaje_dia']}")
        
    if not device_id:
        st.info("⏳ Autenticando tu equipo...")
    else:
        if empleado_en_celu:
            if 'fichaje_exitoso' in st.session_state:
                if "⚠️" in st.session_state['fichaje_exitoso'] or "❌" in st.session_state['fichaje_exitoso']:
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
                                        st.warning("⚠️ Elegí un compañero de la lista.")
                                    elif not s_motivo_salida.strip():
                                        st.warning("⚠️ Escribí el motivo en la nota (Obligatorio para la auditoría).")
                                    else:
                                        ya_pedido = False
                                        ya_salio = not df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Salida")].empty
                                        for sp in salidas_pendientes:
                                            if sp.get("Empleado") == s_emp_salida and sp.get("Fecha") == str(fecha_hoy):
                                                ya_pedido = True
                                                break
                                        if ya_salio:
                                            st.error(f"⚠️ El empleado {s_emp_salida} ya tiene una salida registrada en este turno.")
                                        elif ya_pedido:
                                            st.error(f"⚠️ Ya enviaste una solicitud de salida para {s_emp_salida} hoy.")
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
                                            st.success(f"✅ Solicitud de salida de {s_emp_salida} enviada a Gerencia.")
                                            st.rerun()
                        else:
                            st.info("ℹ️ No hay otros compañeros trabajando en esta sucursal en este momento.")
                    else:
                        st.warning("⚠️ Para auditar la salida de un compañero, primero tenés que registrar tu propia ENTRADA.")
                        
                    st.markdown("---")
                    st.markdown("#### ⭐ Asignar Bono o Multa")
                    with st.form("form_sup_puntos"):
                        s_emp = st.selectbox("Compañero:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu])
                        s_pts = st.number_input("Puntos (+/-):", value=0, step=1)
                        s_mot = st.text_input("Motivo:")
                        if st.form_submit_button("Enviar a Gerencia"):
                            if s_emp == "Seleccionar..." or s_pts == 0 or not s_mot.strip():
                                st.warning("⚠️ ¡Completá todos los campos!")
                            else:
                                lista_puntos.append({"Fecha": fecha_hoy, "Empleado": s_emp, "Puntos": s_pts, "Motivo": s_mot.strip(), "Autor": empleado_en_celu, "Estado": "Pendiente"})
                                save_json("ajustes_puntos", lista_puntos)
                                st.success("✅ Evaluación enviada a Gerencia correctamente.")
                                
            mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu, rol_empleado]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='msg-global alert-box' style='border-color: #3B82F6; background-color: #EFF6FF;'>📢 <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    elif m['destinatario'] == rol_empleado: st.markdown(f"<div class='msg-rol'>👥 <b>Para el equipo de {rol_empleado}s:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='msg-individual report-box'>✉ <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    
            with st.expander("📍 Smart Check-In", expanded=True):
                if estado_laboral == "Adentro":
                    st.info("🕒 Ya tenés una entrada abierta.")
                if estado_laboral == "Fuera":
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
                                    metodo_det = f"🛰️ GPS Satelital ({dist:.1f} metros)"
                                    break
                                    
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
                                    h_ing = pd.to_datetime(lista_turnos[t_name]["ingreso"]).time()
                                    dt_ing = datetime.datetime.combine(ahora.date(), h_ing).replace(tzinfo=zona_arg)
                                    diff = abs((ahora - dt_ing).total_seconds())
                                    if diff < min_diff:
                                        min_diff = diff
                                        idx_defecto = idx
                                except: pass
                                
                        st.markdown(f"<div class='task-box'>✅ <b>Sucursal Detectada:</b> {local_detectado}<br><small>Verificado por: {metodo_det}</small></div>", unsafe_allow_html=True)
                        
                        if nombres_turnos:
                            st.markdown("🕒 **Verificá y confirmá tu turno:**")
                            if turno_planificado != "Libre" and turno_planificado in nombres_turnos:
                                st.markdown(f"*(Turno planificado por Gerencia: **{turno_planificado}**)*")
                            turno_seleccionado = st.selectbox("Turno a fichar:", nombres_turnos, index=idx_defecto, label_visibility="collapsed")
                            st.markdown(f"<small style='color: gray;'>El horario oficial de este turno es de {lista_turnos[turno_seleccionado]['ingreso']} a {lista_turnos[turno_seleccionado]['salida']}</small>", unsafe_allow_html=True)
                            nota_empleado = st.text_input("✍ Novedades (Opcional):", placeholder="¿Llegaste tarde por el colectivo? Dejá tu nota acá...")
                            
                            if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                hora_t_str = lista_turnos[turno_seleccionado]["ingreso"]
                                hora_t_obj = pd.to_datetime(hora_t_str).time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                                
                                insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_detectado), "Turno": str(turno_seleccionado), "Tipo": "Entrada", "Estado": str(estado_llegada), "Distancia_m": round(float(distancia_real), 1), "Nota": str(nota_empleado)})
                                
                                msg_final = f"¡Entrada registrada a las {hora_hoy}!"
                                if estado_llegada == "Tarde": msg_final += f"\\n\\n⚠️ {config_app.get('mensaje_llegada_tarde')}"
                                for a in alertas_ingreso:
                                    if a['destinatario'] in ['Todos', empleado_en_celu, rol_empleado]:
                                        msg_final += f"\\n\\n📢 {a['texto']}"
                                st.session_state['fichaje_exitoso'] = msg_final
                                st.rerun()
                        else:
                            st.warning("No hay turnos configurados en el sistema. Avisale a Gerencia.")
                    else:
                        if config_app.get("verificar_gps", True) and (not ubicacion or 'coords' not in ubicacion):
                            st.info("⏳ Detectando ubicación satelital... Por favor, permití el acceso al GPS en tu celular.")
                        else:
                            st.error(f"❌ Estás fuera del rango de todas las sucursales. Acercate al local para habilitar el fichaje.")
                else:
                    st.markdown("### 🏃‍♂️ Finalizar Turno")
                    local_actual = datos_turno_activo.get("Sucursal", "N/A")
                    turno_actual = datos_turno_activo.get("Turno", "N/A")
                    st.success(f"🏢 Actualmente trabajando en **{local_actual}** (Horario: {turno_actual}).")
                    
                    if not config_app.get("exigir_salida_manual", False):
                        st.info("🤖 **Salida Automática Activada:** No necesitás registrar tu salida.")
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
                            nota_empleado = st.text_input("✍ Novedad al salir (Opcional):")
                            if st.button("🔴 REGISTRAR SALIDA", use_container_width=True):
                                insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_actual), "Turno": str(turno_actual), "Tipo": "Salida", "Estado": "Salida", "Distancia_m": round(float(distancia_salida), 1), "Nota": str(nota_empleado)})
                                st.session_state['fichaje_exitoso'] = f"¡Salida registrada a las {hora_hoy}! Buen descanso."
                                st.rerun()
                        else:
                            st.error("⚠️ El sistema exige que finalices tu turno físicamente dentro de la sucursal.")
                            
            with st.expander("📬 Buzón de Reportes Confidenciales", expanded=False):
                tipo_rep = st.selectbox("Tipo:", ["Falla de equipo/sistema", "Incumplimiento de un compañero", "Queja general", "Otra observación"])
                implicado = st.selectbox("Compañero implicado:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu]) if tipo_rep == "Incumplimiento de un compañero" else "N/A"
                detalle_rep = st.text_area("Detalle:")
                if st.button("📤 Enviar a Gerencia"):
                    if not detalle_rep.strip(): st.warning("⚠️ Error: Tenés que escribir el detalle del reporte.")
                    elif tipo_rep == "Incumplimiento de un compañero" and implicado == "Seleccionar...": st.warning("⚠️ Error: Tenés que seleccionar al compañero implicado.")
                    else:
                        reportes_log.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Emisor": empleado_en_celu, "Tipo": tipo_rep, "Implicado": implicado, "Detalle": detalle_rep.strip(), "Estado": "Pendiente de lectura"})
                        save_json("reportes", reportes_log)
                        st.success("✅ ¡Reporte enviado confidencialmente a Gerencia!")
                        
            tareas_totales = tareas_roles.get(rol_empleado, []) + tareas_individuales.get(empleado_en_celu, [])
            if tareas_totales:
                with st.expander("📋 Mis Tareas del Día", expanded=True):
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
                            c_t1.write(f"🔹 {t_nombre} (+{t_puntos} pts)")
                            if c_t2.button("✔️ Listo", key=f"btn_t_{t_nombre}"):
                                insert_row("tareas_log", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Tarea": str(t_nombre), "Puntos": str(t_puntos), "Estado": "Pendiente"})
                                st.rerun()
                                
            with st.expander("⏱️ Mi historial reciente"):
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
                    if n_emp not in lista_empleados:
                        lista_empleados.append(n_emp)
                        roles_empleados[n_emp] = rol_elegido_auto
                        tareas_individuales[n_emp] = []
                        save_json("empleados", lista_empleados)
                        save_json("roles", roles_empleados)
                        save_json("tareas_individuales", tareas_individuales)
                    else:
                        roles_empleados[n_emp] = rol_elegido_auto
                        save_json("roles", roles_empleados)
                    dispositivos_vinculados[n_emp] = device_id
                    save_json("dispositivos", dispositivos_vinculados)
                    st.rerun()
            else:
                st.info("🔐 **Auto-registro deshabilitado.** Pedile a gerencia que te dé de alta en la lista o seleccioná tu nombre si ya existís.")
                emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()])
                if st.button("🔗 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
                    dispositivos_vinculados[emp_vincular] = device_id
                    save_json("dispositivos", dispositivos_vinculados)
                    st.rerun()

# ==========================================
# 6. PANEL DE GERENCIA (BUSINESS INTELLIGENCE)
# ==========================================
# (La sección Gerencial y de Dueño se mantienen igual, solo tené en cuenta los espacios al copiar)
# ... [Para ahorrar memoria visual no repetiré todo el bloque de gerencia que no tenía errores lógicos, pero la protección de datos ya está instalada globalmente en la función de arriba] ...
