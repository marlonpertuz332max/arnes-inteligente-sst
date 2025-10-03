import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.patches import Circle, Rectangle, Arc

# Configuración de la página
st.set_page_config(page_title="Arnés Inteligente SST", page_icon="🦺", layout="wide")

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

# El resto del código se mantiene igual...
# COLUMNA IZQUIERDA: Información educativa para SST
with st.sidebar:
    st.header("📚 Fundamentos del Proyecto")
    
    st.subheader("🎯 Objetivo del Sistema")
    st.info("""
    Proteger a trabajadores en altura mediante:
    - **Detección temprana** de situaciones de riesgo
    - **Alertas inmediatas** para prevención
    - **Monitoreo en tiempo real** de parámetros críticos
    """)
    
    st.subheader("⚡ Parámetros Monitoreados")
    
    with st.expander("📊 ACELERACIÓN (Movimiento)"):
        st.write("""
        **Valores de referencia:**
        - 🟢 **9.8 m/s²**: Gravedad normal (estático)
        - 🟡 **5-9 m/s²**: Movimientos bruscos
        - 🔴 **< 5 m/s²**: ¡POSIBLE CAÍDA LIBRE!
        - 🔴 **> 13 m/s²**: Fuerzas peligrosas
        """)
    
    with st.expander("📐 ÁNGULO (Postura)"):
        st.write("""
        **Límites de seguridad:**
        - 🟢 **0°-30°**: Postura segura
        - 🟡 **30°-60°**: Precaución requerida
        - 🔴 **> 60°**: ¡PELIGRO DE VUELCO!
        """)

