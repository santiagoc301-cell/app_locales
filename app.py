import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import os
import json

st.set_page_config(page_title="Sistema de Asistencia", page_icon="⏱️", layout="wide")

# ==========================================
# 1. ARCHIVOS DE BASE DE DATOS Y CONFIG
# ==========================================
ARCHIVO_EMPLEADOS = "empleados.json"
ARCHIVO_DISPOSITIVOS = "dispositivos.json"
ARCHIVO_LOCALES = "locales.json"
ARCHIVO_ASISTENCIA = "asistencia.csv"
ARCHIVO_CONFIG = "config.json"
RADIO_MAXIMO_METROS = 50

# --- Cargar o crear Configuración (Admin) ---
if not os.path.exists(ARCHIVO_CONFIG):
    config_inicial = {"admin_password": "1234", "admin_email": "josegarcia0187@gmail.com", "hora_limite": "09:15:00"}
    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(config_inicial, f)
with open(ARCHIVO_CONFIG, 'r') as f:
    config_app = json.load(f)

# Parche por si venimos de una versión anterior que no tenía hora límite
if "hora_limite" not in config_app:
    config_app["hora_limite"] = "09:15:00"
    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(config_app, f)

# --- Cargar Empleados ---
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

# --- Cargar Dispositivos ---
if not os.path.exists(ARCHIVO_DISPOSITIVOS):
    with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
        json.dump({}, f)
with open(ARCHIVO_DISPOSITIVOS, 'r') as f:
    dispositivos_vinculados = json.load(f)

# --- Cargar Sucursales ---
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

# ==========================================
# 2. OBTENER ID DEL CELULAR
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
st.sidebar.title("Navegación")
pestaña = st.sidebar.radio("Ir a:", ["⏱️ Marcar Asistencia", "⚙️ Panel de Administrador"])

# ==========================================
# 4. PANTALLA: MARCAR ASISTENCIA
# ==========================================
if pestaña == "⏱️ Marcar Asistencia":
    st.title("⏱️ Registro Diario de Asistencia")
    
    if not device_id:
        st.info("🔄 Reconociendo dispositivo...")
    else:
        empleado_en_celu = None
        for emp, dev in dispositivos_vinculados.items():
            if dev == device_id:
                empleado_en_celu = emp
                break
        
        if empleado_en_celu:
            st.success(f"📱 Dispositivo reconocido. Bienvenido/a, **{empleado_en_celu}**.")
            
            local_seleccionado = st.selectbox("📍 Seleccioná tu sucursal actual:", ["Seleccionar..."] + list(lista_locales.keys()))
            st.markdown("---")
            
            if local_seleccionado != "Seleccionar...":
                st.info("Buscando tu ubicación GPS...")
                ubicacion = get_geolocation()
                
                if ubicacion:
                    lat_usuario = ubicacion['coords']['latitude']
                    lon_usuario = ubicacion['coords']['longitude']
                    coord_usuario = (lat_usuario, lon_usuario)
                    coord_local = (lista_locales[local_seleccionado]["lat"], lista_locales[local_seleccionado]["lon"])
                    
                    distancia = geodesic(coord_usuario, coord_local).meters
                    
                    if distancia <= RADIO_MAXIMO_METROS:
                        st.success(f"✅ Estás en el local (a {distancia:.1f} metros).")
                        
                        col_b1, col_b2, col_b3 = st.columns([1,2,1])
                        with col_b2:
                            if st.button("🚀 MARCAR ENTRADA AHORA", use_container_width=True):
                                # Hora de Argentina (UTC-3)
                                zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
                                ahora = datetime.datetime.now(zona_arg)
                                fecha = ahora.strftime("%Y-%m-%d")
                                hora = ahora.strftime("%H:%M:%S")
                                
                                # Lógica de llegada tarde
                                hora_limite_dt = datetime.datetime.strptime(config_app["hora_limite"], "%H:%M:%S").time()
                                es_tarde = ahora.time() > hora_limite_dt
                                estado_llegada = "Tarde" if es_tarde else "A tiempo"
                                
                                registro = {
                                    "Fecha": [fecha],
                                    "Hora": [hora],
                                    "Empleado": [empleado_en_celu],
                                    "Sucursal": [local_seleccionado],
                                    "Distancia_Fichaje_m": [round(distancia, 1)],
                                    "Estado": [estado_llegada]
                                }
                                df_nuevo = pd.DataFrame(registro)
                                
                                # Guardar unificando datos viejos y nuevos
                                if not os.path.exists(ARCHIVO_ASISTENCIA):
                                    df_nuevo.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                else:
                                    df_existente = pd.read_csv(ARCHIVO_ASISTENCIA)
                                    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                                    df_final.to_csv(ARCHIVO_ASISTENCIA, index=False)
                                    
                                st.balloons()
                                st.success(f"¡Listo {empleado_en_celu}! Asistencia registrada a las {hora}.")
                                
                                if es_tarde:
                                    st.warning(f"⚠️ ATENCIÓN: Marcaste entrada fuera del horario límite ({config_app['hora_limite']}). Tu ingreso quedó registrado como 'Tarde'.")
                    else:
                        st.error(f"❌ No estás en el local. Estás a {distancia:.1f} metros de distancia.")
                else:
                    st.warning("⚠️ Esperando señal GPS del celular...")
        else:
            st.warning("⚠️ **Este celular aún no está registrado.** Por seguridad, vinculalo a tu cuenta personal por única vez.")
            empleados_disponibles = [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()]
            if empleados_disponibles:
                empleado_a_vincular = st.selectbox("👤 Seleccioná tu nombre:", ["Seleccionar..."] + empleados_disponibles)
                if st.button("🔗 Vincular este Celular a mi Cuenta"):
                    if empleado_a_vincular != "Seleccionar...":
                        dispositivos_vinculados[empleado_a_vincular] = device_id
                        with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
                            json.dump(dispositivos_vinculados, f)
                        st.success(f"¡Celular vinculado con éxito para {empleado_a_vincular}! Recargando...")
                        st.rerun()
                    else:
                        st.warning("Seleccioná tu nombre de la lista.")
            else:
                st.error("Todos los empleados ya tienen un celular vinculado.")

