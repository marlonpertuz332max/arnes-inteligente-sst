import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import pandas as pd
import uuid
from datetime import datetime
from matplotlib.patches import Circle, Rectangle, Arc

# Configuración de la página
st.set_page_config(page_title="Arnés Inteligente SST", page_icon="🦺", layout="wide")

# =============================================
# SISTEMA DE SIMULACIÓN MULTIJUGADOR - INICIALIZACIÓN
# =============================================

# Inicializar session state para el sistema multijugador
if 'monitores' not in st.session_state:
    st.session_state.monitores = {}
if 'salas' not in st.session_state:
    st.session_state.salas = {}
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = {}
if 'ultima_actualizacion_movimiento' not in st.session_state:
    st.session_state.ultima_actualizacion_movimiento = datetime.now()
if 'movimiento_automatico' not in st.session_state:
    st.session_state.movimiento_automatico = True
if "fall_count" not in st.session_state:
    st.session_state.fall_count = 0
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "simulation_start_time" not in st.session_state:
    st.session_state.simulation_start_time = datetime.now()
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Inicio"

# =============================================
# FUNCIONES DEL SISTEMA MULTIJUGADOR
# =============================================

def generar_codigo_sala():
    return f"SIM-{random.randint(1000, 9999)}"

def obtener_icono_personaje(tipo_personaje):
    iconos = {
        "Hombre musculoso": "💪",
        "Mujer atlética": "🏃‍♀️", 
        "Persona mayor": "👴",
        "Persona con sobrepeso": "🧍",
        "Mujer embarazada": "🤰",
        "Persona con discapacidad motriz": "♿"
    }
    return iconos.get(tipo_personaje, "👤")

def enviar_whatsapp_simulacion(numero, mensaje):
    return True, f"Mensaje simulado enviado a {numero}"

# 🚨 SISTEMA DE DETECCIÓN AUTOMÁTICA DE RIESGOS
def evaluar_riesgos_automaticos(estudiante, ubicacion):
    riesgos_detectados = []
    
    condiciones_salud = estudiante.get('condiciones_salud', [])
    
    if "Vértigo" in condiciones_salud and "Andamios" in ubicacion:
        riesgos_detectados.append("🦘 Riesgo de vértigo en altura")
    
    if "Mareos" in condiciones_salud and "Estructura" in ubicacion:
        riesgos_detectados.append("🌀 Posible mareo en estructura elevada")
    
    if "Problemas cardíacos" in condiciones_salud:
        riesgos_detectados.append("❤️ Monitoreo cardíaco requerido")
    
    if "Diabetes" in condiciones_salud:
        riesgos_detectados.append("🩸 Riesgo hipoglucémico - monitoreo continuo")
    
    tipo_personaje = estudiante.get('tipo_personaje', '')
    
    if tipo_personaje == "Persona mayor":
        riesgos_detectados.append("👴 Mayor riesgo de fatiga y caídas")
    
    if tipo_personaje == "Mujer embarazada":
        riesgos_detectados.append("🤰 Riesgo elevado - evitar esfuerzos intensos")
        if "Excavación" in ubicacion:
            riesgos_detectados.append("⚠️ Exposición a vibraciones peligrosa")
    
    if tipo_personaje == "Persona con discapacidad motriz":
        riesgos_detectados.append("♿ Movilidad reducida - rutas de evacuación críticas")
    
    if tipo_personaje == "Persona con sobrepeso":
        riesgos_detectados.append("⚖️ Mayor carga articular - límite de peso reducido")
    
    peso = estudiante.get('peso', 70)
    altura = estudiante.get('altura', 170)
    
    if altura > 0:
        imc = peso / ((altura/100) ** 2)
        if imc > 30:
            riesgos_detectados.append("📊 IMC elevado - mayor riesgo metabólico")
        if imc < 18.5:
            riesgos_detectados.append("📊 Bajo peso - riesgo de fatiga")
    
    herramientas = estudiante.get('herramientas', [])
    
    if "Soldadora" in herramientas and "Andamios" in ubicacion:
        riesgos_detectados.append("🔥 Riesgo de incendio por soldadura en altura")
    
    if "Taladro" in herramientas and "Estructura" in ubicacion:
        riesgos_detectados.append("⚡ Riesgo eléctrico aumentado")
    
    if "Sierra eléctrica" in herramientas:
        riesgos_detectados.append("🔪 Corte severo - EPP completo requerido")
    
    epp_requerido = ["Casco", "Botas con punta de acero"]
    epp_faltante = [ep for ep in epp_requerido if ep not in estudiante.get('epp', [])]
    
    if epp_faltante:
        riesgos_detectados.append(f"🦺 EPP faltante: {', '.join(epp_faltante)}")
    
    if "Andamios" in ubicacion and "Arnés de seguridad" not in estudiante.get('epp', []):
        riesgos_detectados.append("🪂 ALTURA CRÍTICA - Arnés de seguridad requerido")
    
    if "Excavación" in ubicacion:
        riesgos_detectados.append("⛰️ Riesgo de derrumbe o atrapamiento")
    
    if "Estructura" in ubicacion:
        riesgos_detectados.append("🏗️ Caída de objetos - área delimitada")
    
    if len(herramientas) > 3:
        riesgos_detectados.append("🎒 Sobrecarga de herramientas - riesgo ergonómico")
    
    return riesgos_detectados

