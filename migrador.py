import streamlit as st
from supabase import create_client

# Nos conectamos a tu Supabase usando tus mismos secretos
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🚀 Migrador de Datos JSON a SQL")
st.warning("⚠️ Presioná el botón una sola vez para no duplicar datos.")

if st.button("Iniciar Migración de Datos"):
    try:
        # 1. Leer todo el JSON de app_data
        st.write("📥 Leyendo datos antiguos...")
        res = supabase.table('app_data').select('*').execute()
        datos_json = {row['id']: row['data'] for row in res.data}

        # 2. Migrar Empleados, Roles y Dispositivos
        st.write("⏳ Migrando Empleados...")
        empleados = datos_json.get('empleados', [])
        roles = datos_json.get('roles', {})
        dispositivos = datos_json.get('dispositivos', {})
        
        for emp in empleados:
            rol = roles.get(emp, "Staff")
            disp = dispositivos.get(emp, None)
            # Insertar en SQL (usamos upsert para que no tire error si lo corrés 2 veces)
            supabase.table('empleados').upsert({"nombre": emp, "rol": rol, "dispositivo_id": disp}).execute()

        # 3. Migrar Locales
        st.write("⏳ Migrando Sucursales...")
        locales = datos_json.get('locales', {})
        for nombre, info in locales.items():
            supabase.table('locales').upsert({
                "nombre": nombre, 
                "lat": info.get("lat"), 
                "lon": info.get("lon"), 
                "ip": info.get("ip", "")
            }).execute()

        # 4. Migrar Turnos
        st.write("⏳ Migrando Turnos...")
        turnos = datos_json.get('turnos', {})
        for nombre, info in turnos.items():
            supabase.table('turnos').upsert({
                "nombre": nombre, 
                "ingreso": info.get("ingreso"), 
                "salida": info.get("salida")
            }).execute()

        # 5. Migrar Cierres de Caja
        st.write("⏳ Migrando Cierres de Caja...")
        cierres = datos_json.get('cierres_caja', [])
        for c in cierres:
            # Insert normal porque acá hay IDs UUID autogenerados
            supabase.table('cierres_caja').insert({
                "fecha": c.get("Fecha"), 
                "hora": c.get("Hora"), 
                "cajero": c.get("Cajero"), 
                "sucursal": c.get("Sucursal"), 
                "turno": c.get("Turno"), 
                "efectivo": c.get("Efectivo"), 
                "tarjeta": c.get("Tarjeta"), 
                "transferencia": c.get("Transferencia"), 
                "total_ventas": c.get("Total_Ventas"), 
                "nota": c.get("Nota")
            }).execute()

        # 6. Migrar Sueldos
        st.write("⏳ Migrando Historial de Sueldos...")
        sueldos = datos_json.get('sueldos_historico', [])
        for s in sueldos:
            supabase.table('sueldos_historico').insert({
                "empleado": s.get("Empleado"), 
                "fecha_desde": s.get("Fecha_Desde"), 
                "fecha_hasta": s.get("Fecha_Hasta"), 
                "valor_hora": s.get("Valor_Hora")
            }).execute()

        # 7. Migrar Planificación Semanal
        st.write("⏳ Migrando Planillas de Turnos...")
        planificacion = datos_json.get('planificacion_turnos', {})
        for fecha, locales_plan in planificacion.items():
            if isinstance(locales_plan, dict):
                for suc, turnos_plan in locales_plan.items():
                    if isinstance(turnos_plan, dict):
                        for turno, empleados_asignados in turnos_plan.items():
                            if isinstance(empleados_asignados, list):
                                for emp in empleados_asignados:
                                    if emp != "Nadie" and str(emp).strip() != "":
                                        supabase.table('planificacion_turnos').insert({
                                            "fecha": fecha, 
                                            "sucursal": suc, 
                                            "turno": turno, 
                                            "empleado": emp
                                        }).execute()

        st.success("✅ ¡MIGRACIÓN COMPLETADA CON ÉXITO! Todos tus datos ya están en las nuevas tablas SQL.")
        st.balloons()

    except Exception as e:
        st.error(f"❌ Ocurrió un error en la migración: {e}")
