import streamlit as st
import json
import random

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Examen Auxiliar de Farmacia",
    page_icon="💊",
    layout="centered"  # Centered layout se ve mejor para una pregunta a la vez
)

# --- 2. FUNCIÓN PARA CARGAR LAS PREGUNTAS (Sin cambios) ---
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

# --- 3. INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
# session_state es la memoria de Streamlit para cada usuario.
if 'examen_en_curso' not in st.session_state:
    st.session_state.examen_en_curso = False
    st.session_state.preguntas_examen = []
    st.session_state.respuestas = {}
    st.session_state.current_question_index = 0
    st.session_state.examen_finalizado = False

# --- LÓGICA PRINCIPAL DE LA APP ---

# Título principal
st.title("📝 Examen Módulo 2: Auxiliar de Farmacia Hospitalaria")

# Cargar el banco de preguntas completo
todas_las_preguntas = cargar_preguntas()
if not todas_las_preguntas:
    st.stop()

# --- VISTA DE INICIO (Cuando no hay un examen en curso) ---
if not st.session_state.examen_en_curso and not st.session_state.examen_finalizado:
    st.write("""
    **Instrucciones del examen:**
    - **Cantidad:** 30 preguntas seleccionadas al azar.
    - **Navegación:** Responde a cada pregunta para avanzar a la siguiente.
    - **Puntuación:** +1 Correcta, -1 Incorrecta, 0 Omitida ("Pasar").
    """)
    if st.button("🚀 Iniciar Nuevo Examen", type="primary", use_container_width=True):
        if len(todas_las_preguntas) < 30:
            st.warning("Advertencia: El banco de preguntas tiene menos de 30. No se puede generar un examen.")
        else:
            # Reiniciar el estado para un nuevo examen
            st.session_state.preguntas_examen = random.sample(todas_las_preguntas, 30)
            st.session_state.respuestas = {}
            st.session_state.current_question_index = 0
            st.session_state.examen_en_curso = True
            st.session_state.examen_finalizado = False
            st.rerun() # Recargar la app para empezar el examen


# --- VISTA DURANTE EL EXAMEN ---
elif st.session_state.examen_en_curso and not st.session_state.examen_finalizado:
    
    idx = st.session_state.current_question_index
    total_preguntas = len(st.session_state.preguntas_examen)
    
    # Barra de progreso
    st.progress((idx + 1) / total_preguntas, text=f"Pregunta {idx + 1} de {total_preguntas}")

    # Obtener la pregunta actual
    q = st.session_state.preguntas_examen[idx]
    
    st.subheader(f"Pregunta {idx + 1}")
    st.markdown(f"### {q['pregunta']}")
    
    st.write("") # Espacio
    
    # Función para manejar la lógica de los botones
    def registrar_respuesta(respuesta):
        st.session_state.respuestas[idx] = respuesta
        # Avanzar a la siguiente pregunta
        if st.session_state.current_question_index < total_preguntas - 1:
            st.session_state.current_question_index += 1
        else: # Si es la última pregunta, finalizar el examen
            st.session_state.examen_en_curso = False
            st.session_state.examen_finalizado = True
        st.rerun()

    # Mostrar opciones como botones
    opciones = q['opciones']
    for opcion_letra, opcion_texto in opciones.items():
        if st.button(f"**{opcion_letra}:** {opcion_texto}", use_container_width=True):
            registrar_respuesta(opcion_letra)
    
    st.write("") # Espacio
    
    # Botón de "Pasar" con un estilo diferente
    if st.button("⏩ Pasar (Omitir pregunta)", use_container_width=True, type="secondary"):
        registrar_respuesta("Pasar")


# --- VISTA DE RESULTADOS (Cuando el examen ha finalizado) ---
elif st.session_state.examen_finalizado:
    st.header("🏁 Resultados del Examen")
    
    puntuacion = 0
    correctas = 0
    incorrectas = 0
    pasadas = 0

    for i, q in enumerate(st.session_state.preguntas_examen):
        respuesta_usr = st.session_state.respuestas.get(i)
        if respuesta_usr == q['respuesta_correcta']:
            puntuacion += 1
            correctas += 1
        elif respuesta_usr == "Pasar":
            pasadas += 1
        else:
            puntuacion -= 1
            incorrectas += 1

    st.markdown(f"### Puntuación Final: **{puntuacion} puntos**")
    st.markdown(f"- ✅ **Respuestas Correctas:** `{correctas}`")
    st.markdown(f"- ❌ **Respuestas Incorrectas:** `{incorrectas}`")
    st.markdown(f"- ⏩ **Preguntas Omitidas:** `{pasadas}`")

    with st.expander("🔍 Ver corrección detallada"):
        for i, q in enumerate(st.session_state.preguntas_examen):
            st.markdown("---")
            st.markdown(f"**Pregunta {i+1}:** {q['pregunta']}")
            
            resp_usr = st.session_state.respuestas.get(i)
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

    # Botón para volver a empezar
    if st.button("↩️ Volver a la pantalla de inicio", use_container_width=True):
        st.session_state.examen_finalizado = False
        st.session_state.examen_en_curso = False
        st.rerun()
