import streamlit as st
import json
import random
import time

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Examen Auxiliar de Farmacia",
    page_icon="https://github.com/Sebasm2kuy/examenM2/blob/main/Copilot_20250704_171338.png?raw=true",
    layout="centered"
)

# --- 2. METADATOS PARA REDES SOCIALES ---
st.markdown(
    """
    <meta property="og:title" content="Examen Auxiliar de Farmacia">
    <meta property="og:description" content="Practica para el examen con preguntas aleatorias. ¡Cada intento es un nuevo desafío! Completamente gratis y sin límites.">
    <meta property="og:image" content="https://github.com/Sebasm2kuy/examenM2/blob/main/Copilot_20250704_171338.png?raw=true">
    <meta property="og:url" content="https://examenahhm2.streamlit.app/">
    <meta name="twitter:card" content="summary_large_image">
    """,
    unsafe_allow_html=True,
)

# --- 3. FUNCIÓN PARA CARGAR LAS PREGUNTAS ---
@st.cache_data
def cargar_preguntas():
    try:
        with open('preguntas_modulo2.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error crítico: No se encontró 'preguntas_modulo2.json'. Asegúrate de que el archivo está en tu repositorio de GitHub.")
        return None
    except json.JSONDecodeError:
        st.error("Error crítico: 'preguntas_modulo2.json' tiene un formato incorrecto. Por favor, revísalo con un validador de JSON.")
        return None

# --- 4. INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
if 'examen_en_curso' not in st.session_state:
    st.session_state.examen_en_curso = False
    st.session_state.examen_finalizado = False
    st.session_state.preguntas_examen = []
    st.session_state.respuestas = {}
    st.session_state.current_question_index = 0
    st.session_state.start_time = 0
    st.session_state.duration_seconds = 0

# --- LÓGICA PRINCIPAL DE LA APP ---

st.title("📝 Examen Módulo 2: Auxiliar de Farmacia Hospitalaria")

todas_las_preguntas = cargar_preguntas()
if not todas_las_preguntas:
    st.stop()

# --- VISTA DE INICIO ---
if not st.session_state.examen_en_curso and not st.session_state.examen_finalizado:
    st.write("""
    **Instrucciones del examen:**
    - **Cantidad:** 30 preguntas seleccionadas al azar.
    - **Navegación:** Podrás avanzar, retroceder y cambiar tus respuestas.
    - **Puntuación:** +1 Correcta, -0.5 Incorrecta, 0 Omitida.
    - **Tiempo:** Elige un límite de tiempo. Si se acaba, el examen se entregará automáticamente.
    """)
    
    time_option_minutes = st.radio(
        "**Selecciona la duración del examen:**",
        options=[15, 30, 60, "Sin límite"],
        horizontal=True,
        format_func=lambda option: f"{option} min." if isinstance(option, int) else option
    )

    if st.button("🚀 Iniciar Nuevo Examen", type="primary", use_container_width=True):
        if len(todas_las_preguntas) < 30:
            st.warning("Advertencia: El banco de preguntas tiene menos de 30.")
        else:
            st.session_state.preguntas_examen = random.sample(todas_las_preguntas, 30)
            st.session_state.respuestas = {i: "Pasar" for i in range(30)}
            st.session_state.current_question_index = 0
            st.session_state.examen_en_curso = True
            st.session_state.examen_finalizado = False
            
            st.session_state.start_time = time.time()
            if isinstance(time_option_minutes, int):
                st.session_state.duration_seconds = time_option_minutes * 60
            else:
                st.session_state.duration_seconds = 0
            st.rerun()

# --- VISTA DURANTE EL EXAMEN ---
elif st.session_state.examen_en_curso and not st.session_state.examen_finalizado:
    
    # ### <<< INICIO DE LA CORRECCIÓN >>> ###
    
    # Primero, se calcula el tiempo restante.
    remaining_time = st.session_state.duration_seconds
    if st.session_state.duration_seconds > 0:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = st.session_state.duration_seconds - elapsed_time
        
        # Si el tiempo se acabó, se termina el examen y se sale de esta sección.
        if remaining_time <= 0:
            st.session_state.examen_en_curso = False
            st.session_state.examen_finalizado = True
            st.warning("⏰ ¡Se acabó el tiempo! El examen se ha entregado automáticamente.")
            # Pequeña pausa para que el usuario vea el mensaje antes de recargar
            time.sleep(2)
            st.rerun()

    # Segundo, se muestra la pregunta y los controles de navegación.
    # Esta parte ahora SIEMPRE se ejecuta, sin importar si hay tiempo o no.
    
    idx = st.session_state.current_question_index
    total_preguntas = len(st.session_state.preguntas_examen)
    
    # Mostrar el reloj (si está activo)
    if st.session_state.duration_seconds > 0:
        minutes, seconds = divmod(int(remaining_time), 60)
        st.info(f"**Tiempo restante: {minutes:02d}:{seconds:02d}**")
        
    st.progress((idx + 1) / total_preguntas, text=f"Pregunta {idx + 1} de {total_preguntas}")
    
    q = st.session_state.preguntas_examen[idx]
    
    st.subheader(f"Pregunta {idx + 1}")
    st.markdown(f"### {q['pregunta']}")
    
    opciones_dict = q['opciones']
    opciones_display = [f"**{k}:** {v}" for k, v in opciones_dict.items()]
    opciones_keys = list(opciones_dict.keys())
    
    opciones_display.insert(0, "⏩ Pasar (Omitir pregunta)")
    opciones_keys.insert(0, "Pasar")
    
    previous_answer = st.session_state.respuestas.get(idx, "Pasar")
    current_selection_index = opciones_keys.index(previous_answer) if previous_answer in opciones_keys else 0

    respuesta = st.radio(
        "Selecciona tu respuesta:",
        options=opciones_display,
        index=current_selection_index,
        label_visibility="collapsed"
    )
    
    selected_key_index = opciones_display.index(respuesta)
    st.session_state.respuestas[idx] = opciones_keys[selected_key_index]
    
    st.write("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Anterior", use_container_width=True, disabled=(idx == 0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    
    with col3:
        if st.button("Siguiente ➡️", use_container_width=True, disabled=(idx == total_preguntas - 1)):
            st.session_state.current_question_index += 1
            st.rerun()

    st.write("")
    if st.button("🚨 Entregar Examen y Ver Resultados", type="primary", use_container_width=True):
        st.session_state.examen_en_curso = False
        st.session_state.examen_finalizado = True
        st.rerun()

    # Tercero, y solo si hay un temporizador activo, se fuerza la recarga para actualizar el reloj.
    if st.session_state.duration_seconds > 0:
        time.sleep(1)
        st.rerun()

    # ### <<< FIN DE LA CORRECCIÓN >>> ###


# --- VISTA DE RESULTADOS ---
elif st.session_state.examen_finalizado:
    st.header("🏁 Resultados del Examen")
    
    puntuacion = 0.0
    correctas = 0
    incorrectas = 0
    pasadas = 0

    for i, q in enumerate(st.session_state.preguntas_examen):
        respuesta_usr = st.session_state.respuestas.get(i, "Pasar")
        if respuesta_usr == q['respuesta_correcta']:
            puntuacion += 1
            correctas += 1
        elif respuesta_usr == "Pasar":
            pasadas += 1
        else:
            puntuacion -= 0.5
            incorrectas += 1

    st.markdown(f"### Puntuación Final: **{puntuacion} puntos**")
    st.markdown(f"- ✅ **Respuestas Correctas:** `{correctas}`")
    st.markdown(f"- ❌ **Respuestas Incorrectas:** `{incorrectas}`")
    st.markdown(f"- ⏩ **Preguntas Omitidas:** `{pasadas}`")

    with st.expander("🔍 Ver corrección detallada"):
        for i, q in enumerate(st.session_state.preguntas_examen):
            st.markdown("---")
            st.markdown(f"**Pregunta {i+1}:** {q['pregunta']}")
            
            resp_usr = st.session_state.respuestas.get(i, "Pasar")
            letra_ok = q['respuesta_correcta']
            texto_ok = q['opciones'][letra_ok]

            if resp_usr == letra_ok:
                st.success(f"✔️ Tu respuesta fue '{resp_usr}: {q['opciones'][resp_usr]}'. ¡Correcto!")
            elif resp_usr == "Pasar":
                st.info(f"⏩ Omitida. La respuesta correcta era: '{letra_ok}: {texto_ok}'.")
            else:
                texto_usr = q['opciones'].get(resp_usr, "INVÁLIDA")
                st.error(f"❌ Tu respuesta fue '{resp_usr}: {texto_usr}'.")
                st.info(f"✔️ La respuesta correcta era '{letra_ok}: {texto_ok}'.")
    
    st.write("---")
    if st.button("🔄 Iniciar Otro Examen", type="primary", use_container_width=True):
        st.session_state.examen_en_curso = False
        st.session_state.examen_finalizado = False
        st.session_state.preguntas_examen = []
        st.session_state.respuestas = {}
        st.session_state.current_question_index = 0
        st.rerun()
