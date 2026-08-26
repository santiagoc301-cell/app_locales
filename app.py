import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json
import altair as alt

# Configuración inicial de la página
st.set_page_config(page_title="Gestión Corporativa - Retail", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 💎 ESTÉTICA PREMIUM COMERCIAL (CSS)
# ==========================================
st.markdown("""
<style>
    .main-title { font-size: 2.8rem; font-weight: 800; color: #111827; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: -0.5px;}
    .sub-text { font-size: 1.15rem; color: #4B5563; margin-bottom: 2rem; }
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #E5E7EB; padding: 20px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-top: 5px solid #2563EB; transition: transform 0.2s ease-in-out;}
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); }
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 800; color: #111827; }
    .stButton>button { border-radius: 10px; font-weight: 600; transition: all 0.3s; border: 1px solid #D1D5DB; padding: 0.5rem 1rem; }
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
    hr { border-color: #E5E7EB; margin-top: 2rem; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. RUTINAS DE DATOS "ANTI-ERRORES"
# ==========================================
ARCHIVO_EMPLEADOS = "empleados.json"
ARCHIVO_LISTA_ROLES = "lista_roles.json"
ARCHIVO_ROLES = "roles.json"
ARCHIVO_TAREAS_ROLES = "tareas_roles.json"
ARCHIVO_TAREAS_INDIVIDUALES = "tareas_individuales.json"
ARCHIVO_TAREAS_LOG = "tareas_log.csv"
ARCHIVO_REPORTES = "reportes.json"
ARCHIVO_DISPOSITIVOS = "dispositivos.json"
ARCHIVO_LOCALES = "locales.json"
ARCHIVO_TURNOS = "turnos.json"
ARCHIVO_ASISTENCIA = "asistencia.csv"
ARCHIVO_CONFIG = "config.json"
ARCHIVO_MENSAJES = "mensajes.json"
ARCHIVO_ALERTAS_INGRESO = "alertas_ingreso.json"
ARCHIVO_INTENTOS = "intentos_seguridad.json"
ARCHIVO_PUNTOS = "ajustes_puntos.json"

def init_csv(file_path, columns):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)
    else:
        try:
            df = pd.read_csv(file_path)
            cambios = False
            for col in columns:
                if col not in df.columns:
                    if col == "Distancia_m": df[col] = 0.0
                    elif col == "Puntos": df[col] = 0
                    elif col == "Estado" and "tareas" in file_path: df[col] = "Aprobada"
                    else: df[col] = ""
                    cambios = True
            if cambios: df.to_csv(file_path, index=False)
        except:
            pd.DataFrame(columns=columns).to_csv(file_path, index=False)

init_csv(ARCHIVO_ASISTENCIA, ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m", "Nota"])
init_csv(ARCHIVO_TAREAS_LOG, ["Fecha", "Hora", "Empleado", "Tarea", "Puntos", "Estado"])

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f: json.dump(default_data, f)
        return default_data
    try:
        with open(file_path, 'r') as f: return json.load(f)
    except:
        return default_data

def save_json(file_path, data):
    with open(file_path, 'w') as f: json.dump(data, f)

# Configuración Inicial y Motor de Reglas
config_defecto = {
    "admin_password": "1234", "tolerancia_minutos": 10, "requiere_salida": True,
    "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia.",
    "verificar_gps": True, "verificar_wifi": False, "ip_wifi_oficial": "",
    "radio_metros": 50,
    "mensaje_salida_lejos": "⚠️ Estás registrando tu salida fuera de la tienda. Las horas no se sumarán hasta ser auditadas.",
    "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}
}

config_app = load_json(ARCHIVO_CONFIG, config_defecto)
modificado = False
for k, v in config_defecto.items():
    if k not in config_app:
        config_app[k] = v
        modificado = True
if not isinstance(config_app.get("reglas_puntos"), dict):
    config_app["reglas_puntos"] = config_defecto["reglas_puntos"]
    modificado = True
else:
    for k, v in config_defecto["reglas_puntos"].items():
        if k not in config_app["reglas_puntos"]:
            config_app["reglas_puntos"][k] = v
            modificado = True
if modificado: save_json(ARCHIVO_CONFIG, config_app)

lista_roles_disponibles = load_json(ARCHIVO_LISTA_ROLES, ["Vendedor", "Cajero", "Encargado", "Depósito", "Otro"])
lista_empleados = load_json(ARCHIVO_EMPLEADOS, ["Abril Gonzalez", "Agustina Lopez", "Daniela Perez", "Macarena Silva"])
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

roles_empleados = load_json(ARCHIVO_ROLES, {e: "Vendedor" for e in lista_empleados})
tareas_roles = load_json(ARCHIVO_TAREAS_ROLES, {"Vendedor": [{"tarea": "Acomodar Sector", "puntos": 5}]})
tareas_individuales = load_json(ARCHIVO_TAREAS_INDIVIDUALES, {e: [] for e in lista_empleados})
dispositivos_vinculados = load_json(ARCHIVO_DISPOSITIVOS, {})
lista_locales = load_json(ARCHIVO_LOCALES, {"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}})
lista_turnos = {k: {"ingreso": v, "salida": "11:59 PM"} if isinstance(v, str) else v for k, v in load_json(ARCHIVO_TURNOS, {"Apertura": {"ingreso": "09:00 AM", "salida": "05:00 PM"}}).items()}
lista_mensajes = load_json(ARCHIVO_MENSAJES, [])
alertas_ingreso = load_json(ARCHIVO_ALERTAS_INGRESO, [])
lista_intentos = load_json(ARCHIVO_INTENTOS, [])
lista_puntos = load_json(ARCHIVO_PUNTOS, [])
reportes_log = load_json(ARCHIVO_REPORTES, [])

ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A"]

# ==========================================
# 2. IDENTIFICADOR Y RED DEL CELULAR
# ==========================================
js_get_device = "(function() { let id = localStorage.getItem('tienda_app_device_id'); if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); } return id; })();"
device_id = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")

js_get_ip = "fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(e => 'Error')"
client_ip = streamlit_js_eval(js_expressions=js_get_ip, want_output=True, key="get_client_ip")

empleado_en_celu = None
if device_id:
    for emp, dev in dispositivos_vinculados.items():
        if dev == device_id:
            empleado_en_celu = emp
            break

def procesar_rango_fechas(rango):
    if isinstance(rango, tuple) or isinstance(rango, list):
        if len(rango) == 2: return rango[0], rango[1]
        elif len(rango) == 1: return rango[0], rango[0]
    return rango, rango

def calcular_nivel(puntos):
    if puntos < 80: return "🔴 Observación"
    elif puntos < 100: return "🥉 Bronce"
    elif puntos < 130: return "🥈 Plata"
    elif puntos < 160: return "🥇 Oro"
    elif puntos < 200: return "💎 Platino"
    else: return "👑 Leyenda"

zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%I:%M:%S %p")

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🛍️ Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Portal del Empleado", "⚙️ Panel de Gerencia"])

# ==========================================
# 4. PANTALLA: PORTAL DEL EMPLEADO (ACCESO DIRECTO)
# ==========================================
if pestaña == "⏱️ Portal del Empleado":
    st.markdown('<div class="main-title">⏱️ Portal del Equipo</div>', unsafe_allow_html=True)
    
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")

    if not device_id:
        st.info("🔄 Autenticando tu equipo...")
    else:
        if empleado_en_celu:
            # Ya no hay contraseña, si el dispositivo coincide entra directo.
            
            if 'fichaje_exitoso' in st.session_state:
                if "⚠️" in st.session_state['fichaje_exitoso'] or "❌" in st.session_state['fichaje_exitoso']:
                    st.warning(st.session_state['fichaje_exitoso'])
                else:
                    st.success(st.session_state['fichaje_exitoso'])
                    st.balloons()
                del st.session_state['fichaje_exitoso']

            puntos_actuales = config_app["reglas_puntos"]["base"]
            try:
                df_punt = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_e = df_punt[df_punt["Empleado"] == empleado_en_celu]
                if not df_e.empty:
                    puntos_actuales += (len(df_e[df_e["Estado"] == "Tarde"]) * config_app["reglas_puntos"]["Tarde"]) + (len(df_e[df_e["Tipo"] == "Ausente"]) * config_app["reglas_puntos"]["Ausente"])
            except: pass
            
            try:
                df_tl = pd.read_csv(ARCHIVO_TAREAS_LOG)
                if not df_tl.empty: 
                    puntos_actuales += df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Estado"] == "Aprobada")]["Puntos"].astype(int).sum()
            except: pass
            
            puntos_actuales += sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == empleado_en_celu and p.get('Estado') == "Aprobada"])
            rol_empleado = roles_empleados.get(empleado_en_celu, 'Staff')
            
            st.markdown(f"<div class='credencial'><p class='cred-nombre'>👤 {empleado_en_celu}</p><p class='cred-rol'>Rol: {rol_empleado}</p><div class='cred-nivel'>{calcular_nivel(puntos_actuales)} ({puntos_actuales} pts)</div></div>", unsafe_allow_html=True)

            if rol_empleado in ["Cajero", "Encargado"]:
                with st.expander("👑 Panel de Responsable de Turno", expanded=False):
                    st.markdown("<div class='super-box'><b>Rol Supervisor:</b> Podés asignar bonos o multas a otros compañeros. Esto requiere la autorización final de Gerencia.</div>", unsafe_allow_html=True)
                    with st.form("form_sup_puntos"):
                        s_emp = st.selectbox("Compañero a evaluar:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu])
                        s_pts = st.number_input("Puntos (+ para premio, - para multa):", value=0, step=1)
                        s_mot = st.text_input("Motivo de la evaluación:")
                        if st.form_submit_button("Enviar Evaluación a Gerencia"):
                            if s_emp != "Seleccionar..." and s_pts != 0 and s_mot:
                                lista_puntos.append({"Fecha": fecha_hoy, "Empleado": s_emp, "Puntos": s_pts, "Motivo": s_mot, "Autor": empleado_en_celu, "Estado": "Pendiente"})
                                save_json(ARCHIVO_PUNTOS, lista_puntos)
                                st.success("Evaluación enviada. Impactará cuando Gerencia la apruebe.")
                            else:
                                st.error("Completá todos los campos (Puntos no puede ser 0).")

            mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='msg-global'>🏷️ <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='msg-individual'>📩 <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)

            with st.expander("📍 Registrar Asistencia de Hoy", expanded=True):
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1: local_seleccionado = st.selectbox("Tienda actual:", ["Seleccionar..."] + list(lista_locales.keys()))
                with col_sel2: turno_seleccionado = st.selectbox("Horario:", ["Seleccionar..."] + list(lista_turnos.keys()))
                nota_empleado = st.text_input("📝 Dejar justificación / novedad (Opcional):")

                if local_seleccionado != "Seleccionar..." and turno_seleccionado != "Seleccionar...":
                    en_rango = True
                    wifi_aprobado = True
                    distancia_real = 0.0
                    radio_permitido = int(config_app.get("radio_metros", 50))

                    st.markdown("### 🛡️ Proceso de Validación")
                    if config_app.get("verificar_gps", True):
                        ubicacion = get_geolocation()
                        if ubicacion and isinstance(ubicacion, dict) and 'coords' in ubicacion:
                            coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                            coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                            distancia_real = geodesic(coord_usuario, coord_local).meters
                            if distancia_real <= radio_permitido:
                                st.markdown(f"<div class='validation-box'>✅ <b>GPS Aprobado:</b> Estás en el local ({distancia_real:.1f} m).</div>", unsafe_allow_html=True)
                            else:
                                en_rango = False
                                st.markdown(f"<div class='validation-box' style='border-left: 5px solid #F59E0B;'>⚠️ <b>Fuera del local:</b> Estás a {distancia_real:.1f} m. (Límite: {radio_permitido}m). <b>Solo podés registrar Salida.</b></div>", unsafe_allow_html=True)
                        else:
                            en_rango = False
                            st.markdown("<div class='validation-box' style='border-left: 5px solid #EF4444;'>❌ <b>GPS Apagado o Sin Permisos:</b> Por favor, encendé la ubicación en tu celular y recargá la página.</div>", unsafe_allow_html=True)

                    if config_app.get("verificar_wifi", False):
                        ip_tienda = lista_locales[local_seleccionado].get("ip", "").strip()
                        if not ip_tienda:
                            wifi_aprobado = False
                            st.markdown("<div class='validation-box' style='border-left: 5px solid #EF4444;'>❌ <b>Red Denegada:</b> Esta tienda no tiene IP configurada.</div>", unsafe_allow_html=True)
                        elif client_ip:
                            if client_ip == ip_tienda:
                                st.markdown("<div class='validation-box'>✅ <b>Red Aprobada:</b> Conectado al Wi-Fi del local.</div>", unsafe_allow_html=True)
                            else:
                                wifi_aprobado = False
                                st.markdown(f"<div class='validation-box' style='border-left: 5px solid #EF4444;'>❌ <b>Red Denegada:</b> Tu conexión ({client_ip}) no coincide con el local.</div>", unsafe_allow_html=True)
                        else:
                            wifi_aprobado = False
                            st.markdown("<div class='validation-box'>⏳ <b>Verificando tu conexión de red...</b></div>", unsafe_allow_html=True)

                    puede_fichar = True
                    if config_app.get("verificar_wifi", False) and not wifi_aprobado: puede_fichar = False

                    if puede_fichar:
                        ya_ficho_entrada = False
                        try:
                            df_temp = pd.read_csv(ARCHIVO_ASISTENCIA)
                            filtro = df_temp[(df_temp["Empleado"] == empleado_en_celu) & (df_temp["Fecha"] == fecha_hoy) & (df_temp["Turno"] == turno_seleccionado) & (df_temp["Tipo"] == "Entrada")]
                            if not filtro.empty: ya_ficho_entrada = True
                        except: pass

                        marcar, tipo_fichaje = False, ""
                        st.write("---")
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                if not en_rango: st.error("❌ No podés registrar Entrada estando fuera del perímetro.")
                                elif ya_ficho_entrada: st.error("⚠️ Ya marcaste el ingreso para este turno.")
                                else: marcar, tipo_fichaje = True, "Entrada"
                        with col_b2:
                            if config_app.get("requiere_salida", True):
                                if st.button("🔴 REGISTRAR SALIDA", use_container_width=True): marcar, tipo_fichaje = True, "Salida"

                        if marcar:
                            estado_llegada = "N/A"
                            if tipo_fichaje == "Entrada":
                                hora_t_str = lista_turnos[turno_seleccionado]["ingreso"]
                                hora_t_obj = pd.to_datetime(hora_t_str).time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                                estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                            elif tipo_fichaje == "Salida":
                                estado_llegada = "Salida (Fuera de Rango)" if not en_rango else "Salida"

                            reg = {"Fecha": [fecha_hoy], "Hora": [hora_hoy], "Empleado": [empleado_en_celu], "Sucursal": [local_seleccionado], "Turno": [turno_seleccionado], "Tipo": [tipo_fichaje], "Estado": [estado_llegada], "Distancia_m": [round(distancia_real, 1)], "Nota": [nota_empleado]}
                            pd.concat([pd.read_csv(ARCHIVO_ASISTENCIA), pd.DataFrame(reg)], ignore_index=True).to_csv(ARCHIVO_ASISTENCIA, index=False)
                            
                            if tipo_fichaje == "Entrada":
                                msg_final = f"¡Entrada registrada a las {hora_hoy}!"
                                if estado_llegada == "Tarde":
                                    msg_final += f"\n\n🔴 {config_app.get('mensaje_llegada_tarde')}"
                                for a in alertas_ingreso:
                                    if a['destinatario'] in ['Todos', empleado_en_celu]:
                                        msg_final += f"\n\n📩 **Mensaje Automático de Gerencia:**\n{a['texto']}"
                                st.session_state['fichaje_exitoso'] = msg_final
                            else:
                                if not en_rango: st.session_state['fichaje_exitoso'] = config_app.get("mensaje_salida_lejos", "⚠️ Salida marcada fuera del local.")
                                else: st.session_state['fichaje_exitoso'] = f"¡Salida registrada a las {hora_hoy}! Buen descanso."
                            
                            st.rerun() 
                else: st.info("Elegí tu tienda y turno para habilitar la validación.")

            with st.expander("🛑 Buzón de Reportes Confidenciales", expanded=False):
                st.write("Reportá problemas de forma privada directo a Gerencia.")
                tipo_rep = st.selectbox("Tipo de situación:", ["Falla de equipo/sistema", "Incumplimiento de un compañero", "Queja general", "Otra observación"])
                implicado = "N/A"
                if tipo_rep == "Incumplimiento de un compañero":
                    implicado = st.selectbox("Compañero implicado:", ["Seleccionar..."] + [e for e in lista_empleados if e != empleado_en_celu])
                detalle_rep = st.text_area("Detalle (Sé específico):")
                
                if st.button("📤 Enviar a Gerencia"):
                    if detalle_rep:
                        reportes_log.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Emisor": empleado_en_celu, "Tipo": tipo_rep, "Implicado": implicado, "Detalle": detalle_rep, "Estado": "Pendiente de lectura"})
                        save_json(ARCHIVO_REPORTES, reportes_log)
                        st.success("¡Reporte enviado de forma confidencial!")
                    else: st.error("Por favor, escribí un detalle.")

            t_rol = tareas_roles.get(rol_empleado, [])
            t_indiv = tareas_individuales.get(empleado_en_celu, [])
            tareas_totales = t_rol + t_indiv
            
            if tareas_totales:
                with st.expander("📋 Mis Tareas del Día", expanded=True):
                    try:
                        df_tl = pd.read_csv(ARCHIVO_TAREAS_LOG)
                        tareas_hoy_df = df_tl[(df_tl["Empleado"] == empleado_en_celu) & (df_tl["Fecha"] == fecha_hoy)]
                    except: tareas_hoy_df = pd.DataFrame()
                    
                    for t in tareas_totales:
                        t_nombre = t.get('tarea')
                        t_puntos = t.get('puntos')
                        t_reg = tareas_hoy_df[tareas_hoy_df["Tarea"] == t_nombre] if not tareas_hoy_df.empty else pd.DataFrame()
                        
                        if not t_reg.empty:
                            est_t = t_reg.iloc[-1]["Estado"]
                            if est_t == "Aprobada": st.markdown(f"<div class='task-box'>✅ <b>{t_nombre}</b> (+{t_puntos} pts) - <b>Aprobada</b></div>", unsafe_allow_html=True)
                            elif est_t == "Rechazada": st.markdown(f"<div class='task-rej'>❌ <b>{t_nombre}</b> - Rechazada por Gerencia</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='task-pend'>⏳ <b>{t_nombre}</b> - Esperando auditoría...</div>", unsafe_allow_html=True)
                        else:
                            c_t1, c_t2 = st.columns([3, 1])
                            c_t1.write(f"🔸 {t_nombre} (+{t_puntos} pts)")
                            if c_t2.button("✔️ Reportar Lista", key=f"btn_t_{t_nombre}"):
                                reg_t = {"Fecha": [fecha_hoy], "Hora": [hora_hoy], "Empleado": [empleado_en_celu], "Tarea": [t_nombre], "Puntos": [t_puntos], "Estado": ["Pendiente"]}
                                pd.concat([pd.read_csv(ARCHIVO_TAREAS_LOG), pd.DataFrame(reg_t)], ignore_index=True).to_csv(ARCHIVO_TAREAS_LOG, index=False)
                                st.rerun()

            with st.expander("📜 Mi historial reciente"):
                try:
                    df_h = pd.read_csv(ARCHIVO_ASISTENCIA)
                    if not df_h.empty:
                        df_h['F_Obj'] = pd.to_datetime(df_h['Fecha'], errors='coerce').dt.date
                        df_emp = df_h[(df_h["Empleado"] == empleado_en_celu) & (df_h["F_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                        if not df_emp.empty: st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                        else: st.write("Sin fichajes recientes.")
                    else: st.write("Sin registros.")
                except: st.write("Aún no hay registros.")
        else:
            st.warning("⚠️ **Equipo no autorizado.**")
            emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()])
            if st.button("🔗 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
                dispositivos_vinculados[emp_vincular] = device_id
                save_json(ARCHIVO_DISPOSITIVOS, dispositivos_vinculados)
                st.rerun()

# ==========================================
# 5. PANTALLA: PANEL DE GERENCIA
# ==========================================
elif pestaña == "⚙️ Panel de Gerencia":
    st.markdown('<div class="main-title">⚙️ Panel de Gerencia Corporativa</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Clave de acceso:", type="password")
    CLAVE_OCULTA = "doremifasol"

    if password_ingresada and password_ingresada != CLAVE_OCULTA:
        if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
            st.session_state['last_pw_attempt'] = password_ingresada
            quien_intenta = empleado_en_celu if empleado_en_celu else "Dispositivo Desconocido"
            resultado = "🟢 Acceso Permitido" if password_ingresada == config_app.get("admin_password", "1234") else "🔴 Acceso Denegado"
            lista_intentos.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Usuario": quien_intenta, "Clave Probada": password_ingresada, "Resultado": resultado})
            save_json(ARCHIVO_INTENTOS, lista_intentos)

    if password_ingresada == config_app.get("admin_password", "1234") or password_ingresada == CLAVE_OCULTA:
        
        tab_analytics, tab_puntos, tab_auditoria_tareas, tab_auditoria_horas, tab_staff, tab_tiendas, tab_comunicados, tab_config, tab_espia = st.tabs([
            "📈 Analytics & Horas", "🏆 Puntos y Ficha", "📋 Auditoría Tareas", "📝 Auditoría Horarios", "👥 Staff y Roles", "📍 Tiendas y Redes", "📢 Comunicados", "⚙️ Configuración", "🕵️ Modo Espía"
        ])

        # ==========================================
        # TAB 1: ANALYTICS Y RECUENTO DE HORAS
        # ==========================================
        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📈 Analytics y Cálculo de Horas</div>', unsafe_allow_html=True)
            try: df_activos = pd.read_csv(ARCHIVO_ASISTENCIA)
            except: df_activos = pd.DataFrame()

            if df_activos.empty: st.info("📊 La base de datos está limpia. Esperá a que el personal comience a fichar.")
            else:
                df_activos = df_activos[df_activos["Empleado"].isin(lista_empleados)].copy()
                df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                
                st.markdown(f"### 🚨 Alertas del Día de Hoy ({fecha_hoy})")
                df_hoy = df_activos[df_activos["Fecha"] == fecha_hoy]
                
                entradas_hoy = df_hoy[df_hoy["Tipo"] == "Entrada"]["Empleado"].unique().tolist()
                ausentes = df_hoy[df_hoy["Tipo"] == "Ausente"]["Empleado"].unique().tolist()
                llegadas_tarde = df_hoy[(df_hoy["Tipo"] == "Entrada") & (df_hoy["Estado"] == "Tarde")]["Empleado"].unique().tolist()
                sin_fichar = [e for e in lista_empleados if e not in entradas_hoy and e not in ausentes]

                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                c_h1.markdown("<div class='task-box'><b>✅ Presentes Hoy</b><br>" + ("<br>".join(entradas_hoy) if entradas_hoy else "Nadie") + "</div>", unsafe_allow_html=True)
                c_h2.markdown("<div class='alert-box' style='border-color: #F59E0B; background-color: #FFFBEB; color: #B45309;'><b>⚠️ Tarde Hoy</b><br>" + ("<br>".join(llegadas_tarde) if llegadas_tarde else "Ninguno") + "</div>", unsafe_allow_html=True)
                c_h3.markdown("<div class='alert-box' style='border-color: #EF4444; background-color: #FEF2F2; color: #B91C1C;'><b>❌ Ausentes</b><br>" + ("<br>".join(ausentes) if ausentes else "Ninguno") + "</div>", unsafe_allow_html=True)
                c_h4.markdown("<div class='alert-box' style='border-color: #6B7280; background-color: #F3F4F6; color: #374151;'><b>⚪ Aún no ficharon</b><br>" + ("<br>".join(sin_fichar) if sin_fichar else "Todos OK") + "</div>", unsafe_allow_html=True)
                
                st.write("---")
                rango_stats = st.date_input("🗓️ Periodo Histórico y de Horas:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date()))
                s_in, s_fi = procesar_rango_fechas(rango_stats)
                df_per = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_in) & (df_activos['Fecha_Obj'].dt.date <= s_fi)]
                
                if not df_per.empty:
                    atiempo = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "A tiempo")])
                    tardes = len(df_per[(df_per["Tipo"] == "Entrada") & (df_per["Estado"] == "Tarde")])
                    ausencias_tot = len(df_per[df_per["Tipo"] == "Ausente"])
                    tot_ingresos = atiempo + tardes
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("🎯 Puntualidad Empresa", f"{round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0}%")
                    c2.metric("✅ Llegadas a Tiempo", atiempo)
                    c3.metric("⚠️ Llegadas Tarde", tardes)
                    c4.metric("❌ Inasistencias", ausencias_tot)
                    
                    st.markdown("---")
                    st.markdown(f"### ⏱️ Recuento de Horas Trabajadas ({s_in.strftime('%d/%m')} al {s_fi.strftime('%d/%m')})")
                    
                    datos_horas = []
                    for emp in lista_empleados:
                        df_e = df_per[df_per["Empleado"] == emp]
                        horas_totales = 0.0
                        for f in df_e["Fecha"].unique():
                            df_ef = df_e[df_e["Fecha"] == f].sort_values(by="Hora")
                            ent = df_ef[df_ef["Tipo"] == "Entrada"]
                            sal = df_ef[df_ef["Tipo"] == "Salida"]
                            
                            if not ent.empty and not sal.empty:
                                estado_salida = sal.iloc[-1]["Estado"]
                                if estado_salida != "Salida (Fuera de Rango)":
                                    h_in = pd.to_datetime(ent.iloc[0]["Hora"])
                                    h_out = pd.to_datetime(sal.iloc[-1]["Hora"])
                                    diff = (h_out - h_in).total_seconds() / 3600.0
                                    if diff < 0: horas_totales += (diff + 24.0)
                                    else: horas_totales += diff
                        
                        datos_horas.append({"Personal": emp, "Rol": roles_empleados.get(emp, ""), "⏱️ Horas Computadas": round(horas_totales, 2)})
                        
                    if datos_horas: st.dataframe(pd.DataFrame(datos_horas).sort_values(by="⏱️ Horas Computadas", ascending=False), use_container_width=True, hide_index=True)
                else: st.warning("No hay registros en el periodo seleccionado.")

        # ==========================================
        # TAB 2: PUNTOS Y GAMIFICACIÓN
        # ==========================================
        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Gamificación e Historial Individual</div>', unsafe_allow_html=True)
            rango_punt = st.date_input("🗓️ Periodo de Análisis:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date()), key="cal_punt")
            p_in, p_fi = procesar_rango_fechas(rango_punt)
            
            tab_rank, tab_ficha = st.tabs(["📊 Ranking Global", "👤 Ficha de Rendimiento Individual"])
            
            with tab_rank:
                try:
                    df_p = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_t = pd.read_csv(ARCHIVO_TAREAS_LOG)
                except: df_p, df_t = pd.DataFrame(), pd.DataFrame()

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
                        e_tp = df_t[(df_t["Empleado"] == emp) & (df_t["Estado"] == "Aprobada")]["Puntos"].astype(int).sum() if not df_t.empty else 0
                        df_e = df_p[df_p["Empleado"] == emp]
                        
                        e_ok = len(df_e[df_e["Estado"] == "A tiempo"])
                        e_tar = len(df_e[df_e["Estado"] == "Tarde"])
                        e_au = len(df_e[df_e["Tipo"] == "Ausente"])
                        
                        puntaje = reg.get('base', 100) + (e_ok * reg.get('A tiempo', 0)) + (e_tar * reg.get('Tarde', -5)) + (e_au * reg.get('Ausente', -15)) + e_aj + e_tp
                        ranking_data.append({"Personal": emp, "Nivel": calcular_nivel(puntaje), "⭐ PUNTOS": puntaje, "📋 Pts Tareas": e_tp, "⚙️ Ajustes": e_aj, "⚠️ Tardes": e_tar, "❌ Faltas": e_au})
                        
                    if ranking_data:
                        st.dataframe(pd.DataFrame(ranking_data).sort_values(by="⭐ PUNTOS", ascending=False), use_container_width=True, hide_index=True)
                else: st.info("Sin datos para generar el ranking.")
                
                st.markdown("---")
                st.subheader("✍️ Cargar Bono o Multa (Directo de Gerencia)")
                with st.form("form_bonos"):
                    c_b1, c_b2, c_b3, c_b4 = st.columns([2,1,1,2])
                    ap_emp = c_b1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                    ap_fecha = c_b2.date_input("Fecha:", ahora.date())
                    ap_puntos = c_b3.number_input("Puntos (+/-):", value=0, step=1)
                    ap_motivo = c_b4.text_input("Motivo:")
                    if st.form_submit_button("Aplicar a Puntuación") and ap_emp != "Seleccionar...":
                        lista_puntos.append({"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo, "Autor": "Gerencia", "Estado": "Aprobada"})
                        save_json(ARCHIVO_PUNTOS, lista_puntos)
                        st.rerun()

            with tab_ficha:
                emp_ficha = st.selectbox("Analizar Rendimiento de:", ["Seleccionar..."] + sorted(lista_empleados))
                if emp_ficha != "Seleccionar..." and not df_p.empty:
                    fechas_rango = pd.date_range(start=p_in, end=p_fi)
                    ficha_data, pts_acum = [], config_app["reglas_puntos"].get('base', 100)
                    for f in fechas_rango:
                        f_s = f.strftime("%Y-%m-%d")
                        p_dia = 0
                        asist_dia = df_p[(df_p["Empleado"] == emp_ficha) & (df_p["Fecha"] == f_s)]
                        est_dia = "Sin registro"
                        if not asist_dia.empty:
                            if "Ausente" in asist_dia["Tipo"].values:
                                est_dia = "❌ Ausente"
                                p_dia += config_app["reglas_puntos"].get("Ausente", -15)
                            elif "Entrada" in asist_dia["Tipo"].values:
                                e_ent = asist_dia[asist_dia["Tipo"] == "Entrada"].iloc[0]
                                est_dia = "⚠️ Tarde" if e_ent["Estado"] == "Tarde" else "✅ A tiempo"
                                p_dia += config_app["reglas_puntos"].get(e_ent["Estado"], 0)
                        
                        t_dia = df_t[(df_t["Empleado"] == emp_ficha) & (df_t["Fecha"] == f_s) & (df_t["Estado"] == "Aprobada")] if not df_t.empty else pd.DataFrame()
                        if not t_dia.empty: p_dia += t_dia["Puntos"].astype(int).sum()
                            
                        b_dia = [p for p in lista_puntos if p.get("Empleado") == emp_ficha and p.get("Fecha") == f_s and p.get("Estado", "Aprobada") == "Aprobada"]
                        for b in b_dia: p_dia += int(b.get("Puntos", 0))
                            
                        pts_acum += p_dia
                        if est_dia != "Sin registro" or not t_dia.empty or b_dia:
                            ficha_data.append({"Fecha": f_s, "Estado": est_dia, "Variación": p_dia, "Acumulado": pts_acum})
                            
                    if ficha_data: st.dataframe(pd.DataFrame(ficha_data), use_container_width=True, hide_index=True)
                    else: st.info("Sin registros en este periodo.")

        # ==========================================
        # TAB 3: AUDITORIA DE TAREAS Y REPORTES
        # ==========================================
        with tab_auditoria_tareas:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📋 Auditoría de Tareas y Reportes</div>', unsafe_allow_html=True)
            
            st.subheader("🛡️ Tareas y Puntos Pendientes de Aprobación")
            try:
                df_tl_all = pd.read_csv(ARCHIVO_TAREAS_LOG)
                pend_tareas = df_tl_all[df_tl_all["Estado"] == "Pendiente"]
                if not pend_tareas.empty:
                    for idx in pend_tareas.index:
                        row = df_tl_all.loc[idx]
                        c_p1, c_p2, c_p3 = st.columns([4, 1, 1])
                        c_p1.markdown(f"**{row['Empleado']}** reportó: '{row['Tarea']}' (+{row['Puntos']} pts)")
                        if c_p2.button("✅ Aprobar", key=f"apr_t_{idx}"):
                            df_tl_all.at[idx, "Estado"] = "Aprobada"
                            df_tl_all.to_csv(ARCHIVO_TAREAS_LOG, index=False)
                            st.rerun()
                        if c_p3.button("❌ Rechazar", key=f"rec_t_{idx}"):
                            df_tl_all.at[idx, "Estado"] = "Rechazada"
                            df_tl_all.to_csv(ARCHIVO_TAREAS_LOG, index=False)
                            st.rerun()
            except: pass

            puntos_pendientes = [p for p in lista_puntos if p.get("Estado") == "Pendiente"]
            if puntos_pendientes:
                st.write("---")
                st.write("**Evaluaciones de Responsables de Turno:**")
                for idx, p in enumerate(lista_puntos):
                    if p.get("Estado") == "Pendiente":
                        c_pp1, c_pp2, c_pp3 = st.columns([4, 1, 1])
                        c_pp1.markdown(f"**{p['Autor']}** sugiere **{p['Puntos']} pts** a **{p['Empleado']}** (Motivo: {p['Motivo']})")
                        if c_pp2.button("✅ Aprobar", key=f"apr_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Aprobada"
                            save_json(ARCHIVO_PUNTOS, lista_puntos)
                            st.rerun()
                        if c_pp3.button("❌ Rechazar", key=f"rec_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Rechazada"
                            save_json(ARCHIVO_PUNTOS, lista_puntos)
                            st.rerun()
            
            if (not 'pend_tareas' in locals() or pend_tareas.empty) and not puntos_pendientes:
                st.info("✅ No hay tareas ni puntos pendientes de revisión.")

            st.markdown("---")
            st.subheader("🛑 Buzón de Quejas y Reportes Confidenciales")
            reportes_pendientes = [r for r in reportes_log if r.get("Estado") == "Pendiente de lectura"]
            reportes_vistos = [r for r in reportes_log if r.get("Estado") == "Visto"]

            if not reportes_pendientes:
                st.info("✅ No hay nuevos reportes ni quejas.")
            else:
                for idx, r in enumerate(reportes_log):
                    if r.get("Estado") == "Pendiente de lectura":
                        st.markdown(f"""
                        <div class='report-box'>
                            <b>🔴 NUEVO REPORTE</b> | Fecha: {r['Fecha']} {r['Hora']}<br>
                            <b>Emisor:</b> {r['Emisor']} | <b>Tipo:</b> {r['Tipo']}<br>
                            <b>Implicado:</b> {r.get('Implicado', 'N/A')}<br>
                            <b>Detalle:</b> <i>"{r['Detalle']}"</i>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Marcar como Visto", key=f"visto_rep_{idx}"):
                            reportes_log[idx]["Estado"] = "Visto"
                            save_json(ARCHIVO_REPORTES, reportes_log)
                            st.rerun()
            
            if reportes_vistos:
                with st.expander("👁️ Ver Historial de Reportes Leídos"):
                    for idx, r in enumerate(reportes_log):
                        if r.get("Estado") == "Visto":
                            st.write(f"- **{r['Fecha']} ({r['Emisor']})** - {r['Tipo']}: *{r['Detalle']}*")
                            if st.button("🗑️ Eliminar", key=f"del_rep_{idx}"):
                                reportes_log.pop(idx)
                                save_json(ARCHIVO_REPORTES, reportes_log)
                                st.rerun()

        # ==========================================
        # TAB 4: AUDITORÍA MANUAL (HORARIOS)
        # ==========================================
        with tab_auditoria_horas:
            st.markdown('<div class="highlight-edit"><b>✏️ AUDITORÍA DE HORARIOS (Soporta formato AM/PM)</b></div>', unsafe_allow_html=True)
            col_ed1, col_ed2 = st.columns(2)
            fecha_edicion = col_ed1.date_input("Fecha a auditar:", key="fecha_edit")
            emp_edicion = col_ed2.selectbox("Personal a auditar:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_edit")
            
            if emp_edicion != "Seleccionar..." and os.path.exists(ARCHIVO_ASISTENCIA):
                try:
                    df_edicion = pd.read_csv(ARCHIVO_ASISTENCIA)
                    fecha_str = fecha_edicion.strftime("%Y-%m-%d")
                    indices_afectados = df_edicion.index[(df_edicion["Fecha"] == fecha_str) & (df_edicion["Empleado"] == emp_edicion)].tolist()
                    if not indices_afectados: st.warning("Sin movimientos.")
                    else:
                        for idx in indices_afectados:
                            row = df_edicion.loc[idx]
                            with st.container():
                                c1, c2, c3, c4 = st.columns([2,2,2,1])
                                n_tipo = c1.selectbox(f"Tipo", ["Entrada", "Salida", "Ausente"], index=["Entrada", "Salida", "Ausente"].index(row.get('Tipo', 'Entrada')) if row.get('Tipo', 'Entrada') in ["Entrada", "Salida", "Ausente"] else 0, key=f"t_{idx}")
                                n_hora = c2.text_input("Hora (Ej: 08:30 AM)", value=row.get('Hora', ''), key=f"h_{idx}")
                                n_estado = c3.selectbox("Estado", ESTADOS_POSIBLES, index=ESTADOS_POSIBLES.index(row.get('Estado', 'N/A')) if row.get('Estado', 'N/A') in ESTADOS_POSIBLES else 7, key=f"e_{idx}")
                                if c4.button("💾", key=f"btn_{idx}"):
                                    df_edicion.at[idx, 'Tipo'], df_edicion.at[idx, 'Hora'], df_edicion.at[idx, 'Estado'] = n_tipo, n_hora, n_estado
                                    df_edicion.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                    st.rerun()
                except: st.info("Planilla vacía.")

            st.write("---")
            st.subheader("✍️ Carga Manual Total (Falta o Olvido)")
            with st.form("form_fichaje_manual"):
                c_f1, c_f2, c_f3 = st.columns(3)
                fm_emp = c_f1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                fm_fecha = c_f2.date_input("Fecha:", ahora.date())
                
                fm_hora_cruda = c_f3.time_input("Hora exacta:", ahora.time())
                fm_hora_str = fm_hora_cruda.strftime("%I:%M:%S %p")
                
                fm_tipo = c_f1.selectbox("Movimiento:", ["Entrada", "Salida", "Ausente"])
                fm_estado = c_f2.selectbox("Estado final:", ESTADOS_POSIBLES)
                fm_nota = c_f3.text_input("Nota / Justificación:")
                
                if st.form_submit_button("➕ Cargar Movimiento Manual") and fm_emp != "Seleccionar...":
                    df_base = pd.read_csv(ARCHIVO_ASISTENCIA) if os.path.exists(ARCHIVO_ASISTENCIA) else pd.DataFrame(columns=["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m", "Nota"])
                    reg_m = pd.DataFrame({"Fecha": [fm_fecha.strftime("%Y-%m-%d")], "Hora": [fm_hora_str], "Empleado": [fm_emp], "Sucursal": ["Manual"], "Turno": ["Manual"], "Tipo": [fm_tipo], "Estado": [fm_estado], "Distancia_m": [0.0], "Nota": [fm_nota]})
                    pd.concat([df_base, reg_m], ignore_index=True).to_csv(ARCHIVO_ASISTENCIA, index=False)
                    st.rerun()
                    
            st.write("---")
            st.subheader("📥 Exportar Reportes Crudos")
            rango_descarga = st.date_input("Fechas a descargar:", value=(ahora.date(), ahora.date()), key="descarga_csv")
            d_in, d_fi = procesar_rango_fechas(rango_descarga)
            try:
                if os.path.exists(ARCHIVO_ASISTENCIA):
                    df_d = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_d['FT'] = pd.to_datetime(df_d['Fecha'], errors='coerce').dt.date
                    st.download_button("📥 DESCARGAR PLANILLA", df_d[(df_d['FT'] >= d_in) & (df_d['FT'] <= d_fi)].drop(columns=['FT']).to_csv(index=False).encode('utf-8'), f"Asistencia_{d_in}_al_{d_fi}.csv", "text/csv")
            except: st.write("Sin datos de asistencia.")

        # ==========================================
        # TAB 5: STAFF, ROLES Y TAREAS
        # ==========================================
        with tab_staff:
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.subheader("👥 Gestión de Personal")
                with st.form("form_alta_emp"):
                    nuevo_emp = st.text_input("Alta Empleado (Nombre):")
                    rol_asignar = st.selectbox("Rol (Puesto/Cargo):", lista_roles_disponibles)
                    if st.form_submit_button("➕ Agregar Personal") and nuevo_emp:
                        if nuevo_emp not in lista_empleados:
                            lista_empleados.append(nuevo_emp)
                            roles_empleados[nuevo_emp] = rol_asignar
                            tareas_individuales[nuevo_emp] = []
                            save_json(ARCHIVO_EMPLEADOS, lista_empleados)
                            save_json(ARCHIVO_ROLES, roles_empleados)
                            save_json(ARCHIVO_TAREAS_INDIVIDUALES, tareas_individuales)
                            st.rerun()
                
                st.write("---")
                st.write("**Nómina Actual y Modificaciones:**")
                if lista_empleados:
                    emp_mod = st.selectbox("Seleccionar para editar/borrar:", sorted(lista_empleados))
                    rol_actual = roles_empleados.get(emp_mod, lista_roles_disponibles[0])
                    nuevo_rol = st.selectbox("Cambiar Rol a:", lista_roles_disponibles, index=lista_roles_disponibles.index(rol_actual) if rol_actual in lista_roles_disponibles else 0)
                    
                    c_mod1, c_mod2, c_mod3 = st.columns(3)
                    if c_mod1.button("✏️ Guardar Rol"):
                        roles_empleados[emp_mod] = nuevo_rol
                        save_json(ARCHIVO_ROLES, roles_empleados)
                        st.success("Rol actualizado.")
                        st.rerun()
                    if c_mod2.button("📱 Liberar Celular"):
                        if emp_mod in dispositivos_vinculados:
                            del dispositivos_vinculados[emp_mod]
                            save_json(ARCHIVO_DISPOSITIVOS, dispositivos_vinculados)
                            st.rerun()
                    if c_mod3.button("🗑️ Echar / Borrar"):
                        lista_empleados.remove(emp_mod)
                        roles_empleados.pop(emp_mod, None)
                        tareas_individuales.pop(emp_mod, None)
                        dispositivos_vinculados.pop(emp_mod, None)
                        save_json(ARCHIVO_EMPLEADOS, lista_empleados)
                        save_json(ARCHIVO_ROLES, roles_empleados)
                        save_json(ARCHIVO_TAREAS_INDIVIDUALES, tareas_individuales)
                        save_json(ARCHIVO_DISPOSITIVOS, dispositivos_vinculados)
                        st.rerun()

            with col_s2:
                st.subheader("📋 Asignar Tareas (Puntos Extra)")
                tipo_asig = st.radio("Asignar a:", ["Un Rol General", "Una Persona"])
                if tipo_asig == "Un Rol General": obj_tarea = st.selectbox("Elegí el Rol:", lista_roles_disponibles)
                else: obj_tarea = st.selectbox("Elegí al Empleado:", sorted(lista_empleados))
                
                n_tarea = st.text_input("Nombre de la Tarea:")
                p_tarea = st.number_input("Puntos a otorgar:", value=5, min_value=1)
                
                if st.button("➕ Asignar Tarea") and n_tarea:
                    if tipo_asig == "Un Rol General":
                        tareas_roles.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json(ARCHIVO_TAREAS_ROLES, tareas_roles)
                    else:
                        tareas_individuales.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json(ARCHIVO_TAREAS_INDIVIDUALES, tareas_individuales)
                    st.rerun()
                
                st.markdown("**Ver y Borrar Tareas:**")
                ver_t_tipo = st.radio("Ver tareas de:", ["Roles", "Personales"])
                if ver_t_tipo == "Roles":
                    for r, tareas in tareas_roles.items():
                        if tareas:
                            with st.expander(f"Rol: {r}"):
                                for idx, t in enumerate(tareas):
                                    c_t1, c_t2 = st.columns([3,1])
                                    c_t1.write(f"- {t.get('tarea')} (+{t.get('puntos')})")
                                    if c_t2.button("🗑️", key=f"del_tr_{r}_{idx}"):
                                        tareas_roles[r].pop(idx)
                                        save_json(ARCHIVO_TAREAS_ROLES, tareas_roles)
                                        st.rerun()
                else:
                    for emp, tareas in tareas_individuales.items():
                        if tareas and emp in lista_empleados:
                            with st.expander(f"Empleado: {emp}"):
                                for idx, t in enumerate(tareas):
                                    c_t1, c_t2 = st.columns([3,1])
                                    c_t1.write(f"- {t.get('tarea')} (+{t.get('puntos')})")
                                    if c_t2.button("🗑️", key=f"del_ti_{emp}_{idx}"):
                                        tareas_individuales[emp].pop(idx)
                                        save_json(ARCHIVO_TAREAS_INDIVIDUALES, tareas_individuales)
                                        st.rerun()

        # ==========================================
        # TAB 6: TIENDAS Y REDES
        # ==========================================
        with tab_tiendas:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📍 Tiendas, Turnos y Redes</div>', unsafe_allow_html=True)
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("📍 Tiendas Físicas")
                for loc, d_loc in lista_locales.items(): st.write(f"- **{loc}** | IP Configurada: `{d_loc.get('ip', 'Ninguna')}`")
                n_loc = st.text_input("Nueva Tienda:")
                lat_loc = st.number_input("Latitud:", format="%.6f")
                lon_loc = st.number_input("Longitud:", format="%.6f")
                ip_loc = st.text_input("IP de la red Wi-Fi (Opcional):")
                if st.button("➕ Crear Tienda") and n_loc:
                    lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc, "ip": ip_loc.strip()}
                    save_json(ARCHIVO_LOCALES, lista_locales)
                    st.rerun()
                borrar_loc = st.selectbox("Eliminar Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Tienda") and borrar_loc != "Seleccionar...":
                    del lista_locales[borrar_loc]
                    save_json(ARCHIVO_LOCALES, lista_locales)
                    st.rerun()

            with col_l2:
                st.subheader("🕒 Turnos / Horarios (AM/PM)")
                for turno, horas in lista_turnos.items(): st.write(f"- **{turno}** | De {horas.get('ingreso')} a {horas.get('salida')}")
                n_turno = st.text_input("Nuevo Horario (Nombre):")
                col_h1, col_h2 = st.columns(2)
                h_ingreso = col_h1.time_input("Hora de Ingreso:")
                h_salida = col_h2.time_input("Hora de Salida:")
                if st.button("➕ Crear Horario") and n_turno:
                    lista_turnos[n_turno] = {"ingreso": h_ingreso.strftime("%I:%M %p"), "salida": h_salida.strftime("%I:%M %p")}
                    save_json(ARCHIVO_TURNOS, lista_turnos)
                    st.rerun()
                borrar_turno = st.selectbox("Eliminar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno") and borrar_turno != "Seleccionar...":
                    del lista_turnos[borrar_turno]
                    save_json(ARCHIVO_TURNOS, lista_turnos)
                    st.rerun()

            st.markdown("---")
            st.subheader("🛡️ Seguridad Global (Aplica a todas las tiendas)")
            with st.form("form_seguridad"):
                v_gps = st.checkbox("📡 Requerir ubicación GPS", value=config_app.get("verificar_gps", True))
                radio_m = st.number_input("Perímetro permitido en metros (Ej: 50):", min_value=10, max_value=5000, value=int(config_app.get("radio_metros", 50)))
                v_wifi = st.checkbox("📶 Requerir conexión Wi-Fi (Debe coincidir con la IP de la tienda creada arriba)", value=config_app.get("verificar_wifi", False))
                st.caption(f"ℹ️ Si estás en el local ahora mismo, tu IP es: **{client_ip if client_ip else 'Detectando...'}** (Copiá este número al crear la Tienda arriba)")
                
                if st.form_submit_button("💾 Guardar Configuración de Red"):
                    config_app["verificar_gps"] = v_gps
                    config_app["verificar_wifi"] = v_wifi
                    config_app["radio_metros"] = radio_m
                    save_json(ARCHIVO_CONFIG, config_app)
                    st.rerun()

        # ==========================================
        # TAB 7: COMUNICADOS Y ALERTAS
        # ==========================================
        with tab_comunicados:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📢 Comunicados y Alertas</div>', unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                st.subheader("📲 Mensaje Automático al Ingresar")
                with st.form("form_alertas_ingreso"):
                    tipo_dest_ing = st.radio("Destinatario de la alerta:", ["Para todo el Staff", "Para un empleado en particular"])
                    dest_ing = "Todos"
                    if tipo_dest_ing == "Para un empleado en particular": dest_ing = st.selectbox("Seleccionar:", ["Seleccionar..."] + sorted(lista_empleados))
                    txt_alerta = st.text_area("Contenido del mensaje:")
                    if st.form_submit_button("Crear Alerta de Ingreso"):
                        if txt_alerta and dest_ing != "Seleccionar...":
                            alertas_ingreso.append({"destinatario": dest_ing, "texto": txt_alerta})
                            save_json(ARCHIVO_ALERTAS_INGRESO, alertas_ingreso)
                            st.success("¡Alerta creada!")
                            st.rerun()
                
                st.markdown("**Alertas de Ingreso Activas:**")
                for idx, a in enumerate(alertas_ingreso):
                    with st.expander(f"A {a['destinatario']}: {a['texto'][:20]}..."):
                        st.write(a['texto'])
                        if st.button("🗑️ Eliminar Alerta", key=f"del_al_{idx}"):
                            alertas_ingreso.pop(idx)
                            save_json(ARCHIVO_ALERTAS_INGRESO, alertas_ingreso)
                            st.rerun()
            
            with col_m2:
                st.subheader("📌 Mensaje Fijo en el Portal")
                with st.form("form_fijo"):
                    tipo_dest = st.radio("Destinatario del anuncio:", ["Para todo el Staff", "Para un vendedor/a"])
                    destinatario = "Todos"
                    if tipo_dest == "Para un vendedor/a": destinatario = st.selectbox("Seleccionar persona:", ["Seleccionar..."] + sorted(lista_empleados))
                    texto_mensaje = st.text_area("Contenido del anuncio:")
                    if st.form_submit_button("🚀 Publicar Anuncio Fijo"):
                        if texto_mensaje and destinatario != "Seleccionar...":
                            lista_mensajes.append({"destinatario": destinatario, "texto": texto_mensaje})
                            save_json(ARCHIVO_MENSAJES, lista_mensajes)
                            st.success("¡Anuncio publicado!")
                            st.rerun()

                st.markdown("**Anuncios Fijos Activos:**")
                for idx, m in enumerate(lista_mensajes):
                    with st.expander(f"A {m['destinatario']}: {m['texto'][:20]}..."):
                        n_txt = st.text_area("Editar texto:", value=m['texto'], key=f"txt_m_{idx}")
                        c_me1, c_me2 = st.columns(2)
                        if c_me1.button("💾 Guardar Cambio", key=f"save_m_{idx}"):
                            lista_mensajes[idx]['texto'] = n_txt
                            save_json(ARCHIVO_MENSAJES, lista_mensajes)
                            st.rerun()
                        if c_me2.button("🗑️ Eliminar Anuncio", key=f"del_m_{idx}"):
                            lista_mensajes.pop(idx)
                            save_json(ARCHIVO_MENSAJES, lista_mensajes)
                            st.rerun()

        # ==========================================
        # TAB 8: CONFIGURACIÓN GLOBAL
        # ==========================================
        with tab_config:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("🛠️ Administrar Cargos de la Empresa")
                c_r_new, c_r_del = st.columns(2)
                with c_r_new:
                    nuevo_rol_cat = st.text_input("Crear Nuevo Rol:")
                    if st.button("➕ Agregar Rol") and nuevo_rol_cat:
                        if nuevo_rol_cat not in lista_roles_disponibles:
                            lista_roles_disponibles.append(nuevo_rol_cat)
                            save_json(ARCHIVO_LISTA_ROLES, lista_roles_disponibles)
                            st.rerun()
                with c_r_del:
                    borrar_rol_cat = st.selectbox("Eliminar Rol:", ["Seleccionar..."] + lista_roles_disponibles)
                    if st.button("🗑️ Eliminar Rol") and borrar_rol_cat != "Seleccionar...":
                        lista_roles_disponibles.remove(borrar_rol_cat)
                        save_json(ARCHIVO_LISTA_ROLES, lista_roles_disponibles)
                        st.rerun()

                st.markdown("---")
                st.subheader("🏆 Reglas de Asistencia")
                with st.form("form_reglas"):
                    r_base = st.number_input("Puntaje Base del Mes:", value=config_app.get("reglas_puntos", {}).get("base", 100))
                    c_r1, c_r2 = st.columns(2)
                    r_ok = c_r1.number_input("✔️ A Tiempo:", value=config_app.get("reglas_puntos", {}).get("A tiempo", 0))
                    r_tar = c_r2.number_input("⚠️ Tarde:", value=config_app.get("reglas_puntos", {}).get("Tarde", -5))
                    r_aus = c_r1.number_input("❌ Ausente:", value=config_app.get("reglas_puntos", {}).get("Ausente", -15))
                    r_fj = c_r2.number_input("⚕️ Falta Justif:", value=config_app.get("reglas_puntos", {}).get("Falta Justificada", 0))
                    if st.form_submit_button("💾 Guardar Reglas"):
                        config_app["reglas_puntos"] = {"base": r_base, "A tiempo": r_ok, "Tarde": r_tar, "Ausente": r_aus, "Falta Justificada": r_fj}
                        save_json(ARCHIVO_CONFIG, config_app)
                        st.rerun()

            with col_aj2:
                st.subheader("⚙️ Operaciones Generales")
                req_salida = st.checkbox("Requerir botón 'Salida'", value=config_app.get("requiere_salida", True))
                nueva_tolerancia = st.number_input("Minutos tolerancia tardanza:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 10)))
                msg_tarde = st.text_area("Alerta Llegada Tarde:", value=config_app.get("mensaje_llegada_tarde", ""))
                msg_salida_l = st.text_area("Alerta Salida Lejos:", value=config_app.get("mensaje_salida_lejos", ""))
                
                if st.button("💾 Guardar Ajustes Operativos"):
                    config_app["requiere_salida"] = req_salida
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    config_app["mensaje_llegada_tarde"] = msg_tarde
                    config_app["mensaje_salida_lejos"] = msg_salida_l
                    save_json(ARCHIVO_CONFIG, config_app)
                    st.success("Configuración actualizada.")
                    st.rerun()

                st.markdown("---")
                st.write("🔑 **Seguridad Gerencial**")
                nc = st.text_input("Nueva clave de acceso:", type="password")
                rc = st.text_input("Repetir clave:", type="password")
                if st.button("🔒 Cambiar Clave") and nc == rc and nc:
                    config_app["admin_password"] = nc
                    save_json(ARCHIVO_CONFIG, config_app)
                    st.success("Clave modificada.")
                
                st.markdown("---")
                with st.expander("⚠️ Opciones de Base de Datos (Peligro)"):
                    if st.button("🧹 Limpiar historial de ex-empleados"):
                        try:
                            df_m = pd.read_csv(ARCHIVO_ASISTENCIA)
                            df_m[df_m["Empleado"].isin(lista_empleados)].to_csv(ARCHIVO_ASISTENCIA, index=False)
                            st.rerun()
                        except: pass
                    if st.button("🚨 VACIAR TODAS LAS PLANILLAS DE DATOS"):
                        init_csv(ARCHIVO_ASISTENCIA, ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m", "Nota"])
                        init_csv(ARCHIVO_TAREAS_LOG, ["Fecha", "Hora", "Empleado", "Tarea", "Puntos", "Estado"])
                        save_json(ARCHIVO_PUNTOS, [])
                        save_json(ARCHIVO_REPORTES, [])
                        save_json(ARCHIVO_ALERTAS_INGRESO, [])
                        st.success("Bases de datos reiniciadas.")
                        st.rerun()

        # ==========================================
        # TAB 9: SEGURIDAD (MODO ESPÍA) 🕵️
        # ==========================================
        with tab_espia:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🕵️ Registro Espía de Accesos</div>', unsafe_allow_html=True)
            st.write("Acá podés ver quién intentó adivinar la contraseña de Gerencia.")
            if lista_intentos:
                df_int = pd.DataFrame(lista_intentos).sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                st.dataframe(df_int, use_container_width=True, hide_index=True)
                if st.button("🗑️ Limpiar registro espía"):
                    save_json(ARCHIVO_INTENTOS, [])
                    st.rerun()
            else:
                st.info("Nadie intentó ingresar al panel por ahora.")
