import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json

st.set_page_config(
    page_title="Control de Asistencia",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno y limpio
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    .sub-text {
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
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

# Configuración Inicial
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {
        "admin_password": "1234",
        "admin_email": "admin@vet.com",
        "tolerancia_minutos": 15,
        "requiere_salida": True
    }
    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(config_inicial, f)

with open(ARCHIVO_CONFIG, 'r') as f:
    config_app = json.load(f)

# Parches de compatibilidad
if "tolerancia_minutos" not in config_app:
    config_app["tolerancia_minutos"] = 15
if "requiere_salida" not in config_app:
    config_app["requiere_salida"] = True

# Empleados
if not os.path.exists(ARCHIVO_EMPLEADOS):
    empleados_iniciales = [
        "Abril", "Agustina", "Alejandro", "Camila", "Claudia", "Daniela",
        "Debora", "Franco", "Macarena", "Mario", "Nicolás", "Paola", "Viviana"
    ]
    with open(ARCHIVO_EMPLEADOS, 'w') as f:
        json.dump(empleados_iniciales, f)

with open(ARCHIVO_EMPLEADOS, 'r') as f:
    lista_empleados = json.load(f)
if isinstance(lista_empleados, dict):
    lista_empleados = list(lista_empleados.keys())

# Dispositivos
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
        json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f:
    dispositivos_vinculados = json.load(f)

# Locales
if not os.path.exists(ARCHIVO_LOCALES):
    locales_iniciales = {
        "Local 1 - Zuviria 142": {"lat": -24.788296, "lon": -65.409429},
        "Local 2 - Independencia 848": {"lat": -24.808264, "lon": -65.404947},
        "Local 3 - Güemes 1027": {"lat": -24.785736, "lon": -65.416646}
    }
    with open(ARCHIVO_LOCALES, 'w') as f:
        json.dump(locales_iniciales, f)
with open(ARCHIVO_LOCALES, 'r') as f:
    lista_locales = json.load(f)

# Turnos
if not os.path.exists(ARCHIVO_TURNOS):
    turnos_iniciales = {"Mañana": "08:30", "Tarde": "16:30"}
    with open(ARCHIVO_TURNOS, 'w') as f:
        json.dump(turnos_iniciales, f)
with open(ARCHIVO_TURNOS, 'r') as f:
    lista_turnos = json.load(f)

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
    st.markdown('<div class="sub-text">Completá los datos y validá tu ubicación para registrar ingreso o egreso.</div>', unsafe_allow_html=True)

    if not device_id:
        st.info("🔄 Reconociendo dispositivo...")
    else:
        empleado_en_celu = None
        for emp, dev in dispositivos_vinculados.items():
            if dev == device_id:
                empleado_en_celu = emp
                break

        # A. DISPOSITIVO RECONOCIDO
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
                        st.success(f"✅ Ubicación validada: Estás en {local_seleccionado} (a {distancia:.1f} m).")

                        zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                        ahora = datetime.datetime.now(zona_arg)
                        fecha_hoy = ahora.strftime("%Y-%m-%d")

                        # Verificación de entrada previa para evitar doble fichaje
                        ya_ficho_entrada = False
                        if os.path.exists(ARCHIVO_ASISTENCIA):
                            df_temp = pd.read_csv(ARCHIVO_ASISTENCIA)
                            filtro = df_temp[
                                (df_temp["Empleado"] == empleado_en_celu) &
                                (df_temp["Fecha"] == fecha_hoy) &
                                (df_temp["Turno"] == turno_seleccionado) &
                                (df_temp["Tipo"] == "Entrada")
                            ]
                            if not filtro.empty:
                                ya_ficho_entrada = True

                        marcar = False
                        tipo_fichaje = ""

                        # Renderizado según si la salida está habilitada
                        if config_app.get("requiere_salida", True):
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("🟢 MARCAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada:
                                        st.error("⚠️ Ya registraste la entrada para este turno el día de hoy.")
                                    else:
                                        marcar = True
                                        tipo_fichaje = "Entrada"
                            with col_b2:
                                if st.button("🔴 MARCAR SALIDA", use_container_width=True):
                                    marcar = True
                                    tipo_fichaje = "Salida"
                        else:
                            col_centrada, _, _ = st.columns([2, 1, 1])
                            with col_centrada:
                                if st.button("🟢 MARCAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada:
                                        st.error("⚠️ Ya registraste la entrada para este turno el día de hoy.")
                                    else:
                                        marcar = True
                                        tipo_fichaje = "Entrada"

                        if marcar:
                            hora = ahora.strftime("%H:%M:%S")
                            estado_llegada = "N/A"

                            if tipo_fichaje == "Entrada":
                                hora_turno_obj = datetime.datetime.strptime(lista_turnos[turno_seleccionado], "%H:%M").time()
                                dt_turno = datetime.datetime.combine(ahora.date(), hora_turno_obj)
                                dt_turno = dt_turno.replace(tzinfo=zona_arg)
                                dt_limite = dt_turno + datetime.timedelta(minutes=int(config_app["tolerancia_minutos"]))

                                if ahora > dt_limite:
                                    estado_llegada = "Tarde"
                                else:
                                    estado_llegada = "A tiempo"
                            elif tipo_fichaje == "Salida":
                                estado_llegada = "Salida"

                            registro = {
                                "Fecha": [fecha_hoy],
                                "Hora": [hora],
                                "Empleado": [empleado_en_celu],
                                "Sucursal": [local_seleccionado],
                                "Turno": [turno_seleccionado],
                                "Tipo": [tipo_fichaje],
                                "Estado": [estado_llegada],
                                "Distancia_m": [round(distancia, 1)]
                            }
                            df_nuevo = pd.DataFrame(registro)

                            if not os.path.exists(ARCHIVO_ASISTENCIA):
                                df_nuevo.to_csv(ARCHIVO_ASISTENCIA, index=False)
                            else:
                                df_existente = pd.read_csv(ARCHIVO_ASISTENCIA)
                                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                                df_final.to_csv(ARCHIVO_ASISTENCIA, index=False)

                            st.balloons() if tipo_fichaje == "Entrada" and estado_llegada == "A tiempo" else None
                            st.success(f"¡{tipo_fichaje} registrada correctamente a las {hora}!")

                            if estado_llegada == "Tarde":
                                st.warning(f"⚠️ Llegada registrada como 'Tarde' (Tolerancia: {config_app['tolerancia_minutos']} min).")
                    else:
                        st.error(f"❌ Estás fuera del rango permitido. Distancia al local: {distancia:.1f} metros.")
                else:
                    st.warning("⚠️ Esperando señal GPS. Verificá que la ubicación esté activada en el navegador.")
            else:
                st.info("👆 Seleccioná la sucursal y el turno para habilitar los botones.")

            # Historial personal del día
            st.markdown("---")
            st.subheader("📜 Tus registros de hoy")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                fecha_hoy = datetime.datetime.now(zona_arg).strftime("%Y-%m-%d")
                df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha"] == fecha_hoy)]

                if not df_emp.empty:
                    st.dataframe(df_emp[["Hora", "Sucursal", "Turno", "Tipo", "Estado"]], hide_index=True, use_container_width=True)
                else:
                    st.write("Aún no registraste movimientos hoy.")

        # B. DISPOSITIVO NO VINCULADO
        else:
            st.warning("⚠️ **Dispositivo no registrado.**")
            st.write("Es la primera vez que abrís el sistema desde este celular. Seleccioná tu nombre para vincularlo a tu cuenta.")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]

            if empleados_disponibles:
                emp_vincular = st.selectbox("👤 Tu nombre:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Vincular este Celular"):
                    if emp_vincular != "Seleccionar...":
                        dispositivos_vinculados[emp_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
                            json.dump(dispositivos_vinculados, f)
                        st.success("¡Dispositivo vinculado con éxito!")
                        st.rerun()
            else:
                st.error("Todos los empleados ya cuentan con un celular vinculado.")

# ==========================================
# 5. PANTALLA: PANEL ADMINISTRADOR
# ==========================================
elif pestaña == "⚙️ Panel de Administrador":
    st.markdown('<div class="main-title">⚙️ Panel de Administración</div>', unsafe_allow_html=True)
    password_ingresada = st.text_input("Ingresá la contraseña de administrador:", type="password")

    if password_ingresada == config_app["admin_password"]:
        st.success("Acceso autenticado.")

        # Resumen Estadístico
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        cant_empleados = len(lista_empleados)
        cant_celulares = len(dispositivos_vinculados.keys())
        fichajes_hoy = 0

        if os.path.exists(ARCHIVO_ASISTENCIA):
            zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
            hoy_str = datetime.datetime.now(zona_arg).strftime("%Y-%m-%d")
            df_dash = pd.read_csv(ARCHIVO_ASISTENCIA)
            fichajes_hoy = len(df_dash[df_dash["Fecha"] == hoy_str])

        m1.metric("👥 Total Empleados", f"{cant_empleados}")
        m2.metric("📱 Dispositivos Vinculados", f"{cant_celulares}/{cant_empleados}")
        m3.metric("📝 Fichajes Hoy", fichajes_hoy)
        st.markdown("---")

        tab_reportes, tab_personal, tab_locales, tab_ajustes = st.tabs([
            "📊 Reportes y Descargas", "👥 Gestión de Personal", "📍 Sucursales y Turnos", "⚙️ Configuración"
        ])

        # TAB 1: REPORTES
        with tab_reportes:
            st.subheader("📊 Consulta y Exportación de Registros")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                rango_fechas = st.date_input(
                    "📅 Seleccionar rango de fechas:",
                    value=(datetime.date.today(), datetime.date.today())
                )

                if len(rango_fechas) == 2:
                    f_inicio, f_fin = rango_fechas
                    df_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_full['Fecha_Temp'] = pd.to_datetime(df_full['Fecha']).dt.date
                    df_descarga = df_full[
                        (df_full['Fecha_Temp'] >= f_inicio) & (df_full['Fecha_Temp'] <= f_fin)
                    ].drop(columns=['Fecha_Temp'])

                    if not df_descarga.empty:
                        st.download_button(
                            label=f"📥 Descargar CSV ({f_inicio.strftime('%d/%m/%Y')} al {f_fin.strftime('%d/%m/%Y')})",
                            data=df_descarga.to_csv(index=False).encode('utf-8'),
                            file_name=f"Reporte_Asistencia_{f_inicio}_al_{f_fin}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.markdown("##### Vista Previa:")
                        st.dataframe(df_descarga, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No hay registros en el rango de fechas seleccionado.")
            else:
                st.info("Aún no hay registros en la base de datos.")

        # TAB 2: PERSONAL
        with tab_personal:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.subheader("Nómina y Dispositivos")
                for emp in sorted(lista_empleados):
                    estado = "📱 Vinculado" if emp in dispositivos_vinculados else "⚠️ Libre"
                    st.write(f"- **{emp}** ({estado})")

            with col_p2:
                st.subheader("Acciones de Personal")
                nuevo_emp = st.text_input("Nombre del nuevo empleado:")
                if st.button("➕ Agregar Empleado"):
                    if nuevo_emp and nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f:
                            json.dump(lista_empleados, f)
                        st.success(f"{nuevo_emp} agregado.")
                        st.rerun()

                st.markdown("---")
                emp_desv = st.selectbox("Desvincular dispositivo de:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                if st.button("🔓 Desvincular Celular"):
                    if emp_desv != "Seleccionar...":
                        del dispositivos_vinculados[emp_desv]
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
                            json.dump(dispositivos_vinculados, f)
                        st.success(f"Dispositivo de {emp_desv} liberado.")
                        st.rerun()

                st.markdown("---")
                borrar_emp = st.selectbox("Eliminar empleado de la nómina:", ["Seleccionar..."] + sorted(lista_empleados))
                if st.button("🗑️ Eliminar Empleado"):
                    if borrar_emp != "Seleccionar...":
                        lista_empleados.remove(borrar_emp)
                        if borrar_emp in dispositivos_vinculados:
                            del dispositivos_vinculados[borrar_emp]
                            with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
                                json.dump(dispositivos_vinculados, f)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f:
                            json.dump(lista_empleados, f)
                        st.success(f"{borrar_emp} eliminado.")
                        st.rerun()

        # TAB 3: SUCURSALES Y TURNOS
        with tab_locales:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("📍 Sucursales Activas")
                for loc in lista_locales.keys():
                    st.write(f"- **{loc}**")

                st.markdown("---")
                n_loc = st.text_input("Nombre de la nueva sucursal:")
                lat_loc = st.number_input("Latitud GPS:", format="%.6f")
                lon_loc = st.number_input("Longitud GPS:", format="%.6f")
                if st.button("➕ Guardar Sucursal"):
                    if n_loc:
                        lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc}
                        with open(ARCHIVO_LOCALES, 'w') as f:
                            json.dump(lista_locales, f)
                        st.success(f"Sucursal {n_loc} guardada.")
                        st.rerun()

                borrar_loc = st.selectbox("Eliminar sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Sucursal"):
                    if borrar_loc != "Seleccionar...":
                        del lista_locales[borrar_loc]
                        with open(ARCHIVO_LOCALES, 'w') as f:
                            json.dump(lista_locales, f)
                        st.success("Sucursal eliminada.")
                        st.rerun()

            with col_l2:
                st.subheader("🕒 Turnos y Horarios")
                for turno, hora in lista_turnos.items():
                    st.write(f"- **{turno}** | Ingreso: {hora}")

                st.markdown("---")
                n_turno = st.text_input("Nombre del nuevo turno (ej. Noche):")
                h_turno = st.time_input("Hora oficial de ingreso:", datetime.time(8, 30))
                if st.button("➕ Guardar Turno"):
                    if n_turno:
                        lista_turnos[n_turno] = h_turno.strftime("%H:%M")
                        with open(ARCHIVO_TURNOS, 'w') as f:
                            json.dump(lista_turnos, f)
                        st.success(f"Turno {n_turno} guardado.")
                        st.rerun()

                borrar_turno = st.selectbox("Eliminar turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno"):
                    if borrar_turno != "Seleccionar...":
                        del lista_turnos[borrar_turno]
                        with open(ARCHIVO_TURNOS, 'w') as f:
                            json.dump(lista_turnos, f)
                        st.success("Turno eliminado.")
                        st.rerun()

        # TAB 4: AJUSTES GLOBALES
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("⏱️ Reglas de Registro")
                req_salida = st.checkbox(
                    "Habilitar botón de 'Marcar Salida'",
                    value=config_app.get("requiere_salida", True),
                    help="Si se desmarca, los empleados solo registrarán su horario de entrada."
                )

                st.markdown("---")
                st.write("**Margen de Tolerancia (Minutos):**")
                nueva_tolerancia = st.number_input(
                    "Minutos de gracia para marcar 'A tiempo':",
                    min_value=0,
                    max_value=60,
                    value=int(config_app.get("tolerancia_minutos", 15))
                )

                if st.button("💾 Guardar Reglas de Registro"):
                    config_app["requiere_salida"] = req_salida
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    with open(ARCHIVO_CONFIG, 'w') as f:
                        json.dump(config_app, f)
                    st.success("¡Configuración actualizada correctamente!")
                    st.rerun()

            with col_aj2:
                st.subheader("🔑 Seguridad")
                st.write("Cambiar contraseña de administrador:")
                nc = st.text_input("Nueva contraseña:", type="password")
                rc = st.text_input("Repetir nueva contraseña:", type="password")
                if st.button("🔒 Actualizar Contraseña"):
                    if nc and nc == rc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f:
                            json.dump(config_app, f)
                        st.success("Contraseña actualizada exitosamente.")
                    else:
                        st.error("Las contraseñas no coinciden.")

    elif password_ingresada == "":
        st.info("🔒 Ingresá la contraseña para acceder al panel (Por defecto: 1234).")
    else:
        st.error("❌ Contraseña incorrecta.")
