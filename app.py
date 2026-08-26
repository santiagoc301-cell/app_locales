import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json

# Configuración inicial de la página
st.set_page_config(
    page_title="Gestión de Personal - Locales",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 💎 ESTÉTICA PREMIUM COMERCIAL (CSS)
# ==========================================
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #111827; margin-bottom: 0.2rem; text-transform: uppercase; letter-spacing: -0.5px;}
    .sub-text { font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem; }
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #E5E7EB; padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border-left: 5px solid #111827; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #111827; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; border: 1px solid #D1D5DB; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    hr { border-color: #E5E7EB; margin-top: 1.5rem; margin-bottom: 1.5rem; }
    .msg-global { border-left: 5px solid #111827; padding: 10px; background-color: #F3F4F6; border-radius: 5px; margin-bottom: 10px; }
    .msg-individual { border-left: 5px solid #F59E0B; padding: 10px; background-color: #FFFBEB; border-radius: 5px; margin-bottom: 10px; }
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
RADIO_MAXIMO_METROS = 50

# Parche automático para archivos de versiones anteriores
if os.path.exists(ARCHIVO_ASISTENCIA):
    try:
        df_patch = pd.read_csv(ARCHIVO_ASISTENCIA)
        columnas_requeridas = ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m"]
        cambios = False
        for col in columnas_requeridas:
            if col not in df_patch.columns:
                if col == "Tipo": df_patch[col] = "Entrada"
                elif col == "Estado": df_patch[col] = "A tiempo"
                elif col == "Turno": df_patch[col] = "Horario Comercial"
                elif col == "Distancia_m": df_patch[col] = 0.0
                else: df_patch[col] = "N/A"
                cambios = True
        if cambios: df_patch.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except: pass

# Configuración Inicial
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {"admin_password": "1234", "tolerancia_minutos": 10, "requiere_salida": True, "mensaje_llegada_tarde": "⚠️ Registro de llegada fuera del margen de tolerancia."}
    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f: config_app = json.load(f)

if "tolerancia_minutos" not in config_app: config_app["tolerancia_minutos"] = 10
if "requiere_salida" not in config_app: config_app["requiere_salida"] = True
if "mensaje_llegada_tarde" not in config_app: config_app["mensaje_llegada_tarde"] = "⚠️ Registro de llegada fuera del margen de tolerancia."

# Personal
if not os.path.exists(ARCHIVO_EMPLEADOS):
    empleados_iniciales = ["Abril", "Agustina", "Camila", "Daniela", "Macarena", "Nicolás"]
    with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(empleados_iniciales, f)
with open(ARCHIVO_EMPLEADOS, 'r') as f: lista_empleados = json.load(f)
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

# Dispositivos
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f: dispositivos_vinculados = json.load(f)

# Locales y Turnos
if not os.path.exists(ARCHIVO_LOCALES):
    locales_iniciales = {"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}, "Local 2 - Shopping": {"lat": -24.808264, "lon": -65.404947}}
    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(locales_iniciales, f)
with open(ARCHIVO_LOCALES, 'r') as f: lista_locales = json.load(f)

if not os.path.exists(ARCHIVO_TURNOS):
    turnos_iniciales = {"Apertura": "09:00", "Turno Tarde": "17:00"}
    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(turnos_iniciales, f)
with open(ARCHIVO_TURNOS, 'r') as f: lista_turnos = json.load(f)

# Mensajes
if not os.path.exists(ARCHIVO_MENSAJES):
    with open(ARCHIVO_MENSAJES, 'w') as f: json.dump([], f)
with open(ARCHIVO_MENSAJES, 'r') as f: lista_mensajes = json.load(f)

# ==========================================
# 2. IDENTIFICADOR DEL CELULAR (DEVICE BINDING)
# ==========================================
js_get_device = """
(function() {
    let id = localStorage.getItem('tienda_app_device_id');
    if (!id) {
        id = 'dev_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('tienda_app_device_id', id);
    }
    return id;
})();
"""
device_id = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
st.sidebar.title("🛍️ Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Fichar Asistencia", "⚙️ Panel de Gerencia"])

# ==========================================
# 4. PANTALLA: MARCAR ASISTENCIA
# ==========================================
if pestaña == "⏱️ Fichar Asistencia":
    st.markdown('<div class="main-title">⏱️ Portal de Asistencia</div>', unsafe_allow_html=True)
    
    # MENSAJES Y ANUNCIOS DE LA EMPRESA
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")
    else:
        st.markdown('<div class="sub-text">Validá tu ubicación en la sucursal para registrar tu horario.</div>', unsafe_allow_html=True)

    if not device_id:
        st.info("🔄 Verificando dispositivo...")
    else:
        empleado_en_celu = None
        for emp, dev in dispositivos_vinculados.items():
            if dev == device_id:
                empleado_en_celu = emp
                break

        if empleado_en_celu:
            # BANDEJA DE MENSAJES PRIVADOS
            mensajes_usuario = [m for m in lista_mensajes if m['destinatario'] in ['Todos', empleado_en_celu]]
            if mensajes_usuario:
                st.write("### 📬 Avisos del Staff")
                for m in mensajes_usuario:
                    if m['destinatario'] == 'Todos':
                        st.markdown(f"<div class='msg-global'>🏷️ <b>Staff General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='msg-individual'>📩 <b>Mensaje Directo:</b> {m['texto']}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            st.success(f"📱 Hola **{empleado_en_celu}**, tu equipo está enlazado correctamente.")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                local_seleccionado = st.selectbox("📍 Tienda actual:", ["Seleccionar..."] + list(lista_locales.keys()))
            with col_sel2:
                turno_seleccionado = st.selectbox("🕒 Horario:", ["Seleccionar..."] + list(lista_turnos.keys()))

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

                        marcar = False
                        tipo_fichaje = ""

                        if config_app.get("requiere_salida", True):
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada: st.error("⚠️ Ya marcaste el ingreso para este turno.")
                                    else: marcar, tipo_fichaje = True, "Entrada"
                            with col_b2:
                                if st.button("🔴 REGISTRAR SALIDA", use_container_width=True):
                                    marcar, tipo_fichaje = True, "Salida"
                        else:
                            col_centrada, _, _ = st.columns([2, 1, 1])
                            with col_centrada:
                                if st.button("🟢 REGISTRAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada: st.error("⚠️ Ya marcaste el ingreso para este turno.")
                                    else: marcar, tipo_fichaje = True, "Entrada"

                        if marcar:
                            hora = ahora.strftime("%H:%M:%S")
                            estado_llegada = "N/A"
                            if tipo_fichaje == "Entrada":
                                hora_turno_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado], "%H:%M").time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_turno_obj).replace(tzinfo=zona_arg)
                                dt_limite = dt_turno + datetime.timedelta(minutes=int(config_app["tolerancia_minutos"]))
                                estado_llegada = "Tarde" if ahora > dt_limite else "A tiempo"
                            elif tipo_fichaje == "Salida":
                                estado_llegada = "Salida"

                            registro = {"Fecha": [fecha_hoy], "Hora": [hora], "Empleado": [empleado_en_celu], "Sucursal": [local_seleccionado], "Turno": [turno_seleccionado], "Tipo": [tipo_fichaje], "Estado": [estado_llegada], "Distancia_m": [round(distancia, 1)]}
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
                            else:
                                st.success(f"¡Salida registrada a las {hora}! Buen descanso.")
                                
                    else:
                        st.error(f"❌ Estás fuera del radio de la tienda (Distancia: {distancia:.1f} m).")
                else:
                    st.warning("⚠️ Esperando conexión GPS del teléfono...")
            else:
                st.info("👆 Por favor, elegí la tienda y tu horario.")

            st.markdown("---")
            st.subheader("📜 Tus movimientos de hoy")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha"] == datetime.datetime.now(zona_arg).strftime("%Y-%m-%d"))]
                if not df_emp.empty: st.dataframe(df_emp[["Hora", "Sucursal", "Turno", "Tipo", "Estado"]], hide_index=True, use_container_width=True)
                else: st.write("No tenés fichajes en el día de la fecha.")
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
            else:
                st.error("Todo el personal ya tiene un dispositivo enlazado.")

# ==========================================
# 5. PANTALLA: PANEL DE GERENCIA
# ==========================================
elif pestaña == "⚙️ Panel de Gerencia":
    st.markdown('<div class="main-title">⚙️ Panel de Gerencia</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Clave de acceso gerencial:", type="password")

    if password_ingresada == config_app["admin_password"]:
        
        tab_mensajes, tab_estadisticas, tab_reportes, tab_personal, tab_locales, tab_ajustes = st.tabs([
            "📢 Comunicados", "📈 Métricas", "📊 Reportes", "👥 Staff", "📍 Tiendas", "⚙️ Sistema"
        ])

        # TAB 1: COMUNICADOS Y ALERTAS
        with tab_mensajes:
            st.subheader("⚠️ Configuración de Llegadas Tarde")
            st.write("Mensaje automático que verá el empleado si ficha fuera de horario.")
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
                st.write("**Redactar Anuncio**")
                tipo_dest = st.radio("Destinatario del anuncio:", ["Para todo el Staff", "Para un vendedor/a"])
                destinatario = "Todos"
                if tipo_dest == "Para un vendedor/a":
                    destinatario = st.selectbox("Seleccionar persona:", ["Seleccionar..."] + sorted(lista_empleados))
                
                texto_mensaje = st.text_area("Contenido del anuncio:")
                
                if st.button("🚀 Publicar Anuncio"):
                    if texto_mensaje and destinatario != "Seleccionar...":
                        nuevo_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        lista_mensajes.append({"id": nuevo_id, "destinatario": destinatario, "texto": texto_mensaje})
                        with open(ARCHIVO_MENSAJES, 'w') as f: json.dump(lista_mensajes, f)
                        st.success("¡Anuncio publicado!")
                        st.rerun()
                    else:
                        st.error("Completá todos los campos.")

            with col_m2:
                st.write("**Anuncios Activos**")
                if not lista_mensajes:
                    st.info("Sin comunicados activos.")
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

        # TAB 2: MÉTRICAS (ESTADÍSTICAS)
        with tab_estadisticas:
            st.subheader("📊 Métricas de Presentismo")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_stats = pd.read_csv(ARCHIVO_ASISTENCIA)
                if "Tipo" not in df_stats.columns: df_stats["Tipo"] = "Entrada"
                if "Empleado" not in df_stats.columns: df_stats["Empleado"] = "Desconocido"
                
                df_stats = df_stats[df_stats["Empleado"].isin(lista_empleados)]
                df_entradas = df_stats[df_stats["Tipo"] == "Entrada"].copy()
                
                if not df_entradas.empty:
                    df_entradas['Fecha_Obj'] = pd.to_datetime(df_entradas['Fecha'], errors='coerce')
                    zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                    hoy = datetime.datetime.now(zona_arg).date()
                    
                    def mostrar_metricas(titulo, df_filtrado):
                        st.markdown(f"**{titulo}**")
                        c1, c2, c3 = st.columns(3)
                        total = len(df_filtrado)
                        tardes = len(df_filtrado[df_filtrado["Estado"] == "Tarde"])
                        a_tiempo = len(df_filtrado[df_filtrado["Estado"] == "A tiempo"])
                        c1.metric("Presentismo Total", total)
                        c2.metric("✅ En Horario", a_tiempo)
                        c3.metric("⚠️ Fuera de Horario", tardes)
                        st.write("---")

                    st.markdown("### 🔎 Buscar por Rango de Fechas")
                    rango_stats = st.date_input("Analizar periodo (Desde - Hasta):", value=(hoy, hoy), key="calendario_stats")
                    
                    if len(rango_stats) == 2:
                        s_inicio, s_fin = rango_stats
                        entradas_pers = df_entradas[(df_entradas['Fecha_Obj'].dt.date >= s_inicio) & (df_entradas['Fecha_Obj'].dt.date <= s_fin)]
                        mostrar_metricas(f"Corte del {s_inicio.strftime('%d/%m/%Y')} al {s_fin.strftime('%d/%m/%Y')}", entradas_pers)
                    else:
                        st.info("Seleccioná un periodo válido en el calendario.")

                    st.markdown("### 📌 Indicadores Rápidos")
                    entradas_hoy = df_entradas[df_entradas['Fecha_Obj'].dt.date == hoy]
                    hace_7_dias = hoy - datetime.timedelta(days=7)
                    entradas_semana = df_entradas[df_entradas['Fecha_Obj'].dt.date >= hace_7_dias]
                    entradas_mes = df_entradas[(df_entradas['Fecha_Obj'].dt.month == hoy.month) & (df_entradas['Fecha_Obj'].dt.year == hoy.year)]

                    mostrar_metricas("📅 HOY", entradas_hoy)
                    with st.expander("Ver histórico (Semana y Mes)"):
                        mostrar_metricas("🗓️ ÚLTIMOS 7 DÍAS", entradas_semana)
                        mostrar_metricas("📆 ESTE MES", entradas_mes)
                else:
                    st.info("No hay datos de presentismo del staff activo para analizar.")
            else:
                st.info("Planilla vacía.")

        # TAB 3: REPORTES Y EDICIÓN
        with tab_reportes:
            st.subheader("📥 Generar Archivo Excel/CSV")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                rango_fechas = st.date_input("Filtrar descargas por fechas:", value=(datetime.date.today(), datetime.date.today()))
                if len(rango_fechas) == 2:
                    f_inicio, f_fin = rango_fechas
                    df_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                    if "Fecha" in df_full.columns:
                        df_full['Fecha_Temp'] = pd.to_datetime(df_full['Fecha'], errors='coerce').dt.date
                        df_descarga = df_full[(df_full['Fecha_Temp'] >= f_inicio) & (df_full['Fecha_Temp'] <= f_fin)].drop(columns=['Fecha_Temp'])
                        if not df_descarga.empty:
                            st.download_button(label="📥 EXPORTAR PLANILLA", data=df_descarga.to_csv(index=False).encode('utf-8'), file_name=f"Reporte_Tiendas_{f_inicio}_al_{f_fin}.csv", mime="text/csv", use_container_width=True)
                
                st.markdown("---")
                st.subheader("✏️ Modificar Fichajes (Auditoría)")
                fecha_edicion = st.date_input("1. Fecha a auditar:")
                emp_edicion = st.selectbox("2. Personal involucrado:", ["Seleccionar..."] + sorted(lista_empleados))
                
                if emp_edicion != "Seleccionar...":
                    df_edicion = pd.read_csv(ARCHIVO_ASISTENCIA)
                    fecha_str = fecha_edicion.strftime("%Y-%m-%d")
                    if "Fecha" in df_edicion.columns and "Empleado" in df_edicion.columns:
                        indices_afectados = df_edicion.index[(df_edicion["Fecha"] == fecha_str) & (df_edicion["Empleado"] == emp_edicion)].tolist()
                        if not indices_afectados:
                            st.warning("Sin movimientos para esta persona y fecha.")
                        else:
                            st.write("Modificá la hora o el estado:")
                            for idx in indices_afectados:
                                row = df_edicion.loc[idx]
                                with st.container():
                                    c1, c2, c3, c4 = st.columns([2,2,2,1])
                                    c1.write(f"**{row.get('Tipo', 'N/A')}** ({row.get('Turno', 'N/A')})")
                                    nueva_hora = c2.text_input("Hora (HH:MM:SS)", value=row.get('Hora', ''), key=f"h_{idx}")
                                    estados_posibles = ["A tiempo", "Tarde", "Salida", "N/A"]
                                    estado_actual = row.get('Estado', 'N/A')
                                    idx_estado = estados_posibles.index(estado_actual) if estado_actual in estados_posibles else 3
                                    nuevo_estado = c3.selectbox("Estado", estados_posibles, index=idx_estado, key=f"e_{idx}")
                                    
                                    if c4.button("💾 Guardar", key=f"btn_{idx}"):
                                        df_edicion.at[idx, 'Hora'] = nueva_hora
                                        df_edicion.at[idx, 'Estado'] = nuevo_estado
                                        df_edicion.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                        st.success("¡Registro actualizado!")
                                        st.rerun()
                                        
                            st.write("---")
                            if st.button("🗑️ Borrar toda la actividad de este empleado en esta fecha"):
                                df_limpio = df_edicion.drop(indices_afectados)
                                df_limpio.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                st.success("¡Registros borrados!")
                                st.rerun()

                st.markdown("---")
                with st.expander("⚠️ Mantenimiento de la Base de Datos"):
                    st.write("**1. Depurar Personal Inactivo**")
                    if st.button("🧹 Limpiar registros de ex-empleados"):
                        df_mantenimiento = pd.read_csv(ARCHIVO_ASISTENCIA)
                        df_limpio = df_mantenimiento[df_mantenimiento["Empleado"].isin(lista_empleados)]
                        df_limpio.to_csv(ARCHIVO_ASISTENCIA, index=False)
                        st.success("Planilla depurada.")
                        st.rerun()
                        
                    st.write("---")
                    st.write("**2. Resetear el Sistema**")
                    if st.button("🚨 VACIAR TODA LA PLANILLA (Empezar de cero)"):
                        os.remove(ARCHIVO_ASISTENCIA)
                        st.success("¡Planilla formateada!")
                        st.rerun()
            else:
                st.info("Aún no se generó el archivo de asistencia.")

        # TAB 4: PERSONAL (STAFF)
        with tab_personal:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.subheader("Lista de Staff")
                for emp in sorted(lista_empleados):
                    st.write(f"- **{emp}** | {'📱 Enlazado' if emp in dispositivos_vinculados else '⚠️ Falta enlazar'}")
            with col_p2:
                st.subheader("Administración")
                nuevo_emp = st.text_input("Alta de Personal:")
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

        # TAB 5: LOCALES Y TURNOS
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
            with col_l2:
                st.subheader("🕒 Turnos / Horarios")
                for turno, hora in lista_turnos.items(): st.write(f"- **{turno}** | {hora}")
                n_turno = st.text_input("Nuevo Horario:")
                h_turno = st.time_input("Hora de Ingreso:")
                if st.button("➕ Crear Horario") and n_turno:
                    lista_turnos[n_turno] = h_turno.strftime("%H:%M")
                    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                    st.rerun()

        # TAB 6: AJUSTES GLOBALES
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("📢 Anuncio General")
                st.write("Fijá un texto importante en el portal de fichaje principal.")
                nuevo_mensaje = st.text_area("Comunicado Corporativo:", value=config_app.get("mensaje_dia", ""))
                
                st.markdown("---")
                st.subheader("⏱️ Reglas de Operación")
                req_salida = st.checkbox("Requerir botón 'Salida'", value=config_app.get("requiere_salida", True))
                nueva_tolerancia = st.number_input("Minutos de tolerancia:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 10)))

                if st.button("💾 Guardar Configuración"):
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
                if st.button("🔒 Cambiar Clave"):
                    if nc == rc and nc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.success("Clave modificada con éxito.")
                    else: st.error("Las claves no coinciden.")