def evaluar_riesgo_caida(estudiante, ubicacion):
    factores_riesgo = 0
    
    if "Vértigo" in estudiante.get('condiciones_salud', []):
        factores_riesgo += 2
    
    if "Mareos" in estudiante.get('condiciones_salud', []):
        factores_riesgo += 2
    
    if estudiante.get('tipo_personaje') == "Persona mayor":
        factores_riesgo += 2
    
    if estudiante.get('tipo_personaje') == "Mujer embarazada":
        factores_riesgo += 3
    
    if "Andamios" in ubicacion:
        factores_riesgo += 3
    
    if "Estructura" in ubicacion:
        factores_riesgo += 2
    
    if "Arnés de seguridad" not in estudiante.get('epp', []):
        factores_riesgo += 4
    
    if factores_riesgo >= 8:
        return "🔴 ALTO RIESGO de caída"
    elif factores_riesgo >= 5:
        return "🟡 MEDIO RIESGO de caída"
    elif factores_riesgo >= 3:
        return "🟢 BAJO RIESGO de caída"
    else:
        return None

def evaluar_riesgo_sobrecarga(estudiante):
    peso = estudiante.get('peso', 70)
    herramientas = estudiante.get('herramientas', [])
    
    puntaje = 0
    
    if peso > 100:
        puntaje += 3
    elif peso > 85:
        puntaje += 2
    elif peso > 70:
        puntaje += 1
    
    if len(herramientas) > 4:
        puntaje += 3
    elif len(herramientas) > 2:
        puntaje += 2
    
    herramientas_pesadas = ["Soldadora", "Compactadora", "Hidrolavadora"]
    for herramienta in herramientas:
        if herramienta in herramientas_pesadas:
            puntaje += 2
    
    if puntaje >= 5:
        return "⚖️ ALERTA: Posible sobrecarga física"
    elif puntaje >= 3:
        return "⚖️ ADVERTENCIA: Carga física elevada"
    else:
        return None

def simular_movimiento_continuo():
    if not st.session_state.get('movimiento_automatico', False):
        return False
    
    ahora = datetime.now()
    ultima_actualizacion = st.session_state.ultima_actualizacion_movimiento
    
    if (ahora - ultima_actualizacion).total_seconds() >= 20:
        zonas = ["Zona A - Andamios", "Zona B - Excavación", "Zona C - Estructura", "Zona D - Acabados"]
        movimiento_ocurrido = False
        
        for sala_id, sala in st.session_state.salas.items():
            if sala.get('simulacion_iniciada', False):
                for est_id in sala['estudiantes']:
                    estudiante = st.session_state.estudiantes[est_id]
                    
                    if random.random() < 0.35:
                        zonas_posibles = [z for z in zonas if z != estudiante['ubicacion_actual']]
                        if zonas_posibles:
                            nueva_zona = random.choice(zonas_posibles)
                            
                            movimiento_anterior = estudiante['ubicacion_actual']
                            estudiante['ubicacion_actual'] = nueva_zona
                            estudiante['ultimo_movimiento'] = ahora.strftime("%H:%M:%S")
                            estudiante['historial_movimientos'] = estudiante.get('historial_movimientos', [])
                            estudiante['historial_movimientos'].append({
                                'desde': movimiento_anterior,
                                'hacia': nueva_zona,
                                'hora': ahora.strftime("%H:%M:%S")
                            })
                            
                            riesgos_automaticos = evaluar_riesgos_automaticos(estudiante, nueva_zona)
                            for riesgo in riesgos_automaticos:
                                if riesgo not in estudiante['riesgos_detectados']:
                                    estudiante['riesgos_detectados'].append(riesgo)
                            
                            riesgo_caida = evaluar_riesgo_caida(estudiante, nueva_zona)
                            if riesgo_caida and riesgo_caida not in estudiante['riesgos_detectados']:
                                estudiante['riesgos_detectados'].append(riesgo_caida)
                            
                            riesgo_sobrecarga = evaluar_riesgo_sobrecarga(estudiante)
                            if riesgo_sobrecarga and riesgo_sobrecarga not in estudiante['riesgos_detectados']:
                                estudiante['riesgos_detectados'].append(riesgo_sobrecarga)
                            
                            movimiento_ocurrido = True
        
        st.session_state.ultima_actualizacion_movimiento = ahora
        return movimiento_ocurrido
    
    return False

# =============================================
# INTERFAZ PRINCIPAL MEJORADA
# =============================================

# Título principal con diseño especial
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0; font-size: 2.5em;'>🦺 Sistema de Protección Inteligente</h1>
    <h2 style='color: white; margin: 0; font-size: 1.8em;'>para Trabajos en Altura</h2>
</div>
""", unsafe_allow_html=True)

# Tarjeta con el nombre de la ingeniera
st.markdown("""
<div style='text-align: center; padding: 15px; background: #f0f8ff; border-radius: 10px; border-left: 5px solid #667eea; margin-bottom: 20px;'>
    <h3 style='color: #2c3e50; margin: 0; font-size: 1.3em;'>👩‍🔬 Proyecto de Grado</h3>
    <h2 style='color: #8e44ad; margin: 0; font-size: 1.5em; font-weight: bold;'>Ingeniera en Seguridad y Salud en el Trabajo</h2>
    <h1 style='color: #2c3e50; margin: 0; font-size: 1.8em; font-weight: bold;'>💫 Michell Andrea Rodriguez Rivera</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =============================================
# MENÚ PRINCIPAL MEJORADO
# =============================================

menu = st.sidebar.selectbox(
    "*Navegación Principal:*",
    ["🏠 Inicio", "🎮 Simulador Original", "👨‍🏫 Modo Multijugador", "📊 Salas Activas"]
)

# Ejecutar movimiento automático
movimiento_simulado = simular_movimiento_continuo()
if movimiento_simulado:
    st.rerun()

# =============================================
# SECCIÓN: MODO MULTIJUGADOR
# =============================================


