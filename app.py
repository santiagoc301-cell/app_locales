import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json
import altair as alt

# Configuración inicial
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
    .highlight-edit { padding: 20px; background-color: #EFF6FF; border-radius: 12px; border-left: 6px solid #3B82F6; margin-bottom: 20px;}
    .credencial { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); margin-bottom: 20px;}
    .cred-nombre { font-size: 1.8rem; font-weight: 800; margin: 0;}
    .cred-rol { font-size: 1.1rem; opacity: 0.9; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;}
    .cred-nivel { font-size: 1.3rem; font-weight: 700; background-color: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; display: inline-block;}
    hr { border-color: #E5E7EB; margin-top: 2rem; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS Y CONFIGURACIÓN
# ==========================================
ARCHIVO_EMPLEADOS = "empleados.json"
ARCHIVO_ROLES = "roles.json"
ARCHIVO_TAREAS = "tareas_roles.json"
ARCHIVO_TAREAS_LOG = "tareas_log.csv"
ARCHIVO_DISPOSITIVOS = "dispositivos.json"
ARCHIVO_LOCALES = "locales.json"
ARCHIVO_TURNOS = "turnos.json"
ARCHIVO_ASISTENCIA = "asistencia.csv"
ARCHIVO_CONFIG = "config.json"
ARCHIVO_MENSAJES = "mensajes.json"
ARCHIVO_INTENTOS = "intentos_seguridad.json"
ARCHIVO_PUNTOS = "ajustes_puntos.json"
RADIO_MAXIMO_METROS = 50

# Parche automático para CSV Asistencia
if os.path.exists(ARCHIVO_ASISTENCIA):
    try:
        df_patch = pd.read_csv(ARCHIVO_ASISTENCIA)
        columnas_req = ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m", "Nota"]
        cambios = False
        for col in columnas_req:
            if col not in df_patch.columns:
                df_patch[col] = "N/A" if col not in ["Distancia_m", "Nota"] else (0.0 if col == "Distancia_m" else "")
                cambios = True
        if cambios: df_patch.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except: pass

# Crear CSV de Tareas si no existe
if not os.path.exists(ARCHIVO_TAREAS_LOG):
    pd.DataFrame(columns=["Fecha", "Hora", "Empleado", "Rol", "Tarea", "Puntos"]).to_csv(ARCHIVO_TAREAS_LOG, index=False)

# Configuración Inicial y Motor de Reglas
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {
        "admin_password": "1234", "tolerancia_minutos": 10, "requiere_salida": True, "habilitar_descansos": False, 
        "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia.",
        "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}
    }
    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f: config_app = json.load(f)
if "reglas_puntos" not in config_app: config_app["reglas_puntos"] = {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15, "Falta Justificada": 0}

# Carga de JSONs
def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f: json.dump(default_data, f)
    with open(file_path, 'r') as f: return json.load(f)

lista_empleados = load_json(ARCHIVO_EMPLEADOS, ["Abril Gonzalez", "Agustina Lopez", "Daniela Perez", "Macarena Silva"])
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

roles_empleados = load_json(ARCHIVO_ROLES, {e: "Vendedor" for e in lista_empleados})
tareas_roles = load_json(ARCHIVO_TAREAS, {"Vendedor": [{"tarea": "Acomodar Vidriera", "puntos": 5}, {"tarea": "Control de Stock Básico", "puntos": 10}], "Cajero": [{"tarea": "Cierre de Caja", "puntos": 15}]})
dispositivos_vinculados = load_json(ARCHIVO_DISPOSITIVOS, {})
lista_locales = load_json(ARCHIVO_LOCALES, {"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}})
lista_turnos_raw = load_json(ARCHIVO_TURNOS, {"Apertura": {"ingreso": "09:00", "salida": "17:00"}})
lista_turnos = {k: {"ingreso": v, "salida": "23:59"} if isinstance(v, str) else v for k, v in lista_turnos_raw.items()}
lista_mensajes = load_json(ARCHIVO_MENSAJES, [])
lista_intentos = load_json(ARCHIVO_INTENTOS, [])
lista_puntos = load_json(ARCHIVO_PUNTOS, [])

# ==========================================
# 2. IDENTIFICADOR DEL CELULAR
# ==========================================
js_get_device = """
(function() {
    let id = localStorage.getItem('tienda_app_device_id');
    if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); }
    return id;
})();
"""
device_id = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")

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
    elif puntos < 100: return "🥉 Nivel Bronce"
    elif puntos < 130: return "🥈 Nivel Plata"
    elif puntos < 160: return "🥇 Nivel Oro"
    elif puntos < 200: return "💎 Nivel Platino"
    else: return "👑 Nivel Leyenda"

zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%H:%M:%S")

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🛍️ Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Portal del Empleado", "⚙️ Panel de Gerencia"])

# ==========================================
# 4. PANTALLA: PORTAL DEL EMPLEADO
# ==========================================
if pestaña == "⏱️ Portal del Empleado":
    st.markdown('<div class="main-title">⏱️ Portal del Equipo</div>', unsafe_allow_html=True)
    
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")

    if not device_id:
        st.info("🔄 Verificando dispositivo...")
    else:
        if empleado_en_celu:
            # --- CALCULAR PUNTOS ACTUALES PARA LA CREDENCIAL ---
            puntos_actuales = config_app["reglas_puntos"]["base"]
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_punt = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_e = df_punt[df_punt["Empleado"] == empleado_en_celu]
                if not df_e.empty:
                    e_tar = len(df_e[df_e["Estado"] == "Tarde"])
                    e_au = len(df_e[df_e["Tipo"] == "Ausente"])
                    puntos_actuales += (e_tar * config_app["reglas_puntos"]["Tarde"]) + (e_au * config_app["reglas_puntos"]["Ausente"])
            
            df_tareas_log = pd.read_csv(ARCHIVO_TAREAS_LOG)
            puntos_actuales += df_tareas_log[df_tareas_log["Empleado"] == empleado_en_celu]["Puntos"].astype(int).sum() if not df_tareas_log.empty else 0
            puntos_actuales += sum([int(p['Puntos']) for p in lista_puntos if p['Empleado'] == empleado_en_celu])
            
            nivel_actual = calcular_nivel(puntos_actuales)
            rol_empleado = roles_empleados.get(empleado_en_celu, "Staff General")

            # --- CREDENCIAL VIRTUAL ---
            st.markdown(f"""
            <div class='credencial'>
                <p class='cred-nombre'>{empleado_en_celu}</p>
                <p class='cred-rol'>Rol: {rol_empleado}</p>
                <div class='cred-nivel'>{nivel_actual} ({puntos_actuales} pts)</div>
            </div>
            """, unsafe_allow_html=True)

            # Mensajes Directos
            mensajes_usuario = [m for m in lista_mensajes if m['destinatario'] in ['Todos', empleado_en_celu]]
            if mensajes_usuario:
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='msg-global'>🏷️ <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='msg-individual'>📩 <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)

            # --- SECCIÓN FICHAJE ---
            with st.expander("📍 Registrar Asistencia de Hoy", expanded=True):
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1: local_seleccionado = st.selectbox("Tienda actual:", ["Seleccionar..."] + list(lista_locales.keys()))
                with col_sel2: turno_seleccionado = st.selectbox("Horario:", ["Seleccionar..."] + list(lista_turnos.keys()))
                nota_empleado = st.text_input("📝 Dejar justificación / novedad (Opcional):")

                if local_seleccionado != "Seleccionar..." and turno_seleccionado != "Seleccionar...":
                    st.info("🛰️ Validando GPS de la tienda...")
                    ubicacion = get_geolocation()

                    if ubicacion:
                        coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                        coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                        distancia = geodesic(coord_usuario, coord_local).meters

                        if distancia <= RADIO_MAXIMO_METROS:
                            ya_ficho_entrada = False
                            if os.path.exists(ARCHIVO_ASISTENCIA):
                                df_temp = pd.read_csv(ARCHIVO_ASISTENCIA)
                                filtro = df_temp[(df_temp["Empleado"] == empleado_en_celu) & (df_temp["Fecha"] == fecha_hoy) & (df_temp["Turno"] == turno_seleccionado) & (df_temp["Tipo"] == "Entrada")]
                                if not filtro.empty: ya_ficho_entrada = True

                            marcar, tipo_fichaje = False, ""

                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada: st.error("⚠️ Ya marcaste el ingreso para este turno.")
                                    else: marcar, tipo_fichaje = True, "Entrada"
                            with col_b2:
                                if config_app.get("requiere_salida", True):
                                    if st.button("🔴 REGISTRAR SALIDA", use_container_width=True): marcar, tipo_fichaje = True, "Salida"

                            if marcar:
                                estado_llegada = "N/A"
                                if tipo_fichaje == "Entrada":
                                    hora_turno_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado]["ingreso"], "%H:%M").time()
                                    dt_turno = datetime.datetime.combine(ahora.date(), hora_turno_obj).replace(tzinfo=zona_arg)
                                    dt_limite = dt_turno + datetime.timedelta(minutes=int(config_app["tolerancia_minutos"]))
                                    estado_llegada = "Tarde" if ahora > dt_limite else "A tiempo"
                                elif tipo_fichaje == "Salida": estado_llegada = "Salida"

                                registro = {"Fecha": [fecha_hoy], "Hora": [hora_hoy], "Empleado": [empleado_en_celu], "Sucursal": [local_seleccionado], "Turno": [turno_seleccionado], "Tipo": [tipo_fichaje], "Estado": [estado_llegada], "Distancia_m": [round(distancia, 1)], "Nota": [nota_empleado]}
                                
                                # Escudo anti-errores al crear o leer el CSV
                                if not os.path.exists(ARCHIVO_ASISTENCIA):
                                    pd.DataFrame(registro).to_csv(ARCHIVO_ASISTENCIA, index=False)
                                else:
                                    pd.concat([pd.read_csv(ARCHIVO_ASISTENCIA), pd.DataFrame(registro)], ignore_index=True).to_csv(ARCHIVO_ASISTENCIA, index=False)

                                if tipo_fichaje == "Entrada" and estado_llegada == "A tiempo": st.success(f"¡Entrada registrada a las {hora_hoy}!")
                                elif estado_llegada == "Tarde": st.error(f"🔴 {config_app.get('mensaje_llegada_tarde')} ({hora_hoy})")
                                else: st.success(f"¡Salida registrada a las {hora_hoy}!")
                                st.rerun() 
                        else: st.error(f"❌ Fuera de rango (Distancia: {distancia:.1f} m).")
                    else: st.warning("⚠️ Esperando GPS...")
                else: st.info("Elegí tienda y turno para fichar.")

            # --- SECCIÓN TAREAS ---
            tareas_del_rol = tareas_roles.get(rol_empleado, [])
            if tareas_del_rol:
                with st.expander("📋 Mis Tareas del Día (Suman Puntos)", expanded=True):
                    df_tareas_log = pd.read_csv(ARCHIVO_TAREAS_LOG)
                    tareas_completadas_hoy = df_tareas_log[(df_tareas_log["Empleado"] == empleado_en_celu) & (df_tareas_log["Fecha"] == fecha_hoy)]["Tarea"].tolist()
                    
                    for t in tareas_del_rol:
                        nombre_tarea = t['tarea']
                        pts = t['puntos']
                        if nombre_tarea in tareas_completadas_hoy:
                            st.markdown(f"<div class='task-box'>✅ <b>{nombre_tarea}</b> (+{pts} pts) completada.</div>", unsafe_allow_html=True)
                        else:
                            c_t1, c_t2 = st.columns([3, 1])
                            c_t1.write(f"🔸 {nombre_tarea} (+{pts} pts)")
                            if c_t2.button("✔️ Completar", key=f"btn_t_{nombre_tarea}"):
                                reg_t = {"Fecha": [fecha_hoy], "Hora": [hora_hoy], "Empleado": [empleado_en_celu], "Rol": [rol_empleado], "Tarea": [nombre_tarea], "Puntos": [pts]}
                                pd.concat([pd.read_csv(ARCHIVO_TAREAS_LOG), pd.DataFrame(reg_t)], ignore_index=True).to_csv(ARCHIVO_TAREAS_LOG, index=False)
                                st.rerun()

            with st.expander("📜 Mi historial reciente"):
                if os.path.exists(ARCHIVO_ASISTENCIA):
                    df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_hist['Fecha_Obj'] = pd.to_datetime(df_hist['Fecha'], errors='coerce').dt.date
                    df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                    if not df_emp.empty: st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                    else: st.write("Sin fichajes recientes.")
                else: st.write("Sin registros.")
        else:
            st.warning("⚠️ **Equipo no autorizado.**")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]
            if empleados_disponibles:
                emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Enlazar mi teléfono"):
                    if emp_vincular != "Seleccionar...":
                        dispositivos_vinculados[emp_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        st.success("¡Teléfono enlazado!")
                        st.rerun()

# ==========================================
# 5. PANTALLA: PANEL DE GERENCIA
# ==========================================
elif pestaña == "⚙️ Panel de Gerencia":
    st.markdown('<div class="main-title">⚙️ Panel de Gerencia Corporativa</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Clave de acceso gerencial:", type="password")
    CLAVE_OCULTA = "doremifasol"

    if password_ingresada and password_ingresada != CLAVE_OCULTA:
        if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
            st.session_state['last_pw_attempt'] = password_ingresada
            quien_intenta = empleado_en_celu if empleado_en_celu else "Desconocido"
            nuevo_intento = {"Fecha": fecha_hoy, "Hora": hora_hoy, "Usuario": quien_intenta, "Clave Probada": password_ingresada, "Resultado": "🟢 Acceso Permitido" if password_ingresada == config_app["admin_password"] else "🔴 Acceso Denegado"}
            lista_intentos.append(nuevo_intento)
            with open(ARCHIVO_INTENTOS, 'w') as f: json.dump(lista_intentos, f)

    if password_ingresada == config_app["admin_password"] or password_ingresada == CLAVE_OCULTA:
        
        tab_analytics, tab_puntos, tab_auditoria, tab_staff_roles, tab_locales, tab_ajustes = st.tabs([
            "📈 Analytics & Alertas", "🏆 Puntos y Tareas", "📊 Auditoría", "👥 Staff y Roles", "📍 Tiendas/Turnos", "⚙️ Configuración"
        ])

        # ==========================================
        # TAB 1: ANALYTICS Y MONITOR EN VIVO
        # ==========================================
        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📈 Monitor en Vivo y Estadísticas</div>', unsafe_allow_html=True)
            
            # --- ESCUDO ANTI-ERROR DE LECTURA ---
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_stats = pd.read_csv(ARCHIVO_ASISTENCIA)
                
                if df_stats.empty:
                    st.info("La planilla está vacía. Esperá a que los empleados comiencen a fichar para ver los datos.")
                else:
                    df_activos = df_stats[df_stats["Empleado"].isin(lista_empleados)].copy()
                    df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                    
                    # --- MONITOR DIARIO ---
                    st.markdown(f"### 🚨 Tablero de Control de Hoy ({fecha_hoy})")
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
                    # --- ESTADÍSTICAS HISTÓRICAS ---
                    rango_stats = st.date_input("🗓️ Periodo de análisis histórico:", value=(ahora.date() - datetime.timedelta(days=30), ahora.date()))
                    s_inicio, s_fin = procesar_rango_fechas(rango_stats)
                    df_periodo = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_inicio) & (df_activos['Fecha_Obj'].dt.date <= s_fin)]
                    
                    if not df_periodo.empty:
                        entradas = df_periodo[df_periodo["Tipo"] == "Entrada"]
                        ausencias_tot = len(df_periodo[df_periodo["Tipo"] == "Ausente"])
                        atiempo = len(entradas[entradas["Estado"] == "A tiempo"])
                        tardes = len(entradas[entradas["Estado"] == "Tarde"])
                        tot_ingresos = len(entradas)

                        punt_grupal = round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("🎯 Puntualidad Empresa", f"{punt_grupal}%")
                        c2.metric("✅ Llegadas a Tiempo", atiempo)
                        c3.metric("⚠️ Llegadas Tarde", tardes)
                        c4.metric("❌ Inasistencias Periodo", ausencias_tot)
                        
                        # Gráficos
                        graf_col1, graf_col2 = st.columns([2, 1])
                        with graf_col1:
                            st.markdown("**Evolución Diaria de Asistencia**")
                            df_tendencia = entradas.groupby('Fecha').size().reset_index(name='Ingresos')
                            if not df_tendencia.empty:
                                st.altair_chart(alt.Chart(df_tendencia).mark_line(point=True, color="#2563EB", strokeWidth=4).encode(x='Fecha:T', y='Ingresos:Q', tooltip=['Fecha', 'Ingresos']).properties(height=300), use_container_width=True)
                        with graf_col2:
                            st.markdown("**Distribución**")
                            est_df = pd.DataFrame([{"Estado": "A tiempo", "V": atiempo}, {"Estado": "Tarde", "V": tardes}, {"Estado": "Ausencias", "V": ausencias_tot}])
                            st.altair_chart(alt.Chart(est_df).mark_arc(innerRadius=60).encode(theta="V:Q", color=alt.Color("Estado:N", scale=alt.Scale(domain=['A tiempo', 'Tarde', 'Ausencias'], range=['#10b981', '#f59e0b', '#ef4444'])), tooltip=['Estado', 'V']).properties(height=300), use_container_width=True)
                    else: st.warning("No hay registros en el periodo seleccionado.")
            else:
                st.info("Todavía no hay datos de asistencia para analizar.")

        # ==========================================
        # TAB 2: PUNTUACIÓN Y TAREAS
        # ==========================================
        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Gamificación y Puntuación Integral</div>', unsafe_allow_html=True)
            
            rango_punt = st.date_input("🗓️ Periodo de Puntuación:", value=(ahora.date(), ahora.date()), key="cal_punt")
            p_inicio, p_fin = procesar_rango_fechas(rango_punt)
            
            if os.path.exists(ARCHIVO_ASISTENCIA) and not pd.read_csv(ARCHIVO_ASISTENCIA).empty:
                df_punt = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_punt['Fecha_Obj'] = pd.to_datetime(df_punt['Fecha'], errors='coerce')
                df_punt_per = df_punt[(df_punt['Fecha_Obj'].dt.date >= p_inicio) & (df_punt['Fecha_Obj'].dt.date <= p_fin)]
                
                df_tareas_log = pd.read_csv(ARCHIVO_TAREAS_LOG)
                df_tareas_log['Fecha_Obj'] = pd.to_datetime(df_tareas_log['Fecha'], errors='coerce')
                df_tareas_per = df_tareas_log[(df_tareas_log['Fecha_Obj'].dt.date >= p_inicio) & (df_tareas_log['Fecha_Obj'].dt.date <= p_fin)]
                
                reglas = config_app["reglas_puntos"]
                ajustes_periodo = [p for p in lista_puntos if p_inicio <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= p_fin]

                st.caption(f"Reglas: Base {reglas['base']} pts | A tiempo: {reglas['A tiempo']} pts | Tarde: {reglas['Tarde']} pts | Ausente: {reglas['Ausente']} pts | + Tareas")
                
                ranking_data = []
                for emp in lista_empleados:
                    e_ajustes = sum([int(p['Puntos']) for p in ajustes_periodo if p['Empleado'] == emp])
                    e_tareas_pts = df_tareas_per[df_tareas_per["Empleado"] == emp]["Puntos"].astype(int).sum() if not df_tareas_per.empty else 0
                    
                    df_e = df_punt_per[df_punt_per["Empleado"] == emp]
                    e_ok = len(df_e[df_e["Estado"] == "A tiempo"]) if not df_e.empty else 0
                    e_tar = len(df_e[df_e["Estado"] == "Tarde"]) if not df_e.empty else 0
                    e_au = len(df_e[df_e["Tipo"] == "Ausente"]) if not df_e.empty else 0
                    
                    puntaje = reglas['base'] + (e_ok * reglas['A tiempo']) + (e_tar * reglas['Tarde']) + (e_au * reglas['Ausente']) + e_ajustes + e_tareas_pts
                    
                    ranking_data.append({"Personal": emp, "Rol": roles_empleados.get(emp, "Sin Rol"), "Nivel": calcular_nivel(puntaje), "⭐ TOTAL PTS": puntaje, "📋 Pts Tareas": e_tareas_pts, "⚙️ Ajustes": e_ajustes, "✅ A Tiempo": e_ok, "⚠️ Tardes": e_tar, "❌ Faltas": e_au})
                        
                if ranking_data:
                    df_ranking = pd.DataFrame(ranking_data).sort_values(by="⭐ TOTAL PTS", ascending=False)
                    st.dataframe(df_ranking, use_container_width=True, hide_index=True)
                    st.download_button("📥 Exportar Ranking", df_ranking.to_csv(index=False).encode('utf-8'), f"Ranking_{p_inicio}_al_{p_fin}.csv", "text/csv")
            else:
                st.info("No hay datos suficientes para armar un ranking.")
                
            st.markdown("---")
            st.subheader("✍️ Cargar Bono o Multa Manual")
            with st.form("form_bonos"):
                c_b1, c_b2, c_b3, c_b4 = st.columns([2,1,1,2])
                ap_emp = c_b1.selectbox("Vendedor/a:", ["Seleccionar..."] + sorted(lista_empleados))
                ap_fecha = c_b2.date_input("Fecha:", ahora.date())
                ap_puntos = c_b3.number_input("Puntos (+/-):", value=0, step=1)
                ap_motivo = c_b4.text_input("Motivo:")
                if st.form_submit_button("Guardar Ajuste"):
                    if ap_emp != "Seleccionar..." and ap_puntos != 0 and ap_motivo:
                        lista_puntos.append({"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo})
                        with open(ARCHIVO_PUNTOS, 'w') as f: json.dump(lista_puntos, f)
                        st.success("Ajuste guardado.")
                        st.rerun()

        # ==========================================
        # TAB 3: AUDITORÍA Y EDICIÓN
        # ==========================================
        with tab_auditoria:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📊 Auditoría y Edición</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="highlight-edit"><b>✏️ CORREGIR HORARIOS Y JUSTIFICAR</b></div>', unsafe_allow_html=True)
            col_ed1, col_ed2 = st.columns(2)
            fecha_edicion = col_ed1.date_input("Fecha a auditar:", key="fecha_edit")
            emp_edicion = col_ed2.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_edit")
            
            if emp_edicion != "Seleccionar...":
                if os.path.exists(ARCHIVO_ASISTENCIA) and not pd.read_csv(ARCHIVO_ASISTENCIA).empty:
                    df_edicion = pd.read_csv(ARCHIVO_ASISTENCIA)
                    fecha_str = fecha_edicion.strftime("%Y-%m-%d")
                    indices_afectados = df_edicion.index[(df_edicion["Fecha"] == fecha_str) & (df_edicion["Empleado"] == emp_edicion)].tolist()
                    if not indices_afectados: st.warning("Sin movimientos.")
                    else:
                        for idx in indices_afectados:
                            row = df_edicion.loc[idx]
                            with st.container():
                                c1, c2, c3, c4 = st.columns([2,2,2,1])
                                nuevo_tipo = c1.selectbox(f"Tipo", ["Entrada", "Salida", "Inicio Descanso", "Fin Descanso", "Ausente"], index=["Entrada", "Salida", "Inicio Descanso", "Fin Descanso", "Ausente"].index(row.get('Tipo', 'Entrada')) if row.get('Tipo', 'Entrada') in ["Entrada", "Salida", "Inicio Descanso", "Fin Descanso", "Ausente"] else 0, key=f"t_{idx}")
                                nueva_hora = c2.text_input("Hora", value=row.get('Hora', ''), key=f"h_{idx}")
                                estados_list = ["A tiempo", "Tarde", "Salida", "Ausente", "Falta Justificada", "N/A"]
                                nuevo_estado = c3.selectbox("Estado", estados_list, index=estados_list.index(row.get('Estado', 'N/A')) if row.get('Estado', 'N/A') in estados_list else 5, key=f"e_{idx}")
                                if c4.button("💾", key=f"btn_{idx}"):
                                    df_edicion.at[idx, 'Tipo'] = nuevo_tipo
                                    df_edicion.at[idx, 'Hora'] = nueva_hora
                                    df_edicion.at[idx, 'Estado'] = nuevo_estado
                                    df_edicion.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                    st.rerun()
                else: st.info("Planilla de asistencia vacía.")

            st.write("---")
            st.subheader("📥 Exportar Bases de Datos")
            rango_descarga = st.date_input("Fechas a descargar:", value=(ahora.date(), ahora.date()), key="descarga_csv")
            d_in, d_fi = procesar_rango_fechas(rango_descarga)
            if os.path.exists(ARCHIVO_ASISTENCIA) and not pd.read_csv(ARCHIVO_ASISTENCIA).empty:
                df_d = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_d['FT'] = pd.to_datetime(df_d['Fecha'], errors='coerce').dt.date
                df_export = df_d[(df_d['FT'] >= d_in) & (df_d['FT'] <= d_fi)].drop(columns=['FT'])
                st.download_button("📥 DESCARGAR PLANILLA DE ASISTENCIA", df_export.to_csv(index=False).encode('utf-8'), f"Asistencia_{d_in}_al_{d_fi}.csv", "text/csv")
            
            if os.path.exists(ARCHIVO_TAREAS_LOG) and not pd.read_csv(ARCHIVO_TAREAS_LOG).empty:
                df_tl = pd.read_csv(ARCHIVO_TAREAS_LOG)
                df_tl['FT'] = pd.to_datetime(df_tl['Fecha'], errors='coerce').dt.date
                df_ex_t = df_tl[(df_tl['FT'] >= d_in) & (df_tl['FT'] <= d_fi)].drop(columns=['FT'])
                st.download_button("📥 DESCARGAR LOG DE TAREAS", df_ex_t.to_csv(index=False).encode('utf-8'), f"Tareas_{d_in}_al_{d_fi}.csv", "text/csv")

        # ==========================================
        # TAB 4: STAFF Y ROLES
        # ==========================================
        with tab_staff_roles:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader("👥 Gestión de Personal y Roles")
                nuevo_emp = st.text_input("Alta Empleado (Nombre):")
                rol_asignar = st.selectbox("Rol inicial:", ["Vendedor", "Cajero", "Encargado", "Depósito", "Otro"])
                if st.button("➕ Agregar Personal") and nuevo_emp:
                    if nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp)
                        roles_empleados[nuevo_emp] = rol_asignar
                        with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                        with open(ARCHIVO_ROLES, 'w') as f: json.dump(roles_empleados, f)
                        st.rerun()
                
                st.write("**Nómina Actual:**")
                for emp in sorted(lista_empleados):
                    rol_e = roles_empleados.get(emp, "Sin Rol")
                    st.write(f"- **{emp}** | Rol: `{rol_e}` | {'📱 OK' if emp in dispositivos_vinculados else '⚠️ Sin Celular'}")

            with col_s2:
                st.subheader("📋 Tareas Asignadas por Rol")
                st.write("Definí qué tareas deben hacer y cuántos puntos ganan por hacerlas.")
                rol_tarea = st.selectbox("Seleccionar Rol para agregar tarea:", ["Vendedor", "Cajero", "Encargado", "Depósito", "Otro"])
                n_tarea = st.text_input("Nombre de la Tarea (Ej: Limpiar Mostrador):")
                p_tarea = st.number_input("Puntos a otorgar:", value=5, min_value=1)
                
                if st.button("➕ Agregar Tarea al Rol"):
                    if rol_tarea not in tareas_roles: tareas_roles[rol_tarea] = []
                    tareas_roles[rol_tarea].append({"tarea": n_tarea, "puntos": p_tarea})
                    with open(ARCHIVO_TAREAS, 'w') as f: json.dump(tareas_roles, f)
                    st.success("Tarea agregada.")
                    st.rerun()
                    
                st.write("**Tareas por Rol Actuales:**")
                for r, tareas in tareas_roles.items():
                    if tareas:
                        with st.expander(f"Tareas de {r}"):
                            for idx, t in enumerate(tareas):
                                c_t1, c_t2 = st.columns([3,1])
                                c_t1.write(f"- {t['tarea']} (+{t['puntos']} pts)")
                                if c_t2.button("🗑️", key=f"del_t_{r}_{idx}"):
                                    tareas_roles[r].pop(idx)
                                    with open(ARCHIVO_TAREAS, 'w') as f: json.dump(tareas_roles, f)
                                    st.rerun()

        # ==========================================
        # TAB 5: LOCALES Y TURNOS
        # ==========================================
        with tab_locales:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("📍 Tiendas")
                for loc in lista_locales.keys(): st.write(f"- **{loc}**")
                n_loc = st.text_input("Nueva Tienda:")
                lat_loc = st.number_input("Latitud:", format="%.6f")
                lon_loc = st.number_input("Longitud:", format="%.6f")
                if st.button("➕ Crear Tienda") and n_loc:
                    lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc}
                    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(lista_locales, f)
                    st.rerun()
                borrar_loc = st.selectbox("Eliminar Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Tienda") and borrar_loc != "Seleccionar...":
                    del lista_locales[borrar_loc]
                    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(lista_locales, f)
                    st.rerun()

            with col_l2:
                st.subheader("🕒 Turnos / Horarios")
                for turno, horas in lista_turnos.items(): st.write(f"- **{turno}** | De {horas['ingreso']} a {horas['salida']}")
                n_turno = st.text_input("Nuevo Horario (Nombre):")
                col_h1, col_h2 = st.columns(2)
                h_ingreso = col_h1.time_input("Hora de Ingreso:")
                h_salida = col_h2.time_input("Hora de Salida:")
                if st.button("➕ Crear Horario") and n_turno:
                    lista_turnos[n_turno] = {"ingreso": h_ingreso.strftime("%H:%M"), "salida": h_salida.strftime("%H:%M")}
                    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                    st.rerun()
                borrar_turno = st.selectbox("Eliminar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno") and borrar_turno != "Seleccionar...":
                    del lista_turnos[borrar_turno]
                    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                    st.rerun()

        # ==========================================
        # TAB 6: AJUSTES Y MOTOR DE REGLAS
        # ==========================================
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("🏆 Motor de Reglas de Asistencia")
                with st.form("form_reglas"):
                    r_base = st.number_input("Puntaje Base:", value=config_app["reglas_puntos"].get("base", 100))
                    c_r1, c_r2 = st.columns(2)
                    r_ok = c_r1.number_input("✔️ A Tiempo:", value=config_app["reglas_puntos"].get("A tiempo", 0))
                    r_tar = c_r2.number_input("⚠️ Tarde:", value=config_app["reglas_puntos"].get("Tarde", -5))
                    r_aus = c_r1.number_input("❌ Ausente:", value=config_app["reglas_puntos"].get("Ausente", -15))
                    r_fj = c_r2.number_input("⚕️ Falta Justif:", value=config_app["reglas_puntos"].get("Falta Justificada", 0))
                    if st.form_submit_button("💾 Guardar Reglas"):
                        config_app["reglas_puntos"] = {"base": r_base, "A tiempo": r_ok, "Tarde": r_tar, "Ausente": r_aus, "Falta Justificada": r_fj}
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.rerun()
                
                st.markdown("---")
                nuevo_mensaje = st.text_area("📢 Comunicado Corporativo (Global):", value=config_app.get("mensaje_dia", ""))
                req_salida = st.checkbox("Requerir botón 'Salida'", value=config_app.get("requiere_salida", True))
                nueva_tolerancia = st.number_input("Minutos de tolerancia de llegada tarde:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 10)))
                if st.button("💾 Guardar Configuración Operativa"):
                    config_app["mensaje_dia"] = nuevo_mensaje
                    config_app["requiere_salida"] = req_salida
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                    st.success("Configuración actualizada.")
                    st.rerun()

            with col_aj2:
                st.subheader("🔑 Seguridad Gerencial")
                nc = st.text_input("Nueva clave de acceso:", type="password")
                rc = st.text_input("Repetir clave:", type="password")
                if st.button("🔒 Cambiar Clave Principal"):
                    if nc == rc and nc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.success("Clave principal modificada.")
                    else: st.error("Las claves no coinciden.")
                
                st.markdown("---")
                st.write("🕵️ **Registro de Seguridad (Intentos de Acceso)**")
                if lista_intentos:
                    df_intentos = pd.DataFrame(lista_intentos).sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                    st.dataframe(df_intentos.head(10), use_container_width=True, hide_index=True)
                    if st.button("Limpiar historial de seguridad"):
                        with open(ARCHIVO_INTENTOS, 'w') as f: json.dump([], f)
                        st.rerun()
                
                st.markdown("---")
                with st.expander("⚠️ Opciones de Base de Datos (Peligro)"):
                    if st.button("🧹 Limpiar historial de ex-empleados"):
                        if os.path.exists(ARCHIVO_ASISTENCIA) and not pd.read_csv(ARCHIVO_ASISTENCIA).empty:
                            df_m = pd.read_csv(ARCHIVO_ASISTENCIA)
                            df_m[df_m["Empleado"].isin(lista_empleados)].to_csv(ARCHIVO_ASISTENCIA, index=False)
                            st.rerun()
                    if st.button("🚨 VACIAR TODA LA PLANILLA DE ASISTENCIA"):
                        if os.path.exists(ARCHIVO_ASISTENCIA): os.remove(ARCHIVO_ASISTENCIA)
                        if os.path.exists(ARCHIVO_TAREAS_LOG): os.remove(ARCHIVO_TAREAS_LOG)
                        st.rerun()
