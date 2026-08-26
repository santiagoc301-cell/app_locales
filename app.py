import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json

# Configuración inicial de la página
st.set_page_config(
    page_title="Control de Asistencia",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 💎 ESTÉTICA PREMIUM (CSS Personalizado)
# ==========================================
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-text { font-size: 1.1rem; color: #64748B; margin-bottom: 2rem; }
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #0F172A; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); }
    hr { border-color: #e2e8f0; margin-top: 1.5rem; margin-bottom: 1.5rem; }
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
RADIO_MAXIMO_METROS = 50

# 🛠️ PARCHE AUTOMÁTICO PARA ACTUALIZAR ARCHIVOS VIEJOS
if os.path.exists(ARCHIVO_ASISTENCIA):
    try:
        df_patch = pd.read_csv(ARCHIVO_ASISTENCIA)
        columnas_requeridas = ["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Distancia_m"]
        cambios = False
        for col in columnas_requeridas:
            if col not in df_patch.columns:
                if col == "Tipo": df_patch[col] = "Entrada"
                elif col == "Estado": df_patch[col] = "A tiempo"
                elif col == "Turno": df_patch[col] = "Sin Turno"
                elif col == "Distancia_m": df_patch[col] = 0.0
                else: df_patch[col] = "N/A"
                cambios = True
        if cambios:
            df_patch.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except:
        pass

# Configuración Inicial
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {"admin_password": "1234", "tolerancia_minutos": 15, "requiere_salida": True, "mensaje_dia": ""}
    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f: config_app = json.load(f)

# Parches de actualización config
if "tolerancia_minutos" not in config_app: config_app["tolerancia_minutos"] = 15
if "requiere_salida" not in config_app: config_app["requiere_salida"] = True
if "mensaje_dia" not in config_app: config_app["mensaje_dia"] = ""

# Empleados
if not os.path.exists(ARCHIVO_EMPLEADOS):
    empleados_iniciales = ["Abril", "Agustina", "Alejandro", "Camila", "Claudia", "Daniela", "Debora", "Franco", "Macarena", "Mario", "Nicolás", "Paola", "Viviana"]
    with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(empleados_iniciales, f)
with open(ARCHIVO_EMPLEADOS, 'r') as f: lista_empleados = json.load(f)
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

# Dispositivos
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f: dispositivos_vinculados = json.load(f)

# Locales y Turnos
if not os.path.exists(ARCHIVO_LOCALES):
    locales_iniciales = {"Local 1 - Zuviria 142": {"lat": -24.788296, "lon": -65.409429}}
    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(locales_iniciales, f)
with open(ARCHIVO_LOCALES, 'r') as f: lista_locales = json.load(f)

if not os.path.exists(ARCHIVO_TURNOS):
    turnos_iniciales = {"Mañana": "08:30", "Tarde": "16:30"}
    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(turnos_iniciales, f)
with open(ARCHIVO_TURNOS, 'r') as f: lista_turnos = json.load(f)

# ==========================================
# 2. IDENTIFICADOR DEL CELULAR (DEVICE BINDING)
# ==========================================
js_get_device = """
(function() {
    let id = localStorage.getItem('vet_app_device_id');
    if (!id) {
        id = 'dev_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('vet_app_device_id', id);
    }
    return id;
})();
"""
device_id = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
st.sidebar.title("🐾 Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Fichar Asistencia", "⚙️ Panel de Administrador"])

# ==========================================
# 4. PANTALLA: MARCAR ASISTENCIA
# ==========================================
if pestaña == "⏱️ Fichar Asistencia":
    st.markdown('<div class="main-title">⏱️ Registro de Asistencia</div>', unsafe_allow_html=True)
    
    # MENSAJE DEL DÍA
    if config_app.get("mensaje_dia", "").strip() != "":
        st.info(f"📢 **Anuncio de Administración:**\n\n{config_app['mensaje_dia']}")
    else:
        st.markdown('<div class="sub-text">Completá los datos y validá tu ubicación para registrar ingreso o egreso.</div>', unsafe_allow_html=True)

    if not device_id:
        st.info("🔄 Autenticando dispositivo...")
    else:
        empleado_en_celu = None
        for emp, dev in dispositivos_vinculados.items():
            if dev == device_id:
                empleado_en_celu = emp
                break

        if empleado_en_celu:
            st.success(f"📱 Dispositivo verificado: **{empleado_en_celu}**")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                local_seleccionado = st.selectbox("📍 Sucursal actual:", ["Seleccionar..."] + list(lista_locales.keys()))
            with col_sel2:
                turno_seleccionado = st.selectbox("🕒 Turno a cumplir:", ["Seleccionar..."] + list(lista_turnos.keys()))

            st.markdown("---")

            if local_seleccionado != "Seleccionar..." and turno_seleccionado != "Seleccionar...":
                st.info("🛰️ Validando ubicación GPS...")
                ubicacion = get_geolocation()

                if ubicacion:
                    coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                    coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                    distancia = geodesic(coord_usuario, coord_local).meters

                    if distancia <= RADIO_MAXIMO_METROS:
                        st.success(f"✅ GPS Verificado (Distancia: {distancia:.1f} m).")
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
                                if st.button("🟢 MARCAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada: st.error("⚠️ Ya registraste entrada hoy para este turno.")
                                    else: marcar, tipo_fichaje = True, "Entrada"
                            with col_b2:
                                if st.button("🔴 MARCAR SALIDA", use_container_width=True):
                                    marcar, tipo_fichaje = True, "Salida"
                        else:
                            col_centrada, _, _ = st.columns([2, 1, 1])
                            with col_centrada:
                                if st.button("🟢 MARCAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada: st.error("⚠️ Ya registraste entrada hoy para este turno.")
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

                            st.balloons() if tipo_fichaje == "Entrada" and estado_llegada == "A tiempo" else None
                            st.success(f"¡{tipo_fichaje} registrada a las {hora}!")
                            if estado_llegada == "Tarde": st.warning(f"⚠️ Llegada fuera de horario (Tolerancia: {config_app['tolerancia_minutos']} min).")
                    else:
                        st.error(f"❌ Fuera de rango. Distancia al local: {distancia:.1f} m.")
                else:
                    st.warning("⚠️ Esperando GPS...")
            else:
                st.info("👆 Seleccioná la sucursal y el turno.")

            st.markdown("---")
            st.subheader("📜 Tus registros de hoy")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha"] == datetime.datetime.now(zona_arg).strftime("%Y-%m-%d"))]
                if not df_emp.empty: st.dataframe(df_emp[["Hora", "Sucursal", "Turno", "Tipo", "Estado"]], hide_index=True, use_container_width=True)
                else: st.write("Aún no hay movimientos hoy.")
        else:
            st.warning("⚠️ **Dispositivo no registrado.**")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]
            if empleados_disponibles:
                emp_vincular = st.selectbox("👤 Tu nombre:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Vincular este Celular"):
                    if emp_vincular != "Seleccionar...":
                        dispositivos_vinculados[emp_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        st.success("¡Dispositivo vinculado con éxito!")
                        st.rerun()
            else:
                st.error("Todos los empleados tienen un celular asignado.")

# ==========================================
# 5. PANTALLA: PANEL ADMINISTRADOR
# ==========================================
elif pestaña == "⚙️ Panel de Administrador":
    st.markdown('<div class="main-title">⚙️ Panel de Administración</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Ingresá la contraseña:", type="password")

    if password_ingresada == config_app["admin_password"]:
        # PESTAÑAS
        tab_estadisticas, tab_reportes, tab_personal, tab_locales, tab_ajustes = st.tabs([
            "📈 Estadísticas", "📊 Reportes y Edición", "👥 Personal", "📍 Locales y Turnos", "⚙️ Ajustes"
        ])

        # TAB 1: ESTADÍSTICAS
        with tab_estadisticas:
            st.subheader("📊 Análisis de Asistencia (Solo Entradas)")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                df_stats = pd.read_csv(ARCHIVO_ASISTENCIA)
                
                # Asegurarse que exista la columna Tipo por las dudas
                if "Tipo" not in df_stats.columns:
                    df_stats["Tipo"] = "Entrada"
                    
                df_entradas = df_stats[df_stats["Tipo"] == "Entrada"].copy()
                
                if not df_entradas.empty:
                    df_entradas['Fecha_Obj'] = pd.to_datetime(df_entradas['Fecha'], errors='coerce')
                    
                    zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                    hoy = datetime.datetime.now(zona_arg).date()
                    
                    # Diaria
                    entradas_hoy = df_entradas[df_entradas['Fecha_Obj'].dt.date == hoy]
                    # Semanal
                    hace_7_dias = hoy - datetime.timedelta(days=7)
                    entradas_semana = df_entradas[df_entradas['Fecha_Obj'].dt.date >= hace_7_dias]
                    # Mensual
                    entradas_mes = df_entradas[(df_entradas['Fecha_Obj'].dt.month == hoy.month) & (df_entradas['Fecha_Obj'].dt.year == hoy.year)]
                    # Anual
                    entradas_anio = df_entradas[df_entradas['Fecha_Obj'].dt.year == hoy.year]

                    def mostrar_metricas(titulo, df_filtrado):
                        st.markdown(f"**{titulo}**")
                        c1, c2, c3 = st.columns(3)
                        total = len(df_filtrado)
                        tardes = len(df_filtrado[df_filtrado["Estado"] == "Tarde"])
                        a_tiempo = len(df_filtrado[df_filtrado["Estado"] == "A tiempo"])
                        c1.metric("Total Asistencias", total)
                        c2.metric("✅ A Tiempo", a_tiempo)
                        c3.metric("⚠️ Llegadas Tarde", tardes)
                        st.write("---")

                    mostrar_metricas("📅 HOY", entradas_hoy)
                    mostrar_metricas("🗓️ ÚLTIMOS 7 DÍAS", entradas_semana)
                    mostrar_metricas("📆 ESTE MES", entradas_mes)
                    mostrar_metricas("🌎 ESTE AÑO", entradas_anio)
                else:
                    st.info("Aún no hay registros de Entrada para analizar.")
            else:
                st.info("No hay datos para generar estadísticas.")

        # TAB 2: REPORTES Y EDICIÓN
        with tab_reportes:
            st.subheader("📥 Exportar Datos")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                rango_fechas = st.date_input("Seleccionar rango de fechas:", value=(datetime.date.today(), datetime.date.today()))
                if len(rango_fechas) == 2:
                    f_inicio, f_fin = rango_fechas
                    df_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                    
                    if "Fecha" in df_full.columns:
                        df_full['Fecha_Temp'] = pd.to_datetime(df_full['Fecha'], errors='coerce').dt.date
                        df_descarga = df_full[(df_full['Fecha_Temp'] >= f_inicio) & (df_full['Fecha_Temp'] <= f_fin)].drop(columns=['Fecha_Temp'])
                        if not df_descarga.empty:
                            st.download_button(label="📥 DESCARGAR PLANILLA EXCEL (CSV)", data=df_descarga.to_csv(index=False).encode('utf-8'), file_name=f"Asistencia_{f_inicio}_al_{f_fin}.csv", mime="text/csv", use_container_width=True)
                
                st.markdown("---")
                st.subheader("✏️ Editar o Borrar Fichajes Manualmente")
                fecha_edicion = st.date_input("1. Elegí la fecha del error:")
                emp_edicion = st.selectbox("2. Elegí al empleado:", ["Seleccionar..."] + sorted(lista_empleados))
                
                if emp_edicion != "Seleccionar...":
                    df_edicion = pd.read_csv(ARCHIVO_ASISTENCIA)
                    fecha_str = fecha_edicion.strftime("%Y-%m-%d")
                    # Encontrar indices exactos
                    if "Fecha" in df_edicion.columns and "Empleado" in df_edicion.columns:
                        indices_afectados = df_edicion.index[(df_edicion["Fecha"] == fecha_str) & (df_edicion["Empleado"] == emp_edicion)].tolist()
                        
                        if not indices_afectados:
                            st.warning("No hay registros de este empleado en esta fecha.")
                        else:
                            st.write("Fichajes encontrados. Modificá la hora/estado o borralos:")
                            for idx in indices_afectados:
                                row = df_edicion.loc[idx]
                                with st.container():
                                    c1, c2, c3, c4 = st.columns([2,2,2,1])
                                    tipo_mostrar = row.get('Tipo', 'Entrada')
                                    turno_mostrar = row.get('Turno', 'N/A')
                                    estado_mostrar = row.get('Estado', 'N/A')
                                    hora_mostrar = row.get('Hora', '00:00:00')
                                    
                                    c1.write(f"**{tipo_mostrar}** ({turno_mostrar})")
                                    nueva_hora = c2.text_input("Hora (HH:MM:SS)", value=hora_mostrar, key=f"h_{idx}")
                                    estados_posibles = ["A tiempo", "Tarde", "Salida", "N/A"]
                                    idx_estado = estados_posibles.index(estado_mostrar) if estado_mostrar in estados_posibles else 3
                                    nuevo_estado = c3.selectbox("Estado", estados_posibles, index=idx_estado, key=f"e_{idx}")
                                    
                                    if c4.button("💾 Guardar", key=f"btn_{idx}"):
                                        df_edicion.at[idx, 'Hora'] = nueva_hora
                                        df_edicion.at[idx, 'Estado'] = nuevo_estado
                                        df_edicion.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                        st.success("¡Modificado!")
                                        st.rerun()
                            
                            st.write("---")
                            if st.button("🗑️ Eliminar TODOS los registros de este empleado en esta fecha"):
                                df_limpio = df_edicion.drop(indices_afectados)
                                df_limpio.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                st.success("¡Registros eliminados!")
                                st.rerun()
            else:
                st.info("La base de datos está vacía.")

        # TAB 3: PERSONAL
        with tab_personal:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.subheader("Nómina")
                for emp in sorted(lista_empleados):
                    st.write(f"- **{emp}** | {'📱 Vinculado' if emp in dispositivos_vinculados else '⚠️ Libre'}")
            with col_p2:
                st.subheader("Acciones")
                nuevo_emp = st.text_input("Nuevo empleado:")
                if st.button("➕ Agregar Empleado") and nuevo_emp:
                    if nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                        st.rerun()
                emp_desv = st.selectbox("Liberar celular de:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                if st.button("🔓 Desvincular") and emp_desv != "Seleccionar...":
                    del dispositivos_vinculados[emp_desv]
                    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                    st.rerun()

        # TAB 4: LOCALES Y TURNOS
        with tab_locales:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("📍 Sucursales")
                for loc in lista_locales.keys(): st.write(f"- **{loc}**")
                n_loc = st.text_input("Nueva Sucursal:")
                lat_loc = st.number_input("Latitud:", format="%.6f")
                lon_loc = st.number_input("Longitud:", format="%.6f")
                if st.button("➕ Agregar Local") and n_loc:
                    lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc}
                    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(lista_locales, f)
                    st.rerun()
            with col_l2:
                st.subheader("🕒 Turnos")
                for turno, hora in lista_turnos.items(): st.write(f"- **{turno}** | {hora}")
                n_turno = st.text_input("Nuevo Turno:")
                h_turno = st.time_input("Ingreso:")
                if st.button("➕ Crear Turno") and n_turno:
                    lista_turnos[n_turno] = h_turno.strftime("%H:%M")
                    with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                    st.rerun()

        # TAB 5: AJUSTES GLOBALES
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("📢 Mensaje del Administrador")
                st.write("Este texto aparecerá resaltado cuando los empleados abran la app. Dejalo en blanco para ocultarlo.")
                nuevo_mensaje = st.text_area("Mensaje del día:", value=config_app.get("mensaje_dia", ""))
                
                st.markdown("---")
                st.subheader("⏱️ Reglas")
                req_salida = st.checkbox("Requerir 'Marcar Salida'", value=config_app.get("requiere_salida", True))
                nueva_tolerancia = st.number_input("Minutos de tolerancia tarde:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 15)))

                if st.button("💾 Guardar Toda la Configuración"):
                    config_app["mensaje_dia"] = nuevo_mensaje
                    config_app["requiere_salida"] = req_salida
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                    st.success("¡Ajustes guardados!")
                    st.rerun()

            with col_aj2:
                st.subheader("🔑 Seguridad")
                nc = st.text_input("Nueva contraseña:", type="password")
                rc = st.text_input("Repetir contraseña:", type="password")
                if st.button("🔒 Cambiar Contraseña"):
                    if nc == rc and nc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.success("Contraseña actualizada.")
                    else: st.error("Error en las contraseñas.")
