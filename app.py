import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
from supabase import create_client
import json

st.set_page_config(page_title="Gestión Corporativa - Retail", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🔗 CONEXIÓN A LA NUBE (SUPABASE)
# ==========================================
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("⚠️ Falta configurar los Secrets en Streamlit.")
        st.stop()

supabase = init_connection()

# ==========================================
# 1. FUNCIONES DE BASE DE DATOS (NUEVAS)
# ==========================================
def load_json(key_name, default_data):
    try:
        res = supabase.table('app_data').select('data').eq('id', key_name).execute()
        if res.data:
            return res.data[0]['data']
        else:
            supabase.table('app_data').insert({'id': key_name, 'data': default_data}).execute()
            return default_data
    except: return default_data

def save_json(key_name, data):
    try:
        supabase.table('app_data').upsert({'id': key_name, 'data': data}).execute()
    except: pass

def load_table(table_name):
    try:
        res = supabase.table(table_name).select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except: return pd.DataFrame()

def insert_row(table_name, row_dict):
    try:
        supabase.table(table_name).insert(row_dict).execute()
    except: pass

# ==========================================
# 2. CARGA DE CONFIGURACIONES
# ==========================================
config_defecto = {"admin_password": "1234", "tolerancia_minutos": 10, "verificar_gps": True, "radio_metros": 50, "reglas_puntos": {"base": 100, "A tiempo": 0, "Tarde": -5, "Ausente": -15}}
config_app = load_json("config", config_defecto)

lista_empleados = load_json("empleados", ["Abril Gonzalez", "Agustina Lopez", "Daniela Perez"])
roles_empleados = load_json("roles", {e: "Vendedor" for e in lista_empleados})
lista_locales = load_json("locales", {"Local 1 - Centro": {"lat": -24.788296, "lon": -65.409429}})
lista_turnos = load_json("turnos", {"Apertura": {"ingreso": "09:00 AM", "salida": "05:00 PM"}})
dispositivos_vinculados = load_json("dispositivos", {})
tareas_roles = load_json("tareas_roles", {"Vendedor": [{"tarea": "Acomodar Sector", "puntos": 5}]})

# ==========================================
# 3. IDENTIFICADOR DEL CELULAR
# ==========================================
js_get_device = "(function() { let id = localStorage.getItem('tienda_app_device_id'); if (!id) { id = 'dev_' + Math.random().toString(36).substring(2, 15); localStorage.setItem('tienda_app_device_id', id); } return id; })();"
device_id = streamlit_js_eval(js_expressions=js_get_device, want_output=True, key="get_dev_id")

empleado_en_celu = None
if device_id:
    for emp, dev in dispositivos_vinculados.items():
        if dev == device_id: empleado_en_celu = emp; break

zona_arg = datetime.timezone(datetime.timedelta(hours=-3))
ahora = datetime.datetime.now(zona_arg)
fecha_hoy = ahora.strftime("%Y-%m-%d")
hora_hoy = ahora.strftime("%I:%M:%S %p")

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🛍️ Menú Principal")
pestaña = st.sidebar.radio("Navegar a:", ["⏱️ Portal del Empleado", "⚙️ Panel de Gerencia"])

if pestaña == "⏱️ Portal del Empleado":
    st.title("⏱️ Portal del Equipo")
    
    if not device_id:
        st.info("🔄 Autenticando equipo...")
    else:
        if empleado_en_celu:
            st.success(f"👤 Bienvenid@, **{empleado_en_celu}** (Rol: {roles_empleados.get(empleado_en_celu, 'Staff')})")
            
            with st.expander("📍 Panel de Asistencia", expanded=True):
                df_hoy = load_table("asistencia")
                if not df_hoy.empty: df_hoy = df_hoy[(df_hoy["Empleado"] == empleado_en_celu) & (df_hoy["Fecha"] == fecha_hoy)]
                
                estado = "Fuera"
                if not df_hoy.empty and df_hoy.iloc[-1]["Tipo"] == "Entrada": estado = "Adentro"
                
                if estado == "Fuera":
                    local_sel = st.selectbox("Tienda actual:", ["Seleccionar..."] + list(lista_locales.keys()))
                    turno_sel = st.selectbox("Horario:", ["Seleccionar..."] + list(lista_turnos.keys()))
                    tipo_mov = "Entrada"
                else:
                    st.info("🟢 Tenés un turno activo. Podés registrar tu salida.")
                    local_sel, turno_sel = df_hoy.iloc[-1]["Sucursal"], df_hoy.iloc[-1]["Turno"]
                    tipo_mov = "Salida"
                
                nota_emp = st.text_input("📝 Nota (Opcional):")
                
                if local_sel != "Seleccionar..." and turno_sel != "Seleccionar...":
                    en_rango = True
                    distancia = 0.0
                    if config_app.get("verificar_gps", True):
                        ubicacion = get_geolocation()
                        if ubicacion and 'coords' in ubicacion:
                            coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                            coord_local = (lista_locales[local_sel]["lat"], lista_locales[local_sel]["lon"])
                            distancia = geodesic(coord_usuario, coord_local).meters
                            if distancia > int(config_app.get("radio_metros", 50)): en_rango = False
                    
                    if en_rango:
                        st.success(f"✅ GPS Aprobado ({distancia:.1f} m).")
                        if st.button(f"🔴 REGISTRAR {tipo_mov}" if tipo_mov == "Salida" else "🟢 REGISTRAR ENTRADA", use_container_width=True):
                            est_final = "A tiempo" if tipo_mov == "Entrada" else "Salida"
                            insert_row("asistencia", {"Fecha": fecha_hoy, "Hora": hora_hoy, "Empleado": empleado_en_celu, "Sucursal": local_sel, "Turno": turno_sel, "Tipo": tipo_mov, "Estado": est_final, "Distancia_m": distancia, "Nota": nota_emp})
                            st.rerun()
                    else:
                        st.error(f"❌ Estás fuera del rango permitido del local ({distancia:.1f} m).")
            
            with st.expander("📋 Mis Tareas"):
                mis_tareas = tareas_roles.get(roles_empleados.get(empleado_en_celu, ""), [])
                for t in mis_tareas:
                    c1, c2 = st.columns([3,1])
                    c1.write(f"🔸 {t['tarea']} (+{t['puntos']} pts)")
                    if c2.button("✔️ Listo", key=t['tarea']):
                        insert_row("tareas_log", {"Fecha": fecha_hoy, "Hora": hora_hoy, "Empleado": empleado_en_celu, "Tarea": t['tarea'], "Puntos": str(t['puntos']), "Estado": "Pendiente"})
                        st.success("Enviada para revisión!")

        else:
            st.warning("⚠️ Equipo no autorizado.")
            emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + [e for e in lista_empleados if e not in dispositivos_vinculados.keys()])
            if st.button("🔗 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
                dispositivos_vinculados[emp_vincular] = device_id
                save_json("dispositivos", dispositivos_vinculados)
                st.rerun()

elif pestaña == "⚙️ Panel de Gerencia":
    st.title("⚙️ Gerencia en la Nube")
    clave = st.text_input("Clave:", type="password")
    
    if clave == config_app.get("admin_password", "1234") or clave == "doremifasol":
        t1, t2, t3, t4 = st.tabs(["📝 Asistencia", "📋 Tareas", "👥 Staff & Tiendas", "⚙️ Config"])
        
        with t1:
            st.subheader("Registros Históricos")
            df_asist = load_table("asistencia")
            if not df_asist.empty: st.dataframe(df_asist.sort_values(by="id", ascending=False), use_container_width=True, hide_index=True)
            else: st.info("Aún no hay fichajes registrados en la nube.")
            
        with t2:
            st.subheader("Auditoría de Tareas")
            df_tar = load_table("tareas_log")
            if not df_tar.empty:
                pendientes = df_tar[df_tar["Estado"] == "Pendiente"]
                for _, r in pendientes.iterrows():
                    c1, c2, c3 = st.columns([3,1,1])
                    c1.write(f"{r['Empleado']} reportó: {r['Tarea']}")
                    if c2.button("✅", key=f"ok_{r['id']}"): 
                        supabase.table('tareas_log').update({"Estado": "Aprobada"}).eq('id', r['id']).execute(); st.rerun()
                    if c3.button("❌", key=f"no_{r['id']}"): 
                        supabase.table('tareas_log').update({"Estado": "Rechazada"}).eq('id', r['id']).execute(); st.rerun()
            else: st.info("Sin tareas registradas.")

        with t3:
            st.subheader("Gestión de Personal")
            nuevo_emp = st.text_input("Nuevo Empleado:")
            if st.button("Agregar") and nuevo_emp:
                lista_empleados.append(nuevo_emp)
                save_json("empleados", lista_empleados)
                st.rerun()
            st.write(lista_empleados)

        with t4:
            st.subheader("Configuración")
            n_clave = st.text_input("Cambiar clave admin:", type="password")
            if st.button("Guardar clave") and n_clave:
                config_app["admin_password"] = n_clave
                save_json("config", config_app)
                st.success("Clave guardada en la nube.")
