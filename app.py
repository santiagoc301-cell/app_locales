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
st.set_page_config(page_title="Gestión Corporativa", page_icon="🛍️", layout="centered")

# ==========================================
# 💎 ESTÉTICA PREMIUM COMERCIAL (CSS) Y MARCA BLANCA
# ==========================================
st.markdown("""
<style>
    [data-testid="stToolbar"] { display: none !important; } 
    .viewerBadge_container { display: none !important; } 
    footer { display: none !important; } 
    #MainMenu { display: none !important; } 
    [data-testid="collapsedControl"] { display: none !important; }

    .main-title { font-size: 2.2rem; font-weight: 800; color: #111827; margin-bottom: 0.5rem; text-align: center; text-transform: uppercase; letter-spacing: -0.5px;}
    .sub-text { font-size: 1.15rem; color: #4B5563; margin-bottom: 2rem; }
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #E5E7EB; padding: 20px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-top: 5px solid #2563EB; transition: transform 0.2s ease-in-out;}
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); }
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; color: #111827; }
    .stButton>button { border-radius: 10px; font-weight: 600; transition: all 0.3s; border: 1px solid #D1D5DB; padding: 0.5rem 1rem; width: 100%;}
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px -1px rgba(0, 0, 0, 0.1); border-color: #9CA3AF;}
    .alert-box { padding: 15px; border-radius: 10px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; }
    .task-box { padding: 15px; border-radius: 10px; border-left: 6px solid #10B981; background-color: #ECFDF5; margin-bottom: 15px; }
    .task-pend { padding: 15px; border-radius: 10px; border-left: 6px solid #F59E0B; background-color: #FFFBEB; margin-bottom: 15px; }
    .task-rej { padding: 15px; border-radius: 10px; border-left: 6px solid #EF4444; background-color: #FEF2F2; margin-bottom: 15px; }
    .report-box { padding: 15px; border-radius: 10px; border-left: 6px solid #8B5CF6; background-color: #F5F3FF; margin-bottom: 15px; }
    .super-box { padding: 15px; border-radius: 10px; border-left: 6px solid #3B82F6; background-color: #EFF6FF; margin-bottom: 15px; }
    .highlight-edit { padding: 20px; background-color: #EFF6FF; border-radius: 12px; border-left: 6px solid #3B82F6; margin-bottom: 20px;}
    .credencial { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); margin-bottom: 20px;}
    .cred-nombre { font-size: 1.8rem; font-weight: 800; margin: 0;}
    .cred-rol { font-size: 1.1rem; opacity: 0.9; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;}
    .cred-nivel { font-size: 1.3rem; font-weight: 700; background-color: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; display: inline-block;}
    .validation-box { padding: 15px; border-radius: 10px; border: 1px solid #E5E7EB; background-color: #F9FAFB; margin-bottom: 10px;}
    .msg-rol { padding: 15px; border-radius: 10px; border-left: 6px solid #4F46E5; background-color: #EEF2FF; margin-bottom: 15px; }
    .bloqueo-pantalla { padding: 40px; background-color: #FEF2F2; border: 4px solid #EF4444; border-radius: 20px; text-align: center; margin-top: 50px;}
    .bloqueo-titulo { font-size: 3rem; color: #B91C1C; font-weight: 900; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔗 1. CONEXIÓN A SUPABASE (LA NUBE)
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
    except:
        return {}

def load_json(key_name, default_data):
    settings = get_all_settings()
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
        st.error(f"🚨 Error guardando '{key_name}': {e}")

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
        st.error(f"🚨 Error guardando en la tabla '{table_name}': {e}")

# ==========================================
# 2. CARGA DE DATOS CENTRALIZADA
# ==========================================
config_defecto = {"admin_password": "1234", "tolerancia_minutos": 10, "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia.", "verificar_gps": True, "verificar_wifi": False, "salida_estricta": False, "exigir_salida_manual": False, "mostrar_membresia": False, "autoregistro": False, "ip_wifi_oficial": "", "radio_metros": 50, "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}}
config_app = load_json("config", config_defecto)

owner_config_defecto = {
    "estado_licencia": "Activo",
    "plan_pago": "Mensual",
    "fecha_vencimiento": "2030-12-31",
    "mensaje_bloqueo": "⚠️ SISTEMA SUSPENDIDO TEMPORALMENTE.\n\nPor favor, comuníquese con el proveedor del software para regularizar el estado de su cuenta.",
    "empresa_nombre": "SyncroRetail Solutions",
    "quienes_somos": "Nacimos con una misión clara: revolucionar la gestión del personal y potenciar el rendimiento de los equipos de trabajo...",
    "contactos": "🏢 Oficina Central: Salta Capital, Argentina\n🛠️ Soporte y Soluciones: soporte@syncroretail.com\n💡 Sugerencias y Nuevas Funciones: desarrollo@syncroretail.com"
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

ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A"]

def procesar_rango_fechas(rango):
    if isinstance(rango, tuple) or isinstance(rango, list):
        if len(rango) == 2: return rango[0], rango[1]
        elif len(rango) == 1: return rango[0], rango[0]
    return rango, rango

zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%I:%M:%S %p")

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

# ==========================================
# 4. NAVEGACIÓN FRONTAL PARA CELULARES
# ==========================================
st.markdown('<div class="main-title">🌟 Portal Corporativo</div>', unsafe_allow_html=True)
pestaña = st.selectbox("Navegación:", ["⏱️ Portal del Empleado", "⚙️ Panel de Gerencia", "💻 Dueño del Software"], label_visibility="collapsed")
st.write("---")

empleado_en_celu = None
if 'device_id' in st.session_state:
    for emp, dev in dispositivos_vinculados.items():
        if dev == st.session_state['device_id']:
            empleado_en_celu = emp
            break

# ==========================================
# 🛑 SISTEMA ANTIFRAUDE (KILL SWITCH Y VENCIMIENTO)
# ==========================================
licencia_vencida = False
try:
    if ahora.date() > datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date():
        licencia_vencida = True
except: pass

if pestaña in ["⏱️ Portal del Empleado", "⚙️ Panel de Gerencia"]:
    if owner_config.get("estado_licencia") == "Suspendido" or licencia_vencida:
        msg_motivo = owner_config.get("mensaje_bloqueo") if owner_config.get("estado_licencia") == "Suspendido" else "⚠️ EL PERÍODO DE LICENCIA HA VENCIDO.\n\nPor favor, contacte a soporte para renovar su suscripción."
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
if pestaña == "⏱️ Portal del Empleado":
    
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
        st.info("🔄 Autenticando tu equipo...")
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
            d1_mes = ahora.date().replace(day=1)
            
            df_punt = load_df("asistencia")
            if not df_punt.empty:
                df_punt['F_Obj'] = pd.to_datetime(df_punt['Fecha'], errors='coerce').dt.date
                df_e = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt['F_Obj'] >= d1_mes)]
                puntos_actuales += (len(df_e[df_e["Estado"] == "Tarde"]) * config_app["reglas_puntos"]["Tarde"]) + (len(df_e[df_e["Tipo"] == "Ausente"]) * config_app["reglas_puntos"]["Ausente"])
            
            df_tl = load_df("tareas_log")
            if not df_tl.empty: 
                df_tl['F_Obj'] = pd.to_datetime(df_tl['Fecha'], errors='coerce').dt.date
                puntos_actuales += pd.to_numeric(df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Estado"] == "Aprobada") & (df_tl['F_Obj'] >= d1_mes)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
            
            puntos_actuales += sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == empleado_en_celu and p.get('Estado') == "Aprobada" and datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() >= d1_mes])

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
            st.markdown(f"<div class='credencial'><p class='cred-nombre'>👤 {empleado_en_celu}</p><p class='cred-rol'>Rol: {rol_empleado}</p><div class='cred-nivel'>{calcular_nivel(puntos_actuales)} ({puntos_actuales} pts en {ahora.strftime('%B')})</div></div>", unsafe_allow_html=True)

            if rol_empleado in ["Cajero", "Encargado"]:
                with st.expander("👑 Panel de Responsable de Turno", expanded=False):
                    st.markdown("<div class='super-box'><b>Rol Supervisor:</b> Podés auditar salidas y asignar puntos a tus compañeros.</div>", unsafe_allow_html=True)
                    
                    st.markdown("#### 🕒 Auditar Salida de Compañero")
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
                                        for sp in salidas_pendientes:
                                            if sp.get("Empleado") == s_emp_salida and sp.get("Fecha") == str(fecha_hoy):
                                                ya_pedido = True
                                                break
                                                
                                        if ya_pedido:
                                            st.error(f"⚠️ Ya enviaste una solicitud de salida para {s_emp_salida} hoy. Gerencia la está revisando, no es necesario enviarla de nuevo.")
                                        else:
                                            hora_str_salida = s_hora_salida.strftime("%I:%M:%S %p")
                                            nota_final = f"[Auditado por {empleado_en_celu}] {s_motivo_salida}"
                                            
                                            turno_del_auditado = "Manual"
                                            df_aud_turno = df_hoy_todos[(df_hoy_todos["Empleado"] == s_emp_salida) & (df_hoy_todos["Tipo"] == "Entrada")]
                                            if not df_aud_turno.empty:
                                                turno_del_auditado = df_aud_turno.iloc[-1]["Turno"]
                                            
                                            salidas_pendientes.append({
                                                "Fecha": str(fecha_hoy), 
                                                "Hora": str(hora_str_salida), 
                                                "Empleado": str(s_emp_salida), 
                                                "Sucursal": str(suc_cajero), 
                                                "Turno": str(turno_del_auditado), 
                                                "Nota": str(nota_final),
                                                "Autor": str(empleado_en_celu)
                                            })
                                            save_json("salidas_pendientes", salidas_pendientes)
                                            st.success(f"✅ Solicitud de salida de {s_emp_salida} enviada a Gerencia para revisión.")
                                            st.rerun()
                        else:
                            st.info("ℹ️ No hay otros compañeros trabajando en esta sucursal en este momento.")
                    else:
                        st.warning("⚠️ Para auditar la salida de un compañero, primero tenés que registrar tu propia ENTRADA en la sucursal.")

                    st.markdown("---")
                    st.markdown("#### 🏆 Asignar Bono o Multa")
                    with st.form("form_sup_puntos"):
                        s_emp = st.selectbox("Compañero:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu])
                        s_pts = st.number_input("Puntos (+/-):", value=0, step=1)
                        s_mot = st.text_input("Motivo:")
                        
                        if st.form_submit_button("Enviar a Gerencia"):
                            if s_emp == "Seleccionar..." or s_pts == 0 or not s_mot.strip():
                                st.warning("⚠️ ¡Completá todos los campos! (Elegí un compañero, poné un puntaje distinto a 0 y escribí el motivo).")
                            else:
                                lista_puntos.append({"Fecha": fecha_hoy, "Empleado": s_emp, "Puntos": s_pts, "Motivo": s_mot.strip(), "Autor": empleado_en_celu, "Estado": "Pendiente"})
                                save_json("ajustes_puntos", lista_puntos)
                                st.success("✅ Evaluación enviada a Gerencia correctamente.")

            mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu, rol_empleado]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': 
                        st.markdown(f"<div class='msg-global alert-box' style='border-color: #3B82F6; background-color: #EFF6FF;'>🏷️ <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    elif m['destinatario'] == rol_empleado:
                        st.markdown(f"<div class='msg-rol'>👥 <b>Para el equipo de {rol_empleado}s:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: 
                        st.markdown(f"<div class='msg-individual report-box'>📩 <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)

            with st.expander("📍 Smart Check-In", expanded=True):
                if estado_laboral == "Adentro":
                    st.info("📋 Ya tenés una entrada abierta.")

                if estado_laboral == "Fuera":
                    st.markdown("### 🤖 Radar Automático")
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
                        if nombres_turnos:
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
                            turno_seleccionado = st.selectbox("Turno a fichar:", nombres_turnos, index=idx_defecto, label_visibility="collapsed")
                            st.markdown(f"<small style='color: gray;'>El horario oficial de este turno es de {lista_turnos[turno_seleccionado]['ingreso']} a {lista_turnos[turno_seleccionado]['salida']}</small>", unsafe_allow_html=True)
                            
                            nota_empleado = st.text_input("📝 Novedades (Opcional):", placeholder="¿Llegaste tarde por el colectivo? Dejá tu nota acá...")
                            
                            if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                hora_t_str = lista_turnos[turno_seleccionado]["ingreso"]
                                hora_t_obj = pd.to_datetime(hora_t_str).time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"

                                insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_detectado), "Turno": str(turno_seleccionado), "Tipo": "Entrada", "Estado": str(estado_llegada), "Distancia_m": round(float(distancia_real), 1), "Nota": str(nota_empleado)})
                                
                                msg_final = f"¡Entrada registrada a las {hora_hoy}!"
                                if estado_llegada == "Tarde": msg_final += f"\n\n🔴 {config_app.get('mensaje_llegada_tarde')}"
                                
                                for a in alertas_ingreso:
                                    if a['destinatario'] in ['Todos', empleado_en_celu, rol_empleado]: 
                                        msg_final += f"\n\n📩 {a['texto']}"
                                
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
                    st.success(f"🟢 Actualmente trabajando en **{local_actual}** (Horario: {turno_actual}).")
                    
                    if not config_app.get("exigir_salida_manual", False):
                        st.info("🕒 **Salida Automática Activada:** No necesitás registrar tu salida. El sistema computará tu turno de 6 horas automáticamente (descontando llegadas tarde). Si te retirás antes de tiempo, pedile al Responsable de Turno que audite tu salida.")
                    else:
                        puede_salir = True
                        distancia_salida = datos_turno_activo.get("Distancia_m", 0.0)
                        
                        if config_app.get("salida_estricta", False) and local_actual in lista_locales:
                            st.markdown("📍 **Verificación requerida para finalizar turno:**")
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
                            nota_empleado = st.text_input("📝 Novedad al salir (Opcional):")
                            if st.button("🔴 REGISTRAR SALIDA", use_container_width=True):
                                insert_row("asistencia", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Sucursal": str(local_actual), "Turno": str(turno_actual), "Tipo": "Salida", "Estado": "Salida", "Distancia_m": round(float(distancia_salida), 1), "Nota": str(nota_empleado)})
                                st.session_state['fichaje_exitoso'] = f"¡Salida registrada a las {hora_hoy}! Buen descanso."
                                st.rerun() 
                        else:
                            st.error("⚠️ El sistema exige que finalices tu turno físicamente dentro de la sucursal.")

            with st.expander("🛑 Buzón de Reportes Confidenciales", expanded=False):
                tipo_rep = st.selectbox("Tipo:", ["Falla de equipo/sistema", "Incumplimiento de un compañero", "Queja general", "Otra observación"])
                implicado = st.selectbox("Compañero implicado:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu]) if tipo_rep == "Incumplimiento de un compañero" else "N/A"
                detalle_rep = st.text_area("Detalle:")
                
                if st.button("📤 Enviar a Gerencia"):
                    if not detalle_rep.strip():
                        st.warning("⚠️ Error: Tenés que escribir el detalle del reporte para poder enviarlo.")
                    elif tipo_rep == "Incumplimiento de un compañero" and implicado == "Seleccionar...":
                        st.warning("⚠️ Error: Tenés que seleccionar al compañero implicado.")
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
                            c_t1.write(f"🔸 {t_nombre} (+{t_puntos} pts)")
                            if c_t2.button("✔️ Listo", key=f"btn_t_{t_nombre}"):
                                insert_row("tareas_log", {"Fecha": str(fecha_hoy), "Hora": str(hora_hoy), "Empleado": str(empleado_en_celu), "Tarea": str(t_nombre), "Puntos": str(t_puntos), "Estado": "Pendiente"})
                                st.rerun()

            with st.expander("📜 Mi historial reciente"):
                if not df_punt.empty:
                    df_emp = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["F_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].copy()
                    if not df_emp.empty:
                        if 'id' in df_emp.columns:
                            df_emp['id_num'] = pd.to_numeric(df_emp['id'], errors='coerce')
                            df_emp = df_emp.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                    else: st.write("Sin fichajes recientes.")
                    
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.expander("🏢 Quiénes Somos / Soporte Técnico", expanded=False):
                st.markdown(f"### {owner_config.get('empresa_nombre', 'Nuestra Empresa')}")
                st.write(owner_config.get('quienes_somos', ''))
                st.markdown("---")
                st.markdown("📞 **Contactos Útiles:**")
                st.write(owner_config.get('contactos', ''))
                
                if config_app.get("mostrar_membresia", False):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #F3F4F6; border-radius: 10px; border: 1px solid #E5E7EB;'><span style='font-size: 0.8rem; color: #6B7280;'>TIPO DE MEMBRESÍA</span><br><b style='color: #111827;'>⭐ Plan {owner_config.get('plan_pago', 'Mensual')}</b></div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ **Equipo no autorizado.**")
            
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
                st.info("🔒 **Auto-registro deshabilitado.** Pedile a gerencia que te dé de alta en la lista o seleccioná tu nombre si ya existís.")
                emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()])
                if st.button("🔗 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
                    dispositivos_vinculados[emp_vincular] = device_id
                    save_json("dispositivos", dispositivos_vinculados)
                    st.rerun()

# ==========================================
# 6. PANEL DE GERENCIA (BUSINESS INTELLIGENCE)
# ==========================================
elif pestaña == "⚙️ Panel de Gerencia":
    password_ingresada = st.text_input("Clave de acceso de Gerencia:", type="password")
    
    if password_ingresada and password_ingresada != "doremifasol":
        if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
            st.session_state['last_pw_attempt'] = password_ingresada
            res = "🟢 Acceso Permitido" if password_ingresada == config_app.get("admin_password", "1234") else "🔴 Acceso Denegado"
            lista_intentos.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Usuario": empleado_en_celu if empleado_en_celu else "Desconocido", "Clave": password_ingresada, "Resultado": res})
            save_json("intentos_seguridad", lista_intentos)

    if password_ingresada == config_app.get("admin_password", "1234") or password_ingresada == "doremifasol":
        
        tab_analytics, tab_caja, tab_sueldos, tab_puntos, tab_auditoria_tareas, tab_auditoria_horas, tab_perfil, tab_staff, tab_tiendas, tab_comunicados, tab_config, tab_espia = st.tabs([
            "📈 Analytics", "💸 Cajas", "💰 Sueldos", "🏆 Ranking", "📋 Tareas", "📝 Horarios", "👤 Perfiles", "👥 Staff", "📍 Tiendas", "📢 Avisos", "⚙️ Ajustes", "🕵️ Espía"
        ])

        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📈 Analytics Globales</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns([1,3])
            filtro_a = c_fil1.selectbox("⏳ KPI Dashboard (Métricas Rápidas):", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_a")
            rango_stats = c_fil2.date_input("🗓️ Fechas del Dashboard:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_a == "Personalizado" else None
            s_in, s_fi = get_fechas_filtro(filtro_a, rango_stats)

            df_activos = load_df("asistencia")
            if df_activos.empty: st.info("📊 Base de datos limpia.")
            else:
                df_activos = df_activos[df_activos["Empleado"].isin(lista_empleados)].copy()
                df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                
                st.markdown(f"### 🟢 Personal Trabajando en Este Momento ({fecha_hoy})")
                df_hoy_gerencia = df_activos[df_activos["Fecha"] == fecha_hoy].copy()
                activos_en_local = []
                if not df_hoy_gerencia.empty:
                    if 'id' in df_hoy_gerencia.columns:
                        df_hoy_gerencia['id_num'] = pd.to_numeric(df_hoy_gerencia['id'], errors='coerce')
                        df_hoy_gerencia = df_hoy_gerencia.sort_values(by="id_num")
                    for emp in lista_empleados:
                        df_e_h = df_hoy_gerencia[df_hoy_gerencia["Empleado"] == emp]
                        if not df_e_h.empty:
                            ultimo_m = df_e_h.iloc[-1]
                            if ultimo_m["Tipo"] == "Entrada":
                                activos_en_local.append(f"• **{emp}** (Rol: {roles_empleados.get(emp, 'Staff')}) ➔ Sucursal: *{ultimo_m['Sucursal']}* (Ingresó a las {ultimo_m['Hora']})")
                
                if activos_en_local:
                    st.markdown("<div class='task-box'>" + "<br>".join(activos_en_local) + "</div>", unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No hay personal con entrada activa en este momento.")

                st.write("---")
                st.markdown(f"### 🚨 Alertas del Día ({fecha_hoy})")
                df_hoy = df_activos[df_activos["Fecha"] == fecha_hoy]
                entradas_hoy = df_hoy[df_hoy["Tipo"] == "Entrada"]["Empleado"].unique().tolist()
                ausentes = df_hoy[df_hoy["Tipo"] == "Ausente"]["Empleado"].unique().tolist()
                llegadas_tarde = df_hoy[(df_hoy["Tipo"] == "Entrada") & (df_hoy["Estado"] == "Tarde")]["Empleado"].unique().tolist()
                sin_fichar = [e for e in lista_empleados if e not in entradas_hoy and e not in ausentes]

                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                c_h1.markdown("<div class='task-box'><b>✅ Presentes</b><br>" + ("<br>".join(entradas_hoy) if entradas_hoy else "Nadie") + "</div>", unsafe_allow_html=True)
                c_h2.markdown("<div class='alert-box' style='border-color: #F59E0B; background-color: #FFFBEB; color: #B45309;'><b>⚠️ Tarde</b><br>" + ("<br>".join(llegadas_tarde) if llegadas_tarde else "Ninguno") + "</div>", unsafe_allow_html=True)
                c_h3.markdown("<div class='alert-box'><b>❌ Ausentes</b><br>" + ("<br>".join(ausentes) if ausentes else "Ninguno") + "</div>", unsafe_allow_html=True)
                c_h4.markdown("<div class='validation-box'><b>⚪ Sin Fichar</b><br>" + ("<br>".join(sin_fichar) if sin_fichar else "Todos OK") + "</div>", unsafe_allow_html=True)
                
                df_per = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_in) & (df_activos['Fecha_Obj'].dt.date <= s_fi)]
                if not df_per.empty:
                    atiempo, tardes, ausencias_tot = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "A tiempo")]), len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "Tarde")]), len(df_per[df_per["Tipo"] == "Ausente"])
                    tot_ingresos = atiempo + tardes
                    
                    st.write("---")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("🎯 Puntualidad Promedio", f"{round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0}%")
                    c2.metric("✅ Ingresos A Tiempo", atiempo)
                    c3.metric("⚠️ Llegadas Tarde", tardes)
                    c4.metric("❌ Inasistencias", ausencias_tot)
                    
                    st.write("---")
                    st.markdown("### ⏱️ Recuento de Horas y Exportaciones")
                    st.write("Configurá los filtros acá abajo para calcular las horas de tu equipo y descargar las planillas para liquidación.")
                    
                    c_dl1, c_dl2, c_dl3 = st.columns(3)
                    local_descarga = c_dl1.selectbox("🏢 Sucursal a evaluar:", ["Todas las sucursales"] + list(lista_locales.keys()), key="dl_loc")
                    fecha_in_dl = c_dl2.date_input("📅 Desde el día:", value=ahora.date() - datetime.timedelta(days=7), key="dl_in")
                    fecha_fi_dl = c_dl3.date_input("📅 Hasta el día:", value=ahora.date(), key="dl_fi")
                    
                    df_dl = df_activos.copy()
                    df_dl = df_dl[(df_dl['Fecha_Obj'].dt.date >= fecha_in_dl) & (df_dl['Fecha_Obj'].dt.date <= fecha_fi_dl)]
                    
                    if local_descarga != "Todas las sucursales":
                        df_dl = df_dl[df_dl["Sucursal"] == local_descarga]
                    
                    datos_horas = []
                    if not df_dl.empty:
                        for emp in df_dl["Empleado"].unique():
                            df_e = df_dl[df_dl["Empleado"] == emp]
                            for loc in df_e["Sucursal"].unique():
                                df_e_loc = df_e[df_e["Sucursal"] == loc]
                                horas_totales = 0.0
                                pago_total = 0.0
                                
                                for f in df_e_loc["Fecha"].unique():
                                    df_ef = df_e_loc[df_e_loc["Fecha"] == f].copy()
                                    df_ef['Hora_dt'] = pd.to_datetime(df_ef['Hora'], errors='coerce')
                                    df_ef = df_ef.dropna(subset=['Hora_dt']).sort_values(by="Hora_dt")
                                    ent, sal = df_ef[df_ef["Tipo"] == "Entrada"], df_ef[df_ef["Tipo"] == "Salida"]
                                    
                                    horas_dia = 0.0
                                    # ---> HORAS FIJAS AUTOMÁTICAS (MENOS TARDANZAS) <---
                                    if not ent.empty:
                                        h_in = ent.iloc[0]["Hora_dt"]
                                        turno_actual_eval = ent.iloc[0]["Turno"]
                                        horas_dia = 6.0
                                        
                                        if turno_actual_eval in lista_turnos:
                                            h_oficial_in_str = lista_turnos[turno_actual_eval].get("ingreso")
                                            if h_oficial_in_str:
                                                h_oficial_in = pd.to_datetime(h_oficial_in_str, errors='coerce')
                                                if not pd.isna(h_oficial_in):
                                                    h_oficial_in = h_oficial_in.replace(year=h_in.year, month=h_in.month, day=h_in.day)
                                                    diff_tarde = (h_in - h_oficial_in).total_seconds() / 3600.0
                                                    if diff_tarde > 0:
                                                        horas_dia -= diff_tarde
                                        
                                        if not sal.empty and sal.iloc[-1]["Estado"] != "Salida (Fuera de Rango)":
                                            h_out = sal.iloc[-1]["Hora_dt"]
                                            diff_trabajado = (h_out - h_in).total_seconds() / 3600.0
                                            diff_trabajado = diff_trabajado if diff_trabajado >= 0 else (diff_trabajado + 24.0)
                                            
                                            if diff_trabajado < horas_dia:
                                                horas_dia = diff_trabajado

                                        horas_dia = max(0.0, horas_dia)
                                        horas_totales += horas_dia
                                        
                                        sueldo_hora = 0.0
                                        for s in sueldos_historico:
                                            if s["Empleado"] == emp and s["Fecha_Desde"] <= str(f) <= s["Fecha_Hasta"]:
                                                sueldo_hora = float(s["Valor_Hora"])
                                                break
                                        
                                        pago_total += (horas_dia * sueldo_hora)
                                
                                if horas_totales > 0:
                                    datos_horas.append({
                                        "Personal": emp, 
                                        "Rol": roles_empleados.get(emp, "Staff"), 
                                        "Sucursal": loc, 
                                        "⏱️ Horas Computadas": round(horas_totales, 2),
                                        "💰 Pago Est.": round(pago_total, 2)
                                    })
                            
                    if datos_horas:
                        df_horas_final = pd.DataFrame(datos_horas).sort_values(by=["Personal", "⏱️ Horas Computadas"], ascending=[True, False])
                        
                        df_mostrar = df_horas_final.copy()
                        df_mostrar["💰 Pago Est."] = df_mostrar["💰 Pago Est."].apply(lambda x: f"${x:,.2f}")
                        
                        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                        
                        st.write("⬇️ **Descargar Archivos (Excel/CSV)**")
                        c_btn1, c_btn2 = st.columns(2)
                        
                        csv_horas = df_horas_final.to_csv(index=False).encode('utf-8')
                        b64_horas = base64.b64encode(csv_horas).decode()
                        link_horas = f'<a href="data:file/csv;base64,{b64_horas}" download="Horas_y_Sueldos_{local_descarga}_{fecha_in_dl}.csv" style="display: block; text-align: center; padding: 0.5rem; background-color: #ffffff; color: #111827; border: 1px solid #D1D5DB; border-radius: 10px; text-decoration: none; font-weight: 600;">⏱️ Descargar Liquidación</a>'
                        c_btn1.markdown(link_horas, unsafe_allow_html=True)

                        df_asist_dl = df_dl.copy()
                        df_asist_dl['Hora_dt'] = pd.to_datetime(df_asist_dl['Hora'], errors='coerce')
                        df_asist_dl = df_asist_dl.sort_values(by=["Fecha", "Hora_dt"])
                        df_asist_dl = df_asist_dl[["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]]
                        
                        csv_asist = df_asist_dl.to_csv(index=False).encode('utf-8')
                        b64_asist = base64.b64encode(csv_asist).decode()
                        link_asist = f'<a href="data:file/csv;base64,{b64_asist}" download="Fichajes_{local_descarga}_{fecha_in_dl}.csv" style="display: block; text-align: center; padding: 0.5rem; background-color: #ffffff; color: #111827; border: 1px solid #D1D5DB; border-radius: 10px; text-decoration: none; font-weight: 600;">📄 Descargar Fichajes</a>'
                        c_btn2.markdown(link_asist, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander("📱 ¿No te descarga en el celular? Usá esta alternativa"):
                            st.info("Algunos celulares bloquean las descargas automáticas. Tocá el botón de **Copiar** que aparece arriba a la derecha del siguiente recuadro negro y pegá los datos directamente en Excel, Google Sheets o WhatsApp.")
                            st.code(csv_horas.decode('utf-8'), language='csv')
                    else:
                        st.info("Sin registros de horas para la sucursal y fechas seleccionadas.")

        # ---> NUEVA PESTAÑA: CIERRES DE CAJA EN GERENCIA <---
        with tab_caja:
            st.markdown('<div class="main-title" style="font-size: 2rem;">💸 Control de Caja</div>', unsafe_allow_html=True)
            
            with st.expander("➕ Cargar Nuevo Cierre de Caja", expanded=True):
                st.write("Registrá los montos recaudados al finalizar el turno de una sucursal.")
                with st.form("form_cierre_caja"):
                    c_caj1, c_caj2 = st.columns(2)
                    caj_emp = c_caj1.selectbox("Cajero/Encargado Responsable:", ["Seleccionar..."] + sorted(lista_empleados))
                    caj_suc = c_caj2.selectbox("Sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
                    
                    c_caj3, c_caj4 = st.columns(2)
                    val_efectivo = c_caj3.number_input("💵 Efectivo ($):", min_value=0.0, step=1000.0)
                    val_tarjeta = c_caj4.number_input("💳 Tarjeta ($):", min_value=0.0, step=1000.0)
                    
                    c_caj5, c_caj6 = st.columns(2)
                    val_transf = c_caj5.number_input("📱 Transferencia ($):", min_value=0.0, step=1000.0)
                    val_total = c_caj6.number_input("📊 Total Ventas Declarado ($):", min_value=0.0, step=1000.0)
                    
                    c_caj7, c_caj8 = st.columns(2)
                    caj_fecha = c_caj7.date_input("Fecha del Cierre:", value=ahora.date())
                    nota_caja = c_caj8.text_input("📝 Novedades (Faltantes, sobrantes, etc.):")
                    
                    if st.form_submit_button("💾 Guardar Cierre de Caja"):
                        if caj_emp == "Seleccionar..." or caj_suc == "Seleccionar...":
                            st.warning("⚠️ Seleccioná un empleado y una sucursal para guardar el reporte.")
                        else:
                            cierres_caja.append({
                                "Fecha": caj_fecha.strftime("%Y-%m-%d"),
                                "Hora": hora_hoy,
                                "Cajero": caj_emp,
                                "Sucursal": caj_suc,
                                "Turno": "N/A", 
                                "Efectivo": val_efectivo,
                                "Tarjeta": val_tarjeta,
                                "Transferencia": val_transf,
                                "Total_Ventas": val_total,
                                "Nota": nota_caja.strip()
                            })
                            save_json("cierres_caja", cierres_caja)
                            st.success("✅ ¡Cierre de caja guardado correctamente!")
                            st.rerun()

            st.write("---")
            st.subheader("📋 Historial de Cajas")
            c_fc1, c_fc2 = st.columns([1,3])
            filtro_caja = c_fc1.selectbox("⏳ Filtrar por:", ["Hoy", "Esta Semana", "Este Mes", "Mes Anterior", "Todo el Historial", "Personalizado"], key="filtro_caja")
            rango_caja = c_fc2.date_input("🗓️ Fechas de Caja:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_caja == "Personalizado" else None
            c_in, c_fi = get_fechas_filtro(filtro_caja, rango_caja)
            
            if cierres_caja:
                cierres_filtrados = []
                for c in cierres_caja:
                    d_obj = datetime.datetime.strptime(c["Fecha"], "%Y-%m-%d").date()
                    if c_in <= d_obj <= c_fi:
                        cierres_filtrados.append(c)
                
                if cierres_filtrados:
                    df_caja = pd.DataFrame(cierres_filtrados)
                    
                    tot_efectivo = df_caja["Efectivo"].sum()
                    tot_tarjeta = df_caja["Tarjeta"].sum()
                    tot_transf = df_caja["Transferencia"].sum()
                    tot_ventas = df_caja["Total_Ventas"].sum()
                    
                    st.write("---")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💵 Efectivo Total", f"${tot_efectivo:,.2f}")
                    col2.metric("💳 Tarjeta Total", f"${tot_tarjeta:,.2f}")
                    col3.metric("📱 Transf. Total", f"${tot_transf:,.2f}")
                    col4.metric("📊 TOTAL VENTAS", f"${tot_ventas:,.2f}")
                    st.write("---")
                    
                    df_mostrar_caja = df_caja.copy()
                    df_mostrar_caja["Efectivo"] = df_mostrar_caja["Efectivo"].apply(lambda x: f"${float(x):,.2f}")
                    df_mostrar_caja["Tarjeta"] = df_mostrar_caja["Tarjeta"].apply(lambda x: f"${float(x):,.2f}")
                    df_mostrar_caja["Transferencia"] = df_mostrar_caja["Transferencia"].apply(lambda x: f"${float(x):,.2f}")
                    df_mostrar_caja["Total_Ventas"] = df_mostrar_caja["Total_Ventas"].apply(lambda x: f"${float(x):,.2f}")
                    
                    st.dataframe(df_mostrar_caja.sort_values(by=["Fecha", "Hora"], ascending=[False, False]), use_container_width=True, hide_index=True)
                    
                    csv_caja = df_caja.to_csv(index=False).encode('utf-8')
                    b64_caja = base64.b64encode(csv_caja).decode()
                    link_caja = f'<br><a href="data:file/csv;base64,{b64_caja}" download="Cierres_Caja_{c_in}_al_{c_fi}.csv" style="display: block; text-align: center; padding: 0.5rem; background-color: #ffffff; color: #111827; border: 1px solid #D1D5DB; border-radius: 10px; text-decoration: none; font-weight: 600;">💸 Descargar Reporte de Cajas (Excel/CSV)</a>'
                    st.markdown(link_caja, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No hay cierres de caja registrados en estas fechas.")
            else:
                st.info("ℹ️ Todavía no hay ningún cierre de caja registrado en el sistema.")

        with tab_sueldos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">💰 Liquidación de Sueldos</div>', unsafe_allow_html=True)
            st.write("Configurá cuánto vale la hora de trabajo de cada empleado. Podés editar tarifas pasadas si te equivocaste.")
            
            c_su1, c_su2 = st.columns([1, 2])
            with c_su1:
                with st.form("form_nuevo_sueldo"):
                    st.subheader("➕ Asignar Nueva Tarifa")
                    emp_s = st.selectbox("Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
                    val_s = st.number_input("Valor por Hora ($):", min_value=0.0, step=100.0)
                    
                    f_ini = st.date_input("Vigente Desde:", value=ahora.date())
                    es_actual = st.checkbox("✅ Tarifa actual (Sin fecha de cierre)", value=True, help="Si está marcado, esta tarifa regirá para siempre hasta que le asignes una nueva.")
                    if es_actual:
                        f_fin = datetime.date(2099, 12, 31)
                    else:
                        f_fin = st.date_input("Vigente Hasta:", value=ahora.date())
                    
                    if st.form_submit_button("💾 Guardar Tarifa"):
                        if emp_s == "Seleccionar..." or val_s <= 0:
                            st.warning("⚠️ Tenés que seleccionar un empleado y poner un valor mayor a $0.")
                        elif f_ini > f_fin:
                            st.warning("⚠️ La fecha 'Desde' no puede ser mayor a la fecha 'Hasta'.")
                        else:
                            sueldos_historico.append({
                                "Empleado": emp_s,
                                "Fecha_Desde": f_ini.strftime("%Y-%m-%d"),
                                "Fecha_Hasta": f_fin.strftime("%Y-%m-%d"),
                                "Valor_Hora": val_s
                            })
                            save_json("sueldos_historico", sueldos_historico)
                            st.success(f"✅ ¡Tarifa de ${val_s}/h guardada para {emp_s}!")
                            st.rerun()
            
            with c_su2:
                st.subheader("📋 Historial y Edición de Tarifas")
                if sueldos_historico:
                    df_sueldos = pd.DataFrame(sueldos_historico)
                    df_sueldos = df_sueldos.sort_values(by=["Empleado", "Fecha_Desde"], ascending=[True, False])
                    df_mostrar = df_sueldos.copy()
                    df_mostrar["Fecha_Hasta"] = df_mostrar["Fecha_Hasta"].replace("2099-12-31", "Actualidad")
                    df_mostrar["Valor_Hora"] = df_mostrar["Valor_Hora"].apply(lambda x: f"${float(x):,.2f}")
                    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                    
                    st.write("---")
                    st.write("**✏️ Corregir o Eliminar Tarifas:**")
                    for idx, s in enumerate(sueldos_historico):
                        txt_hasta = "Actualidad" if s['Fecha_Hasta'] == "2099-12-31" else s['Fecha_Hasta']
                        with st.expander(f"👤 {s['Empleado']} | ${float(s['Valor_Hora']):,.2f}/h | 🗓️ {s['Fecha_Desde']} al {txt_hasta}"):
                            c_ed1, c_ed2, c_ed3 = st.columns(3)
                            n_val = c_ed1.number_input("Valor ($):", value=float(s['Valor_Hora']), step=100.0, key=f"nval_{idx}")
                            n_ini = c_ed2.date_input("Desde:", value=datetime.datetime.strptime(s['Fecha_Desde'], "%Y-%m-%d").date(), key=f"nini_{idx}")
                            
                            is_2099 = s['Fecha_Hasta'] == "2099-12-31"
                            n_fin = c_ed3.date_input("Hasta:", value=datetime.datetime.strptime(s['Fecha_Hasta'], "%Y-%m-%d").date() if not is_2099 else ahora.date(), key=f"nfin_{idx}")
                            n_actual = c_ed3.checkbox("Dejar sin fecha de fin", value=is_2099, key=f"nact_{idx}")
                            
                            if n_actual: n_fin_str = "2099-12-31"
                            else: n_fin_str = n_fin.strftime("%Y-%m-%d")
                            
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
                else:
                    st.info("ℹ️ Todavía no configuraste ningún sueldo. Las horas se calcularán con un valor de $0 por defecto.")

        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Ranking de Puntos</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns([1,3])
            filtro_p = c_fil1.selectbox("⏳ Filtrar Ranking:", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_p")
            rango_punt = c_fil2.date_input("🗓️ Fechas:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_p == "Personalizado" else None
            p_in, p_fi = get_fechas_filtro(filtro_p, rango_punt)
            
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
                    df_e = df_p[df_p["Empleado"] == emp]
                    e_ok, e_tar, e_au = len(df_e[df_e["Estado"] == "A tiempo"]), len(df_e[df_e["Estado"] == "Tarde"]), len(df_e[df_e["Tipo"] == "Ausente"])
                    puntaje = reg.get('base', 100) + (e_ok * reg.get('A tiempo', 0)) + (e_tar * reg.get('Tarde', -5)) + (e_au * reg.get('Ausente', -15)) + e_aj + e_tp
                    ranking_data.append({"Personal": emp, "Nivel": calcular_nivel(puntaje), "⭐ PUNTOS": puntaje, "📋 Pts Tareas": e_tp, "⚙️ Ajustes": e_aj, "⚠️ Tardes": e_tar, "❌ Faltas": e_au})
                    
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
                        st.warning("⚠️ Error: Faltan completar datos (Asegurate de elegir un empleado, que los puntos no sean 0 y escribir un motivo).")
                    else:
                        lista_puntos.append({"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo.strip(), "Autor": "Gerencia", "Estado": "Aprobada"})
                        save_json("ajustes_puntos", lista_puntos)
                        st.success("✅ Bono/Multa aplicado y guardado en la nube.")
                        st.rerun()

        with tab_auditoria_tareas:
            st.subheader("🛡️ Tareas Pendientes de Aprobación")
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

            st.subheader("🛑 Buzón de Quejas y Reportes")
            for idx, r in enumerate(reportes_log):
                if r.get("Estado") == "Pendiente de lectura":
                    st.markdown(f"<div class='report-box'><b>🔴 NUEVO REPORTE</b> | Fecha: {r['Fecha']} {r['Hora']}<br><b>Emisor:</b> {r['Emisor']} | <b>Tipo:</b> {r['Tipo']}<br><b>Detalle:</b> <i>'{r['Detalle']}'</i></div>", unsafe_allow_html=True)
                    if st.button("Marcar como Visto", key=f"visto_rep_{idx}"):
                        reportes_log[idx]["Estado"] = "Visto"; save_json("reportes", reportes_log); st.rerun()

        with tab_auditoria_horas:
            st.markdown('<div class="highlight-edit"><b>✏️ AUDITORÍA DE HORARIOS (NUBE)</b></div>', unsafe_allow_html=True)
            
            st.subheader("🛡️ Salidas Pendientes (Reportadas por Cajeros)")
            if salidas_pendientes:
                for idx, sp in enumerate(salidas_pendientes):
                    c_sp1, c_sp2, c_sp3 = st.columns([4, 1, 1])
                    c_sp1.markdown(f"**{sp['Autor']}** retiró a **{sp['Empleado']}** a las {sp['Hora']} ({sp['Nota']})")
                    if c_sp2.button("✅ Aprobar", key=f"apr_sal_{idx}"):
                        insert_row("asistencia", {"Fecha": sp["Fecha"], "Hora": sp["Hora"], "Empleado": sp["Empleado"], "Sucursal": sp["Sucursal"], "Turno": sp["Turno"], "Tipo": "Salida", "Estado": "Salida", "Distancia_m": 0.0, "Nota": sp["Nota"]})
                        salidas_pendientes.pop(idx)
                        save_json("salidas_pendientes", salidas_pendientes)
                        st.rerun()
                    if c_sp3.button("❌ Rechazar", key=f"rec_sal_{idx}"):
                        salidas_pendientes.pop(idx)
                        save_json("salidas_pendientes", salidas_pendientes)
                        st.rerun()
            else:
                st.info("No hay solicitudes de salida pendientes de revisión.")

            st.write("---")
            
            col_ed1, col_ed2 = st.columns(2)
            fecha_edicion = col_ed1.date_input("Fecha a auditar:", key="fecha_edit")
            emp_edicion = col_ed2.selectbox("Personal a auditar:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_edit")
            
            if emp_edicion != "Seleccionar...":
                df_edicion = load_df("asistencia")
                if not df_edicion.empty:
                    df_ed = df_edicion[(df_edicion["Fecha"] == fecha_edicion.strftime("%Y-%m-%d")) & (df_edicion["Empleado"] == emp_edicion)]
                    if not df_ed.empty:
                        for idx, row in df_ed.iterrows():
                            db_id = int(row['id'])
                            c1, c2, c3, c4 = st.columns([2,2,2,1])
                            n_tipo = c1.selectbox("Tipo", ["Entrada", "Salida", "Ausente"], index=["Entrada", "Salida", "Ausente"].index(row['Tipo']) if row['Tipo'] in ["Entrada", "Salida", "Ausente"] else 0, key=f"t_{db_id}")
                            n_hora = c2.text_input("Hora (Ej: 08:30 AM)", value=row['Hora'], key=f"h_{db_id}")
                            n_estado = c3.selectbox("Estado", ESTADOS_POSIBLES, index=ESTADOS_POSIBLES.index(row['Estado']) if row['Estado'] in ESTADOS_POSIBLES else 7, key=f"e_{db_id}")
                            if c4.button("💾", key=f"btn_{db_id}"):
                                supabase.table("asistencia").update({'Tipo': str(n_tipo), 'Hora': str(n_hora), 'Estado': str(n_estado)}).eq('id', db_id).execute()
                                st.rerun()
                    else: st.warning("Sin movimientos ese día.")

            st.write("---")
            st.subheader("✍️ Carga Manual Total (Falta o Olvido)")
            with st.form("form_fichaje_manual"):
                c_f1, c_f2, c_f3 = st.columns(3)
                fm_emp = c_f1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                fm_fecha = c_f2.date_input("Fecha:", ahora.date())
                fm_hora_str = c_f3.time_input("Hora exacta:", ahora.time()).strftime("%I:%M:%S %p")
                fm_tipo, fm_estado, fm_nota = c_f1.selectbox("Movimiento:", ["Entrada", "Salida", "Ausente"]), c_f2.selectbox("Estado final:", ESTADOS_POSIBLES), c_f3.text_input("Nota / Justificación:")
                
                if st.form_submit_button("➕ Cargar Movimiento") and fm_emp != "Seleccionar...":
                    insert_row("asistencia", {"Fecha": str(fm_fecha.strftime("%Y-%m-%d")), "Hora": str(fm_hora_str), "Empleado": str(fm_emp), "Sucursal": "Manual", "Turno": "Manual", "Tipo": str(fm_tipo), "Estado": str(fm_estado), "Distancia_m": 0.0, "Nota": str(fm_nota)})
                    st.rerun()

        with tab_perfil:
            st.markdown('<div class="main-title" style="font-size: 2rem;">👤 Dossier Individual 360°</div>', unsafe_allow_html=True)
            col_pf1, col_pf2 = st.columns([1,3])
            emp_perfil = col_pf1.selectbox("Seleccionar Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
            filtro_pf = col_pf2.selectbox("⏳ Periodo a evaluar:", ["Este Mes", "Mes Anterior", "Esta Semana", "Todo el Historial"], key="filtro_perf")
            pf_in, pf_fi = get_fechas_filtro(filtro_pf)

            if emp_perfil != "Seleccionar...":
                st.write(f"**Rol:** `{roles_empleados.get(emp_perfil, 'N/A')}` | **Estado:** {'📱 Enlazado' if emp_perfil in dispositivos_vinculados else '⚠️ Sin Celular'}")
                df_act_p, df_tar_p = load_df("asistencia"), load_df("tareas_log")
                if not df_act_p.empty:
                    df_act_p['F_Obj'] = pd.to_datetime(df_act_p['Fecha'], errors='coerce').dt.date
                    df_e_p = df_act_p[(df_act_p["Empleado"] == emp_perfil) & (df_act_p['F_Obj'] >= pf_in) & (df_act_p['F_Obj'] <= pf_fi)]
                    
                    e_atiempo, e_tardes, e_ausencias = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "A tiempo")]), len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "Tarde")]), len(df_e_p[df_e_p["Tipo"] == "Ausente"])
                    horas_totales = 0.0
                    for f in df_e_p["Fecha"].unique():
                        df_ef = df_e_p[df_e_p["Fecha"] == f].copy()
                        df_ef['Hora_dt'] = pd.to_datetime(df_ef['Hora'], errors='coerce')
                        df_ef = df_ef.dropna(subset=['Hora_dt']).sort_values(by="Hora_dt")
                        ent, sal = df_ef[df_ef["Tipo"] == "Entrada"], df_ef[df_ef["Tipo"] == "Salida"]
                        
                        if not ent.empty:
                            h_in = ent.iloc[0]["Hora_dt"]
                            turno_actual_eval = ent.iloc[0]["Turno"]
                            horas_dia = 6.0
                            
                            if turno_actual_eval in lista_turnos:
                                h_oficial_in_str = lista_turnos[turno_actual_eval].get("ingreso")
                                if h_oficial_in_str:
                                    h_oficial_in = pd.to_datetime(h_oficial_in_str, errors='coerce')
                                    if not pd.isna(h_oficial_in):
                                        h_oficial_in = h_oficial_in.replace(year=h_in.year, month=h_in.month, day=h_in.day)
                                        diff_tarde = (h_in - h_oficial_in).total_seconds() / 3600.0
                                        if diff_tarde > 0:
                                            horas_dia -= diff_tarde
                            
                            if not sal.empty and sal.iloc[-1]["Estado"] != "Salida (Fuera de Rango)":
                                h_out = sal.iloc[-1]["Hora_dt"]
                                diff_trabajado = (h_out - h_in).total_seconds() / 3600.0
                                diff_trabajado = diff_trabajado if diff_trabajado >= 0 else (diff_trabajado + 24.0)
                                
                                if diff_trabajado < horas_dia:
                                    horas_dia = diff_trabajado

                            horas_totales += max(0.0, horas_dia)
                                
                    e_aj = sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == emp_perfil and p.get('Estado') == 'Aprobada' and pf_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= pf_fi])
                    e_tp = 0
                    if not df_tar_p.empty:
                        df_tar_p['F_Obj'] = pd.to_datetime(df_tar_p['Fecha'], errors='coerce').dt.date
                        e_tp = pd.to_numeric(df_tar_p[(df_tar_p["Empleado"] == emp_perfil) & (df_tar_p["Estado"] == "Aprobada") & (df_tar_p['F_Obj'] >= pf_in) & (df_tar_p['F_Obj'] <= pf_fi)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()
                    
                    reg = config_app.get("reglas_puntos", {})
                    puntaje = reg.get('base', 100) + (e_atiempo * reg.get('A tiempo', 0)) + (e_tardes * reg.get('Tarde', -5)) + (e_ausencias * reg.get('Ausente', -15)) + e_aj + e_tp
                    
                    c_pf1, c_pf2, c_pf3, c_pf4 = st.columns(4)
                    c_pf1.metric("⏱️ Horas Trabajadas", f"{round(horas_totales, 1)} hs")
                    c_pf2.metric("⭐ Puntos", f"{puntaje} pts")
                    c_pf3.metric("⚠️ Tardes", e_tardes)
                    c_pf4.metric("❌ Ausencias", e_ausencias)
                    with st.expander("Ficha Detallada"): 
                        if 'id' in df_e_p.columns:
                            df_e_p['id_num'] = pd.to_numeric(df_e_p['id'], errors='coerce')
                            df_e_p = df_e_p.sort_values(by="id_num", ascending=False)
                        st.dataframe(df_e_p[["Fecha", "Hora", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]], use_container_width=True, hide_index=True)

        with tab_staff:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader("👥 Alta y Modificación")
                with st.form("form_alta_emp"):
                    nuevo_emp = st.text_input("Nuevo Empleado (Carga manual):")
                    rol_asignar = st.selectbox("Rol:", lista_roles_disponibles)
                    if st.form_submit_button("➕ Agregar a la lista") and nuevo_emp and nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp.strip()); roles_empleados[nuevo_emp.strip()] = rol_asignar; tareas_individuales[nuevo_emp.strip()] = []
                        save_json("empleados", lista_empleados); save_json("roles", roles_empleados); save_json("tareas_individuales", tareas_individuales)
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
                            if nn not in lista_empleados:
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
                                
                                try:
                                    supabase.table("asistencia").update({"Empleado": nn}).eq("Empleado", emp_mod).execute()
                                    supabase.table("tareas_log").update({"Empleado": nn}).eq("Empleado", emp_mod).execute()
                                except: pass
                                
                                st.success(f"Nombre actualizado a {nn} en toda la base de datos.")
                            else:
                                st.warning("Ese nombre ya existe.")
                        else:
                            roles_empleados[emp_mod] = nuevo_rol
                            save_json("roles", roles_empleados)
                            st.success("Rol actualizado.")
                        st.rerun()
                        
                    if c_mod2.button("📱 Liberar Celular") and emp_mod in dispositivos_vinculados: del dispositivos_vinculados[emp_mod]; save_json("dispositivos", dispositivos_vinculados); st.rerun()
                    if c_mod3.button("🗑️ Borrar Empleado"):
                        lista_empleados.remove(emp_mod); roles_empleados.pop(emp_mod, None); tareas_individuales.pop(emp_mod, None); dispositivos_vinculados.pop(emp_mod, None)
                        save_json("empleados", lista_empleados); save_json("roles", roles_empleados); save_json("tareas_individuales", tareas_individuales); save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()

            with col_s2:
                st.subheader("📋 Asignar Tareas Extra")
                tipo_asig = st.radio("Asignar a:", ["Rol General", "Personal"])
                obj_tarea = st.selectbox("Elegí el destino:", lista_roles_disponibles if tipo_asig == "Rol General" else sorted(lista_empleados))
                n_tarea, p_tarea = st.text_input("Nombre Tarea:"), st.number_input("Puntos:", value=5, min_value=1)
                if st.button("➕ Asignar Tarea") and n_tarea:
                    if tipo_asig == "Rol General": tareas_roles.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea}); save_json("tareas_roles", tareas_roles)
                    else: tareas_individuales.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea}); save_json("tareas_individuales", tareas_individuales)
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
                                    diccionario_ver[clave].pop(idx); save_json("tareas_roles" if ver_t_tipo == "Roles" else "tareas_individuales", diccionario_ver); st.rerun()

        with tab_tiendas:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("📍 Tiendas Físicas")
                for loc, d_loc in lista_locales.items(): st.write(f"- **{loc}** | IP: `{d_loc.get('ip', 'Ninguna')}`")
                
                st.markdown("---")
                ip_gerencia = st.session_state.get('client_ip')
                if not ip_gerencia:
                    ip_eval = streamlit_js_eval(js_expressions="fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')", want_output=True, key="ip_manager")
                    if ip_eval:
                        st.session_state['client_ip'] = ip_eval
                        ip_gerencia = ip_eval

                if ip_gerencia and ip_gerencia != 'Error':
                    st.info(f"💡 **Ayuda de Configuración:** La IP actual de tu conexión es `{ip_gerencia}`. (Si estás físicamente en la sucursal nueva, podés copiar y pegar este número abajo).")
                else:
                    st.info("💡 Buscando tu IP actual para ayudarte a configurar...")

                n_loc, lat_loc, lon_loc, ip_loc = st.text_input("Nueva Tienda:"), st.number_input("Lat:", format="%.6f"), st.number_input("Lon:", format="%.6f"), st.text_input("IP Wi-Fi:")
                if st.button("➕ Crear Tienda") and n_loc: lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc, "ip": ip_loc.strip()}; save_json("locales", lista_locales); st.rerun()
                borrar_loc = st.selectbox("Eliminar Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Tienda") and borrar_loc != "Seleccionar...": del lista_locales[borrar_loc]; save_json("locales", lista_locales); st.rerun()

            with col_l2:
                st.subheader("🕒 Turnos / Horarios")
                for turno, horas in lista_turnos.items(): st.write(f"- **{turno}** | De {horas.get('ingreso')} a {horas.get('salida')}")
                n_turno = st.text_input("Nuevo Horario (Nombre):")
                c_h1, c_h2 = st.columns(2)
                h_ingreso, h_salida = c_h1.time_input("Ingreso:"), c_h2.time_input("Salida:")
                if st.button("➕ Crear Horario") and n_turno: lista_turnos[n_turno] = {"ingreso": h_ingreso.strftime("%I:%M %p"), "salida": h_salida.strftime("%I:%M %p")}; save_json("turnos", lista_turnos); st.rerun()
                borrar_turno = st.selectbox("Eliminar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno") and borrar_turno != "Seleccionar...": del lista_turnos[borrar_turno]; save_json("turnos", lista_turnos); st.rerun()

        with tab_comunicados:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.subheader("📲 Alerta al Ingresar")
                with st.form("form_alertas"):
                    dest_ing = st.selectbox("Destinatario:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados))
                    txt_alerta = st.text_area("Mensaje:")
                    if st.form_submit_button("Crear Alerta") and txt_alerta: alertas_ingreso.append({"destinatario": dest_ing, "texto": txt_alerta}); save_json("alertas_ingreso", alertas_ingreso); st.rerun()
                for idx, a in enumerate(alertas_ingreso):
                    with st.expander(f"A {a['destinatario']}: {a['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_al_{idx}"): alertas_ingreso.pop(idx); save_json("alertas_ingreso", alertas_ingreso); st.rerun()
            with col_m2:
                st.subheader("📌 Anuncio Fijo")
                with st.form("form_fijo"):
                    dest_fijo = st.selectbox("Destinatario:", ["Todos"] + lista_roles_disponibles + sorted(lista_empleados), key="fijo")
                    txt_fijo = st.text_area("Mensaje:")
                    if st.form_submit_button("Publicar") and txt_fijo: lista_mensajes.append({"destinatario": dest_fijo, "texto": txt_fijo}); save_json("mensajes", lista_mensajes); st.rerun()
                for idx, m in enumerate(lista_mensajes):
                    with st.expander(f"A {m['destinatario']}: {m['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_m_{idx}"): lista_mensajes.pop(idx); save_json("mensajes", lista_mensajes); st.rerun()

        with tab_config:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("🛠️ Roles de la Empresa")
                nuevo_rol_cat = st.text_input("Crear Nuevo Rol:")
                if st.button("➕ Agregar Rol") and nuevo_rol_cat and nuevo_rol_cat not in lista_roles_disponibles: lista_roles_disponibles.append(nuevo_rol_cat); save_json("lista_roles", lista_roles_disponibles); st.rerun()
                borrar_rol_cat = st.selectbox("Eliminar Rol:", ["Seleccionar..."] + lista_roles_disponibles)
                if st.button("🗑️ Eliminar Rol") and borrar_rol_cat != "Seleccionar...": lista_roles_disponibles.remove(borrar_rol_cat); save_json("lista_roles", lista_roles_disponibles); st.rerun()
                
                st.subheader("🏆 Reglas de Asistencia")
                with st.form("form_reglas"):
                    r_base = st.number_input("Puntaje Base:", value=config_app.get("reglas_puntos", {}).get("base", 100))
                    c_r1, c_r2 = st.columns(2)
                    r_ok, r_tar = c_r1.number_input("✔️ A Tiempo:", value=config_app.get("reglas_puntos", {}).get("A tiempo", 0)), c_r2.number_input("⚠️ Tarde:", value=config_app.get("reglas_puntos", {}).get("Tarde", -5))
                    r_aus, r_fj = c_r1.number_input("❌ Ausente:", value=config_app.get("reglas_puntos", {}).get("Ausente", -15)), c_r2.number_input("⚕️ Justif:", value=config_app.get("reglas_puntos", {}).get("Falta Justificada", 0))
                    if st.form_submit_button("💾 Guardar Reglas"): config_app["reglas_puntos"] = {"base": r_base, "A tiempo": r_ok, "Tarde": r_tar, "Ausente": r_aus, "Falta Justificada": r_fj}; save_json("config", config_app); st.rerun()

            with col_aj2:
                st.subheader("⚙️ Seguridad de Red y Ajustes")
                with st.form("form_seguridad"):
                    v_autoregistro = st.checkbox("📝 Permitir Auto-registro de empleados", value=config_app.get("autoregistro", False), help="Los empleados podrán escribir su propio nombre al abrir la app por primera vez.")
                    v_gps = st.checkbox("📡 Requerir GPS para Entrada", value=config_app.get("verificar_gps", True))
                    radio_m = st.number_input("Radio en metros:", value=int(config_app.get("radio_metros", 50)))
                    v_wifi = st.checkbox("📶 Requerir Wi-Fi para Entrada", value=config_app.get("verificar_wifi", False))
                    nueva_tolerancia = st.number_input("Minutos tolerancia (llegada tarde):", value=int(config_app.get("tolerancia_minutos", 10)))
                    
                    st.markdown("---")
                    v_exigir_salida_manual = st.checkbox("🛑 Exigir Fichaje de Salida Manual", value=config_app.get("exigir_salida_manual", False), help="Si se desactiva, la salida es automática y no se les pedirá fichar al irse (El sistema asumirá 6 horas menos las llegadas tarde).")
                    v_mostrar_membresia = st.checkbox("👁️ Mostrar tipo de membresía contratada", value=config_app.get("mostrar_membresia", False), help="Muestra a todos los empleados el plan de software contratado en el menú lateral.")
                    
                    if st.form_submit_button("💾 Guardar Ajustes"):
                        config_app.update({"autoregistro": v_autoregistro, "verificar_gps": v_gps, "verificar_wifi": v_wifi, "radio_metros": radio_m, "tolerancia_minutos": nueva_tolerancia, "exigir_salida_manual": v_exigir_salida_manual, "mostrar_membresia": v_mostrar_membresia})
                        save_json("config", config_app); st.rerun()
                
                st.write("🔑 **Cambiar Clave de Gerencia**")
                nc = st.text_input("Nueva clave:", type="password")
                if st.button("🔒 Cambiar Clave") and nc: config_app["admin_password"] = nc; save_json("config", config_app); st.success("Clave modificada.")

            st.markdown("---")
            st.subheader("🧹 Reseteo Quirúrgico en Nube")
            c_cl1, c_cl2 = st.columns(2)
            with c_cl1:
                del_asist = st.checkbox("Registros de Asistencia")
                del_tareas = st.checkbox("Tareas Realizadas")
                del_bonos = st.checkbox("Bonos/Multas Manuales")
            with c_cl2:
                filtro_b = st.selectbox("⏳ Rango a borrar:", ["Hoy", "Esta Semana", "Este Mes", "Mes Anterior", "Todo el Historial", "Personalizado"], key="filtro_borrado")
                rango_borrado = st.date_input("🗓️ Fechas a limpiar:", value=(ahora.date(), ahora.date())) if filtro_b == "Personalizado" else None

            if st.button("⚠️ CONFIRMAR BORRADO"):
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
elif pestaña == "💻 Dueño del Software":
    st.markdown('<div class="main-title">💻 Administrador del Sistema</div>', unsafe_allow_html=True)
    st.info("🔐 Área restringida exclusiva para el propietario y desarrollador del software.")
    
    pass_dueño = st.text_input("Ingrese la Clave Maestra:", type="password")
    
    if pass_dueño == "SantiMaster2026":
        st.success("✅ Acceso Maestro Concedido")
        
        tab_licencia, tab_equipos, tab_empresa, tab_reset = st.tabs([
            "🔴 Control de Licencia", "📱 Gestión de Sesiones", "🏢 Empresa", "☢️ Botón Nuclear"
        ])
        
        with tab_licencia:
            st.subheader("Estado de la Licencia del Cliente")
            with st.form("form_licencia"):
                estado_actual = st.selectbox("Estado del Sistema:", ["Activo", "Suspendido"], index=["Activo", "Suspendido"].index(owner_config.get("estado_licencia", "Activo")))
                plan_actual = st.selectbox("Plan de Pago contratado:", ["Mensual", "Anual", "Vitalicio"], index=["Mensual", "Anual", "Vitalicio"].index(owner_config.get("plan_pago", "Mensual")))
                
                fecha_venc = st.date_input("Fecha de Vencimiento Automático:", value=datetime.datetime.strptime(owner_config.get("fecha_vencimiento", "2030-12-31"), "%Y-%m-%d").date())
                msg_bloqueo = st.text_area("Mensaje de Bloqueo (Se muestra al suspender o vencer):", value=owner_config.get("mensaje_bloqueo", ""))
                
                if st.form_submit_button("💾 Guardar Estado"):
                    owner_config.update({"estado_licencia": estado_actual, "plan_pago": plan_actual, "fecha_vencimiento": str(fecha_venc), "mensaje_bloqueo": msg_bloqueo})
                    save_json("owner_config", owner_config)
                    st.success("¡Licencia actualizada! El sistema obedecerá automáticamente.")
                    st.rerun()
                    
        with tab_equipos:
            st.subheader("🔌 Desconectar Dispositivos Remotamente")
            st.write("Acá podés ver quién está logueado en la aplicación y forzar el cierre de sesión.")
            
            if dispositivos_vinculados:
                for emp, dev in dispositivos_vinculados.items():
                    st.markdown(f"- 👤 **{emp}** (ID Interno: `{dev[:10]}...`)")
                
                emp_desvincular = st.selectbox("Seleccionar empleado para cerrar sesión:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                
                c_eq1, c_eq2 = st.columns(2)
                if c_eq1.button("🔌 Desconectar a este empleado") and emp_desvincular != "Seleccionar...":
                    del dispositivos_vinculados[emp_desvincular]
                    save_json("dispositivos", dispositivos_vinculados)
                    st.success(f"✅ Sesión cerrada para {emp_desvincular}.")
                    st.rerun()
                    
                if c_eq2.button("⚠️ CERRAR TODAS LAS SESIONES"):
                    dispositivos_vinculados.clear()
                    save_json("dispositivos", {})
                    st.success("✅ ¡Todos los empleados han sido desconectados!")
                    st.rerun()
            else:
                st.info("No hay ningún empleado logueado en este momento.")

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
            st.subheader("🚀 Instalación 0KM para Nuevo Cliente")
            st.error("¡CUIDADO! Este botón borra ABSOLUTAMENTE TODO (Empleados, roles, tareas, mensajes, fichajes y tiendas). Deja la aplicación en blanco para instalarla en una empresa nueva.")
            
            check_seguridad = st.checkbox("Estoy seguro que quiero borrar toda la empresa actual.")
            if st.button("☢️ INICIAR DE FÁBRICA (FACTORY RESET)") and check_seguridad:
                save_json("empleados", [])
                save_json("roles", {})
                save_json("tareas_roles", {})
                save_json("tareas_individuales", {})
                save_json("dispositivos", {})
                save_json("locales", {})
                save_json("turnos", {})
                save_json("mensajes", [])
                save_json("alertas_ingreso", [])
                save_json("intentos_seguridad", [])
                save_json("ajustes_puntos", [])
                save_json("reportes", [])
                save_json("salidas_pendientes", [])
                save_json("sueldos_historico", [])
                save_json("cierres_caja", [])
                
                supabase.table("asistencia").delete().neq("id", 0).execute()
                supabase.table("tareas_log").delete().neq("id", 0).execute()
                
                st.success("¡SISTEMA BORRADO! La aplicación está lista para un nuevo cliente.")
                st.rerun()
