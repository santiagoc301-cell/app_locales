import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json

st.set_page_config(page_title="Gestión de Personal Vet", page_icon="🐾", layout="wide")

# ==========================================
# 1. ARCHIVOS DE BASE DE DATOS Y CONFIG
# ==========================================
ARCHIVO_EMPLEADOS = "empleados.json"
ARCHIVO_DISPOSITIVOS = "dispositivos.json"
ARCHIVO_LOCALES = "locales.json"
ARCHIVO_TURNOS = "turnos.json"
ARCHIVO_ASISTENCIA = "asistencia.csv"
ARCHIVO_CONFIG = "config.json"
RADIO_MAXIMO_METROS = 50

# --- Cargar Configuración (Admin) ---
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {"admin_password": "1234", "tolerancia_minutos": 15, "requiere_salida": True}
    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f:
    config_app = json.load(f)
# Parches de actualización de versión
if "tolerancia_minutos" not in config_app: config_app["tolerancia_minutos"] = 15
if "requiere_salida" not in config_app: config_app["requiere_salida"] = True

# --- Cargar Empleados ---
if not os.path.exists(ARCHIVO_EMPLEADOS):
    empleados_iniciales = ["Abril", "Agustina", "Alejandro", "Camila", "Claudia", "Daniela", "Debora", "Franco", "Macarena", "Mario", "Nicolás", "Paola", "Viviana"]
    with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(empleados_iniciales, f)
with open(ARCHIVO_EMPLEADOS, 'r') as f:
    lista_empleados = json.load(f)
if isinstance(lista_empleados, dict): lista_empleados = list(lista_empleados.keys())

# --- Cargar Dispositivos ---
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f: dispositivos_vinculados = json.load(f)

# --- Cargar Sucursales ---
if not os.path.exists(ARCHIVO_LOCALES):
    locales_iniciales = {
        "Local 1 - Zuviria 142": {"lat": -24.788296, "lon": -65.409429},
        "Local 2 - Independencia 848": {"lat": -24.808264, "lon": -65.404947},
        "Local 3 - Güemes 1027": {"lat": -24.785736, "lon": -65.416646}
    }
    with open(ARCHIVO_LOCALES, 'w') as f: json.dump(locales_iniciales, f)
with open(ARCHIVO_LOCALES, 'r') as f: lista_locales = json.load(f)

# --- Cargar Turnos ---
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
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2865/2865784.png", width=100)
st.sidebar.title("Sistema Vet")
pestaña = st.sidebar.radio("Menú Principal:", ["⏱️ Fichar Asistencia", "⚙️ Panel Administrativo"])

