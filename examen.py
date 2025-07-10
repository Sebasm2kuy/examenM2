import streamlit as st
import json
import random
import time
import math

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
        st.error("Error crítico: No se encontró 'preguntas_modulo2.json'.")
        return None
    except json.JSONDecodeError:
        st.error("Error crítico: 'preguntas_modulo2.json' tiene un formato incorrecto.")
        return None

# --- FUNCIÓN PARA CONTADOR SIMULADO ---
def get_fake_online_users():
    base_users = 5
    sin_variation = math.sin(time.time() * (2 * math.pi / 86400)) * 3 
    random_noise = random.randint(-2, 2)
    online_users = int(base_users + sin_variation + random_noise)
    return max(online_users, 3)

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

todas_las_preguntas = cargar_preguntas()
if not todas_las_preguntas:
    st.stop()

# --- VISTA DE INICIO ---
if not st.session_state.examen_en_curso and not st.session_state.examen_finalizado:
    
    st.markdown("<h2 style='text-align: center; margin-bottom: -15px;'>📝 Examen Módulo 2</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Auxiliar de Farmacia Hospitalaria</p>", unsafe_allow_html=True)
    
    online_users = get_fake_online_users()
    st.markdown(f"<p style='text-align: center; color: #28a745; margin-top: -10px;'>● {online_users} estudiantes online</p>", unsafe_allow_html=True)
    st.write("---")

    with st.expander("📖 Ver Instrucciones del Examen"):
        st.markdown("""
        - **Cantidad:** 30 preguntas seleccionadas al azar.
        - **Navegación:** Podrás avanzar, retroceder y cambiar tus respuestas.
        - **Puntuación:** +1 Correcta, -0.5 Incorrecta, 0 Omitida.
        - **Tiempo:** Elige un límite de tiempo. Si se acaba, el examen se entregará automáticamente.
        """)
    
    time_option_minutes = st.radio(
        "**Duración:**",
        options=[15, 30, 60, "Sin límite"],
        horizontal=True,
        format_func=lambda option: f"{option} min." if isinstance(option, int) else option
    )

    if st.button("🚀 Iniciar Nuevo Examen", type="primary", use_container_width=True):
        if len(todas_las_preguntas) < 30:
            st.warning("Advertencia: El banco de preguntas tiene menos de 30.")
        else:
            # ### <<< INICIO DE LA SOLUCIÓN DEL EASTER EGG >>> ###
            # 1. Separar la pregunta secreta del resto
            pregunta_secreta = None
            otras_preguntas = []
            for p in todas_las_preguntas:
                if p.get("id") == 9999:
                    pregunta_secreta = p
                else:
                    otras_preguntas.append(p)
            
            # 2. Decidir si se incluye (probabilidad de 1/3)
            if pregunta_secreta and random.random() < 0.33:
                # Se incluye: tomar 29 normales + la secreta
                examen_temporal = random.sample(otras_preguntas, 29)
                examen_temporal.append(pregunta_secreta)
                # ¡Barajar para que no aparezca siempre al final!
                random.shuffle(examen_temporal)
                st.session_state.preguntas_examen = examen_temporal
            else:
                # No se incluye: tomar 30 normales
                st.session_state.preguntas_examen = random.sample(otras_preguntas, 30)
            # ### <<< FIN DE LA SOLUCIÓN DEL EASTER EGG >>> ###

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
elif st.session_state.examen_en_curso: # <-- Lógica simplificada
    
    remaining_time = st.session_state.duration_seconds
    if st.session_state.duration_seconds > 0:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = st.session_state.duration_seconds - elapsed_time
        
        if remaining_time <= 0:
            st.session_state.examen_en_curso = False
            st.session_state.examen_finalizado = True
            st.warning("⏰ ¡Se acabó el tiempo! El examen se ha entregado automáticamente.")
            time.sleep(2)
            st.rerun()

    idx = st.session_state.current_question_index
    total_preguntas = len(st.session_state.preguntas_examen)
    
    if st.session_state.duration_seconds > 0:
        minutes, seconds = divmod(int(remaining_time), 60)
        st.info(f"**Tiempo restante: {minutes:02d}:{seconds:02d}**")
        
    st.progress((idx + 1) / total_preguntas, text=f"Pregunta {idx + 1} de {total_preguntas}")
    
    st.write("---")
    if st.button("🚨 Entregar Examen Ahora", type="primary", use_container_width=True):
        st.session_state.examen_en_curso = False
        st.session_state.examen_finalizado = True
        st.rerun()
    st.write("---")

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

    respuesta_display = st.radio(
        "Selecciona tu respuesta:",
        options=opciones_display,
        index=current_selection_index,
        label_visibility="collapsed"
    )
    
    selected_key_index = opciones_display.index(respuesta_display)
    respuesta_seleccionada = opciones_keys[selected_key_index]
    st.session_state.respuestas[idx] = respuesta_seleccionada
    
    if q.get("id") == 9999 and respuesta_seleccionada == "C":
        st.balloons()
        st.success("¡Efecto Placebo Activado!")
        st.code("...", language="text")
        st.info("A veces, la mejor respuesta es tomarse un respiro. ¡Ánimo con el examen, vas genial!")
        time.sleep(7)
        
    st.write("---") 

    nav_container = st.container()
    with nav_container:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ **Atrás**", use_container_width=True, disabled=(idx == 0)):
                st.session_state.current_question_index -= 1
                st.rerun()
        
        with col2:
            if st.button("**Siguiente** ➡️", use_container_width=True, disabled=(idx == total_preguntas - 1)):
                st.session_state.current_question_index += 1
                st.rerun()

    if st.session_state.duration_seconds > 0:
        time.sleep(1)
        st.rerun()

# --- VISTA DE RESULTADOS ---
# ### <<< INICIO DE LA SOLUCIÓN DE LOS RESULTADOS >>> ###
# Esta condición ahora se activa correctamente
elif st.session_state.examen_finalizado:
    st.markdown("<h3>🏁 Resultados del Examen</h3>", unsafe_allow_html=True)
    
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
        else: # Incluye respuestas incorrectas
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
        # Reseteo completo del estado
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
