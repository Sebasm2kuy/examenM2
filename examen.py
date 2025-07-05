import streamlit as st
import json
import random

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# Se establece el título que aparecerá en la pestaña del navegador, el ícono y el layout.
st.set_page_config(
    page_title="Examen Auxiliar de Farmacia",
    page_icon="💊",
    layout="wide"
)

# --- 2. FUNCIÓN PARA CARGAR LAS PREGUNTAS ---
# Usa un decorador de caché para que las preguntas se carguen desde el archivo JSON solo una vez.
# Esto hace que la app sea mucho más rápida cada vez que un usuario interactúa.
@st.cache_data
def cargar_preguntas():
    """
    Carga las preguntas desde el archivo 'preguntas_modulo2.json'.
    Maneja el error si el archivo no se encuentra.
    """
    try:
        with open('preguntas_modulo2.json', 'r', encoding='utf-8') as f:
            preguntas = json.load(f)
        return preguntas
    except FileNotFoundError:
        st.error("Error crítico: No se pudo encontrar el archivo 'preguntas_modulo2.json'. Asegúrate de que el archivo esté en el mismo repositorio de GitHub que 'examen.py'.")
        return None
    except json.JSONDecodeError:
        st.error("Error crítico: El archivo 'preguntas_modulo2.json' tiene un formato incorrecto. Por favor, revísalo.")
        return None

# --- 3. LÓGICA PRINCIPAL DE LA APLICACIÓN ---

# Título principal e instrucciones para el usuario.
st.title("📝 Examen Módulo 2: Auxiliar de Farmacia Hospitalaria")
st.write("""
**Instrucciones del examen:**
- **Cantidad:** Se presentarán 30 preguntas de opción múltiple (A, B, C).
- **Selección:** Las preguntas son seleccionadas al azar de un banco de preguntas más grande.
- **Puntuación:**
  - **Respuesta Correcta:** +1 punto.
  - **Respuesta Incorrecta:** -1 punto.
  - **Pregunta Omitida ("Pasar"):** 0 puntos.
- Para comenzar, haz clic en el botón de abajo. ¡Mucho éxito!
""")

# Se cargan todas las preguntas del archivo JSON.
todas_las_preguntas = cargar_preguntas()

# Solo se continúa si el archivo de preguntas se cargó correctamente.
if todas_las_preguntas:
    # Botón para iniciar un nuevo examen. Esto reinicia el estado.
    if st.button("🚀 Iniciar Nuevo Examen", type="primary"):
        # Se verifica que haya suficientes preguntas en el banco.
        if len(todas_las_preguntas) < 30:
            st.warning("Advertencia: El banco de preguntas tiene menos de 30. No se puede generar un examen completo.")
            st.stop() # Detiene la ejecución si no hay suficientes preguntas.

        # **Lógica clave**: Se seleccionan 30 preguntas al azar sin repetición.
        st.session_state.preguntas_examen = random.sample(todas_las_preguntas, 30)
        # Se inicializan las respuestas del usuario y el estado del examen.
        st.session_state.respuestas = {}
        st.session_state.examen_finalizado = False
        st.rerun() # Se recarga la página para mostrar el examen.

    # Si ya se ha generado un examen, se muestran las preguntas.
    if 'preguntas_examen' in st.session_state and not st.session_state.get('examen_finalizado', False):
        
        # Se usa un formulario para agrupar todas las preguntas.
        # Esto evita que la página se recargue cada vez que se responde una pregunta.
        with st.form("examen_form"):
            for i, q in enumerate(st.session_state.preguntas_examen):
                st.subheader(f"Pregunta {i + 1}")
                st.markdown(f"**{q['pregunta']}**")
                
                # Se crea la lista de opciones para el radio button, incluyendo "Pasar".
                opciones = q['opciones']
                opciones_radio = ["Pasar"] + list(opciones.keys())
                
                # Se crea el radio button para la pregunta.
                respuesta = st.radio(
                    "Selecciona tu respuesta:",
                    options=opciones_radio,
                    key=f"q_{i}",
                    # Esta función formatea cómo se ven las opciones.
                    format_func=lambda x: f"{x}: {opciones[x]}" if x != "Pasar" else "Pasar (omitir pregunta)"
                )
                
                st.session_state.respuestas[i] = respuesta
            
            # Botón de envío al final del formulario.
            submitted = st.form_submit_button("Calificar Examen y Ver Resultados")
            if submitted:
                st.session_state.examen_finalizado = True
                st.rerun()

    # --- 4. CÁLCULO Y VISUALIZACIÓN DE RESULTADOS ---
    # Esto se muestra solo después de que el examen ha sido enviado.
    if st.session_state.get('examen_finalizado', False):
        st.header("🏁 Resultados del Examen")
        
        puntuacion = 0
        correctas = 0
        incorrectas = 0
        pasadas = 0

        # Se itera sobre las preguntas del examen para calcular el puntaje.
        for i, q in enumerate(st.session_state.preguntas_examen):
            respuesta_usr = st.session_state.respuestas.get(i)
            respuesta_ok = q['respuesta_correcta']

            if respuesta_usr == respuesta_ok:
                puntuacion += 1
                correctas += 1
            elif respuesta_usr == "Pasar":
                pasadas += 1
            else: # Respuesta incorrecta
                puntuacion -= 1
                incorrectas += 1

        # Se muestra un resumen del puntaje.
        st.markdown(f"""
        ### Puntuación Final Obtenida: **{puntuacion} puntos**
        - ✅ **Respuestas Correctas:** `{correctas}`
        - ❌ **Respuestas Incorrectas:** `{incorrectas}`
        - ⏩ **Preguntas Omitidas:** `{pasadas}`
        """)

        # Se crea una sección expandible para ver la corrección detallada.
        with st.expander("🔍 Ver corrección detallada de cada pregunta"):
            for i, q in enumerate(st.session_state.preguntas_examen):
                st.markdown("---")
                st.markdown(f"**Pregunta {i+1}:** {q['pregunta']}")
                
                respuesta_usr = st.session_state.respuestas.get(i)
                letra_ok = q['respuesta_correcta']
                texto_ok = q['opciones'][letra_ok]

                if respuesta_usr == letra_ok:
                    st.success(f"✔️ Tu respuesta fue '{respuesta_usr}: {texto_ok}'. ¡Correcto!")
                elif respuesta_usr == "Pasar":
                    st.info(f"⏩ Omitiste esta pregunta. La respuesta correcta era '{letra_ok}: {texto_ok}'.")
                else:
                    texto_usr = q['opciones'].get(respuesta_usr, "INVÁLIDA")
                    st.error(f"❌ Tu respuesta fue '{respuesta_usr}: {texto_usr}'.")
                    st.info(f"✔️ La respuesta correcta era '{letra_ok}: {texto_ok}'.")

# Mensaje final en caso de que el archivo de preguntas no se cargue al inicio.
else:
    st.info("La aplicación está lista. Esperando el archivo de preguntas para poder generar los exámenes.")