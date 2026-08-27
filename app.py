import streamlit as st
from geopy.distance import geodesic
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import datetime
import pandas as pd
import json
import altair as alt
from supabase import create_client

# Configuración inicial de la página
st.set_page_config(
    page_title="Gestión Corporativa - Retail", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 ESTÉTICA PREMIUM COMERCIAL (CSS)
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
.msg-global { padding: 15px; border-radius: 10px; border-left: 6px solid #3B82F6; background-color: #EFF6FF; margin-bottom: 15px;}
.msg-individual { padding: 15px; border-radius: 10px; border-left: 6px solid #EC4899; background-color: #FDF2F8; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔌 1. CONEXIÓN A SUPABASE (LA NUBE)
# ==========================================
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("🔌 Error: No se encontraron los secretos de Supabase en Streamlit.")
        st.stop()

supabase = init_connection()

# MODO DIAGNÓSTICO ACTIVADO
def load_json(key_name, default_data):
    try:
        res = supabase.table('app_data').select('data').eq('id', key_name).execute()
        if res.data: 
            return res.data['data']
        else:
            supabase.table('app_data').insert({'id': key_name, 'data': default_data}).execute()
            return default_data
    except Exception as e:
        st.error(f"❌ Error cargando '{key_name}': {e}")
        st.stop()

def save_json(key_name, data):
    try:
        res = supabase.table('app_data').select('id').eq('id', key_name).execute()
        if res.data: 
            supabase.table('app_data').update({'data': data}).eq('id', key_name).execute()
        else: 
            supabase.table('app_data').insert({'id': key_name, 'data': data}).execute()
    except Exception as e:
        st.error(f"❌ Error guardando '{key_name}': {e}")
        st.stop()

def load_df(table_name):
    try:
        res = supabase.table(table_name).select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error leyendo la tabla '{table_name}': {e}")
        st.stop()

def insert_row(table_name, row_dict):
    try:
        supabase.table(table_name).insert(row_dict).execute()
    except Exception as e:
        st.error(f"❌ Error guardando en la tabla '{table_name}': {e}")
        st.stop()

# ==========================================
# 2. CARGA DE DATOS CENTRALIZADA
# ==========================================
config_defecto = {
    "admin_password": "1234", 
    "tolerancia_minutos": 10,
    "mensaje_llegada_tarde": "⚠️ Llegada fuera del margen de tolerancia.", 
    "verificar_gps": True,
    "verificar_wifi": False, 
    "ip_wifi_oficial": "", 
    "radio_metros": 50, 
    "reglas_puntos": {
        "base": 100,
        "A tiempo": 0, 
        "Tarde": -5, 
        "Ausente": -15, 
        "Falta Justificada": 0
    }
}

config_app = load_json("config", config_defecto)
lista_roles_disponibles = load_json("lista_roles", ["Vendedor", "Cajero", "Encargado", "Depósito", "Planchador", "Otro"])
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
ESTADOS_POSIBLES = ["A tiempo", "Tarde", "Salida", "Salida (Fuera de Rango)", "Ausente", "Falta Justificada", "Pausa", "N/A"]

# ==========================================
# 3. IDENTIFICADOR Y RED DEL CELULAR
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
        if len(rango) == 2: return rango, rango
        elif len(rango) == 1: return rango, rango
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
    if puntos < 80: return "🔍 Observación"
    elif puntos < 100: return "🥉 Bronce"
    elif puntos < 130: return "🥈 Plata"
    elif puntos < 160: return "🥇 Oro"
    elif puntos < 200: return "💎 Platino"
    else: return "👑 Leyenda"

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown('<div class="main-title">Gestión Corporativa - Retail</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Sincronización operativa, gamificación e inventario en tiempo real</div>', unsafe_allow_html=True)

if config_app.get("mensaje_dia", "").strip() != "":
    st.info(f"📢 **Comunicado Interno:**\n\n{config_app['mensaje_dia']}")

if not device_id:
    st.info("⌛ Autenticando tu equipo...")
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

        rol_empleado = roles_empleados.get(empleado_en_celu, 'Staff')
        st.markdown(f"<div class='credencial'><p class='cred-nombre'>👤 {empleado_en_celu}</p><p class='cred-rol'>Rol: {rol_empleado}</p><div class='cred-nivel'>{calcular_nivel(puntos_actuales)} ({puntos_actuales} pts en {ahora.strftime('%B')})</div></div>", unsafe_allow_html=True)

        # MÓDULOS DEL EMPLEADO / COLABORADOR
        if rol_empleado in ["Cajero", "Encargado"]:
            with st.expander("👑 Panel de Responsable de Turno", expanded=False):
                st.markdown("<div class='super-box'><b>Rol Supervisor:</b> Podés asignar bonos o multas a otros compañeros. Requiere auditoría.</div>", unsafe_allow_html=True)
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

        mensajes_usuario = [m for m in lista_mensajes if m.get('destinatario') in ['Todos', empleado_en_celu]]
        if mensajes_usuario:
            for m in mensajes_usuario:
                if m['destinatario'] == 'Todos': 
                    st.markdown(f"<div class='msg-global'>📢 <b>Aviso General:</b> {m['texto']}</div>", unsafe_allow_html=True)
                else: 
                    st.markdown(f"<div class='msg-individual'>💌 <b>Mensaje Privado:</b> {m['texto']}</div>", unsafe_allow_html=True)

        with st.expander("📍 Smart Check-In", expanded=True):
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
                    datos_turno_activo = {"Sucursal": ultimo_reg["Sucursal"], "Turno": ultimo_reg["Turno"], "Distancia_m": ultimo_reg.get("Distancia_m", 0.0)}
                else:
                    st.info("ℹ️ Ya tenés turnos finalizados hoy. Podés registrar un nuevo ingreso si es necesario.")

            if estado_laboral == "Fuera":
                st.markdown("### 📡 Radar Automático")
                local_detectado = None
                distancia_real = 0.0
                metodo_det = ""
                ubicacion = get_geolocation() if config_app.get("verificar_gps", True) else None
                if config_app.get("verificar_wifi", False) and client_ip and client_ip != 'Error':
                    for loc, d_loc in lista_locales.items():
                        if d_loc.get("ip", "").strip() == client_ip:
                            local_detectado = loc
                            metodo_det = "🌐 Red Wi-Fi de la tienda"
                            break
                if not local_detectado and config_app.get("verificar_gps", True):
                    if ubicacion and 'coords' in ubicacion:
                        coord_usuario = (ubicacion['coords']['latitude'], ubicacion['coords']['longitude'])
                        for loc, d_loc in lista_locales.items():
                            coord_local = (d_loc["lat"], d_loc["lon"])
                            dist = geodesic(coord_usuario, coord_local).meters
                            if dist <= int(config_app.get("radio_metros", 50)):
                                local_detectado = loc
                                distancia_real = dist
                                metodo_det = f"🛰️ GPS Satelital ({dist:.1f} metros)"
                                break

                if local_detectado:
                    turno_detectado = None
                    min_diff = float('inf')
                    for t_name, t_data in lista_turnos.items():
                        try:
                            h_ing = pd.to_datetime(t_data["ingreso"]).time()
                            dt_ing = datetime.datetime.combine(ahora.date(), h_ing).replace(tzinfo=zona_arg)
                            diff = abs((ahora - dt_ing).total_seconds())
                            if diff < min_diff:
                                min_diff = diff
                                turno_detectado = t_name
                        except: pass
                    st.markdown(f"<div class='task-box'>✅ <b>Sucursal Detectada:</b> {local_detectado}<br><small>Verificado por: {metodo_det}</small></div>", unsafe_allow_html=True)
                    if turno_detectado:
                        st.markdown(f"<div class='super-box'>🕒 <b>Turno Asignado:</b> {turno_detectado}<br><small>({lista_turnos[turno_detectado]['ingreso']} a {lista_turnos[turno_detectado]['salida']})</small></div>", unsafe_allow_html=True)
                        nota_empleado = st.text_input("📝 Novedades (Opcional):", placeholder="¿Llegaste tarde por el colectivo? Dejá tu nota acá...")
                        if st.button("🚀 REGISTRAR ENTRADA", use_container_width=True) and turno_detectado:
                            hora_t_str = lista_turnos[turno_detectado]["ingreso"]
                            hora_t_obj = pd.to_datetime(hora_t_str).time()
                            dt_turno = datetime.datetime.combine(ahora.date(), hora_t_obj).replace(tzinfo=zona_arg)
                            estado_llegada = "Tarde" if ahora > (dt_turno + datetime.timedelta(minutes=int(config_app.get("tolerancia_minutos", 10)))) else "A tiempo"
                            insert_row("asistencia", {"Fecha": fecha_hoy, "Hora": hora_hoy, "Empleado": empleado_en_celu, "Sucursal": local_detectado, "Turno": turno_detectado, "Tipo": "Entrada", "Estado": estado_llegada, "Distancia_m": round(distancia_real, 1), "Nota": nota_empleado})
                            msg_final = f"¡Entrada registrada a las {hora_hoy}!"
                            if estado_llegada == "Tarde": 
                                msg_final += f"\n\n⚠️ {config_app.get('mensaje_llegada_tarde')}"
                            st.session_state['fichaje_exitoso'] = msg_final
                            st.rerun()
                else:
                    if config_app.get("verificar_gps", True) and (not ubicacion or 'coords' not in ubicacion):
                        st.info("⏳ Detectando ubicación satelital... Por favor, permití el acceso al GPS en tu celular.")
                    else:
                        st.error(f"❌ Estás fuera del rango de todas las sucursales. Acercate al local para habilitar el fichaje.")
            else:
                st.markdown("### 🚶‍♂️ Finalizar Turno")
                local_actual = datos_turno_activo.get("Sucursal", "N/A")
                turno_actual = datos_turno_activo.get("Turno", "N/A")
                st.success(f"💼 Actualmente trabajando en **{local_actual}** (Horario: {turno_actual}).")
                nota_empleado = st.text_input("📝 Novedad al salir (Opcional):")
                if st.button("🚪 REGISTRAR SALIDA", use_container_width=True):
                    insert_row("asistencia", {"Fecha": fecha_hoy, "Hora": hora_hoy, "Empleado": empleado_en_celu, "Sucursal": local_actual, "Turno": turno_actual, "Tipo": "Salida", "Estado": "Salida", "Distancia_m": datos_turno_activo.get("Distancia_m", 0.0), "Nota": nota_empleado})
                    st.session_state['fichaje_exitoso'] = f"¡Salida registrada a las {hora_hoy}! Buen descanso."
                    st.rerun()

        # ==========================================
        # 📦 NUEVO: GESTIÓN DE INVENTARIO POR SECTOR (AUDIO: ROPA.M4A)
        # ==========================================
        with st.expander("📦 Control de Stock y Lotes (Sectores)", expanded=False):
            st.markdown("##### Registrá movimientos de prendas según tu sector asignado.")
            sector_opcion = st.selectbox("Seleccionar Sector / Operación:", ["Depósito (Ingreso de Fardos)", "Planchado (Apertura y Conteo)", "Salón (Recepción en Tienda)", "Caja (Venta de Prendas)"])
            
            stock_fardos = load_json("stock_fardos", [])
            planchado_log = load_json("planchado_log", [])
            salon_log = load_json("salon_log", [])
            ventas_ropa = load_json("ventas_ropa", [])
            
            if sector_opcion == "Depósito (Ingreso de Fardos)":
                st.write("**📥 Registrar Entrada de Fardo al Depósito Principal (Independencia)**")
                with st.form("form_deposito"):
                    cod_fardo = st.text_input("Código de Fardo (Ej: FB-102):").strip()
                    cat_fardo = st.selectbox("Categoría de Ropa:", ["Blusas Blancas", "Blusas de Colores", "Pantalones", "Jeans", "Camperas", "Remeras", "Otros"])
                    col_dep1, col_dep2, col_dep3 = st.columns(3)
                    fila_g = col_dep1.selectbox("Fila (Ajedrez):", ["A", "B", "C", "D", "E"])
                    col_g = col_dep2.selectbox("Columna (Ajedrez):", ["1", "2", "3", "4", "5", "6"])
                    niv_g = col_dep3.selectbox("Nivel (Ajedrez):", ["AA1", "AA2", "AA3", "AA4"])
                    cant_fardos = st.number_input("Cantidad de Fardos:", min_value=1, value=1)
                    notas_dep = st.text_input("Observaciones:")
                    
                    if st.form_submit_button("Guardar en Depósito"):
                        if not cod_fardo:
                            st.error("El código de fardo es obligatorio.")
                        elif any(f.get("codigo") == cod_fardo for f in stock_fardos):
                            st.error("Ya existe un fardo con ese código.")
                        else:
                            fardo_nuevo = {
                                "Fecha": fecha_hoy,
                                "Hora": hora_hoy,
                                "Empleado": empleado_en_celu,
                                "codigo": cod_fardo,
                                "categoria": cat_fardo,
                                "posicion": f"{fila_g}{col_g}-{niv_g}",
                                "cantidad": cant_fardos,
                                "estado": "En Depósito",
                                "notas": notas_dep
                            }
                            stock_fardos.append(fardo_nuevo)
                            save_json("stock_fardos", stock_fardos)
                            st.success(f"✅ Fardo {cod_fardo} guardado en la posición {fila_g}{col_g}-{niv_g}.")
                            st.rerun()
            
            elif sector_opcion == "Planchado (Apertura y Conteo)":
                st.write("**🧼 Registrar Apertura de Fardo y Conteo en Planchado**")
                fardos_disponibles = [f.get("codigo") for f in stock_fardos if f.get("estado") == "En Depósito"]
                if not fardos_disponibles:
                    st.info("No hay fardos disponibles en depósito para procesar.")
                else:
                    with st.form("form_planchado"):
                        fardo_sel = st.selectbox("Seleccionar Fardo a abrir:", fardos_disponibles)
                        st.write("---")
                        st.write("**Prendas Obtenidas por Categoría de Precio:**")
                        col_p1, col_p2, col_p3 = st.columns(3)
                        cant_normal = col_p1.number_input("Precio Normal (Cant):", min_value=0, value=0)
                        cant_liq = col_p2.number_input("Liquidación (Cant):", min_value=0, value=0)
                        cant_descarte = col_p3.number_input("Descarte/Donación (Cant):", min_value=0, value=0)
                        sucursal_destino = st.selectbox("Enviar a Sucursal:", list(lista_locales.keys()))
                        notas_plancha = st.text_input("Notas de Planchado:")
                        
                        if st.form_submit_button("Confirmar Apertura"):
                            for f in stock_fardos:
                                if f.get("codigo") == fardo_sel:
                                    f["estado"] = "Planchado/Procesado"
                                    f["destino"] = sucursal_destino
                                    break
                            save_json("stock_fardos", stock_fardos)
                            
                            plancha_id = f"PL-{fardo_sel}"
                            registro_p = {
                                "id": plancha_id,
                                "Fecha": fecha_hoy,
                                "Hora": hora_hoy,
                                "Empleado": empleado_en_celu,
                                "fardo": fardo_sel,
                                "normal": cant_normal,
                                "liquidacion": cant_liq,
                                "descarte": cant_descarte,
                                "total": cant_normal + cant_liq + cant_descarte,
                                "sucursal": sucursal_destino,
                                "estado": "Pendiente en Salón",
                                "notas": notas_plancha
                            }
                            planchado_log.append(registro_p)
                            save_json("planchado_log", planchado_log)
                            st.success(f"✅ Fardo {fardo_sel} procesado. {cant_normal + cant_liq + cant_descarte} prendas listas para {sucursal_destino}.")
                            st.rerun()
            
            elif sector_opcion == "Salón (Recepción en Tienda)":
                st.write("**🛍️ Confirmar Recepción de Ropa en Salón de Ventas**")
                sucursal_emp = datos_turno_activo.get("Sucursal", "Todas")
                pendientes_rec = [p for p in planchado_log if p.get("estado") == "Pendiente en Salón" and (sucursal_emp == "Todas" or p.get("sucursal") == sucursal_emp)]
                
                if not pendientes_rec:
                    st.info("No hay prendas pendientes de recepción para tu sucursal actual.")
                else:
                    for p in pendientes_rec:
                        with st.container():
                            st.markdown(f"**Lote Planchado:** `{p['id']}` (Fardo: `{p['fardo']}`)")
                            st.write(f"📍 Destino: {p['sucursal']} | 📅 Enviado: {p['Fecha']} {p['Hora']}")
                            st.write(f"👕 Detalle: {p['normal']} Normal, {p['liquidacion']} Liquidación, {p['descarte']} Descarte. **Total: {p['total']} prendas.**")
                            
                            c_rec1, c_rec2 = st.columns()
                            obs_rec = c_rec1.text_input("Observaciones de recepción:", key=f"obs_rec_{p['id']}")
                            if c_rec2.button("📥 Confirmar Recepción", key=f"btn_rec_{p['id']}"):
                                for item in planchado_log:
                                    if item.get("id") == p['id']:
                                        item["estado"] = "Recibido en Salón"
                                        item["obs_recepcion"] = obs_rec
                                        item["fecha_recepcion"] = fecha_hoy
                                        item["hora_recepcion"] = hora_hoy
                                        item["receptor"] = empleado_en_celu
                                        break
                                save_json("planchado_log", planchado_log)
                                
                                salon_log.append({
                                    "planchado_id": p['id'],
                                    "fardo": p['fardo'],
                                    "Fecha": fecha_hoy,
                                    "Empleado": empleado_en_celu,
                                    "normal_recibido": p['normal'],
                                    "liquidacion_recibido": p['liquidacion'],
                                    "total_recibido": p['normal'] + p['liquidacion'],
                                    "sucursal": p['sucursal']
                                })
                                save_json("salon_log", salon_log)
                                st.success("✅ Lote recibido y agregado al stock del salón de ventas.")
                                st.rerun()
                            st.write("---")
            
            elif sector_opcion == "Caja (Venta de Prendas)":
                st.write("**💸 Registrar Ventas de Prendas (Control Diario de Caja)**")
                with st.form("form_caja_ventas"):
                    sucursal_venta = st.selectbox("Sucursal de la Venta:", list(lista_locales.keys()))
                    tipo_venta = st.selectbox("Tipo de Prenda / Precio:", ["Precio Normal", "Liquidación"])
                    cant_venta = st.number_input("Cantidad Vendida:", min_value=1, value=1)
                    monto_venta = st.number_input("Monto Total de Venta ($):", min_value=0, value=0)
                    notas_venta = st.text_input("Comentarios de la Venta:")
                    
                    if st.form_submit_button("Registrar Venta"):
                        nueva_v = {
                            "Fecha": fecha_hoy,
                            "Hora": hora_hoy,
                            "Empleado": empleado_en_celu,
                            "sucursal": sucursal_venta,
                            "tipo": tipo_venta,
                            "cantidad": cant_venta,
                            "monto": monto_venta,
                            "notas": notas_venta
                        }
                        ventas_ropa.append(nueva_v)
                        save_json("ventas_ropa", ventas_ropa)
                        st.success(f"✅ Venta registrada: {cant_venta} prendas ({tipo_venta}) por ${monto_venta:,} en {sucursal_venta}.")
                        st.rerun()

        # ==========================================
        # 📸 NUEVO: REGISTRO DE MARKETING DIGITAL (AUDIO: ROPA.M4A)
        # ==========================================
        with st.expander("📸 Registro de Contenido y Publicación en Redes", expanded=False):
            st.markdown("<div class='super-box'><b>¡Sumá puntos por Marketing!</b> Publicá contenido en redes sociales durante tu turno y registralo acá. Se validará para otorgarte puntos adicionales.</div>", unsafe_allow_html=True)
            redes_log = load_json("redes_log", [])
            with st.form("form_redes"):
                red_social = st.selectbox("Red Social:", ["Instagram Post/Reel", "Instagram Story", "TikTok", "Facebook", "Otro"])
                tipo_contenido = st.selectbox("Tipo de Contenido:", ["Outfit del Día", "Ingreso de Mercadería", "Promoción/Oferta", "Lote Especial", "Humor/Informativo"])
                url_post = st.text_input("Enlace / Descripción de la publicación (Ej: @cuenta, link del video...):")
                det_redes = st.text_area("Detalles de la publicación (¿Qué prendas mostraste?):")
                
                if st.form_submit_button("Enviar Publicación para Auditoría"):
                    if not url_post.strip():
                        st.warning("⚠️ Debes ingresar un enlace o descripción de la publicación.")
                    else:
                        redes_log.append({
                            "Fecha": fecha_hoy,
                            "Hora": hora_hoy,
                            "Empleado": empleado_en_celu,
                            "red": red_social,
                            "tipo": tipo_contenido,
                            "url": url_post.strip(),
                            "detalle": det_redes.strip(),
                            "estado": "Pendiente"
                        })
                        save_json("redes_log", redes_log)
                        st.success("✅ ¡Publicación enviada! Gerencia auditará el contenido para sumar tus puntos.")
                        st.rerun()

        # ==========================================
        # 📅 NUEVO: PREMIACIONES Y EXTRA DE DOMINGOS (AUDIO: ROPA.M4A)
        # ==========================================
        with st.expander("📅 Solicitud de Turno Domingo (Incentivo)", expanded=False):
            st.markdown("<div class='task-box'><b>Incentivo de Horas Extra:</b> Los turnos del domingo se asignan a los colaboradores con mejor rendimiento y puntaje acumulado. ¡Postulate acá!</div>", unsafe_allow_html=True)
            domingos_log = load_json("domingos_log", [])
            
            proximo_domingo = (ahora.date() + datetime.timedelta(days=(6 - ahora.date().weekday()) % 7)).strftime("%Y-%m-%d")
            ya_postulado = any(d.get("Empleado") == empleado_en_celu and d.get("fecha_domingo") == proximo_domingo for d in domingos_log)
            
            if ya_postulado:
                st.success(f"Ya estás postulado para el turno del Domingo {proximo_domingo}. ¡Gerencia evaluará el ranking de puntos para asignar los lugares!")
            else:
                with st.form("form_domingo"):
                    sucursal_dom = st.selectbox("Sucursal de Preferencia:", list(lista_locales.keys()))
                    turno_dom = st.selectbox("Turno de Preferencia:", ["Mañana", "Tarde", "Cualquier Turno"])
                    comentario_dom = st.text_input("Comentarios / Mensaje a Gerencia:")
                    
                    if st.form_submit_button("Postularme para este Domingo"):
                        domingos_log.append({
                            "fecha_registro": fecha_hoy,
                            "Empleado": empleado_en_celu,
                            "fecha_domingo": proximo_domingo,
                            "sucursal": sucursal_dom,
                            "turno": turno_dom,
                            "puntos_al_postular": puntos_actuales,
                            "comentario": comentario_dom,
                            "estado": "Pendiente"
                        })
                        save_json("domingos_log", domingos_log)
                        st.success(f"✅ ¡Postulación enviada correctamente para el Domingo {proximo_domingo}!")
                        st.rerun()

        # BUZÓN DE REPORTES
        with st.expander("📩 Buzón de Reportes Confidenciales", expanded=False):
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

        # TAREAS DEL DIA
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
                        c_t1, c_t2 = st.columns()
                        c_t1.write(f"▪️ {t_nombre} (+{t_puntos} pts)")
                        if c_t2.button("✔ Listo", key=f"btn_t_{t_nombre}"):
                            insert_row("tareas_log", {"Fecha": fecha_hoy, "Hora": hora_hoy, "Empleado": empleado_en_celu, "Tarea": t_nombre, "Puntos": str(t_puntos), "Estado": "Pendiente"})
                            st.rerun()

        # HISTORIAL RECIENTE
        with st.expander("🕒 Mi historial reciente"):
            if not df_punt.empty:
                df_emp = df_punt[(df_punt["Empleado"] == empleado_en_celu) & (df_punt["F_Obj"] >= (ahora.date() - datetime.timedelta(days=7)))].copy()
                if not df_emp.empty:
                    if 'id' in df_emp.columns:
                        df_emp['id_num'] = pd.to_numeric(df_emp['id'], errors='coerce')
                    df_emp = df_emp.sort_values(by="id_num", ascending=False)
                    st.dataframe(df_emp[["Fecha", "Hora", "Tipo", "Estado", "Nota"]], hide_index=True, use_container_width=True)
                else: st.write("Sin fichajes recientes.")
    else:
        st.warning("⚠️ **Equipo no autorizado.**")
        emp_vincular = st.selectbox("Identificate:", ["Seleccionar..."] + [e for e in sorted(lista_empleados) if e not in dispositivos_vinculados.keys()])
        if st.button("📱 Enlazar mi teléfono") and emp_vincular != "Seleccionar...":
            dispositivos_vinculados[emp_vincular] = device_id
            save_json("dispositivos", dispositivos_vinculados)
            st.rerun()

# ==========================================
# 👑 5. PANEL DE GERENCIA (BUSINESS INTELLIGENCE)
# ==========================================
st.markdown("---")
st.markdown('<div class="main-title" style="font-size: 2rem;">👑 Panel de Gerencia (Business Intelligence)</div>', unsafe_allow_html=True)
password_ingresada = st.text_input("Clave de acceso de Gerencia:", type="password")

if password_ingresada:
    if password_ingresada != "doremifasol":
        if 'last_pw_attempt' not in st.session_state or st.session_state['last_pw_attempt'] != password_ingresada:
            st.session_state['last_pw_attempt'] = password_ingresada
            res = "🔓 Acceso Permitido" if password_ingresada == config_app.get("admin_password", "1234") else "❌ Acceso Denegado"
            lista_intentos.append({"Fecha": fecha_hoy, "Hora": hora_hoy, "Usuario": empleado_en_celu if empleado_en_celu else "Desconocido", "Clave": password_ingresada, "Resultado": res})
            save_json("intentos_seguridad", lista_intentos)

    if password_ingresada == config_app.get("admin_password", "1234") or password_ingresada == "doremifasol":
        tab_analytics, tab_puntos, tab_auditoria_tareas, tab_auditoria_horas, tab_perfil, tab_inventario, tab_redes_domingo, tab_staff, tab_tiendas, tab_comunicados, tab_config, tab_espia = st.tabs([
            "📊 Analytics", "🏆 Ranking", "📋 Auditar Tareas", "✏️ Auditar Horarios", "👤 Perfil Empleado",
            "📦 Inventario y Fugas", "📸 Redes y Domingos", "👥 Staff", "🏪 Tiendas", "📢 Avisos", "⚙️ Config/Reseteo", "🚨 Espía"
        ])

        with tab_analytics:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📊 Analytics Globales</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns()
            filtro_a = c_fil1.selectbox("⏳ KPI Dashboard (Métricas Rápidas):", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_a")
            rango_stats = c_fil2.date_input("📅 Fechas del Dashboard:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_a == "Personalizado" else None
            s_in, s_fi = get_fechas_filtro(filtro_a, rango_stats)
            df_activos = load_df("asistencia")

            if df_activos.empty: st.info("📦 Base de datos limpia.")
            else:
                df_activos = df_activos[df_activos["Empleado"].isin(lista_empleados)].copy()
                df_activos['Fecha_Obj'] = pd.to_datetime(df_activos['Fecha'], errors='coerce')
                st.markdown(f"### 🔔 Alertas del Día ({fecha_hoy})")
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
                    c1.metric("📊 Puntualidad Promedio", f"{round((atiempo / tot_ingresos) * 100, 1) if tot_ingresos > 0 else 0}%")
                    c2.metric("✅ Ingresos A Tiempo", atiempo)
                    c3.metric("⚠️ Llegadas Tarde", tardes)
                    c4.metric("❌ Inasistencias", ausencias_tot)
                    st.write("---")

                st.markdown("### 📊 Recuento de Horas y Exportaciones")
                st.write("Configurá los filtros acá abajo para calcular las horas de tu equipo y descargar las planillas para liquidación.")
                c_dl1, c_dl2, c_dl3 = st.columns(3)
                local_descarga = c_dl1.selectbox("🏬 Sucursal a evaluar:", ["Todas las sucursales"] + list(lista_locales.keys()), key="dl_loc")
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
                            for f in df_e_loc["Fecha"].unique():
                                df_ef = df_e_loc[df_e_loc["Fecha"] == f].copy()
                                df_ef['Hora_dt'] = pd.to_datetime(df_ef['Hora'], errors='coerce')
                                df_ef = df_ef.dropna(subset=['Hora_dt']).sort_values(by="Hora_dt")
                                ent, sal = df_ef[df_ef["Tipo"] == "Entrada"], df_ef[df_ef["Tipo"] == "Salida"]
                                if not ent.empty and not sal.empty:
                                    if sal.iloc[-1]["Estado"] != "Salida (Fuera de Rango)":
                                        h_in = ent.iloc["Hora_dt"]
                                        h_out = sal.iloc[-1]["Hora_dt"]
                                        diff = (h_out - h_in).total_seconds() / 3600.0
                                        horas_totales += diff if diff >= 0 else (diff + 24.0)
                            if horas_totales > 0:
                                datos_horas.append({
                                    "Personal": emp,
                                    "Rol": roles_empleados.get(emp, "Staff"),
                                    "Sucursal": loc,
                                    "🕒 Horas Computadas": round(horas_totales, 2)
                                })
                    if datos_horas:
                        df_horas_final = pd.DataFrame(datos_horas).sort_values(by=["Personal", "🕒 Horas Computadas"], ascending=[True, False])
                        st.dataframe(df_horas_final, use_container_width=True, hide_index=True)

                        st.write("⬇️ **Descargar Archivos (Excel/CSV)**")
                        c_btn1, c_btn2 = st.columns(2)
                        csv_horas = df_horas_final.to_csv(index=False).encode('utf-8')
                        c_btn1.download_button(label="📊 Descargar Recuento de Horas", data=csv_horas, file_name=f"HorasTotales_{local_descarga}_{fecha_in_dl}.csv", mime="text/csv", use_container_width=True)

                        df_asist_dl = df_dl.copy()
                        df_asist_dl['Hora_dt'] = pd.to_datetime(df_asist_dl['Hora'], errors='coerce')
                        df_asist_dl = df_asist_dl.sort_values(by=["Fecha", "Hora_dt"])
                        df_asist_dl = df_asist_dl[["Fecha", "Hora", "Empleado", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]]
                        csv_asist = df_asist_dl.to_csv(index=False).encode('utf-8')
                        c_btn2.download_button(label="📋 Descargar Fichajes Detallados", data=csv_asist, file_name=f"Fichajes_{local_descarga}_{fecha_in_dl}.csv", mime="text/csv", use_container_width=True)
                    else:
                        st.info("Sin registros de horas para la sucursal y fechas seleccionadas.")
                else:
                    st.info("Sin registros de horas para la sucursal y fechas seleccionadas.")

        with tab_puntos:
            st.markdown('<div class="main-title" style="font-size: 2rem;">🏆 Ranking de Puntos</div>', unsafe_allow_html=True)
            c_fil1, c_fil2 = st.columns()
            filtro_p = c_fil1.selectbox("⏳ Filtrar Ranking:", ["Este Mes", "Mes Anterior", "Esta Semana", "Hoy", "Todo el Historial", "Personalizado"], key="filtro_p")
            rango_punt = c_fil2.date_input("📅 Fechas del Ranking:", value=(ahora.date() - datetime.timedelta(days=7), ahora.date())) if filtro_p == "Personalizado" else None
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
                df_e = df_p[df_p["Empleado"] == emp] if not df_p.empty else pd.DataFrame()
                e_ok = len(df_e[df_e["Estado"] == "A tiempo"]) if not df_e.empty else 0
                e_tar = len(df_e[df_e["Estado"] == "Tarde"]) if not df_e.empty else 0
                e_au = len(df_e[df_e["Tipo"] == "Ausente"]) if not df_e.empty else 0

                puntaje = reg.get('base', 100) + (e_ok * reg.get('A tiempo', 0)) + (e_tar * reg.get('Tarde', -5)) + (e_au * reg.get('Ausente', -15)) + e_aj + e_tp
                ranking_data.append({"Personal": emp, "Nivel": calcular_nivel(puntaje), "⭐ PUNTOS": puntaje, "📋 Pts Tareas": e_tp, "📊 Ajustes": e_aj, "⚠️ Tardes": e_tar, "❌ Faltas": e_au})

            st.dataframe(pd.DataFrame(ranking_data).sort_values(by="⭐ PUNTOS", ascending=False), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("✍ Cargar Bono o Multa Manual")
            with st.form("form_bonos"):
                c_b1, c_b2, c_b3, c_b4 = st.columns()
                ap_emp = c_b1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                ap_fecha = c_b2.date_input("Fecha de Ajuste:", ahora.date())
                ap_puntos = c_b3.number_input("Puntos (+/-):", value=0, step=1)
                ap_motivo = c_b4.text_input("Motivo del Ajuste:")

                if st.form_submit_button("Aplicar a Puntuación"):
                    if ap_emp == "Seleccionar..." or ap_puntos == 0 or not ap_motivo.strip():
                        st.warning("⚠️ Error: Faltan completar datos (Asegurate de elegir un empleado, que los puntos no sean 0 y escribir un motivo).")
                    else:
                        lista_puntos.append({"Fecha": ap_fecha.strftime("%Y-%m-%d"), "Empleado": ap_emp, "Puntos": ap_puntos, "Motivo": ap_motivo.strip(), "Autor": "Gerencia", "Estado": "Aprobada"})
                        save_json("ajustes_puntos", lista_puntos)
                        st.success("✅ Bono/Multa aplicado y guardado en la nube.")
                        st.rerun()

        with tab_auditoria_tareas:
            st.subheader("📋 Tareas Pendientes de Aprobación")
            df_tl_all = load_df("tareas_log")
            if not df_tl_all.empty:
                pend_tareas = df_tl_all[df_tl_all["Estado"] == "Pendiente"]
                if pend_tareas.empty:
                    st.info("No hay tareas de colaboradores pendientes de aprobación.")
                else:
                    for idx, row in pend_tareas.iterrows():
                        c_p1, c_p2, c_p3 = st.columns()
                        c_p1.markdown(f"**{row['Empleado']}** reportó: '{row['Tarea']}' (+{row['Puntos']} pts)")
                        if c_p2.button("✅ Aprobar", key=f"apr_t_{row['id']}"):
                            supabase.table("tareas_log").update({"Estado": "Aprobada"}).eq("id", int(row['id'])).execute()
                            st.rerun()
                        if c_p3.button("❌ Rechazar", key=f"rec_t_{row['id']}"):
                            supabase.table("tareas_log").update({"Estado": "Rechazada"}).eq("id", int(row['id'])).execute()
                            st.rerun()
            else:
                st.info("Sin registros de tareas en el historial.")

            puntos_pendientes = [p for p in lista_puntos if p.get("Estado") == "Pendiente"]
            if puntos_pendientes:
                st.write("**Evaluaciones Pendientes (De Supervisores):**")
                for idx, p in enumerate(lista_puntos):
                    if p.get("Estado") == "Pendiente":
                        c_pp1, c_pp2, c_pp3 = st.columns()
                        c_pp1.markdown(f"**{p['Autor']}** sugiere **{p['Puntos']} pts** a **{p['Empleado']}** (Motivo: {p['Motivo']})")
                        if c_pp2.button("✅ Aprobar", key=f"apr_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Aprobada"
                            save_json("ajustes_puntos", lista_puntos)
                            st.rerun()
                        if c_pp3.button("❌ Rechazar", key=f"rec_p_{idx}"):
                            lista_puntos[idx]["Estado"] = "Rechazada"
                            save_json("ajustes_puntos", lista_puntos)
                            st.rerun()

            st.subheader("📩 Buzón de Quejas y Reportes")
            for idx, r in enumerate(reportes_log):
                if r.get("Estado") == "Pendiente de lectura":
                    st.markdown(f"<div class='report-box'><b>📩 NUEVO REPORTE</b> | Fecha: {r['Fecha']} {r['Hora']}<br><b>Emisor:</b> {r['Emisor']} | <b>Tipo:</b> {r['Tipo']}<br><b>Detalle:</b> <i>'{r['Detalle']}'</i></div>", unsafe_allow_html=True)
                    if st.button("Marcar como Visto", key=f"visto_rep_{idx}"):
                        reportes_log[idx]["Estado"] = "Visto"
                        save_json("reportes", reportes_log)
                        st.rerun()

        with tab_auditoria_horas:
            st.markdown('<div class="highlight-edit"><b>✏️ AUDITORÍA DE HORARIOS (NUBE)</b></div>', unsafe_allow_html=True)
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
                            c1, c2, c3, c4 = st.columns()
                            n_tipo = c1.selectbox("Tipo", ["Entrada", "Salida", "Ausente"], index=["Entrada", "Salida", "Ausente"].index(row['Tipo']) if row['Tipo'] in ["Entrada", "Salida", "Ausente"] else 0, key=f"t_{db_id}")
                            n_hora = c2.text_input("Hora (Ej: 08:30 AM)", value=row['Hora'], key=f"h_{db_id}")
                            n_estado = c3.selectbox("Estado", ESTADOS_POSIBLES, index=ESTADOS_POSIBLES.index(row['Estado']) if row['Estado'] in ESTADOS_POSIBLES else 7, key=f"e_{db_id}")
                            if c4.button("💾", key=f"btn_{db_id}"):
                                supabase.table("asistencia").update({'Tipo': n_tipo, 'Hora': n_hora, 'Estado': n_estado}).eq('id', db_id).execute()
                                st.rerun()
                    else: st.warning("Sin movimientos ese día.")

            st.write("---")
            st.subheader("✍ Carga Manual Total (Falta o Olvido)")
            with st.form("form_fichaje_manual"):
                c_f1, c_f2, c_f3 = st.columns(3)
                fm_emp = c_f1.selectbox("Personal:", ["Seleccionar..."] + sorted(lista_empleados))
                fm_fecha = c_f2.date_input("Fecha Manual:", ahora.date())
                fm_hora_str = c_f3.time_input("Hora exacta:", ahora.time()).strftime("%I:%M:%S %p")
                fm_tipo = c_f1.selectbox("Movimiento:", ["Entrada", "Salida", "Ausente"])
                fm_estado = c_f2.selectbox("Estado final:", ESTADOS_POSIBLES)
                fm_nota = c_f3.text_input("Nota / Justificación:")

                if st.form_submit_button("➕ Cargar Movimiento") and fm_emp != "Seleccionar...":
                    insert_row("asistencia", {"Fecha": fm_fecha.strftime("%Y-%m-%d"), "Hora": fm_hora_str, "Empleado": fm_emp, "Sucursal": "Manual", "Turno": "Manual", "Tipo": fm_tipo, "Estado": fm_estado, "Distancia_m": 0.0, "Nota": fm_nota})
                    st.success("✅ Fichaje manual cargado exitosamente.")
                    st.rerun()

        with tab_perfil:
            st.markdown('<div class="main-title" style="font-size: 2rem;">👤 Dossier Individual 360°</div>', unsafe_allow_html=True)
            col_pf1, col_pf2 = st.columns()
            emp_perfil = col_pf1.selectbox("Seleccionar Empleado:", ["Seleccionar..."] + sorted(lista_empleados))
            filtro_pf = col_pf2.selectbox("⏳ Periodo a evaluar:", ["Este Mes", "Mes Anterior", "Esta Semana", "Todo el Historial"], key="filtro_perf")
            pf_in, pf_fi = get_fechas_filtro(filtro_pf)

            if emp_perfil != "Seleccionar...":
                st.write(f"**Rol:** `{roles_empleados.get(emp_perfil, 'N/A')}` | **Estado:** {'📱 Enlazado' if emp_perfil in dispositivos_vinculados else '⚠️ Sin Celular'}")
                df_act_p, df_tar_p = load_df("asistencia"), load_df("tareas_log")
                if not df_act_p.empty:
                    df_act_p['F_Obj'] = pd.to_datetime(df_act_p['Fecha'], errors='coerce').dt.date
                    df_e_p = df_act_p[(df_act_p["Empleado"] == emp_perfil) & (df_act_p['F_Obj'] >= pf_in) & (df_act_p['F_Obj'] <= pf_fi)]
                    e_atiempo = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "A tiempo")]) if not df_e_p.empty else 0
                    e_tardes = len(df_e_p[(df_e_p["Tipo"] == "Entrada") & (df_e_p["Estado"] == "Tarde")]) if not df_e_p.empty else 0
                    e_ausencias = len(df_e_p[df_e_p["Tipo"] == "Ausente"]) if not df_e_p.empty else 0

                    horas_totales = 0.0
                    for f in df_e_p["Fecha"].unique() if not df_e_p.empty else []:
                        df_ef = df_e_p[df_e_p["Fecha"] == f].copy()
                        df_ef['Hora_dt'] = pd.to_datetime(df_ef['Hora'], errors='coerce')
                        df_ef = df_ef.dropna(subset=['Hora_dt']).sort_values(by="Hora_dt")
                        ent, sal = df_ef[df_ef["Tipo"] == "Entrada"], df_ef[df_ef["Tipo"] == "Salida"]
                        if not ent.empty and not sal.empty and sal.iloc[-1]["Estado"] != "Salida (Fuera de Rango)":
                            h_in, h_out = ent.iloc["Hora_dt"], sal.iloc[-1]["Hora_dt"]
                            diff = (h_out - h_in).total_seconds() / 3600.0
                            horas_totales += diff if diff >= 0 else (diff + 24.0)

                    e_aj = sum([int(p.get('Puntos', 0)) for p in lista_puntos if p.get('Empleado') == emp_perfil and p.get('Estado') == 'Aprobada' and pf_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= pf_fi])
                    e_tp = 0
                    if not df_tar_p.empty:
                        df_tar_p['F_Obj'] = pd.to_datetime(df_tar_p['Fecha'], errors='coerce').dt.date
                        e_tp = pd.to_numeric(df_tar_p[(df_tar_p["Empleado"] == emp_perfil) & (df_tar_p["Estado"] == "Aprobada") & (df_tar_p['F_Obj'] >= pf_in) & (df_tar_p['F_Obj'] <= pf_fi)]["Puntos"], errors='coerce').fillna(0).astype(int).sum()

                    reg = config_app.get("reglas_puntos", {})
                    puntaje = reg.get('base', 100) + (e_atiempo * reg.get('A tiempo', 0)) + (e_tardes * reg.get('Tarde', -5)) + (e_ausencias * reg.get('Ausente', -15)) + e_aj + e_tp

                    c_pf1, c_pf2, c_pf3, c_pf4 = st.columns(4)
                    c_pf1.metric("🕒 Horas Trabajadas", f"{round(horas_totales, 1)} hs")
                    c_pf2.metric("⭐ Puntos", f"{puntaje} pts")
                    c_pf3.metric("⚠️ Tardes", e_tardes)
                    c_pf4.metric("❌ Ausencias", e_ausencias)

                    with st.expander("Ficha Detallada"):
                        if not df_e_p.empty:
                            if 'id' in df_e_p.columns:
                                df_e_p['id_num'] = pd.to_numeric(df_e_p['id'], errors='coerce')
                            df_e_p = df_e_p.sort_values(by="id_num", ascending=False)
                            st.dataframe(df_e_p[["Fecha", "Hora", "Sucursal", "Turno", "Tipo", "Estado", "Nota"]], use_container_width=True, hide_index=True)
                        else: st.write("Sin fichajes en este período.")

        # ==========================================
        # 📦 NUEVO: AUDITORÍA DE INVENTARIO Y FUGAS (GERENCIA)
        # ==========================================
        with tab_inventario:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📦 Auditoría de Inventario y Control de Fugas</div>', unsafe_allow_html=True)
            
            stock_fardos = load_json("stock_fardos", [])
            planchado_log = load_json("planchado_log", [])
            salon_log = load_json("salon_log", [])
            ventas_ropa = load_json("ventas_ropa", [])
            
            col_inv1, col_inv2, col_inv3, col_inv4 = st.columns(4)
            fardos_dep = len([f for f in stock_fardos if f.get("estado") == "En Depósito"])
            fardos_proc = len([f for f in stock_fardos if f.get("estado") == "Planchado/Procesado"])
            total_planchado = sum([p.get("total", 0) for p in planchado_log])
            total_vendido = sum([v.get("cantidad", 0) for v in ventas_ropa])
            
            col_inv1.metric("📦 Fardos en Depósito", fardos_dep)
            col_inv2.metric("🧼 Fardos Abiertos/Planchados", fardos_proc)
            col_inv3.metric("👕 Prendas Totales Planchadas", f"{total_planchado} u")
            col_inv4.metric("💸 Ventas Totales en Caja", f"{total_vendido} u")
            
            st.write("---")
            st.subheader("🏁 Mapa de Almacenamiento (Ajedrez Depósito)")
            st.write("Distribución espacial de fardos en el Depósito Principal (Independencia) según su coordenada de almacenamiento:")
            
            filas_grid = ["A", "B", "C", "D", "E"]
            cols_grid = [str(x) for x in range(1, 7)]
            grid_data = {col: ["" for _ in filas_grid] for col in cols_grid}
            
            for f in stock_fardos:
                if f.get("estado") == "En Depósito":
                    pos = f.get("posicion", "")
                    if "-" in pos:
                        coord, niv = pos.split("-")
                        if len(coord) >= 2:
                            f_char = coord
                            c_char = coord
                            if f_char in filas_grid and c_char in cols_grid:
                                f_idx = filas_grid.index(f_char)
                                grid_data[c_char][f_idx] += f"[{f.get('codigo')}: {f.get('categoria')}] "
            
            df_grid = pd.DataFrame(grid_data, index=filas_grid)
            st.dataframe(df_grid, use_container_width=True)
            
            st.write("---")
            st.subheader("🚨 Conciliación Operativa (Prevención de Fugas)")
            st.write("Comparación de prendas recibidas en el salón de ventas contra ventas reales registradas por caja por cada sucursal:")
            
            recon_data = []
            for loc in list(lista_locales.keys()):
                planchado_loc = sum([p.get("normal", 0) + p.get("liquidacion", 0) for p in planchado_log if p.get("sucursal") == loc and p.get("estado") == "Recibido en Salón"])
                ventas_loc = sum([v.get("cantidad", 0) for v in ventas_ropa if v.get("sucursal") == loc])
                diferencia = planchado_loc - ventas_loc
                estado_alerta = "✅ Consistencia Correcta" if diferencia <= 5 else "⚠️ Diferencia Alta (Posible Fuga / Pérdida)"
                
                recon_data.append({
                    "Sucursal / Tienda": loc,
                    "👕 Recibido en Salón (Planchado)": planchado_loc,
                    "💸 Vendido en Caja": ventas_loc,
                    "Diferencia Acumulada": diferencia,
                    "Estado de Alerta": estado_alerta
                })
            
            if recon_data:
                st.dataframe(pd.DataFrame(recon_data), use_container_width=True, hide_index=True)
            else:
                st.info("Sin registros suficientes para análisis de conciliación.")
                
            st.write("---")
            st.subheader("📋 Base de Datos de Lotes (Fardos)")
            if stock_fardos:
                st.dataframe(pd.DataFrame(stock_fardos), use_container_width=True, hide_index=True)
            else:
                st.info("No hay fardos creados todavía.")

        # ==========================================
        # 📸 NUEVO: AUDITORÍA DE REDES Y DOMINGOS (GERENCIA)
        # ==========================================
        with tab_redes_domingo:
            st.markdown('<div class="main-title" style="font-size: 2rem;">📸 Gestión de Redes y Premiación de Domingos</div>', unsafe_allow_html=True)
            
            redes_log = load_json("redes_log", [])
            domingos_log = load_json("domingos_log", [])
            
            st.subheader("📸 Auditoría de Publicaciones del Personal")
            st.write("Audita y aprueba las publicaciones del personal para otorgar los puntos correspondientes.")
            
            pendientes_redes = [r for r in redes_log if r.get("estado") == "Pendiente"]
            if not pendientes_redes:
                st.info("No hay publicaciones en redes pendientes de aprobación.")
            else:
                for idx, r in enumerate(redes_log):
                    if r.get("estado") == "Pendiente":
                        with st.container():
                            st.write(f"👤 **{r['Empleado']}** publicó en **{r['red']}** ({r['tipo']}) el {r['Fecha']} {r['Hora']}")
                            st.write(f"🔗 **Link/Ref:** `{r['url']}`")
                            if r.get("detalle"): st.write(f"📝 **Detalle:** {r['detalle']}")
                            
                            c_red_ok, c_red_no = st.columns()
                            if c_red_ok.button("✅ Aprobar (+10 Puntos)", key=f"apr_red_{idx}"):
                                redes_log[idx]["estado"] = "Aprobada"
                                save_json("redes_log", redes_log)
                                
                                lista_puntos.append({
                                    "Fecha": fecha_hoy,
                                    "Empleado": r['Empleado'],
                                    "Puntos": 10,
                                    "Motivo": f"Publicación aprobada en {r['red']} ({r['tipo']})",
                                    "Autor": "Gerencia (Automático)",
                                    "Estado": "Aprobada"
                                })
                                save_json("ajustes_puntos", lista_puntos)
                                st.success(f"Publicación aprobada. Se otorgaron +10 puntos a {r['Empleado']}.")
                                st.rerun()
                                
                            if c_red_no.button("❌ Rechazar", key=f"rec_red_{idx}"):
                                redes_log[idx]["estado"] = "Rechazada"
                                save_json("redes_log", redes_log)
                                st.warning("Publicación rechazada.")
                                st.rerun()
                            st.write("---")
            
            st.write("---")
            st.subheader("💰 Calculadora de Rentabilidad en Marketing")
            st.markdown("<div class='super-box'><b>Ahorro por Colaboración de Empleados:</b> Al delegar publicaciones diarias al staff en sus tiempos libres, se reduce el costo de contratar modelos externos ($60,000 por sesión semanal).</div>", unsafe_allow_html=True)
            
            aprobados_count = len([r for r in redes_log if r.get("estado") == "Aprobada"])
            ahorro_por_post = 5000  # Estimación en pesos ahorrados por post de colaborador
            ahorro_total = aprobados_count * ahorro_por_post
            
            col_sav1, col_sav2 = st.columns(2)
            col_sav1.metric("📸 Publicaciones de Empleados Aprobadas", aprobados_count)
            col_sav2.metric("💵 Ahorro Estimado en Marketing", f"${ahorro_total:,} ARS")
            
            st.write("---")
            st.subheader("📅 Asignación de Turnos de Domingo (Incentivo de Desempeño)")
            st.write("Los turnos se otorgan prioritariamente a los mejores posicionados en el ranking mensual de puntos:")
            
            proximo_domingo = (ahora.date() + datetime.timedelta(days=(6 - ahora.date().weekday()) % 7)).strftime("%Y-%m-%d")
            st.markdown(f"**Postulaciones para el Domingo {proximo_domingo}:**")
            
            domingos_pendientes = [d for d in domingos_log if d.get("fecha_domingo") == proximo_domingo and d.get("estado") == "Pendiente"]
            
            if not domingos_pendientes:
                st.info("No hay postulaciones de colaboradores para este domingo.")
            else:
                reg_p = config_app.get("reglas_puntos", {})
                p_in_mes = ahora.date().replace(day=1)
                p_fi_mes = ahora.date()
                df_p, df_t = load_df("asistencia"), load_df("tareas_log")
                if not df_p.empty:
                    df_p['F_Obj'] = pd.to_datetime(df_p['Fecha'], errors='coerce').dt.date
                    df_p = df_p[(df_p['F_Obj'] >= p_in_mes) & (df_p['F_Obj'] <= p_fi_mes)]
                if not df_t.empty:
                    df_t['F_Obj'] = pd.to_datetime(df_t['Fecha'], errors='coerce').dt.date
                    df_t = df_t[(df_t['F_Obj'] >= p_in_mes) & (df_t['F_Obj'] <= p_fi_mes)]
                    
                puntos_mes_actual = {}
                for emp in lista_empleados:
                    e_aj = sum([int(p.get('Puntos', 0)) for p in lista_puntos if p_in_mes <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= p_fi_mes and p.get('Empleado') == emp and p.get('Estado', 'Aprobada') == 'Aprobada'])
                    e_tp = pd.to_numeric(df_t[(df_t["Empleado"] == emp) & (df_t["Estado"] == "Aprobada")]["Puntos"], errors='coerce').fillna(0).astype(int).sum() if not df_t.empty else 0
                    df_e = df_p[df_p["Empleado"] == emp] if not df_p.empty else pd.DataFrame()
                    e_ok = len(df_e[df_e["Estado"] == "A tiempo"]) if not df_e.empty else 0
                    e_tar = len(df_e[df_e["Estado"] == "Tarde"]) if not df_e.empty else 0
                    e_au = len(df_e[df_e["Tipo"] == "Ausente"]) if not df_e.empty else 0
                    puntos_mes_actual[emp] = reg_p.get('base', 100) + (e_ok * reg_p.get('A tiempo', 0)) + (e_tar * reg_p.get('Tarde', -5)) + (e_au * reg_p.get('Ausente', -15)) + e_aj + e_tp
                
                domingos_pendientes_sorted = sorted(domingos_pendientes, key=lambda x: puntos_mes_actual.get(x.get("Empleado"), 0), reverse=True)
                
                for idx, d in enumerate(domingos_pendientes_sorted):
                    real_idx = domingos_log.index(d)
                    emp_name = d.get("Empleado")
                    emp_pts = puntos_mes_actual.get(emp_name, 0)
                    
                    with st.container():
                        st.markdown(f"🏆 **Rank #{idx+1}: {emp_name}** | Puntos Acumulados: **{emp_pts} pts**")
                        st.write(f"🏪 Sucursal: {d.get('sucursal')} | 🕒 Turno: {d.get('turno')}")
                        if d.get("comentario"): st.write(f"💬 Comentario: {d.get('comentario')}")
                        
                        col_dom_ok, col_dom_no = st.columns()
                        if col_dom_ok.button("✅ Asignar Turno Domingo", key=f"apr_dom_{real_idx}"):
                            domingos_log[real_idx]["estado"] = "Asignado"
                            save_json("domingos_log", domingos_log)
                            st.success(f"Turno asignado a {emp_name} para el {proximo_domingo}.")
                            st.rerun()
                        if col_dom_no.button("❌ Descartar", key=f"rec_dom_{real_idx}"):
                            domingos_log[real_idx]["estado"] = "Rechazado"
                            save_json("domingos_log", domingos_log)
                            st.warning("Postulación rechazada.")
                            st.rerun()
                        st.write("---")
            
            st.write("---")
            st.subheader("📋 Historial de Asignaciones de Domingo")
            historial_dom = [d for d in domingos_log if d.get("estado") != "Pendiente"]
            if historial_dom:
                st.dataframe(pd.DataFrame(historial_dom), use_container_width=True, hide_index=True)
            else:
                st.info("Sin registros de asignación históricos.")

        with tab_staff:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.subheader("👥 Alta y Modificación")
                with st.form("form_alta_emp"):
                    nuevo_emp = st.text_input("Nuevo Empleado:")
                    rol_asignar = st.selectbox("Rol:", lista_roles_disponibles)
                    if st.form_submit_button("➕ Agregar") and nuevo_emp and nuevo_emp not in lista_empleados:
                        lista_empleados.append(nuevo_emp)
                        roles_empleados[nuevo_emp] = rol_asignar
                        tareas_individuales[nuevo_emp] = []
                        save_json("empleados", lista_empleados)
                        save_json("roles", roles_empleados)
                        save_json("tareas_individuales", tareas_individuales)
                        st.rerun()

                if lista_empleados:
                    emp_mod = st.selectbox("Editar/Borrar:", sorted(lista_empleados))
                    nuevo_rol = st.selectbox("Cambiar Rol a:", lista_roles_disponibles, index=lista_roles_disponibles.index(roles_empleados.get(emp_mod, lista_roles_disponibles)) if roles_empleados.get(emp_mod) in lista_roles_disponibles else 0)
                    c_mod1, c_mod2, c_mod3 = st.columns(3)
                    if c_mod1.button("✏️ Guardar Rol"):
                        roles_empleados[emp_mod] = nuevo_rol
                        save_json("roles", roles_empleados)
                        st.rerun()
                    if c_mod2.button("📱 Liberar Celular") and emp_mod in dispositivos_vinculados:
                        del dispositivos_vinculados[emp_mod]
                        save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()
                    if c_mod3.button("🗑️ Borrar"):
                        lista_empleados.remove(emp_mod)
                        roles_empleados.pop(emp_mod, None)
                        tareas_individuales.pop(emp_mod, None)
                        dispositivos_vinculados.pop(emp_mod, None)
                        save_json("empleados", lista_empleados)
                        save_json("roles", roles_empleados)
                        save_json("tareas_individuales", tareas_individuales)
                        save_json("dispositivos", dispositivos_vinculados)
                        st.rerun()
            with col_s2:
                st.subheader("📋 Asignar Tareas Extra")
                tipo_asig = st.radio("Asignar a:", ["Rol General", "Personal"])
                obj_tarea = st.selectbox("Elegí el destino:", lista_roles_disponibles if tipo_asig == "Rol General" else sorted(lista_empleados))
                n_tarea = st.text_input("Nombre Tarea:")
                p_tarea = st.number_input("Puntos de Tarea:", value=5, min_value=1)
                if st.button("➕ Asignar Tarea") and n_tarea:
                    if tipo_asig == "Rol General":
                        tareas_roles.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json("tareas_roles", tareas_roles)
                    else:
                        tareas_individuales.setdefault(obj_tarea, []).append({"tarea": n_tarea, "puntos": p_tarea})
                        save_json("tareas_individuales", tareas_individuales)
                    st.rerun()

                ver_t_tipo = st.radio("Ver tareas de:", ["Roles", "Personales"])
                diccionario_ver = tareas_roles if ver_t_tipo == "Roles" else tareas_individuales
                for clave, tareas in list(diccionario_ver.items()):
                    if tareas:
                        with st.expander(f"{clave}"):
                            for idx, t in enumerate(tareas):
                                c_t1, c_t2 = st.columns()
                                c_t1.write(f"- {t.get('tarea')} (+{t.get('puntos')})")
                                if c_t2.button("🗑️", key=f"del_t_{clave}_{idx}"):
                                    diccionario_ver[clave].pop(idx)
                                    save_json("tareas_roles" if ver_t_tipo == "Roles" else "tareas_individuales", diccionario_ver)
                                    st.rerun()

        with tab_tiendas:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.subheader("🏪 Tiendas Físicas")
                for loc, d_loc in lista_locales.items():
                    st.write(f"- **{loc}** | IP: `{d_loc.get('ip', 'Ninguna')}`")
                st.markdown("---")
                if client_ip and client_ip != 'Error':
                    st.info(f"💡 **Ayuda de Configuración:** La IP actual de tu conexión es `{client_ip}`. (Si estás físicamente en la sucursal nueva, podés copiar y pegar este número abajo).")
                else:
                    st.info("📡 Buscando tu IP actual para ayudarte a configurar...")
                n_loc = st.text_input("Nueva Tienda:")
                lat_loc = st.number_input("Lat:", format="%.6f")
                lon_loc = st.number_input("Lon:", format="%.6f")
                ip_loc = st.text_input("IP Wi-Fi:")
                if st.button("➕ Crear Tienda") and n_loc:
                    lista_locales[n_loc] = {"lat": lat_loc, "lon": lon_loc, "ip": ip_loc.strip()}
                    save_json("locales", lista_locales)
                    st.rerun()

                borrar_loc = st.selectbox("Eliminar Tienda:", ["Seleccionar..."] + list(lista_locales.keys()))
                if st.button("🗑️ Eliminar Tienda") and borrar_loc != "Seleccionar...":
                    del lista_locales[borrar_loc]
                    save_json("locales", lista_locales)
                    st.rerun()
            with col_l2:
                st.subheader("🕒 Turnos / Horarios")
                for turno, horas in lista_turnos.items():
                    st.write(f"- **{turno}** | De {horas.get('ingreso')} a {horas.get('salida')}")
                n_turno = st.text_input("Nuevo Horario (Nombre):")
                c_h1, c_h2 = st.columns(2)
                h_ingreso = c_h1.time_input("Ingreso:")
                h_salida = c_h2.time_input("Salida:")
                if st.button("➕ Crear Horario") and n_turno:
                    lista_turnos[n_turno] = {"ingreso": h_ingreso.strftime("%I:%M %p"), "salida": h_salida.strftime("%I:%M %p")}
                    save_json("turnos", lista_turnos)
                    st.rerun()

                borrar_turno = st.selectbox("Eliminar Turno:", ["Seleccionar..."] + list(lista_turnos.keys()))
                if st.button("🗑️ Eliminar Turno") and borrar_turno != "Seleccionar...":
                    del lista_turnos[borrar_turno]
                    save_json("turnos", lista_turnos)
                    st.rerun()

        with tab_comunicados:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.subheader("🔔 Alerta al Ingresar")
                with st.form("form_alertas"):
                    dest_ing = st.selectbox("Destinatario:", ["Todos"] + sorted(lista_empleados))
                    txt_alerta = st.text_area("Mensaje:")
                    if st.form_submit_button("Crear Alerta") and txt_alerta:
                        alertas_ingreso.append({"destinatario": dest_ing, "texto": txt_alerta})
                        save_json("alertas_ingreso", alertas_ingreso)
                        st.rerun()

                for idx, a in enumerate(alertas_ingreso):
                    with st.expander(f"A {a['destinatario']}: {a['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_al_{idx}"):
                            alertas_ingreso.pop(idx)
                            save_json("alertas_ingreso", alertas_ingreso)
                            st.rerun()
            with col_m2:
                st.subheader("📢 Anuncio Fijo")
                with st.form("form_fijo"):
                    dest_fijo = st.selectbox("Destinatario:", ["Todos"] + sorted(lista_empleados), key="fijo")
                    txt_fijo = st.text_area("Mensaje:")
                    if st.form_submit_button("Publicar") and txt_fijo:
                        lista_mensajes.append({"destinatario": dest_fijo, "texto": txt_fijo})
                        save_json("mensajes", lista_mensajes)
                        st.rerun()

                for idx, m in enumerate(lista_mensajes):
                    with st.expander(f"A {m['destinatario']}: {m['texto'][:20]}..."):
                        if st.button("🗑️ Eliminar", key=f"del_m_{idx}"):
                            lista_mensajes.pop(idx)
                            save_json("mensajes", lista_mensajes)
                            st.rerun()

        with tab_config:
            col_aj1, col_aj2 = st.columns(2)
            with col_aj1:
                st.subheader("👥 Roles de la Empresa")
                nuevo_rol_cat = st.text_input("Crear Nuevo Rol:")
                if st.button("➕ Agregar Rol") and nuevo_rol_cat and nuevo_rol_cat not in lista_roles_disponibles:
                    lista_roles_disponibles.append(nuevo_rol_cat)
                    save_json("lista_roles", lista_roles_disponibles)
                    st.rerun()

                borrar_rol_cat = st.selectbox("Eliminar Rol:", ["Seleccionar..."] + lista_roles_disponibles)
                if st.button("🗑️ Eliminar Rol") and borrar_rol_cat != "Seleccionar...":
                    lista_roles_disponibles.remove(borrar_rol_cat)
                    save_json("lista_roles", lista_roles_disponibles)
                    st.rerun()

                st.subheader("⚖️ Reglas de Asistencia")
                with st.form("form_reglas"):
                    r_base = st.number_input("Puntaje Base:", value=config_app.get("reglas_puntos", {}).get("base", 100))
                    c_r1, c_r2 = st.columns(2)
                    r_ok = c_r1.number_input("✔ A Tiempo:", value=config_app.get("reglas_puntos", {}).get("A tiempo", 0))
                    r_tar = c_r2.number_input("⚠️ Tarde:", value=config_app.get("reglas_puntos", {}).get("Tarde", -5))
                    r_aus = c_r1.number_input("❌ Ausente:", value=config_app.get("reglas_puntos", {}).get("Ausente", -15))
                    r_fj = c_r2.number_input("Justif:", value=config_app.get("reglas_puntos", {}).get("Falta Justificada", 0))
                    if st.form_submit_button("💾 Guardar Reglas"):
                        config_app["reglas_puntos"] = {"base": r_base, "A tiempo": r_ok, "Tarde": r_tar, "Ausente": r_aus, "Falta Justificada": r_fj}
                        save_json("config", config_app)
                        st.rerun()
            with col_aj2:
                st.subheader("🛡️ Seguridad de Red y Ajustes")
                with st.form("form_seguridad"):
                    v_gps = st.checkbox("📡 Requerir GPS", value=config_app.get("verificar_gps", True))
                    radio_m = st.number_input("Radio en metros:", value=int(config_app.get("radio_metros", 50)))
                    v_wifi = st.checkbox("🌐 Requerir Wi-Fi", value=config_app.get("verificar_wifi", False))
                    nueva_tolerancia = st.number_input("Minutos tolerancia:", value=int(config_app.get("tolerancia_minutos", 10)))
                    if st.form_submit_button("💾 Guardar Ajustes"):
                        config_app.update({"verificar_gps": v_gps, "verificar_wifi": v_wifi, "radio_metros": radio_m, "tolerancia_minutos": nueva_tolerancia})
                        save_json("config", config_app)
                        st.rerun()

                st.write("🔑 **Cambiar Clave de Gerencia**")
                nc = st.text_input("Nueva clave:", type="password")
                if st.button("🔑 Cambiar Clave") and nc:
                    config_app["admin_password"] = nc
                    save_json("config", config_app)
                    st.success("Clave modificada.")

                st.markdown("---")
                st.subheader("🧼 Reseteo Quirúrgico en Nube")
                c_cl1, c_cl2 = st.columns(2)
                with c_cl1:
                    del_asist = st.checkbox("Registros de Asistencia")
                    del_tareas = st.checkbox("Tareas Realizadas")
                    del_bonos = st.checkbox("Bonos/Multas Manuales")
                with c_cl2:
                    filtro_b = st.selectbox("⏳ Rango a borrar:", ["Hoy", "Esta Semana", "Este Mes", "Mes Anterior", "Todo el Historial", "Personalizado"], key="filtro_borrado")
                    rango_borrado = st.date_input("📅 Fechas a limpiar:", value=(ahora.date(), ahora.date())) if filtro_b == "Personalizado" else None

                if st.button("🚨 CONFIRMAR BORRADO"):
                    b_in, b_fi = get_fechas_filtro(filtro_b, rango_borrado)
                    if del_asist: 
                        supabase.table("asistencia").delete().gte("Fecha", b_in.strftime("%Y-%m-%d")).lte("Fecha", b_fi.strftime("%Y-%m-%d")).execute()
                    if del_tareas: 
                        supabase.table("tareas_log").delete().gte("Fecha", b_in.strftime("%Y-%m-%d")).lte("Fecha", b_fi.strftime("%Y-%m-%d")).execute()
                    if del_bonos:
                        lista_puntos = [p for p in lista_puntos if not (b_in <= datetime.datetime.strptime(p['Fecha'], "%Y-%m-%d").date() <= b_fi)]
                        save_json("ajustes_puntos", lista_puntos)
                    st.success("¡Datos borrados de la nube exitosamente!")
                    st.rerun()

        with tab_espia:
            if lista_intentos:
                st.dataframe(pd.DataFrame(lista_intentos).sort_values(by=["Fecha", "Hora"], ascending=[False, False]), use_container_width=True, hide_index=True)
                if st.button("🗑️ Limpiar registro"): 
                    save_json("intentos_seguridad", [])
                    st.rerun()
            else:
                st.info("Sin intentos de acceso.")