# ==========================================
# 5. PANTALLA: PANEL ADMINISTRADOR
# ==========================================
elif pestaña == "⚙️ Panel de Administrador":
    st.title("⚙️ Panel de Control - Acceso Restringido")
    
    password_ingresada = st.text_input("Ingresá la contraseña de administrador:", type="password")
    
    if password_ingresada == config_app["admin_password"]:
        st.success("¡Acceso autorizado!")
        st.markdown("---")
        
        # 1. VISUALIZACIÓN RÁPIDA POR DÍA
        st.header("👀 Ver Registros en Pantalla (Día por Día)")
        if os.path.exists(ARCHIVO_ASISTENCIA):
            df_asistencia = pd.read_csv(ARCHIVO_ASISTENCIA)
            fecha_seleccionada = st.date_input("📅 Seleccioná la fecha a consultar:", datetime.date.today(), key="vista_dia")
            fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
            
            for sucursal_nombre in lista_locales.keys():
                st.markdown(f"#### 📍 {sucursal_nombre}")
                df_filtrado = df_asistencia[(df_asistencia["Sucursal"] == sucursal_nombre) & (df_asistencia["Fecha"] == fecha_str)]
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                else:
                    st.info(f"Sin registros para el {fecha_str} en {sucursal_nombre}.")
                st.markdown("---")
        else:
            st.info("Todavía no hay registros de asistencia guardados.")
            
        # 2. DESCARGA POR RANGO DE FECHAS
        st.header("📥 Descargar Reporte (Por Rango de Fechas)")
        if os.path.exists(ARCHIVO_ASISTENCIA):
            rango_fechas = st.date_input("Seleccioná Desde y Hasta:", 
                                         value=(datetime.date.today(), datetime.date.today()),
                                         max_value=datetime.date.today())
            
            if len(rango_fechas) == 2:
                f_inicio, f_fin = rango_fechas
                df_asistencia_full = pd.read_csv(ARCHIVO_ASISTENCIA)
                
                # Filtrar el CSV original
                df_descarga = df_asistencia_full.copy()
                df_descarga['Fecha_Temp'] = pd.to_datetime(df_descarga['Fecha']).dt.date
                df_descarga = df_descarga[(df_descarga['Fecha_Temp'] >= f_inicio) & (df_descarga['Fecha_Temp'] <= f_fin)]
                df_descarga = df_descarga.drop(columns=['Fecha_Temp'])
                
                if not df_descarga.empty:
                    csv_data = df_descarga.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📊 Descargar Excel CSV ({f_inicio.strftime('%d/%m/%Y')} al {f_fin.strftime('%d/%m/%Y')})",
                        data=csv_data,
                        file_name=f"Reporte_Asistencia_{f_inicio}_al_{f_fin}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No hay registros en el rango de fechas seleccionado.")
        
        st.markdown("---")
        col_adm1, col_adm2 = st.columns(2)
        
        # 3. EMPLEADOS Y DISPOSITIVOS
        with col_adm1:
            st.subheader("👥 Empleados y Celulares Vinculados")
            for emp in sorted(lista_empleados):
                estado_vinculo = "📱 Celular vinculado" if emp in dispositivos_vinculados else "⚠️ Sin celular vinculado"
                st.write(f"- **{emp}** ({estado_vinculo})")
                
            st.markdown("---")
            emp_a_desv = st.selectbox("Desvincular celular de:", ["Seleccionar..."] + [e for e in dispositivos_vinculados.keys()])
            if st.button("🔓 Desvincular Dispositivo"):
                if emp_a_desv != "Seleccionar...":
                    del dispositivos_vinculados[emp_a_desv]
                    with open(ARCHIVO_DISPOSITIVOS, 'w') as f:
                        json.dump(dispositivos_vinculados, f)
                    st.success(f"Dispositivo desvinculado.")
                    st.rerun()

            st.markdown("---")
            nuevo_empleado = st.text_input("Agregar nuevo empleado:")
            if st.button("➕ Agregar Empleado"):
                if nuevo_empleado and nuevo_empleado not in lista_empleados:
                    lista_empleados.append(nuevo_empleado)
                    with open(ARCHIVO_EMPLEADOS, 'w') as f:
                        json.dump(lista_empleados, f)
                    st.success(f"Empleado agregado.")
                    st.rerun()
                    
            borrar_empleado = st.selectbox("Eliminar empleado:", ["Seleccionar..."] + sorted(lista_empleados))
            if st.button("🗑️ Eliminar Empleado"):
                if borrar_empleado != "Seleccionar...":
                    lista_empleados.remove(borrar_empleado)
                    with open(ARCHIVO_EMPLEADOS, 'w') as f:
                        json.dump(lista_empleados, f)
                    st.success(f"{borrar_empleado} eliminado.")
                    st.rerun()

        # 4. SUCURSALES
        with col_adm2:
            st.subheader("📍 Gestión de Sucursales")
            for loc in lista_locales.keys():
                st.write(f"- {loc}")
                
            st.markdown("---")
            nombre_loc = st.text_input("Nombre del Local (ej: Local 4):")
            lat_loc = st.number_input("Latitud:", format="%.6f")
            lon_loc = st.number_input("Longitud:", format="%.6f")
            if st.button("➕ Agregar Local"):
                if nombre_loc and nombre_loc not in lista_locales:
                    lista_locales[nombre_loc] = {"lat": lat_loc, "lon": lon_loc}
                    with open(ARCHIVO_LOCALES, 'w') as f:
                        json.dump(lista_locales, f)
                    st.success(f"Local agregado.")
                    st.rerun()
                    
            borrar_loc = st.selectbox("Eliminar sucursal:", ["Seleccionar..."] + list(lista_locales.keys()))
            if st.button("🗑️ Eliminar Local"):
                if borrar_loc != "Seleccionar...":
                    del lista_locales[borrar_loc]
                    with open(ARCHIVO_LOCALES, 'w') as f:
                        json.dump(lista_locales, f)
                    st.success(f"Local eliminado.")
                    st.rerun()
                    
        st.markdown("---")
        
        # 5. AJUSTES (HORARIO Y CONTRASEÑA)
        col_ajustes1, col_ajustes2 = st.columns(2)
        
        with col_ajustes1:
            st.subheader("⏱️ Configurar Horario Límite")
            try:
                hora_actual_limite = datetime.datetime.strptime(config_app["hora_limite"], "%H:%M:%S").time()
            except:
                hora_actual_limite = datetime.time(9, 15)
                
            nuevo_limite = st.time_input("Horario máximo para marcar entrada a tiempo:", hora_actual_limite)
            if st.button("Guardar Horario Límite"):
                config_app["hora_limite"] = nuevo_limite.strftime("%H:%M:%S")
                with open(ARCHIVO_CONFIG, 'w') as f:
                    json.dump(config_app, f)
                st.success(f"¡Horario límite actualizado a las {config_app['hora_limite']}!")
                
        with col_ajustes2:
            st.subheader("🔑 Cambiar Contraseña")
            nc = st.text_input("Nueva contraseña:", type="password")
            rc = st.text_input("Repetir contraseña:", type="password")
            if st.button("Actualizar Contraseña Admin"):
                if nc and nc == rc:
                    config_app["admin_password"] = nc
                    with open(ARCHIVO_CONFIG, 'w') as f:
                        json.dump(config_app, f)
                    st.success("¡Contraseña actualizada con éxito!")
                else:
                    st.error("Las contraseñas no coinciden.")
                
    elif password_ingresada == "":
        st.info("🔒 Ingresá la contraseña para acceder al panel (Clave por defecto: 1234).")
    else:
        st.error("❌ Contraseña incorrecta.")