if menu == "👨‍🏫 Modo Multijugador":
    st.header("🎮 Sistema de Simulación Multijugador")
    
    submenu = st.selectbox("Selecciona el modo:", 
                          ["👨‍🏫 Crear Sala como Monitor", "🎓 Unirse como Estudiante"])
    
    if submenu == "👨‍🏫 Crear Sala como Monitor":
        # ... (código existente para crear sala) ...
        pass
        
    elif submenu == "🎓 Unirse como Estudiante":
        st.subheader("🎓 Unirse a Sala de Simulación")
        
        codigo_sala = st.text_input("Ingresa el código de la sala:", placeholder="SIM-1234").upper()
        
        if codigo_sala:
            sala_encontrada = None
            for sala_id, sala in st.session_state.salas.items():
                if sala['codigo'] == codigo_sala and sala.get('activa', True):
                    sala_encontrada = sala
                    break
            
            if sala_encontrada:
                if len(sala_encontrada['estudiantes']) >= sala_encontrada['max_estudiantes']:
                    st.error("❌ La sala está llena. No se pueden unir más estudiantes.")
                else:
                    st.success(f"✅ Sala encontrada: {sala_encontrada['tipo_escenario']}")
                    st.info(f"👨‍🏫 Monitor: {sala_encontrada['monitor_nombre']}")
                    
                    with st.form("registro_estudiante"):
                        st.subheader("👤 Registro del Estudiante")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            nombre_estudiante = st.text_input("Nombre completo *", placeholder="Ana García López")
                            edad = st.number_input("Edad *", min_value=18, max_value=65, value=25)
                            experiencia = st.selectbox("Experiencia en construcción *",
                                                     ["Ninguna", "Menos de 1 año", "1-3 años", "3-5 años", "Más de 5 años"])
                        
                        with col2:
                            institucion = st.text_input("Institución/Empresa *", placeholder="Universidad Técnica")
                            telefono = st.text_input("WhatsApp *", placeholder="+52 55 1234 5678")
                            email = st.text_input("Email *", placeholder="ana.garcia@email.com")
                        
                        st.markdown("---")
                        st.subheader("🎭 Personalización del Personaje")
                        
                        col3, col4, col5 = st.columns(3)
                        
                        with col3:
                            tipo_personaje = st.selectbox("Tipo de personaje *",
                                                        ["Hombre musculoso", "Mujer atlética", "Persona mayor", 
                                                         "Persona con sobrepeso", "Mujer embarazada", "Persona con discapacidad motriz"])
                            
                            tono_piel = st.selectbox("Tono de piel *",
                                                   ["Muy claro", "Claro", "Medio", "Oscuro", "Muy oscuro"])
                        
                        with col4:
                            cabello = st.selectbox("Estilo de cabello *",
                                                 ["Cabello corto", "Cabello largo", "Calvo", "Rasta", "Moño/Recogido"])
                            
                            altura = st.number_input("Altura (cm) *", min_value=140, max_value=200, value=170)
                        
                        with col5:
                            complexión = st.selectbox("Complexión física *",
                                                    ["Delgado", "Atlético", "Mediano", "Robusto", "Obeso"])
                            
                            peso = st.number_input("Peso (kg) *", min_value=40, max_value=150, value=70)
                        
                        st.markdown("---")
                        st.subheader("🏥 Condiciones de Salud (Opcional)")
                        
                        condiciones_salud = st.multiselect("Condiciones de salud conocidas:",
                                                          ["Vértigo", "Mareos", "Problemas cardíacos", "Diabetes", 
                                                           "Problemas respiratorios", "Problemas de espalda", "Ninguna"])
                        
                        st.subheader("🛠 Equipamiento y EPP")
                        
                        col_equipo1, col_equipo2 = st.columns(2)
                        
                        with col_equipo1:
                            herramientas = st.multiselect("Herramientas a utilizar:",
                                                         ["Martillo", "Taladro", "Soldadora", "Sierra eléctrica", 
                                                          "Llave inglesa", "Nivel", "Ninguna"])
                        
                        with col_equipo2:
                            epp = st.multiselect("Equipo de protección personal (EPP):",
                                                ["Casco", "Botas con punta de acero", "Guantes", "Gafas de seguridad",
                                                 "Arnés de seguridad", "Chaleco reflectante", "Protector auditivo"])
                        
                        submitted_estudiante = st.form_submit_button("🎮 Unirse a la Simulación", type="primary")
                        
                        if submitted_estudiante:
                            if nombre_estudiante and institucion and telefono:
                                # Crear estudiante
                                estudiante_id = str(uuid.uuid4())[:8]
                                estudiante = {
                                    'id': estudiante_id,
                                    'nombre': nombre_estudiante,
                                    'edad': edad,
                                    'experiencia': experiencia,
                                    'institucion': institucion,
                                    'telefono': telefono,
                                    'email': email,
                                    'tipo_personaje': tipo_personaje,
                                    'tono_piel': tono_piel,
                                    'cabello': cabello,
                                    'altura': altura,
                                    'complexion': complexión,
                                    'peso': peso,
                                    'condiciones_salud': condiciones_salud,
                                    'herramientas': herramientas,
                                    'epp': epp,
                                    'sala_id': sala_encontrada['sala_id'],
                                    'ubicacion_actual': "Zona A - Andamios",
                                    'riesgos_detectados': [],
                                    'ultimo_movimiento': datetime.now().strftime("%H:%M:%S"),
                                    'historial_movimientos': [],
                                    'fecha_union': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                                # Añadir a la sala
                                sala_encontrada['estudiantes'].append(estudiante_id)
                                st.session_state.estudiantes[estudiante_id] = estudiante
                                
                                # Evaluar riesgos iniciales
                                riesgos_iniciales = evaluar_riesgos_automaticos(estudiante, estudiante['ubicacion_actual'])
                                estudiante['riesgos_detectados'].extend(riesgos_iniciales)
                                
                                st.success(f"✅ Te has unido exitosamente a la sala!")
                                st.balloons()
                                
                                st.markdown("---")
                                st.subheader("👤 Tu Personaje Creado")
                                
                                col_per1, col_per2 = st.columns(2)
                                
                                with col_per1:
                                    st.metric("Nombre", nombre_estudiante)
                                    st.metric("Personaje", f"{obtener_icono_personaje(tipo_personaje)} {tipo_personaje}")
                                    st.metric("Experiencia", experiencia)
                                
                                with col_per2:
                                    st.metric("Ubicación Inicial", "Zona A - Andamios")
                                    st.metric("Riesgos Detectados", len(riesgos_iniciales))
                                    st.metric("EPP Equipado", len(epp))
                                
                                if riesgos_iniciales:
                                    st.warning("⚠️ **Riesgos detectados inicialmente:**")
                                    for riesgo in riesgos_iniciales:
                                        st.write(f"- {riesgo}")
                                
                            else:
                                st.error("❌ Por favor completa todos los campos obligatorios (*)")
            else:
                st.error("❌ No se encontró ninguna sala activa con ese código")
                st.info("💡 Asegúrate de que:")
                st.write("• El código sea correcto (ej: SIM-1234)")
                st.write("• La sala esté activa")
                st.write("• El monitor haya creado la sala recientemente")
                
                # Mostrar salas disponibles para debugging
                if st.checkbox("Mostrar salas disponibles (para debugging)"):
                    if st.session_state.salas:
                        st.write("Salas activas:")
                        for sala_id, sala in st.session_state.salas.items():
                            if sala.get('activa', True):
                                st.write(f"- {sala['codigo']}: {sala['tipo_escenario']} ({len(sala['estudiantes'])}/{sala['max_estudiantes']} estudiantes)")
                    else:
                        st.write("No hay salas creadas aún")
# =============================================
# SECCIÓN: SALAS ACTIVAS (PARA MONITORES) - COMPLETA
# =============================================

elif menu == "📊 Salas Activas":
    st.header("📊 Salas de Simulación Activas")
    
    if not st.session_state.salas:
        st.info("📝 No hay salas activas. Crea una sala en 'Modo Multijugador'.")
    else:
        # Contadores generales
        total_estudiantes = sum(len(sala['estudiantes']) for sala in st.session_state.salas.values() if sala['activa'])
        total_salas_activas = sum(1 for sala in st.session_state.salas.values() if sala['activa'])
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Salas Activas", total_salas_activas)
        with col_stats2:
            st.metric("Estudiantes Totales", total_estudiantes)
        with col_stats3:
            salas_simulando = sum(1 for sala in st.session_state.salas.values() if sala.get('simulacion_iniciada', False))
            st.metric("Simulaciones Activas", salas_simulando)
        
        for sala_id, sala in st.session_state.salas.items():
            if sala['activa']:
                with st.expander(f"🏠 {sala['codigo']} - {sala['tipo_escenario']} ({len(sala['estudiantes'])}/{sala['max_estudiantes']} estudiantes)", expanded=True):
                    
                    col_sala1, col_sala2, col_sala3 = st.columns(3)
                    
                    with col_sala1:
                        st.metric("Monitor", sala['monitor_nombre'])
                        st.metric("Dificultad", sala['nivel_dificultad'])
                        st.metric("Empresa", sala['empresa'])
                    
                    with col_sala2:
                        st.metric("Estudiantes", f"{len(sala['estudiantes'])}/{sala['max_estudiantes']}")
                        st.metric("Duración", f"{sala['duracion']} min")
                        st.metric("Clima", sala['condiciones_climaticas'])
                    
                    with col_sala3:
                        st.metric("Riesgos Configurados", len(sala['riesgos_activados']))
                        estado = "🎬 Activa" if sala.get('simulacion_iniciada', False) else "⏸️ Pausada"
                        st.metric("Estado Simulación", estado)
                        st.metric("Creada", sala['fecha_creacion'].split()[0])
                    
                    # Descripción del escenario
                    st.write("**Descripción:**", sala['descripcion_escenario'])
                    
                    # Botones de control para el monitor
                    st.subheader("🎮 Controles de Simulación")
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    
                    with col_btn1:
                        if st.button(f"🎬 Iniciar Simulación", key=f"start_{sala_id}", type="primary"):
                            sala['simulacion_iniciada'] = True
                            st.success("✅ Simulación iniciada! Los estudiantes comenzarán a moverse automáticamente.")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button(f"⏸️ Pausar Simulación", key=f"pause_{sala_id}"):
                            sala['simulacion_iniciada'] = False
                            st.warning("⏸️ Simulación pausada")
                            st.rerun()
                    
                    with col_btn3:
                        if st.button(f"🔄 Reiniciar Movimientos", key=f"reset_{sala_id}"):
                            # Reiniciar ubicaciones de todos los estudiantes
                            for est_id in sala['estudiantes']:
                                if est_id in st.session_state.estudiantes:
                                    st.session_state.estudiantes[est_id]['ubicacion_actual'] = "Zona A - Andamios"
                                    st.session_state.estudiantes[est_id]['riesgos_detectados'] = []
                            st.info("🔄 Ubicaciones reiniciadas")
                            st.rerun()
                    
                    with col_btn4:
                        if st.button(f"🔴 Finalizar Sala", key=f"end_{sala_id}"):
                            sala['activa'] = False
                            st.error("🔴 Sala finalizada. Los estudiantes ya no podrán conectarse.")
                            st.rerun()
                    
                    # Lista de estudiantes en la sala
                    if sala['estudiantes']:
                        st.subheader("🎓 Estudiantes Conectados")
                        
                        for est_id in sala['estudiantes']:
                            if est_id in st.session_state.estudiantes:
                                estudiante = st.session_state.estudiantes[est_id]
                                
                                # Crear tarjeta para cada estudiante
                                with st.container():
                                    col_est1, col_est2, col_est3 = st.columns([1, 2, 1])
                                    
                                    with col_est1:
                                        st.write(f"**{obtener_icono_personaje(estudiante['tipo_personaje'])} {estudiante['nombre']}**")
                                        st.write(f"*{estudiante['institucion']}*")
                                        st.write(f"Edad: {estudiante['edad']}")
                                        st.write(f"Exp: {estudiante['experiencia']}")
                                    
                                    with col_est2:
                                        # Información de ubicación y movimiento
                                        ubicacion_actual = estudiante['ubicacion_actual']
                                        st.write(f"📍 **Ubicación actual:** {ubicacion_actual}")
                                        st.write(f"⏰ **Último movimiento:** {estudiante['ultimo_movimiento']}")
                                        
                                        # Evaluar riesgos actualizados
                                        riesgos_actuales = evaluar_riesgos_automaticos(estudiante, ubicacion_actual)
                                        riesgo_caida = evaluar_riesgo_caida(estudiante, ubicacion_actual)
                                        riesgo_sobrecarga = evaluar_riesgo_sobrecarga(estudiante)
                                        
                                        # Combinar todos los riesgos
                                        todos_riesgos = riesgos_actuales
                                        if riesgo_caida:
                                            todos_riesgos.append(riesgo_caida)
                                        if riesgo_sobrecarga:
                                            todos_riesgos.append(riesgo_sobrecarga)
                                        
                                        # Mostrar riesgos
                                        if todos_riesgos:
                                            st.error(f"🚨 **{len(todos_riesgos)} riesgos detectados**")
                                            for riesgo in todos_riesgos[:4]:  # Mostrar máximo 4 riesgos
                                                st.write(f"• {riesgo}")
                                        else:
                                            st.success("✅ Sin riesgos detectados")
                                    
                                    with col_est3:
                                        # Información de equipamiento
                                        st.write("**EPP:**", ", ".join(estudiante['epp']) if estudiante['epp'] else "Ninguno")
                                        st.write("**Herramientas:**", ", ".join(estudiante['herramientas']) if estudiante['herramientas'] else "Ninguna")
                                        
                                        # Botón para forzar movimiento (solo para testing)
                                        if st.button(f"🚶‍♂️ Mover", key=f"move_{est_id}"):
                                            zonas = ["Zona A - Andamios", "Zona B - Excavación", "Zona C - Estructura", "Zona D - Acabados"]
                                            nueva_zona = random.choice([z for z in zonas if z != estudiante['ubicacion_actual']])
                                            estudiante['ubicacion_actual'] = nueva_zona
                                            estudiante['ultimo_movimiento'] = datetime.now().strftime("%H:%M:%S")
                                            st.success(f"Movido a {nueva_zona}")
                                            st.rerun()
                        
                        # Estadísticas de la sala
                        st.subheader("📈 Estadísticas de la Sala")
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        
                        with col_stat1:
                            estudiantes_con_riesgos = sum(1 for est_id in sala['estudiantes'] 
                                                         if est_id in st.session_state.estudiantes 
                                                         and st.session_state.estudiantes[est_id]['riesgos_detectados'])
                            st.metric("Estudiantes con Riesgos", estudiantes_con_riesgos)
                        
                        with col_stat2:
                            total_movimientos = sum(len(st.session_state.estudiantes[est_id].get('historial_movimientos', [])) 
                                                   for est_id in sala['estudiantes'] 
                                                   if est_id in st.session_state.estudiantes)
                            st.metric("Total Movimientos", total_movimientos)
                        
                        with col_stat3:
                            sin_arnes = sum(1 for est_id in sala['estudiantes'] 
                                           if est_id in st.session_state.estudiantes 
                                           and "Arnés de seguridad" not in st.session_state.estudiantes[est_id]['epp'])
                            st.metric("Sin Arnés", sin_arnes)
                    
                    else:
                        st.info("👥 No hay estudiantes conectados aún. Comparte el código de la sala para que se unan.")


# =============================================
# SECCIÓN: SIMULADOR ORIGINAL - MEJORADA
# =============================================

elif menu == "🎮 Simulador Original":
    st.header("🎮 Simulador de Arnés Inteligente - Modo Individual")
    
    # Configuración inicial
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⚙️ Configuración del Trabajador")
        
        # Información básica
        trabajador_nombre = st.text_input("Nombre del trabajador", "Carlos Rodríguez")
        trabajador_edad = st.slider("Edad", 18, 65, 35)
        trabajador_experiencia = st.selectbox("Experiencia en alturas", 
                                            ["Principiante (<1 año)", "Intermedio (1-3 años)", "Avanzado (>3 años)"])
        
        # Condiciones de salud
        st.subheader("🏥 Condiciones de Salud")
        condiciones_salud = st.multiselect("Selecciona condiciones relevantes:",
                                         ["Vértigo", "Mareos", "Problemas cardíacos", "Diabetes", 
                                          "Problemas de espalda", "Ninguna"])
        
        # Equipamiento
        st.subheader("🛠️ Equipamiento")
        epp_equipado = st.multiselect("EPP utilizado:",
                                    ["Arnés de seguridad", "Casco", "Botas de seguridad", 
                                     "Guantes", "Gafas de protección", "Línea de vida"])
        
    with col2:
        st.subheader("🎯 Estado Actual")
        
        # Botón de inicio de simulación
        if st.button("🎬 Iniciar Simulación", type="primary", use_container_width=True):
            st.session_state.simulation_running = True
            st.session_state.simulation_start_time = datetime.now()
            st.success("Simulación iniciada!")
            
        if st.button("⏹️ Detener Simulación", use_container_width=True):
            st.session_state.simulation_running = False
            st.warning("Simulación detenida")
        
        # Estado de la simulación
        if st.session_state.get('simulation_running', False):
            st.success("🟢 SIMULACIÓN ACTIVA")
            tiempo_transcurrido = datetime.now() - st.session_state.simulation_start_time
            st.metric("Tiempo transcurrido", f"{int(tiempo_transcurrido.total_seconds())} seg")
        else:
            st.info("⏸️ SIMULACIÓN DETENIDA")
        
        # Simulación de métricas en tiempo real
        st.metric("Ritmo cardíaco", f"{random.randint(65, 85)} lpm", delta="Normal")
        st.metric("Oxígeno en sangre", f"{random.randint(95, 99)}%", delta="Óptimo")
        st.metric("Temperatura corporal", f"{random.uniform(36.1, 36.8):.1f}°C", delta="Normal")
        
        # Estado del arnés
        estado_arnes = st.selectbox("Estado del arnés", 
                                  ["Correctamente ajustado", "Ajuste deficiente", "No verificado"])
        
        if estado_arnes != "Correctamente ajustado":
            st.error("⚠️ Verificar ajuste del arnés")
        else:
            st.success("✅ Arnés correctamente ajustado")
    
    # Simulación de escenario
    st.markdown("---")
    st.subheader("🏗️ Simulación de Escenario de Trabajo")
    
    escenario = st.selectbox("Selecciona el escenario de trabajo:",
                           ["Andamios en fachada", "Estructura metálica", "Torre de comunicación", 
                            "Trabajos en cubierta", "Espacios confinados verticales"])
    
    # Visualización del escenario MEJORADA
    col_viz1, col_viz2 = st.columns([2, 1])
    
    with col_viz1:
        # Crear una visualización MEJORADA del escenario
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Dibujar el escenario según la selección con más detalle
        if "Andamios" in escenario:
            # Dibujar andamios más detallados
            for i in range(6):
                ax.add_patch(Rectangle((i*0.8, 0), 0.6, 5, fill=False, edgecolor='#8B4513', linewidth=3))
                # Plataformas
                if i < 5:
                    ax.add_patch(Rectangle((i*0.8 + 0.1, 2), 0.4, 0.1, color='#DEB887'))
                    ax.add_patch(Rectangle((i*0.8 + 0.1, 4), 0.4, 0.1, color='#DEB887'))
            
            # Trabajador en andamios
            ax.plot([2.5], [3.5], 'o', markersize=15, color='red', label='Trabajador')
            ax.text(2.5, 3.8, '👷', fontsize=20, ha='center')
            
            # Línea de vida
            ax.plot([2.5, 2.5], [3.5, 5], 'g--', linewidth=2, alpha=0.7, label='Línea de vida')
            
            ax.set_title("🔨 Trabajo en Andamios - Nivel 4", fontsize=16, fontweight='bold', pad=20)
            ax.text(2.5, -0.5, f"Trabajador: {trabajador_nombre}\nAltura: 12 metros", 
                   ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            
        elif "Estructura" in escenario:
            # Dibujar estructura metálica más detallada
            # Base
            ax.add_patch(Rectangle((1, 0), 3, 0.3, color='#555555'))
            
            # Columnas principales
            ax.add_patch(Rectangle((1.5, 0.3), 0.2, 4, color='#888888'))
            ax.add_patch(Rectangle((3.3, 0.3), 0.2, 4, color='#888888'))
            
            # Vigas
            ax.add_patch(Rectangle((1, 2), 3, 0.15, color='#666666'))
            ax.add_patch(Rectangle((1, 4), 3, 0.15, color='#666666'))
            
            # Trabajador en estructura
            ax.plot([2.0], [3.0], 'o', markersize=15, color='red')
            ax.text(2.0, 3.3, '👷', fontsize=20, ha='center')
            
            # Arnés y línea
            ax.plot([2.0, 2.0], [3.0, 4.2], 'g-', linewidth=2, alpha=0.7)
            ax.plot([2.0], [4.2], 's', markersize=8, color='blue', label='Punto de anclaje')
            
            ax.set_title("🔩 Estructura Metálica - Montaje", fontsize=16, fontweight='bold', pad=20)
            ax.text(2.5, -0.5, f"Trabajador: {trabajador_nombre}\nAltura: 15 metros", 
                   ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            
        elif "Torre" in escenario:
            # Dibujar torre de comunicación más detallada
            # Torre principal
            ax.plot([2.5, 2.5], [0, 4.5], color='#333333', linewidth=8)
            
            # Plataformas de trabajo
            ax.add_patch(Rectangle((1.5, 1.5), 2, 0.1, color='#666666'))
            ax.add_patch(Rectangle((1.5, 3.0), 2, 0.1, color='#666666'))
            
            # Antenas
            ax.plot([2.5], [4.7], '^', markersize=15, color='gray')
            ax.plot([1.8, 3.2], [4.5, 4.5], color='gray', linewidth=3)
            
            # Trabajador en torre
            ax.plot([2.0], [3.2], 'o', markersize=15, color='red')
            ax.text(2.0, 3.5, '👷', fontsize=20, ha='center')
            
            # Sistema anticaídas
            ax.plot([2.0, 2.5], [3.2, 4.5], 'r-', linewidth=2, alpha=0.7, label='Sistema anticaídas')
            ax.plot([2.5], [4.5], 'o', markersize=10, color='orange', label='Anclaje superior')
            
            ax.set_title("📡 Torre de Comunicación - Mantenimiento", fontsize=16, fontweight='bold', pad=20)
            ax.text(2.5, -0.5, f"Trabajador: {trabajador_nombre}\nAltura: 45 metros", 
                   ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        elif "cubierta" in escenario.lower():
            # Dibujar cubierta
            ax.add_patch(Rectangle((0.5, 1), 4, 2, color='#8B4513', alpha=0.7))
            ax.add_patch(Rectangle((0.5, 1), 4, 0.1, color='#A0522D'))  # Borde
            
            # Trabajador en cubierta
            ax.plot([2.5], [2.0], 'o', markersize=15, color='red')
            ax.text(2.5, 2.3, '👷', fontsize=20, ha='center')
            
            # Línea de vida horizontal
            ax.plot([1, 4], [2.8, 2.8], 'g-', linewidth=3, alpha=0.7)
            ax.plot([2.5, 2.5], [2.0, 2.8], 'g--', linewidth=2, alpha=0.7)
            
            ax.set_title("🏠 Trabajos en Cubierta Inclinada", fontsize=16, fontweight='bold', pad=20)
            ax.text(2.5, -0.5, f"Trabajador: {trabajador_nombre}\nInclinación: 30°", 
                   ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        # Configuración común del gráfico
        ax.set_xlim(0, 5)
        ax.set_ylim(-1, 6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Leyenda de seguridad
        ax.text(0.1, 5.5, '🚨 SISTEMA DE SEGURIDAD ACTIVO', 
               fontsize=12, fontweight='bold', color='red',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7))
        
        st.pyplot(fig)
    
    with col_viz2:
        st.subheader("📊 Análisis de Riesgos")
        
        # Evaluar riesgos basados en la configuración
        riesgos = []
        recomendaciones = []
        
        if "Vértigo" in condiciones_salud and "Andamios" in escenario:
            riesgos.append("🦘 Alto riesgo por vértigo en altura")
            recomendaciones.append("• Evaluar aptitud médica para trabajo en altura")
            
        if "Principiante" in trabajador_experiencia:
            riesgos.append("🎓 Experiencia limitada - supervisión requerida")
            recomendaciones.append("• Asignar supervisor experimentado")
            recomendaciones.append("• Realizar entrenamiento adicional")
            
        if "Arnés de seguridad" not in epp_equipado:
            riesgos.append("🪂 CRÍTICO: Arnés de seguridad no equipado")
            recomendaciones.append("• SUSPENDER TRABAJO hasta equipar arnés")
            
        if "Línea de vida" not in epp_equipado and "Andamios" in escenario:
            riesgos.append("🔗 Sistema de anclaje recomendado")
            recomendaciones.append("• Instalar línea de vida continua")
            
        if trabajador_edad > 55:
            riesgos.append("👴 Mayor riesgo de fatiga - pausas frecuentes")
            recomendaciones.append("• Programar pausas cada 45 minutos")
            
        if "Torre" in escenario:
            recomendaciones.extend([
                "• Verificar condiciones climáticas",
                "• Usar equipo anticaídas certificado", 
                "• Comunicación constante con base",
                "• Verificar anclajes estructurales"
            ])
            
        if "Estructura" in escenario:
            recomendaciones.extend([
                "• Inspeccionar puntos de soldadura",
                "• Verificar estabilidad de componentes",
                "• Delimitar área de trabajo"
            ])
        
        # Mostrar riesgos
        if len(riesgos) > 0:
            st.error("🚨 **Riesgos Detectados:**")
            for riesgo in riesgos:
                st.write(f"• {riesgo}")
        else:
            st.success("✅ **Sin riesgos críticos detectados**")
            
        # Mostrar recomendaciones
        st.subheader("💡 Recomendaciones de Seguridad")
        for recomendacion in recomendaciones[:6]:  # Mostrar máximo 6 recomendaciones
            st.write(recomendacion)
    
    # Sistema de alertas y controles
    st.markdown("---")
    st.subheader("🎮 Controles de Simulación")
    
    col_control1, col_control2, col_control3, col_control4 = st.columns(4)
    
    with col_control1:
        if st.button("🔴 Simular Caída", type="secondary", use_container_width=True):
            st.session_state.fall_count += 1
            st.error("""
            🚨 **¡ALERTA DE CAÍDA DETECTADA!**
            
            **Acciones automáticas:**
            • Bloqueo instantáneo del arnés
            • Notificación a supervisores
            • Activación de protocolo de rescate
            • Envío de ubicación GPS
            """)
            
    with col_control2:
        if st.button("🟡 Simular Mal Ajuste", type="secondary", use_container_width=True):
            st.warning("""
            ⚠️ **ARNÉS MAL AJUSTADO**
            
            **Recomendaciones:**
            • Verificar ajuste de piernas
            • Revisar hebilla pectoral
            • Ajustar cintas sobrantes
            """)
            
    with col_control3:
        if st.button("🟢 Condiciones Normales", type="secondary", use_container_width=True):
            st.success("""
            ✅ **CONDICIONES NORMALES**
            
            **Estado del sistema:**
            • Monitoreo activo
            • Comunicación estable
            • Equipamiento correcto
            """)
            
    with col_control4:
        if st.button("📊 Generar Reporte", type="secondary", use_container_width=True):
            st.info("""
            📋 **REPORTE DE SIMULACIÓN**
            
            **Datos recopilados:**
            • Tiempo de simulación: Activo
            • Alertas generadas: Sí
            • Riesgos identificados: {}
            """.format(len(riesgos)))
    
    # Métricas de la simulación
    st.markdown("---")
    st.subheader("📈 Métricas de la Simulación")
    
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        st.metric("Caídas simuladas", st.session_state.fall_count)
        
    with col_metric2:
        st.metric("Riesgos detectados", len(riesgos))
        
    with col_metric3:
        st.metric("Nivel de seguridad", 
                 f"{max(0, 100 - len(riesgos)*15)}%",
                 delta=f"-{len(riesgos)*15}%" if riesgos else "+0%")
        
    with col_metric4:
        if st.session_state.get('simulation_running', False):
            tiempo = datetime.now() - st.session_state.simulation_start_time
            st.metric("Tiempo activo", f"{int(tiempo.total_seconds())}s")
        else:
            st.metric("Tiempo activo", "0s")
# =============================================
# SECCIÓN: INICIO - COMPLETA
# =============================================

else:  # Inicio
    st.header("🏠 Bienvenido al Sistema de Protección Inteligente")
    
    # Tarjetas informativas
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        <div style='padding: 20px; background: #e8f4fd; border-radius: 10px; border-left: 5px solid #2196F3;'>
            <h3 style='color: #1976D2; margin: 0;'>🎮 Simulador Individual</h3>
            <p style='color: #424242;'>Prueba el sistema de detección de riesgos en modo individual con diferentes escenarios y configuraciones.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div style='padding: 20px; background: #f3e5f5; border-radius: 10px; border-left: 5px solid #9C27B0;'>
            <h3 style='color: #7B1FA2; margin: 0;'>👨‍🏫 Modo Multijugador</h3>
            <p style='color: #424242;'>Crea salas de simulación para entrenamiento grupal con monitoreo en tiempo real.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown("""
        <div style='padding: 20px; background: #e8f5e8; border-radius: 10px; border-left: 5px solid #4CAF50;'>
            <h3 style='color: #388E3C; margin: 0;'>📊 Salas Activas</h3>
            <p style='color: #424242;'>Monitorea y gestiona todas las simulaciones activas con análisis detallado.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Estadísticas del sistema
    st.subheader("📈 Estadísticas del Sistema")
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        total_salas = len(st.session_state.salas)
        st.metric("Salas Creadas", total_salas)
    
    with col_stats2:
        total_estudiantes = len(st.session_state.estudiantes)
        st.metric("Estudiantes Registrados", total_estudiantes)
    
    with col_stats3:
        salas_activas = sum(1 for sala in st.session_state.salas.values() if sala.get('activa', False))
        st.metric("Salas Activas", salas_activas)
    
    with col_stats4:
        simulaciones_activas = sum(1 for sala in st.session_state.salas.values() if sala.get('simulacion_iniciada', False))
        st.metric("Simulaciones Activas", simulaciones_activas)
    
    # Información del proyecto
    st.markdown("---")
    st.subheader("🎓 Información del Proyecto de Grado")
    
    col_proj1, col_proj2 = st.columns([2, 1])
    
    with col_proj1:
        st.markdown("""
        ### Objetivos del Sistema
        
        Este sistema de protección inteligente para trabajos en altura tiene como objetivos:
        
        - **Detección temprana** de riesgos y condiciones peligrosas
        - **Simulación realista** de escenarios de trabajo en altura
        - **Entrenamiento interactivo** para trabajadores y estudiantes
        - **Monitoreo en tiempo real** de múltiples usuarios
        - **Análisis predictivo** de comportamientos de riesgo
        
        ### Características Principales
        
        ✅ **Sistema multijugador** para entrenamiento grupal  
        ✅ **Detección automática** de riesgos basada en perfiles  
        ✅ **Simulación de movimientos** y cambios de ubicación  
        ✅ **Alertas inteligentes** personalizadas por perfil  
        ✅ **Análisis en tiempo real** de condiciones de trabajo  
        ✅ **Interfaz intuitiva** para monitores y estudiantes  
        
        ### Tecnologías Utilizadas
        
        - **Streamlit** para la interfaz web interactiva
        - **Python** para la lógica de simulación y análisis
        - **Session State** para gestión de estado multiusuario
        - **Matplotlib** para visualizaciones
        - **Sistema de tiempo real** para simulaciones continuas
        """)
    
    with col_proj2:
        st.markdown("""
        <div style='padding: 20px; background: #fff3e0; border-radius: 10px; border: 2px solid #FF9800;'>
            <h3 style='color: #E65100; text-align: center;'>👩‍🔬 Autora</h3>
            <div style='text-align: center; font-size: 3em;'>💫</div>
            <h2 style='color: #E65100; text-align: center;'>Michell Andrea</h2>
            <h2 style='color: #E65100; text-align: center;'>Rodriguez Rivera</h2>
            <p style='text-align: center; color: #5D4037;'><strong>Ingeniera en Seguridad y Salud en el Trabajo</strong></p>
            <hr>
            <p style='text-align: center; color: #5D4037;'>Sistema desarrollado como Proyecto de Grado para la obtención del título de Ingeniería en Seguridad y Salud en el Trabajo</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================
# PIE DE PÁGINA
# =============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>🦺 Sistema de Protección Inteligente para Trabajos en Altura</strong></p>
    <p>Desarrollado por Michell Andrea Rodriguez Rivera | Proyecto de Grado - Ingeniería en Seguridad y Salud en el Trabajo</p>
    <p>© 2024 - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