# ==========================================
# 4. PANTALLA: MARCAR ASISTENCIA
# ==========================================
if pestaña == "⏱️ Fichar Asistencia":
    st.title("⏱️ Portal de Asistencia")
    
    if not device_id:
        st.info("🔄 Autenticando dispositivo de forma segura...")
    else:
        empleado_en_celu = None
        for emp, dev in dispositivos_vinculados.items():
            if dev == device_id:
                empleado_en_celu = emp
                break
        
        if empleado_en_celu:
            st.success(f"👋 ¡Hola **{empleado_en_celu}**! Tu identidad está verificada.")
            
            st.markdown("### 📋 Completá tus datos de ingreso")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                local_seleccionado = st.selectbox("📍 ¿En qué sucursal estás?", ["Seleccionar..."] + list(lista_locales.keys()))
            with col_sel2:
                turno_seleccionado = st.selectbox("🕒 ¿Qué turno hacés?", ["Seleccionar..."] + list(lista_turnos.keys()))
            
            st.markdown("---")
            
            if local_seleccionado != "Seleccionar..." and turno_seleccionado != "Seleccionar...":
                st.info("🛰️ Obteniendo coordenadas GPS...")
                ubicacion = get_geolocation()
                
                if ubicacion:
                    coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                    coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                    distancia = geodesic(coord_usuario, coord_local).meters
                    
                    if distancia <= RADIO_MAXIMO_METROS:
                        st.success(f"✅ GPS OK: Te encontrás a {distancia:.1f}m del local.")
                        
                        marcar = False
                        tipo_fichaje = ""
                        
                        # VALIDACIÓN ANTI-DOBLE FICHAJE
                        zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                        ahora = datetime.datetime.now(zona_arg)
                        fecha_hoy = ahora.strftime("%Y-%m-%d")
                        
                        ya_ficho_entrada = False
                        if os.path.exists(ARCHIVO_ASISTENCIA):
                            df_temp = pd.read_csv(ARCHIVO_ASISTENCIA)
                            filtro = df_temp[(df_temp["Empleado"] == empleado_en_celu) & 
                                             (df_temp["Fecha"] == fecha_hoy) & 
                                             (df_temp["Turno"] == turno_seleccionado) & 
                                             (df_temp["Tipo"] == "Entrada")]
                            if not filtro.empty:
                                ya_ficho_entrada = True

                        # RENDERIZADO DE BOTONES SEGÚN CONFIGURACIÓN
                        if config_app.get("requiere_salida", True):
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("🟢 MARCAR ENTRADA", use_container_width=True):
                                    if ya_ficho_entrada:
                                        st.error("⚠️ Ya marcaste tu entrada para este turno el día de hoy.")
                                    else:
                                        marcar = True
                                        tipo_fichaje = "Entrada"
                            with col_btn2:
                                if st.button("🔴 MARCAR SALIDA", use_container_width=True):
                                    if not ya_ficho_entrada:
                                        st.warning("⚠️ Ojo: Estás marcando salida sin haber registrado una entrada para este turno.")
                                    marcar = True
                                    tipo_fichaje = "Salida"
                        else:
                            # Solo mostrar Entrada si está desactivada la Salida
                            col_centrada, _, _ = st.columns([2, 1, 1])
                            with col_centrada:
                                if st.button("🟢 REGISTRAR MI ENTRADA HOY", use_container_width=True):
                                    if ya_ficho_entrada:
                                        st.error("⚠️ Ya marcaste tu entrada para este turno el día de hoy.")
                                    else:
                                        marcar = True
                                        tipo_fichaje = "Entrada"
                                        
                        # LÓGICA DE GUARDADO
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
                                "Fecha": [fecha_hoy], "Hora": [hora], "Empleado": [empleado_en_celu],
                                "Sucursal": [local_seleccionado], "Turno": [turno_seleccionado],
                                "Tipo": [tipo_fichaje], "Estado": [estado_llegada], "Distancia_m": [round(distancia, 1)]
                            }
                            df_nuevo = pd.DataFrame(registro)
                            if not os.path.exists(ARCHIVO_ASISTENCIA):
                                df_nuevo.to_csv(ARCHIVO_ASISTENCIA, index=False)
                            else:
                                df_existente = pd.read_csv(ARCHIVO_ASISTENCIA)
                                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                                df_final.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                
                            st.balloons() if tipo_fichaje == "Entrada" and estado_llegada == "A tiempo" else None
                            st.success(f"¡Excelente! Fichaje de {tipo_fichaje} guardado a las {hora}.")
                            
                            if estado_llegada == "Tarde":
                                st.warning(f"⚠️ Llegada registrada fuera del margen de {config_app['tolerancia_minutos']} minutos. Estado: Tarde.")
                    else:
                        st.error(f"❌ Ubicación inválida. El GPS detecta que estás a {distancia:.1f} metros del local.")
                else:
                    st.warning("⚠️ Aguardando señal GPS del celular... Asegurate de tener la ubicación activada.")
            else:
                st.info("👆 Por favor, completá los campos de Sucursal y Turno para habilitar los botones.")
                
            # Historial visual personal
            st.markdown("---")
            st.markdown("#### 📜 Mi registro de hoy")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                fecha_hoy = datetime.datetime.now(zona_arg).strftime("%Y-%m-%d")
                df_hist = pd.read_csv(ARCHIVO_ASISTENCIA)
                df_emp = df_hist[(df_hist["Empleado"] == empleado_en_celu) & (df_hist["Fecha"] == fecha_hoy)]
                
                if not df_emp.empty:
                    st.dataframe(df_emp[["Hora", "Sucursal", "Turno", "Tipo", "Estado"]], hide_index=True, use_container_width=True)
                else:
                    st.write("No tenés fichajes registrados el día de hoy.")

        # CASO B: Celular NO vinculado
        else:
            st.warning("⚠️ **Dispositivo no reconocido.**")
            st.write("Esta es la primera vez que abrís el sistema en este teléfono. Por seguridad, vinculalo a tu nombre de usuario.")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]
            if empleados_disponibles:
                emp_vincular = st.selectbox("👤 Elegí tu nombre en la lista:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Atar celular a mi cuenta personal"):
                    if emp_vincular != "Seleccionar...":
                        dispositivos_vinculados[emp_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        st.success("¡Dispositivo vinculado permanentemente! Recargando...")
                        st.rerun()
            else:
                st.error("Todos los perfiles de la veterinaria ya tienen un celular asignado.")

# ==========================================
# 5. PANEL ADMINISTRADOR
# ==========================================
elif pestaña == "⚙️ Panel Administrativo":
    st.title("⚙️ Centro de Control")
    password_ingresada = st.text_input("Ingresá tu clave maestra:", type="password")
    
    if password_ingresada == config_app["admin_password"]:
        # --- DASHBOARD METRICS ---
        st.markdown("---")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        cant_empleados = len(lista_empleados)
        cant_celulares = len(dispositivos_vinculados.keys())
        
        fichajes_hoy = 0
        if os.path.exists(ARCHIVO_ASISTENCIA):
            zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
            hoy_str = datetime.datetime.now(zona_arg).strftime("%Y-%m-%d")
            df_dash = pd.read_csv(ARCHIVO_ASISTENCIA)
            fichajes_hoy = len(df_dash[df_dash["Fecha"] == hoy_str])

        metric_col1.metric("👥 Plantilla Total", f"{cant_empleados} Empleados")
        metric_col2.metric("📱 Celulares Vinculados", f"{cant_celulares}/{cant_empleados}")
        metric_col3.metric("📝 Fichajes Hoy", fichajes_hoy)
        st.markdown("---")
        
        # PESTAÑAS DEL PANEL
        tab_reportes, tab_personal, tab_locales, tab_ajustes = st.tabs(["📊 Descargar Datos", "👥 Equipo", "📍 Config. Locales/Turnos", "⚙️ Configuración Global"])
        
        # --- TAB: REPORTES ---
        with tab_reportes:
            st.subheader("Generador de Reportes")
            st.write("Elegí las fechas de inicio y fin para descargar la planilla oficial de la veterinaria.")
            if os.path.exists(ARCHIVO_ASISTENCIA):
                rango_fechas = st.date_input("📅 Seleccionar Periodo (Desde - Hasta):", value=(datetime.date.today(), datetime.date.today()))
                
                if len(rango_fechas) == 2:
                    f_inicio, f_fin = rango_fechas
                    df_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                    df_full['Fecha_Temp'] = pd.to_datetime(df_full['Fecha']).dt.date
                    df_descarga = df_full[(df_full['Fecha_Temp'] >= f_inicio) & (df_full['Fecha_Temp'] <= f_fin)].drop(columns=['Fecha_Temp'])
                    
                    if not df_descarga.empty:
                        st.download_button(
                            label="📥 DESCARGAR PLANILLA EN EXCEL (CSV)",
                            data=df_descarga.to_csv(index=False).encode('utf-8'),
                            file_name=f"Reporte_Vet_{f_inicio}_al_{f_fin}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.markdown("##### Vista Previa de los Datos:")
                        st.dataframe(df_descarga, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No hay movimientos registrados en esas fechas.")
            else:
                st.info("La base de datos está limpia. Aún no hay fichajes.")
                
        # --- TAB: PERSONAL ---
        with tab_personal:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.subheader("Estado del Equipo")
                for emp in sorted(lista_empleados):
                    estado = "🟢 App Lista" if emp in dispositivos_vinculados else "🔴 Falta vincular"
                    st.write(f"- **{emp}** | {estado}")
            
            with col_p2:
                st.subheader("Administrar Personal")
                nuevo_empleado = st.text_input("Ingresar nuevo empleado (Nombre):")
                if st.button("➕ Alta de Empleado"):
                    if nuevo_empleado and nuevo_empleado not in lista_empleados:
                        lista_empleados.append(nuevo_empleado)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                        st.rerun()
                
                st.markdown("---")
                emp_desvincular = st.selectbox("Formatear celular de:", ["Seleccionar..."] + list(dispositivos_vinculados.keys()))
                if st.button("🔓 Liberar Dispositivo"):
                    if emp_desvincular != "Seleccionar...":
                        del dispositivos_vinculados[emp_desvincular]
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        st.success("Teléfono desvinculado. El empleado podrá registrar uno nuevo.")
                        st.rerun()
                        
                st.markdown("---")
                borrar_emp = st.selectbox("Dar de baja empleado:", ["Seleccionar..."] + sorted(lista_empleados))
                if st.button("🗑️ Eliminar Definitivamente"):
                    if borrar_emp != "Seleccionar...":
                        lista_empleados.remove(borrar_emp)
                        if borrar_emp in dispositivos_vinculados:
                            del dispositivos_vinculados[borrar_emp]
                            with open(ARCHIVO_DISPOSITIVOS, 'w') as f: json.dump(dispositivos_vinculados, f)
                        with open(ARCHIVO_EMPLEADOS, 'w') as f: json.dump(lista_empleados, f)
                        st.rerun()
                        
        # --- TAB: LOCALES Y TURNOS ---
        with tab_locales:
            col_l1, col_l2 = st.columns(2)
            
            with col_l1:
                st.subheader("📍 Sedes Habilitadas")
                for loc in lista_locales.keys(): st.write(f"- **{loc}**")
                st.markdown("---")
                n_loc = st.text_input("Agregar Sucursal (Nombre):")
                lat_loc = st.number_input("Latitud GPS:", format="%.6f")
                lon_loc = st.number_input("Longitud GPS:", format="%.6f")
                if st.button("➕ Guardar Sucursal"):
                    if n_loc:
                        lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc}
                        with open(ARCHIVO_LOCALES, 'w') as f: json.dump(lista_locales, f)
                        st.rerun()
                        
                borrar_loc = st.selectbox("Cerrar sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Sede"):
                    if borrar_loc != "Seleccionar...":
                        del lista_locales[borrar_loc]
                        with open(ARCHIVO_LOCALES, 'w') as f: json.dump(lista_locales, f)
                        st.rerun()
                        
            with col_l2:
                st.subheader("🕒 Cuadro de Turnos")
                for turno, hora in lista_turnos.items(): st.write(f"- **{turno}** | Ingreso estricto: {hora}")
                st.markdown("---")
                n_turno = st.text_input("Nuevo Turno (Ej: Rotativo Noche):")
                try: h_turno_default = datetime.time(9, 0)
                except: h_turno_default = datetime.time(9, 0)
                h_turno = st.time_input("Hora Oficial de Ingreso:", h_turno_default)
                
                if st.button("➕ Guardar Turno"):
                    if n_turno:
                        lista_turnos[n_turno] = h_turno.strftime("%H:%M")
                        with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                        st.rerun()
                        
                borrar_turno = st.selectbox("Borrar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Horario"):
                    if borrar_turno != "Seleccionar...":
                        del lista_turnos[borrar_turno]
                        with open(ARCHIVO_TURNOS, 'w') as f: json.dump(lista_turnos, f)
                        st.rerun()
                        
        # --- TAB: AJUSTES ---
        with tab_ajustes:
            col_aj1, col_aj2 = st.columns(2)
            
            with col_aj1:
                st.subheader("⏱️ Reglas de Asistencia")
                st.info("Configurá cómo se comporta la aplicación para el personal.")
                
                # Checkbox para requerir o no el botón de salida
                req_salida = st.checkbox("Habilitar botón de 'Marcar Salida'", value=config_app.get("requiere_salida", True))
                
                st.write("---")
                # Selector de tolerancia
                st.write("**Minutos de Tolerancia:**")
                st.caption("Tiempo de gracia luego de la hora de ingreso oficial antes de marcar 'Llegada Tarde'.")
                nueva_tolerancia = st.number_input("Minutos:", min_value=0, max_value=60, value=int(config_app.get("tolerancia_minutos", 15)))
                
                if st.button("💾 Guardar Reglas"):
                    config_app["requiere_salida"] = req_salida
                    config_app["tolerancia_minutos"] = nueva_tolerancia
                    with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                    st.success(f"¡Configuración de sistema actualizada con éxito!")
                    st.rerun()
                
            with col_aj2:
                st.subheader("🔑 Seguridad")
                st.write("Modificar la clave de acceso al Panel Administrativo.")
                nc = st.text_input("Nueva contraseña:", type="password")
                rc = st.text_input("Repetir contraseña:", type="password")
                if st.button("🔒 Actualizar Credenciales"):
                    if nc and nc == rc:
                        config_app["admin_password"] = nc
                        with open(ARCHIVO_CONFIG, 'w') as f: json.dump(config_app, f)
                        st.success("¡Contraseña maestra actualizada!")
                    else:
                        st.error("Las contraseñas no coinciden. Verificalas.")

    elif password_ingresada == "":
        st.info("🔒 Ingresá la credencial maestra para acceder al sistema.")
    else:
        st.error("❌ Credencial denegada.")
