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

# =============================================
# FUNCIONES DEL SISTEMA MULTIJUGADOR
# =============================================

def generar_codigo_sala():
    return f"SIM-{random.randint(1000, 9999)}"

def obtener_icono_personaje(tipo_personaje):
    iconos = {
        "Hombre musculoso": "💪",
        "Mujer atlética": "🏃‍♀", 
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
        riesgos_detectados.append("❤ Monitoreo cardíaco requerido")
    
    if "Diabetes" in condiciones_salud:
        riesgos_detectados.append("🩸 Riesgo hipoglucémico - monitoreo continuo")
    
    tipo_personaje = estudiante.get('tipo_personaje', '')
    
    if tipo_personaje == "Persona mayor":
        riesgos_detectados.append("👴 Mayor riesgo de fatiga y caídas")
    
    if tipo_personaje == "Mujer embarazada":
        riesgos_detectados.append("🤰 Riesgo elevado - evitar esfuerzos intensos")
        if "Excavación" in ubicacion:
            riesgos_detectados.append("⚠ Exposición a vibraciones peligrosa")
    
    if tipo_personaje == "Persona con discapacidad motriz":
        riesgos_detectados.append("♿ Movilidad reducida - rutas de evacuación críticas")
    
    if tipo_personaje == "Persona con sobrepeso":
        riesgos_detectados.append("⚖ Mayor carga articular - límite de peso reducido")
    
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
        riesgos_detectados.append("⛰ Riesgo de derrumbe o atrapamiento")
    
    if "Estructura" in ubicacion:
        riesgos_detectados.append("🏗 Caída de objetos - área delimitada")
    
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
        return "⚖ ALERTA: Posible sobrecarga física"
    elif puntaje >= 3:
        return "⚖ ADVERTENCIA: Carga física elevada"
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
        st.subheader("👨‍🏫 Crear Nueva Sala de Simulación")
        
        with st.form("registro_monitor"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_monitor = st.text_input("Nombre del monitor *", placeholder="Ing. Carlos Rodríguez")
                email_monitor = st.text_input("Email *", placeholder="carlos@empresa.com")
                especialidad = st.selectbox("Especialidad *", 
                                          ["Seguridad en Alturas", "Espacios Confinados", "Electricidad", 
                                           "Manejo de Maquinaria", "Construcción General"])
            
            with col2:
                empresa = st.text_input("Empresa/Institución *", placeholder="Constructora Segura S.A.")
                duracion_simulacion = st.number_input("Duración estimada (minutos) *", min_value=5, max_value=120, value=30)
                max_estudiantes = st.number_input("Máximo de estudiantes *", min_value=1, max_value=20, value=10)
            
            st.subheader("🎯 Configuración del Escenario")
            
            col3, col4 = st.columns(2)
            
            with col3:
                tipo_escenario = st.selectbox("Tipo de escenario *",
                                            ["Edificación en construcción", "Estructura metálica", 
                                             "Torre de comunicación", "Planta industrial", "Puente en construcción"])
                
                nivel_dificultad = st.select_slider("Nivel de dificultad *",
                                                  ["Básico", "Intermedio", "Avanzado", "Experto"])
            
            with col4:
                riesgos_activados = st.multiselect("Riesgos a simular *",
                                                 ["Caídas de altura", "Electrocución", "Golpes por objetos",
                                                  "Atrapamientos", "Quemaduras", "Exposición a químicos",
                                                  "Sobreesfuerzos", "Ruido excesivo"])
                
                condiciones_climaticas = st.selectbox("Condiciones climáticas",
                                                    ["Soleado", "Nublado", "Lluvia ligera", "Lluvia intensa", "Viento fuerte"])
            
            descripcion_escenario = st.text_area("Descripción del escenario *",
                                               placeholder="Describa el contexto de trabajo y objetivos de la simulación...")
            
            submitted = st.form_submit_button("🎬 Crear Sala de Simulación", type="primary")
            
            if submitted:
                if nombre_monitor and email_monitor and empresa:
                    sala_id = str(uuid.uuid4())[:8]
                    codigo_sala = generar_codigo_sala()
                    
                    sala = {
                        'sala_id': sala_id,
                        'codigo': codigo_sala,
                        'monitor_nombre': nombre_monitor,
                        'monitor_email': email_monitor,
                        'empresa': empresa,
                        'especialidad': especialidad,
                        'duracion': duracion_simulacion,
                        'max_estudiantes': max_estudiantes,
                        'tipo_escenario': tipo_escenario,
                        'nivel_dificultad': nivel_dificultad,
                        'riesgos_activados': riesgos_activados,
                        'condiciones_climaticas': condiciones_climaticas,
                        'descripcion_escenario': descripcion_escenario,
                        'estudiantes': [],
                        'activa': True,
                        'simulacion_iniciada': False,
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.salas[sala_id] = sala
                    
                    st.success(f"✅ Sala creada exitosamente!")
                    st.balloons()
                    
                    st.markdown("---")
                    st.subheader("📋 Información de la Sala Creada")
                    
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.metric("Código de Sala", codigo_sala)
                        st.metric("Monitor", nombre_monitor)
                        st.metric("Escenario", tipo_escenario)
                        
                    with col_info2:
                        st.metric("Dificultad", nivel_dificultad)
                        st.metric("Duración", f"{duracion_simulacion} min")
                        st.metric("Estudiantes", f"0/{max_estudiantes}")
                    
                    st.info("🎓 *Comparte este código con tus estudiantes para que se unan:*")
                    st.code(codigo_sala, language="")
    
    elif submenu == "🎓 Unirse como Estudiante":
        st.subheader("🎓 Unirse a Sala de Simulación")
        
        codigo_sala = st.text_input("Ingresa el código de la sala:", placeholder="SIM-1234").upper()
        
        if codigo_sala:
            sala_encontrada = None
            for sala in st.session_state.salas.values():
                if sala['codigo'] == codigo_sala:
                    sala_encontrada = sala
                    break
            
            if sala_encontrada:
                if len(sala_encontrada['estudiantes']) >= sala_encontrada['max_estudiantes']:
                    st.error("❌ La sala está llena. No se pueden unir más estudiantes.")
                else:
                    st.success(f"✅ Sala encontrada: {sala_encontrada['tipo_escenario']}")
                    
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
                                    st.warning("⚠ **Riesgos detectados inicialmente:**")
                                    for riesgo in riesgos_iniciales:
                                        st.write(f"- {riesgo}")
                                
                            else:
                                st.error("❌ Por favor completa todos los campos obligatorios (*)")
            
            else:
                st.error("❌ No se encontró ninguna sala con ese código")

# =============================================
# SECCIÓN: SALAS ACTIVAS (PARA MONITORES)
# =============================================

elif menu == "📊 Salas Activas":
    st.header("📊 Salas de Simulación Activas")
    
    if not st.session_state.salas:
        st.info("📝 No hay salas activas. Crea una sala en 'Modo Multijugador'.")
    else:
        for sala_id, sala in st.session_state.salas.items():
            if sala['activa']:
                with st.expander(f"🏠 {sala['codigo']} - {sala['tipo_escenario']} ({len(sala['estudiantes'])}/{sala['max_estudiantes']} estudiantes)", expanded=True):
                    
                    col_sala1, col_sala2, col_sala3 = st.columns(3)
                    
                    with col_sala1:
                        st.metric("Monitor", sala['monitor_nombre'])
                        st.metric("Dificultad", sala['nivel_dificultad'])
                        st.metric("Duración", f"{sala['duracion']} min")
                    
                    with col_sala2:
                        st.metric("Estudiantes", f"{len(sala['estudiantes'])}/{sala['max_estudiantes']}")
                        st.metric("Escenario", sala['tipo_escenario'])
                        st.metric("Clima", sala['condiciones_climaticas'])
                    
                    with col_sala3:
                        st.metric("Riesgos", len(sala['riesgos_activados']))
                        st.metric("Estado", "🟢 Activa" if sala['activa'] else "🔴 Inactiva")
                        st.metric("Creada", sala['fecha_creacion'].split()[0])
                    
                    # Botones de control para el monitor
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button(f"🎬 Iniciar Simulación", key=f"start_{sala_id}"):
                            sala['simulacion_iniciada'] = True
                            st.success("✅ Simulación iniciada!")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button(f"⏸ Pausar Simulación", key=f"pause_{sala_id}"):
                            sala['simulacion_iniciada'] = False
                            st.warning("⏸ Simulación pausada")
                            st.rerun()
                    
                    with col_btn3:
                        if st.button(f"🔴 Finalizar Sala", key=f"end_{sala_id}"):
                            sala['activa'] = False
                            st.error("🔴 Sala finalizada")
                            st.rerun()
                    
                    # Lista de estudiantes en la sala
                    if sala['estudiantes']:
                        st.subheader("🎓 Estudiantes Conectados")
                        
                        for est_id in sala['estudiantes']:
                            estudiante = st.session_state.estudiantes[est_id]
                            
                            col_est1, col_est2, col_est3 = st.columns([1, 2, 1])
                            
                            with col_est1:
                                st.write(f"**{obtener_icono_personaje(estudiante['tipo_personaje'])} {estudiante['nombre']}**")
                                st.write(f"*{estudiante['institucion']}*")
                            
                            with col_est2:
                                st.write(f"📍 **Ubicación:** {estudiante['ubicacion_actual']}")
                                st.write(f"⏰ **Último movimiento:** {estudiante['ultimo_movimiento']}")
                                
                                if estudiante['riesgos_detectados']:
                                    st.error(f"🚨 **{len(estudiante['riesgos_detectados'])} riesgos detectados**")
                                    for riesgo in estudiante['riesgos_detectados'][:3]:
                                        st.write(f"• {riesgo}")
                                else:
                                    st.success("✅ Sin riesgos detectados")
                            
                            with col_est3:
                                # Botón para ver detalles del estudiante
                                if st.button(f"👀 Ver Detalles", key=f"view_{est_id}"):
                                    st.session_state.estudiante_detalle = est_id
                    
                    else:
                        st.info("👥 No hay estudiantes conectados aún.")

# =============================================
# SECCIONES ORIGINALES (MANTENER TUS OTRAS PESTAÑAS)
# =============================================

elif menu == "🏠 Inicio":
    st.header("🏠 Página de Inicio")
    st.markdown("""
    ## Bienvenida al Sistema de Protección Inteligente
    
    Este sistema permite simular entornos laborales en construcción con detección automática de riesgos.
    
    ### Características principales:
    - 🎮 **Simulación multijugador** en tiempo real
    - 🚨 **Detección automática** de riesgos laborales  
    - 👨‍🏫 **Modo monitor** para supervisar múltiples estudiantes
    - 📊 **Dashboard en vivo** de movimientos y alertas
    - 🦺 **Sistema de EPP** inteligente
    
    ### Cómo usar:
    1. **Como Monitor**: Crea una sala y comparte el código
    2. **Como Estudiante**: Únete con el código proporcionado
    3. **Monitoreo**: Visualiza riesgos en tiempo real en 'Salas Activas'
    """)

elif menu == "🎮 Simulador Original":
    st.header("🎮 Simulador Original de Arnés Inteligente")
    st.info("Esta es la versión original del simulador individual")
    
    # Aquí puedes mantener tu simulador original existente
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Iniciar Simulación Individual"):
            st.session_state.simulation_running = True
            st.success("Simulación individual iniciada")
    
    with col2:
        if st.button("Detener Simulación"):
            st.session_state.simulation_running = False
            st.warning("Simulación detenida")

# =============================================
# SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA
# =============================================

# Actualizar automáticamente cada 10 segundos si hay salas activas
salas_activas = any(sala.get('simulacion_iniciada', False) for sala in st.session_state.salas.values())
if salas_activas:
    time.sleep(10)
    st.rerun()