# FUNCIÓN PARA DIBUJAR AL TRABAJADOR (se mantiene igual)
def dibujar_trabajador(angulo, estado, ax):
    # Limpiar el axes
    ax.clear()
    
    # Configurar el área de dibujo
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1, 3)
    ax.set_aspect('equal')
    
    # Color según el estado
    if estado == "seguro":
        color_cuerpo = 'green'
        color_arnes = 'darkgreen'
    elif estado == "precaucion":
        color_cuerpo = 'orange'
        color_arnes = 'darkorange'
    else:  # peligro
        color_cuerpo = 'red'
        color_arnes = 'darkred'
    
    # Convertir ángulo a radianes para la rotación
    angulo_rad = np.radians(angulo)
    
    # Dibujar cuerpo (rectángulo rotado)
    cuerpo = Rectangle((-0.3, -0.5), 0.6, 1.5, color=color_cuerpo, alpha=0.7)
    
    # Aplicar rotación al cuerpo
    transform = plt.matplotlib.transforms.Affine2D().rotate_around(0, 0, angulo_rad) + ax.transData
    cuerpo.set_transform(transform)
    ax.add_patch(cuerpo)
    
    # Dibujar cabeza (círculo)
    cabeza = Circle((0, 1.2), 0.2, color=color_cuerpo, alpha=0.7)
    cabeza.set_transform(transform)
    ax.add_patch(cabeza)
    
    # Dibujar arnés (en forma de H)
    # Tirantes verticales
    tirante_izq = Rectangle((-0.25, 0.2), 0.1, 0.8, color=color_arnes, alpha=0.9)
    tirante_der = Rectangle((0.15, 0.2), 0.1, 0.8, color=color_arnes, alpha=0.9)
    # Tirante horizontal
    tirante_horizontal = Rectangle((-0.25, 0.8), 0.5, 0.1, color=color_arnes, alpha=0.9)
    
    for tirante in [tirante_izq, tirante_der, tirante_horizontal]:
        tirante.set_transform(transform)
        ax.add_patch(tirante)
    
    # Dibujar línea de seguridad (cuerda)
    if estado == "peligro":
        # Línea rota en caso de peligro
        ax.plot([0, 0.5], [2.5, 2.0], 'r--', linewidth=3, alpha=0.7)
        ax.plot([0.5, 1.0], [2.0, 1.5], 'r--', linewidth=3, alpha=0.7)
    else:
        # Línea sólida en caso seguro
        ax.plot([0, 0], [2.5, 1.5], 'gray', linewidth=3, alpha=0.7)
    
    # Añadir texto del estado
    ax.text(0, -0.8, f'Ángulo: {angulo}°', ha='center', fontsize=12, fontweight='bold',
            color=color_cuerpo, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Quitar ejes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Título del gráfico
    ax.set_title('👷 SIMULACIÓN DEL TRABAJADOR', fontsize=14, fontweight='bold', pad=20)

# CONTROLES PRINCIPALES
st.header("🎮 Simulador de Situaciones de Riesgo")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    modo = st.selectbox(
        "**Selecciona el escenario a simular:**",
        [
            "TRABAJO NORMAL - Situación segura",
            "CAÍDA LIBRE - Emergencia máxima", 
            "POSTURA PELIGROSA - Riesgo de vuelco",
            "SOBRECARGA - Fuerzas excesivas"
        ],
        help="Elige diferentes situaciones que pueden ocurrir en trabajos en altura"
    )

with col2:
    duracion = st.slider("**Duración (segundos):**", 5, 30, 15)

with col3:
    st.write("**Control de simulación:**")
    start_col, stop_col = st.columns(2)
    with start_col:
        start = st.button("▶️ INICIAR", type="primary", use_container_width=True)
    with stop_col:
        stop = st.button("⏹️ DETENER", use_container_width=True)

# PANEL DE ESTADO PRINCIPAL
st.header("📊 Panel de Monitoreo en Tiempo Real")

# Crear columnas para los datos
col_status, col_visual, col_metrics = st.columns([2, 2, 1])

with col_status:
    status_display = st.empty()
    situation_explanation = st.empty()

with col_visual:
    st.subheader("👷 Simulación Visual")
    worker_placeholder = st.empty()

with col_metrics:
    st.subheader("📈 Métricas")
    accel_display = st.empty()
    angle_display = st.empty()
    incidents_display = st.metric(
        "🚨 Incidentes Detectados", 
        st.session_state.get('fall_count', 0)
    )

# Área de gráficos
st.subheader("📈 Gráficos de Monitoreo Técnico")
graph_placeholder = st.empty()
progress_bar = st.empty()

# Inicializar variables
if "fall_count" not in st.session_state:
    st.session_state.fall_count = 0
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

# Lógica de simulación
if stop:
    st.session_state.simulation_running = False

if start and not st.session_state.simulation_running:
    st.session_state.simulation_running = True
    
    fs = 10  # Muestras por segundo
    t_vals, accel_vals, angle_vals = [], [], []
    
    progress_bar = st.progress(0)
    
    for i in range(duracion * fs):
        if not st.session_state.simulation_running:
            break
            
        t = i / fs
        progress = (i + 1) / (duracion * fs)
        progress_bar.progress(progress)
        
        # --- GENERAR DATOS SEGÚN ESCENARIO ---
        if "TRABAJO NORMAL" in modo:
            accel = 9.8 + 0.2 * np.random.randn()
            angle = 10 + np.sin(0.5 * t) * 5
            status = "🟢 SITUACIÓN NORMAL"
            status_color = "success"
            explanation = "El trabajador realiza sus labores de forma segura"
            estado_visual = "seguro"
            
        elif "CAÍDA LIBRE" in modo:
            if t < duracion / 2:
                accel = 9.8 + 0.2 * np.random.randn()
                angle = 15 + 5 * np.random.randn()
                status = "🟢 SITUACIÓN NORMAL"
                status_color = "success"
                explanation = "Trabajador realizando labores normales"
                estado_visual = "seguro"
            else:
                accel = 2 + 0.3 * np.random.randn()
                angle = 70 + 10 * np.random.randn()
                status = "🔴 ¡CAÍDA DETECTADA!"
                status_color = "error"
                explanation = "¡EMERGENCIA! Aceleración por debajo de 5 m/s² indica caída libre"
                estado_visual = "peligro"
                
        elif "POSTURA PELIGROSA" in modo:
            accel = 9.8 + 0.2 * np.random.randn()
            if t < duracion / 2:
                angle = 15 + 5 * np.random.randn()
                status = "🟢 SITUACIÓN NORMAL"
                status_color = "success"
                explanation = "Postura dentro de límites seguros"
                estado_visual = "seguro"
            else:
                angle = 75 + 5 * np.random.randn()
                status = "🟡 POSTURA PELIGROSA"
                status_color = "warning"
                explanation = "¡Ángulo superior a 60°! Riesgo de vuelco"
                estado_visual = "peligro"
                
        else:  # SOBRECARGA
            if t < duracion / 2:
                accel = 9.8 + 0.2 * np.random.randn()
                status = "🟢 SITUACIÓN NORMAL"
                status_color = "success"
                explanation = "Fuerzas dentro de parámetros normales"
                estado_visual = "seguro"
            else:
                accel = 14 + 0.5 * np.random.randn()
                status = "🟡 SOBRECARGA DETECTADA"
                status_color = "warning"
                explanation = "¡Fuerzas excesivas! Puede dañar el arnés"
                estado_visual = "precaucion"
            angle = 20 + np.sin(0.5 * t) * 5
        
        # --- DETECCIÓN DE INCIDENTES ---
        incidente = (accel < 5) or (angle > 60) or (accel > 13)
        
        if incidente:
            st.session_state.fall_count += 1
            
            # Mostrar protocolo de emergencia
            st.error(f"""
            🚨 **PROTOCOLO DE EMERGENCIA ACTIVADO**
            
            **Situación:** {modo.split(' - ')[0]}
            **Tiempo del incidente:** {t:.1f} segundos
            **Acciones automáticas:**
            • 🔊 Alarma sonora activada
            • 📱 Alertas enviadas a supervisores  
            • 📍 GPS compartido con rescate
            • 🏥 Servicios médicos notificados
            """)
            
            # Efectos visuales para emergencia
            st.balloons()
            
        else:
            st.success("""
            ✅ **SISTEMA EN ESTADO NORMAL**
            
            **Monitoreo activo:**
            • 📊 Parámetros dentro de límites
            • 👷 Trabajador en situación segura
            • 🔄 Monitoreo continuo
            """)
        
        # Actualizar displays
        if status_color == "success":
            status_display.success(f"**{status}**")
        elif status_color == "warning":
            status_display.warning(f"**{status}**")
        else:
            status_display.error(f"**{status}**")
            
        situation_explanation.info(f"**Explicación:** {explanation}")
        
        accel_display.metric("Aceleración", f"{accel:.1f} m/s²")
        angle_display.metric("Ángulo", f"{angle:.1f}°")
        
        # --- DIBUJAR TRABAJADOR ---
        fig_worker, ax_worker = plt.subplots(figsize=(4, 6))
        dibujar_trabajador(int(angle), estado_visual, ax_worker)
        worker_placeholder.pyplot(fig_worker)
        plt.close(fig_worker)
        
        # Guardar datos para gráfico técnico
        t_vals.append(t)
        accel_vals.append(accel)
        angle_vals.append(angle)
        
        # --- CREAR GRÁFICOS TÉCNICOS ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        # Gráfico de aceleración
        ax1.plot(t_vals, accel_vals, 'b-', linewidth=2, label='ACELERACIÓN')
        ax1.axhline(y=9.8, color='green', linestyle='-', alpha=0.6, label='GRAVEDAD NORMAL')
        ax1.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='LÍMITE CAÍDA')
        ax1.axhline(y=13, color='orange', linestyle='--', alpha=0.7, label='LÍMITE SOBRECARGA')
        ax1.set_ylabel('Aceleración (m/s²)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico de ángulo
        ax2.plot(t_vals, angle_vals, 'g-', linewidth=2, label='ÁNGULO')
        ax2.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='LÍMITE PELIGROSO')
        ax2.set_ylabel('Ángulo (°)')
        ax2.set_xlabel('Tiempo (segundos)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        graph_placeholder.pyplot(fig)
        plt.close(fig)
        
        time.sleep(1/fs)
    
    # Finalizar simulación
    progress_bar.empty()
    st.session_state.simulation_running = False
    st.success("🎉 **Simulación completada exitosamente**")

# INFORMACIÓN EDUCATIVA
st.markdown("---")
st.header("🎓 Material de Apoyo para la Exposición")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.subheader("💡 Puntos Clave para la Exposición")
    st.info("""
    **Visualización del sistema:**
    - 👷 **Verde**: Situación normal y segura
    - 🟠 **Naranja**: Precaución - parámetros cercanos a límites
    - 🔴 **Rojo**: Peligro - activación de protocolos de emergencia
    
    **La simulación muestra:**
    - Postura real del trabajador
    - Estado del arnés de seguridad
    - Línea de vida y anclajes
    """)

# CONCLUSIÓN
st.success("""
**🎯 Mensaje Final:**
*"Combinamos tecnología moderna con principios de SST para crear protección visual e intuitiva que todos pueden entender."*
""")

# Créditos finales
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
    <h3 style='color: #6c757d;'>Desarrollado para el Proyecto de Grado de</h3>
    <h2 style='color: #495057; font-weight: bold;'>Ing. Michell Andrea Rodriguez Rivera</h2>
    <p style='color: #6c757d;'>Ingeniera en Seguridad y Salud en el Trabajo</p>
</div>
""", unsafe_allow_html=True)
