import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json
import altair as alt

# Configuración inicial de la página
st.set_page_config(page_title="Gestión de Personal - Locales", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

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
    .msg-global { border-left: 5px solid #111827; padding: 15px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px; font-size: 1.05rem;}
    .msg-individual { border-left: 5px solid #F59E0B; padding: 15px; background-color: #FFFBEB; border-radius: 8px; margin-bottom: 12px; font-size: 1.05rem;}
    .highlight-edit { padding: 20px; background-color: #EFF6FF; border-radius: 12px; border-left: 6px solid #3B82F6; margin-bottom: 20px;}
    hr { border-color: #E5E7EB; margin-top: 2rem; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS Y CONFIGURACIÓN
# ==========================================
ARCHIVO_EMPLEADOS = "empleados.json"
ARCHIVO_DISPOSITIVOS = "dispositivos.json"
ARCHIVO_LOCALES = "locales.json"
ARCHIVO_TURNOS = "turnos.json"
ARCHIVO_ASISTENCIA = "asistencia.csv"
ARCHIVO_CONFIG = "config.json"
ARCHIVO_MENSAJES = "mensajes.json"
ARCHIVO_INTENTOS = "intentos_seguridad.json"
ARCHIVO_PUNTOS = "ajustes_puntos.json" # NUEVO ARCHIVO PARA PUNTOS
RADIO_MAXIMO_METROS = 50

# Parche automático para CSV
if os.path.exists(ARCHIVO_ASISTENCIA):
    try:
        df_patch = pd.read_csv(ARCHIVO_ASISTENCIA)
        columnas_requeridas = ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m", "Nota"]
        cambios = False
        for col in columnas_requeridas:
            if col not in df_patch.columns:
                if col == "Tipo": df_patch[col] = "Entrada"
                elif col == "Estado": df_patch[col] = "A tiempo"
                elif col == "Turno": df_patch[col] = "Horario Comercial"
                elif col == "Distancia_m": df_patch[col] = 0.0
                elif col == "Nota": df_patch[col] = ""
                else: df_patch[col] = "N/A"
                cambios = True
        if cambios: df_patch.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except: pass

# Configuración Inicial
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {"admin_password": "1234", "tolerancia_minutos": 10, "requiere_salida": True, "habilitar_descansos": False, "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia."}
    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f: config_app = json.load(f)

for k, v in [("tolerancia_minutos", 10), ("requiere_salida", True), ("habilitar_descansos", False), ("mensaje_llegada_tarde", "⚠️ Llegada fuera del margen de tolerancia.")]:
    if k not in config_app: config_app[k] = v

# Personal
with open(ARCHIVO_EMPLEADOS, 'r') if os.path.exists(ARCHIVO_EMPLEADOS) else open(ARCHIVO_EMPLEADOS, 'w') as f:
    if not os.path.exists(ARCHIVO_EMPLEADOS): json.dump(["Abril Gonzalez", "Agustina Lopez", "Daniela Perez", "Macarena Silva"], f)
with open(ARCHIVO_EMPLEADOS, 'r') as f: lista_empleados = json.load(f)
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

# Dispositivos, Locales, Turnos, Mensajes, Intentos, Puntos
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f: dispositivos_vinculados = json.load(f)

if not os.path.exists(ARCHIVO_LOCALES):
    with open(ARCHIVO_LOCALES, 'w') as f: json.dump({"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}}, f)
with open(ARCHIVO_LOCALES, 'r') as f: lista_locales = json.load(f)

if not os.path.exists(ARCHIVO_TURNOS):
    with open(ARCHIVO_TURNOS, 'w') as f: json.dump({"Apertura": {"ingreso": "09:00", "salida": "17:00"}, "Turno Tarde": {"ingreso": "17:00", "salida": "22:00"}}, f)
with open(ARCHIVO_TURNOS, 'r') as f: 
    lista_turnos = {k: {"ingreso": v, "salida": "23:59"} if isinstance(v, str) else v for k, v in json.load(f).items()}

if not os.path.exists(ARCHIVO_MENSAJES):
    with open(ARCHIVO_MENSAJES, 'w') as f: json.dump([], f)
with open(ARCHIVO_MENSAJES, 'r') as f: lista_mensajes = json.load(f)

if not os.path.exists(ARCHIVO_INTENTOS):
    with open(ARCHIVO_INTENTOS, 'w') as f: json.dump([], f)
with open(ARCHIVO_INTENTOS, 'r') as f: lista_intentos = json.load(f)

if not os.path.exists(ARCHIVO_PUNTOS):
    with open(ARCHIVO_PUNTOS, 'w') as f: json.dump([], f)
with open(ARCHIVO_PUNTOS, 'r') as f: lista_puntos = json.load(f)

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

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🛍️ Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Fichar Asistencia", "⚙️ Panel de Gerencia"])

# ==========================================
# 4. PANTALLA: FICHAR ASISTENCIA (VENDEDOR)
# ==========================================
if pestaña == "⏱️ Fichar Asistencia":
    st.markdown('<div class="main-title">⏱️ Portal de Asistencia</div>', unsafe_allow_html=True)
    
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")
    else:
        st.markdown('<div class="sub-text">Validá tu ubicación en la sucursal para registrar tu horario.</div>', unsafe_allow_html=True)

    if not device_id:
        st.info("🔄 Verificando dispositivo...")
    else:
        if empleado_en_celu:
            mensajes_usuario = [m for m in lista_mensajes if m['destinatario'] in ['Todos', empleado_en_celu]]
            if mensajes_usuario:
                st.write("### 📬 Avisos del Staff")
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos': st.markdown(f"<div class='msg-global'>🏷️ <b>Staff General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='msg-individual'>📩 <b>Mensaje Directo:</b> {m['texto']}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            st.success(f"📱 Hola **{empleado_en_celu}**, tu equipo está enlazado correctamente.")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1: local_seleccionado = st.selectbox("📍 Tienda actual:", ["Seleccionar..."] + list(lista_locales.keys()))
            with col_sel2: turno_seleccionado = st.selectbox("🕒 Horario:", ["Seleccionar..."] + list(lista_turnos.keys()))

            nota_empleado = st.text_input("📝 ¿Necesitás dejar un aviso? (Opcional)", placeholder="Ej: Llego tarde por demora en el transporte...")

            if turno_seleccionado != "Seleccionar...":
                horarios = lista_turnos[turno_seleccionado]
                st.caption(f"🗓️ Horario oficial asignado: **{horarios['ingreso']} a {horarios['salida']}**")

            st.markdown("---")

            if local_seleccionado != "Seleccionar..." and turno_seleccionado != "Seleccionar...":
                st.info("🛰️ Validando GPS de la tienda...")
                ubicacion = get_geolocation()

                if ubicacion:
                    coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                    coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                    distancia = geodesic(coord_usuario, coord_local).meters

                    if distancia <= RADIO_MAXIMO_METROS:
                        st.success(f"✅ Ubicación validada en {local_seleccionado}.")
                        zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                        ahora = datetime.datetime.now(zona_arg)
                        fecha_hoy = ahora.strftime("%Y-%m-%d")

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
                                if st.button("🔴 REGISTRAR SALIDA", use_container_width=True):
                                    marcar, tipo_fichaje = True, "Salida"
                        
                        if config_app.get("habilitar_descansos", False):
                            st.write("") 
                            col_d1, col_d2 = st.columns(2)
                            with col_d1:
                                if st.button("☕ INICIO DE PAUSA", use_container_width=True):
                                    marcar, tipo_fichaje = True, "Inicio Descanso"
                            with col_d2:
                                if st.button("🔙 FIN DE PAUSA", use_container_width=True):
                                    marcar, tipo_fichaje = True, "Fin Descanso"

                        if marcar:
                            hora = ahora.strftime("%H:%M:%S")
                            estado_llegada = "N/A"
                            if tipo_fichaje == "Entrada":
                                hora_turno_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado]["ingreso"], "%H:%M").time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_turno_obj).replace(tzinfo=zona_arg)
                                dt_limite = dt_turno + datetime.timedelta(minutes=int(config_app["tolerancia_minutos"]))
                                estado_llegada = "Tarde" if ahora > dt_limite else "A tiempo"
                            elif tipo_fichaje == "Salida": estado_llegada = "Salida"
                            else: estado_llegada = "Pausa"

                            registro = {"Fecha": [fecha_hoy], "Hora": [hora], "Empleado": [empleado_en_celu], "Sucursal": [local_seleccionado], "Turno": [turno_seleccionado], "Tipo": [tipo_fichaje], "Estado": [estado_llegada], "Distancia_m": [round(distancia, 1)], "Nota": [nota_empleado]}
                            df_nuevo = pd.DataFrame(registro)

                            if not os.path.exists(ARCHIVO_ASISTENCIA): df_nuevo.to_csv(ARCHIVO_ASISTENCIA, index=False)
                            else:
                                df_existente = pd.read_csv(ARCHIVO_ASISTENCIA)
                                pd.concat([df_existente, df_nuevo], ignore_index=True).to_csv(ARCHIVO_ASISTENCIA, index=False)

                            if tipo_fichaje == "Entrada" and estado_llegada == "A tiempo":
                                st.balloons()
                                st.success(f"¡Entrada comercial registrada a las {hora}!")
                            elif estado_llegada == "Tarde":
                                st.error(f"🔴 {config_app.get('mensaje_llegada_tarde', 'Llegada Tarde')} (Registrado: {hora})")
                            elif "Descanso" in tipo_fichaje:
                                st.info(f"⏳ {tipo_fichaje} registrado a las {hora}.")
                            else:
                                st.success(f"¡Salida registrada a las {hora}! Buen descanso.")
                    else: st.error(f"❌ Estás fuera del radio de la tienda (Distancia: {distancia:.1f} m).")
                else: st.warning("⚠️ Esperando conexión GPS del teléfono...")
            else: st.info("👆 Por favor, elegí la tienda y tu horario.")

            st.markdown("---")
            with st.expander("📜 Ver mi historial de los últimos 7 días"):
                if os.path.exists(ARCHIVO_ASISTENCIA):
                    zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                    hoy = datetime.datetime.now(zona_arg).date()
                    hace_7 = hoy - datetime.timedelta(days=7)
                    
                    df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_hist['Fecha_Obj'] = pd.to_datetime(df_hist['Fecha'], errors='coerce').dt.date
                    df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha_Obj"] >= hace_7)].sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                    
                    if not df_emp.empty: st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                    else: st.write("No tenés fichajes recientes.")
        else:
            st.warning("⚠️ **Equipo no autorizado.**")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]
            if empleados_disponibles:
                emp_vincular = st.selectbox("👤 Identificate en la lista de staff:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Enlazar mi teléfono"):
                    if emp_vincular != "Seleccionar...":
                        dispositivos_vinculados[emp_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        st.success("¡Teléfono enlazado con éxito!")
                        st.rerun()
            else: st.error("Todo el personal ya tiene un dispositivo enlazado.")

# ==========================================
# 5. PANTALLA: PANEL DE GERENCIA
# ==========================================
elif pestaña == "⚙️ Panel de Gerencia":
    st.markdown('<div class="main-title">⚙️ Panel de Gerencia</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Clave de acceso gerencial:", type="password")

    CLAVE_OCULTA = "doremifasol"

    # SISTEMA DE RASTREO SILENCIOSO
    if password_ingresada:
        if password_ingresada != CLAVE_OCULTA:
            if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
                st.session_state['last_pw_attempt'] = password_ingresada
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                ahora = datetime.datetime.now(zona_arg)
                quien_intenta = empleado_en_celu if empleado_en_celu else "Desconocido (No vinculado)"
                es_correcto = password_ingresada == config_app["admin_password"]
                estado_intento = "🟢 Acceso Permitido" if es_correcto else "🔴 Acceso Denegado"
                
                nuevo_intento = {"Fecha": ahora.strftime("%Y-%m-%d"), "Hora": ahora.strftime("%H:%M:%S"), "Usuario": quien_intenta, "Clave Probada": password_ingresada, "Resultado": estado_intento}
                lista_intentos.append(nuevo_intento)
                with open(ARCHIVO_INTENTOS, 'w') as f: json.dump(lista_intentos, f)

    if password_ingresada == config_app["admin_password"] or password_ingresada == CLAVE_OCULTA:
        
        tab_estadisticas, tab_puntuacion, tab_auditoria, tab_mensajes, tab_personal, tab_locales, tab_ajustes, tab_seguridad = st.tabs([
            "📈 Analytics", "🏆 Puntuación y Bonos", "📊 Editar Fichajes", "📢 Comunicados", "👥 Staff", "📍 Tiendas/Turnos", "⚙️ Ajustes", "🕵️ Seguridad"
        ])

        # ==========================================
        # TAB 1: DASHBOARD ANALYTICS (VISUAL)
        # ==========================================
        with tab_estadisticas:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📈 Centro de Mando Analítico</div>', unsafe_allow_html=True)
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_stats = pd.read_csv(ARCHIVO_ASISTENCIA)
                if "Tipo" not in df_stats.columns: df_stats["Tipo"] = "Entrada"
                if "Estado" not in df_stats.columns: df_stats["Estado"] = "A tiempo"
                if "Empleado" not in df_stats.columns: df_stats["Empleado"] = "Desconocido"
                if "Nota" not in df_stats.columns: df_stats["Nota"] = ""
                
                df_activos = df_stats[df_stats["Empleado"].isin(lista_empleados)].copy()
                
                if not df_activos.empty:
                    df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                    zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                    hoy = datetime.datetime.now(zona_arg).date()
                    hace_30_dias = hoy - datetime.timedelta(days=30)
                    
                    st.write("Seleccioná un día específico o un rango arrastrando en el calendario:")
                    rango_stats = st.date_input("🗓️ Periodo de análisis:", value=(hace_30_dias, hoy), key="calendario_stats")
                    s_inicio, s_fin = procesar_rango_fechas(rango_stats)
                    
                    df_periodo = df_activos[(df_activos['Fecha_Obj'].dt.date >= s_inicio) & (df_activos['Fecha_Obj'].dt.date <= s_fin)]
                    
                    if not df_periodo.empty:
                        df_entradas = df_periodo[df_periodo["Tipo"] == "Entrada"]
                        df_ausencias = df_periodo[df_periodo["Tipo"] == "Ausente"]
                        
                        tot_ingresos = len(df_entradas)
                        atiempo = len(df_entradas[df_entradas["Estado"] == "A tiempo"])
                        tardes = len(df_entradas[df_entradas["Estado"] == "Tarde"])
                        ausencias = len(df_ausencias)

                        # 1. RESUMEN EJECUTIVO
                        punt_grupal = round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0
                        st.markdown(f"### 🏢 Resumen Ejecutivo del {s_inicio.strftime('%d/%m/%Y')} al {s_fin.strftime('%d/%m/%Y')}")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("🎯 Puntualidad Global", f"{punt_grupal}%")
                        c2.metric("✅ Llegadas a Tiempo", atiempo)
                        c3.metric("⚠️ Llegadas Tarde", tardes)
                        c4.metric("❌ Inasistencias", ausencias)
                        st.write("---")

                        # 2. GRÁFICOS VISUALES
                        st.markdown("### 📊 Gráficos de Rendimiento")
                        estados_simp = []
                        for idx, row in df_periodo.iterrows():
                            if row["Tipo"] == "Ausente": estados_simp.append({"Empleado": row["Empleado"], "Estado": "Ausente", "Cantidad": 1})
                            elif row["Tipo"] == "Entrada":
                                if row["Estado"] == "Tarde": estados_simp.append({"Empleado": row["Empleado"], "Estado": "Tarde", "Cantidad": 1})
                                elif row["Estado"] == "A tiempo": estados_simp.append({"Empleado": row["Empleado"], "Estado": "A tiempo", "Cantidad": 1})
                        
                        if estados_simp:
                            st.markdown("**Comparativa de Desempeño por Empleado**")
                            df_barras = pd.DataFrame(estados_simp).groupby(['Empleado', 'Estado']).sum().reset_index()
                            chart_barras = alt.Chart(df_barras).mark_bar().encode(
                                x=alt.X('Empleado:N', title='Personal'),
                                y=alt.Y('Cantidad:Q', title='Días'),
                                color=alt.Color('Estado:N', scale=alt.Scale(domain=['A tiempo', 'Tarde', 'Ausente'], range=['#10b981', '#f59e0b', '#ef4444'])),
                                tooltip=['Empleado', 'Estado', 'Cantidad']
                            ).properties(height=350)
                            st.altair_chart(chart_barras, use_container_width=True)

                        graf_col1, graf_col2 = st.columns([2, 1])
                        with graf_col1:
                            st.markdown("**Evolución Diaria de Asistencia**")
                            df_tendencia = df_entradas.groupby('Fecha').size().reset_index(name='Ingresos')
                            if not df_tendencia.empty:
                                chart_tendencia = alt.Chart(df_tendencia).mark_line(point=True, color="#2563EB", strokeWidth=4).encode(
                                    x=alt.X('Fecha:T', title='Fecha'), y=alt.Y('Ingresos:Q', title='Cantidad de Fichajes'), tooltip=['Fecha', 'Ingresos']
                                ).properties(height=300)
                                st.altair_chart(chart_tendencia, use_container_width=True)

                        with graf_col2:
                            st.markdown("**Distribución General**")
                            df_torta = pd.DataFrame(estados_simp).groupby('Estado').sum().reset_index()
                            if not df_torta.empty:
                                chart_estado = alt.Chart(df_torta).mark_arc(innerRadius=60).encode(
                                    theta=alt.Theta(field="Cantidad", type="quantitative"),
                                    color=alt.Color(field="Estado", type="nominal", scale=alt.Scale(domain=['A tiempo', 'Tarde', 'Ausente'], range=['#10b981', '#f59e0b', '#ef4444'])),
                                    tooltip=['Estado', 'Cantidad']
                                ).properties(height=300)
                                st.altair_chart(chart_estado, use_container_width=True)

                    else: st.warning("No hay registros en el periodo seleccionado para graficar.")
                else: st.info("No hay datos de presentismo del staff activo para analizar.")
            else: st.info("Planilla vacía.")

        # ==========================================
        # TAB 2: SISTEMA DE PUNTUACIÓN Y BONOS (MODIFICABLE)
        # ==========================================
        with tab_puntuacion:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Puntuación, Ranking y Bonos</div>', unsafe_allow_html=True)
            
            zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
            hoy = datetime.datetime.now(zona_arg).date()
            
            rango_punt = st.date_input("🗓️ Elegí el periodo para calcular los puntos:", value=(hoy, hoy), key="calendario_puntos")
            p_inicio, p_fin = procesar_rango_fechas(rango_punt)
            
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_punt = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_punt['Fecha_Obj'] = pd.to_datetime(df_punt['Fecha'], errors='coerce')
                df_punt_per = df_punt[(df_punt['Fecha_Obj'].dt.date >= p_inicio) & (df_punt['Fecha_Obj'].dt.date <= p_fin)]
                
                # Filtrar ajustes manuales para el periodo
                ajustes_periodo = [p for p in lista_puntos if p_inicio <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= p_fin]

                if not df_punt_per.empty or ajustes_periodo:
                    st.markdown("##### Reglas de Puntuación (Base: 100 pts)")
                    st.caption("✔️ Llegar a tiempo: 0pts | ⚠️ Llegada Tarde: -5pts | ❌ Ausente: -15pts | ➕/➖ Ajustes Manuales")
                    
                    ranking_data = []
                    for emp in lista_empleados:
                        # Extraer puntos manuales
                        e_ajustes = sum([int(p['Puntos']) for p in ajustes_periodo if p['Empleado'] == emp])
                        
                        df_e = df_punt_per[df_punt_per["Empleado"] == emp]
                        if not df_e.empty or e_ajustes != 0:
                            e_ent = df_e[df_e["Tipo"] == "Entrada"] if not df_e.empty else pd.DataFrame()
                            e_aus = df_e[df_e["Tipo"] == "Ausente"] if not df_e.empty else pd.DataFrame()
                            
                            e_ok = len(e_ent[e_ent["Estado"] == "A tiempo"]) if not e_ent.empty else 0
                            e_tar = len(e_ent[e_ent["Estado"] == "Tarde"]) if not e_ent.empty else 0
                            e_au = len(e_aus) if not e_aus.empty else 0
                            
                            # CÁLCULO DEL PUNTAJE FINAL CON LOS AJUSTES MANUALES
                            puntaje = 100 - (e_tar * 5) - (e_au * 15) + e_ajustes
                            
                            ranking_data.append({"Personal": emp, "⭐ PUNTAJE FINAL": puntaje, "Ajustes Manuales": e_ajustes, "✅ A Tiempo": e_ok, "⚠️ Tardes": e_tar, "❌ Faltas": e_au})
                            
                    if ranking_data:
                        df_ranking = pd.DataFrame(ranking_data).sort_values(by="⭐ PUNTAJE FINAL", ascending=False)
                        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
                        st.download_button(label="📥 Descargar Reporte de Puntuación", data=df_ranking.to_csv(index=False).encode('utf-8'), file_name=f"Puntuacion_{p_inicio}_al_{p_fin}.csv", mime="text/csv")
                    
                    # SECCIÓN DE BONOS Y MULTAS
                    st.markdown("---")
                    st.markdown("### ✍️ Modificar Puntaje (Bonos y Penalizaciones)")
                    st.write("Acá podés sumarle puntos a un vendedor por buen desempeño, o restarle por una falta de conducta.")
                    
                    with st.form("form_ajustes_puntos"):
                        col_ap1, col_ap2, col_ap3 = st.columns([2, 1, 1])
                        ap_emp = col_ap1.selectbox("Vendedor/a:", ["Seleccionar..."] + sorted(lista_empleados))
                        ap_fecha = col_ap2.date_input("Fecha de aplicación:", hoy)
                        ap_puntos = col_ap3.number_input("Puntos (+ para sumar, - para restar):", value=0, step=1)
                        ap_motivo = st.text_input("Motivo (Ej: Bono por excelente venta, Multa por no usar uniforme):")
                        
                        if st.form_submit_button("💾 Guardar Ajuste"):
                            if ap_emp != "Seleccionar..." and ap_puntos != 0 and ap_motivo:
                                nuevo_ajuste = {"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo}
                                lista_puntos.append(nuevo_ajuste)
                                with open(ARCHIVO_PUNTOS, 'w') as f: json.dump(lista_puntos, f)
                                st.success(f"¡Ajuste de {ap_puntos} puntos guardado para {ap_emp}!")
                                st.rerun()
                            else: st.error("Completá todos los campos y asegurate de que los puntos no sean cero.")
                    
                    # Ver historial de ajustes
                    if ajustes_periodo:
                        st.markdown("**Historial de Ajustes en este periodo:**")
                        for idx, p in enumerate(lista_puntos):
                            if p_inicio <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= p_fin:
                                st.info(f"[{p['Fecha']}] **{p['Empleado']}** | {p['Puntos']} pts | Motivo: {p['Motivo']}")
                                if st.button("🗑️ Anular ajuste", key=f"del_ajuste_{idx}"):
                                    lista_puntos.pop(idx)
                                    with open(ARCHIVO_PUNTOS, 'w') as f: json.dump(lista_puntos, f)
                                    st.rerun()

                else: st.info("No hay fichajes ni ajustes registrados en el lapso seleccionado.")
            else: st.info("La base de datos está vacía.")

        # ==========================================
        # TAB 3: AUDITORÍA (EDITAR HORARIOS Y EXPORTAR)
        # ==========================================
        with tab_auditoria:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📊 Edición y Planillas</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="highlight-edit"><b>✏️ MODIFICAR HORARIOS Y ESTADOS</b><br>Buscá un registro para corregir la hora exacta de ingreso o justificar una falta/ausencia.</div>', unsafe_allow_html=True)
            col_ed1, col_ed2 = st.columns(2)
            fecha_edicion = col_ed1.date_input("1. Fecha a auditar:", key="fecha_edit")
            emp_edicion = col_ed2.selectbox("2. Personal involucrado:", ["Seleccionar..."] + sorted(lista_empleados), key="emp_edit")
            
            if emp_edicion != "Seleccionar...":
                if os.path.exists(ARCHIVO_ASISTENCIA):
                    df_edicion = pd.read_csv(ARCHIVO_ASISTENCIA)
                    fecha_str = fecha_edicion.strftime("%Y-%m-%d")
                    if "Fecha" in df_edicion.columns and "Empleado" in df_edicion.columns:
                        indices_afectados = df_edicion.index[(df_edicion["Fecha"] == fecha_str) & (df_edicion["Empleado"] == emp_edicion)].tolist()
                        if not indices_afectados: st.warning("Sin movimientos para esta persona en la fecha seleccionada.")
                        else:
                            for idx in indices_afectados:
                                row = df_edicion.loc[idx]
                                with st.container():
                                    c1, c2, c3, c4 = st.columns([2,2,2,1])
                                    tipos_posibles = ["Entrada", "Salida", "Inicio Descanso", "Fin Descanso", "Ausente"]
                                    tipo_actual = row.get('Tipo', 'Entrada')
                                    idx_tipo = tipos_posibles.index(tipo_actual) if tipo_actual in tipos_posibles else 0
                                    nuevo_tipo = c1.selectbox(f"Tipo ({row.get('Turno','N/A')})", tipos_posibles, index=idx_tipo, key=f"t_{idx}")
                                    
                                    nueva_hora = c2.text_input("Hora (HH:MM:SS)", value=row.get('Hora', ''), key=f"h_{idx}")
                                    
                                    estados_posibles = ["A tiempo", "Tarde", "Salida", "Ausente", "Falta Justificada", "Pausa", "N/A"]
                                    estado_actual = row.get('Estado', 'N/A')
                                    idx_estado = estados_posibles.index(estado_actual) if estado_actual in estados_posibles else 6
                                    nuevo_estado = c3.selectbox("Estado", estados_posibles, index=idx_estado, key=f"e_{idx}")
                                    
                                    if c4.button("💾 GUARDAR", key=f"btn_{idx}"):
                                        df_edicion.at[idx, 'Tipo'] = nuevo_tipo
                                        df_edicion.at[idx, 'Hora'] = nueva_hora
                                        df_edicion.at[idx, 'Estado'] = nuevo_estado
                                        df_edicion.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                        st.success("¡Horario actualizado en la base de datos!")
                                        st.rerun()
                            st.write("---")
                            if st.button("🗑️ Borrar toda la actividad de este empleado en esta fecha"):
                                df_limpio = df_edicion.drop(indices_afectados)
                                df_limpio.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                st.success("¡Registros borrados!")
                                st.rerun()

            st.markdown("---")
            st.subheader("📥 Exportar Planillas a Excel / CSV")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                rango_descarga = st.date_input("Seleccionar rango de fechas a descargar:", value=(datetime.date.today(), datetime.date.today()), key="descarga_csv")
                d_inicio, d_fin = procesar_rango_fechas(rango_descarga)
                df_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                if "Fecha" in df_full.columns:
                    df_full['Fecha_Temp'] = pd.to_datetime(df_full['Fecha'], errors='coerce').dt.date
                    df_descarga = df_full[(df_full['Fecha_Temp'] >= d_inicio) & (df_full['Fecha_Temp'] <= d_fin)].drop(columns=['Fecha_Temp'])
                    if not df_descarga.empty:
                        st.download_button(label="📥 DESCARGAR PLANILLA DE ASISTENCIA", data=df_descarga.to_csv(index=False).encode('utf-8'), file_name=f"Asistencia_{d_inicio}_al_{d_fin}.csv", mime="text/csv", use_container_width=True)

            st.markdown("---")
            st.subheader("✍️ Carga Manual de Fichaje o Falta")
            with st.form("form_fichaje_manual"):
                col_fm1, col_fm2, col_fm3 = st.columns(3)
                fm_emp = col_fm1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                fm_local = col_fm2.selectbox("Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                fm_turno = col_fm3.selectbox("Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                
                fm_fecha = col_fm1.date_input("Fecha de registro:", datetime.date.today())
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                fm_hora = col_fm2.time_input("Hora exacta:", datetime.datetime.now(zona_arg).time())
                
                fm_tipo = col_fm3.selectbox("Tipo de Movimiento:", ["Entrada", "Salida", "Ausente", "Inicio Descanso", "Fin Descanso"])
                fm_estado = st.selectbox("Estado final para el reporte:", ["A tiempo", "Tarde", "Salida", "Ausente", "Falta Justificada", "Pausa", "N/A"])
                fm_nota = st.text_input("Nota / Justificación (Opcional):")
                
                submit_fm = st.form_submit_button("➕ Cargar Movimiento Manual")
                if submit_fm:
                    if fm_emp != "Seleccionar..." and fm_local != "Seleccionar..." and fm_turno != "Seleccionar...":
                        nuevo_registro = {
                            "Fecha": [fm_fecha.strftime("%Y-%m-%d")], "Hora": [fm_hora.strftime("%H:%M:%S")],
                            "Empleado": [fm_emp], "Sucursal": [fm_local], "Turno": [fm_turno],
                            "Tipo": [fm_tipo], "Estado": [fm_estado], "Distancia_m": [0.0], "Nota": [fm_nota]
                        }
                        df_nuevo = pd.DataFrame(nuevo_registro)
                        if not os.path.exists(ARCHIVO_ASISTENCIA): df_nuevo.to_csv(ARCHIVO_ASISTENCIA, index=False)
                        else:
                            df_existente = pd.read_csv(ARCHIVO_ASISTENCIA)
                            pd.concat([df_existente, df_nuevo], ignore_index=True).to_csv(ARCHIVO_ASISTENCIA, index=False)
                        st.success("¡Registro manual ingresado al sistema!")
                        st.rerun()
                    else: st.error("Faltan datos por seleccionar.")

        # TAB 4: COMUNICADOS Y ALERTAS
        with tab_mensajes:
            st.subheader("⚠️ Configuración de Llegadas Tarde")
            msg_tarde = st.text_area("Texto de Alerta:", value=config_app.get("mensaje_llegada_tarde", ""))
            if st.button("💾 Actualizar Alerta"):
                config_app["mensaje_llegada_tarde"] = msg_tarde
                with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                st.success("Alerta actualizada.")
                st.rerun()

            st.markdown("---")
            st.subheader("📬 Bandeja de Comunicados al Staff")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                tipo_dest = st.radio("Destinatario del anuncio:", ["Para todo el Staff", "Para un vendedor/a"])
                destinatario = "Todos"
                if tipo_dest == "Para un vendedor/a": destinatario = st.selectbox("Seleccionar persona:", ["Seleccionar..."] + sorted(lista_empleados))
                texto_mensaje = st.text_area("Contenido del anuncio:")
                if st.button("🚀 Publicar Anuncio"):
                    if texto_mensaje and destinatario != "Seleccionar...":
                        nuevo_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        lista_mensajes.append({"id": nuevo_id, "destinatario": destinatario, "texto": texto_mensaje})
                        with open(ARCHIVO_MENSAJES, 'w') as f: json.dump(lista_mensajes, f)
                        st.success("¡Anuncio publicado!")
                        st.rerun()
            with col_m2:
                st.write("**Anuncios Activos**")
                if not lista_mensajes: st.info("Sin comunicados activos.")
                else:
                    for idx, m in enumerate(lista_mensajes):
                        with st.container():
                            if m['destinatario'] == 'Todos': st.markdown(f"🏷️ **GLOBAL:** {m['texto']}")
                            else: st.markdown(f"👤 **A {m['destinatario']}:** {m['texto']}")
                            if st.button("🗑️ Quitar", key=f"del_msg_{idx}"):
                                lista_mensajes.pop(idx)
                                with open(ARCHIVO_MENSAJES, 'w') as f: json.dump(lista_mensajes, f)
                                st.rerun()
                            st.write("---")

        # TAB 5: PERSONAL (STAFF)
        with tab_personal:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.subheader("Lista de Staff")
                for emp in sorted(lista_empleados):
                    st.write(f"- **{emp}** | {'📱 Enlazado' if emp in dispositivos_vinculados else '⚠️ Falta enlazar'}")
            with col_p2:
                st.subheader("Administración")
                nuevo_emp = st.text_input("Alta de Personal (Nombre y Apellido):")
                if st.button("➕ Ingresar") and nuevo_emp:
                    if nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                        st.rerun()
                emp_desv = st.selectbox("Desenlace de celular:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                if st.button("🔓 Desenlazar") and emp_desv != "Seleccionar...":
                    del dispositivos_vinculados[emp_desv]
                    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                    st.rerun()
                borrar_emp = st.selectbox("Baja de Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                if st.button("🗑️ Eliminar Staff") and borrar_emp != "Seleccionar...":
                    lista_empleados.remove(borrar_emp)
                    if borrar_emp in dispositivos_vinculados:
                        del dispositivos_vinculados[borrar_emp]
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                    with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                    st.rerun()

        # TAB 6: LOCALES Y TURNOS
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

        # TAB 7: AJUSTES GLOBALES
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("📢 Anuncio General")
                nuevo_mensaje = st.text_area("Comunicado Corporativo:", value=config_app.get("mensaje_dia", ""))
                st.markdown("---")
                st.subheader("⏱️ Reglas de Operación")
                req_salida = st.checkbox("Requerir botón 'Salida'", value=config_app.get("requiere_salida", True))
                hab_descansos = st.checkbox("Habilitar botones de 'Pausa / Descanso'", value=config_app.get("habilitar_descansos", False))
                nueva_tolerancia = st.number_input("Minutos de tolerancia:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 10)))
                if st.button("💾 Guardar Configuración"):
                    config_app["mensaje_dia"] = nuevo_mensaje
                    config_app["requiere_salida"] = req_salida
                    config_app["habilitar_descansos"] = hab_descansos
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                    st.success("Configuración actualizada.")
                    st.rerun()
                    
                st.markdown("---")
                with st.expander("⚠️ Opciones de Base de Datos (Depurar/Eliminar)"):
                    if st.button("🧹 Limpiar historial de ex-empleados"):
                        df_mantenimiento = pd.read_csv(ARCHIVO_ASISTENCIA)
                        df_limpio = df_mantenimiento[df_mantenimiento["Empleado"].isin(lista_empleados)]
                        df_limpio.to_csv(ARCHIVO_ASISTENCIA, index=False)
                        st.success("Planilla depurada.")
                        st.rerun()
                    if st.button("🚨 VACIAR TODA LA PLANILLA DE ASISTENCIA"):
                        os.remove(ARCHIVO_ASISTENCIA)
                        st.success("¡Planilla formateada por completo!")
                        st.rerun()

            with col_aj2:
                st.subheader("🔑 Seguridad Gerencial")
                nc = st.text_input("Nueva clave de acceso:", type="password")
                rc = st.text_input("Repetir clave:", type="password")
                if st.button("🔒 Cambiar Clave Principal"):
                    if nc == rc and nc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.success("Clave principal modificada con éxito.")
                    else: st.error("Las claves no coinciden.")

        # TAB 8: SEGURIDAD (OCULTO)
        with tab_seguridad:
            st.subheader("🕵️ Registro de Auditoría de Accesos")
            st.write("Acá podés auditar quién y con qué clave intentó acceder a este Panel de Gerencia.")
            if lista_intentos:
                df_intentos = pd.DataFrame(lista_intentos)
                df_intentos = df_intentos.sort_values(by=["Fecha", "Hora"], ascending=[False, False])
                st.dataframe(df_intentos, use_container_width=True, hide_index=True)
                if st.button("🗑️ Limpiar registro de seguridad"):
                    with open(ARCHIVO_INTENTOS, 'w') as f: json.dump([], f)
                    st.success("Registro formateado.")
                    st.rerun()
            else:
                st.info("No hay ingresos ni intentos sospechosos registrados todavía.")
