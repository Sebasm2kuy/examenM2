import re
import json
import random

def limpiar_texto(texto):
    # Eliminar espacios extra y líneas vacías
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def extraer_oraciones(texto):
    # Dividir el texto en oraciones usando puntos o signos de interrogación
    oraciones = re.split(r'(?<=[.!?])\s+', texto)
    return [s.strip() for s in oraciones if len(s.strip()) > 20]

def generar_pregunta(oracion):
    # Buscar patrones comunes para crear preguntas
    patrones = [
        (r'principal ventaja de ([^,.]+)', '¿Cuál es la principal ventaja de {tema}?'),
        (r'mejor ([^,.]+) es ([^,.]+)', '¿Cuál es el mejor {tema}?'),
        (r'característica ([^,.]+) es ([^,.]+)', '¿Cuál es la característica {tema}?'),
        (r'función ([^,.]+) es ([^,.]+)', '¿Cuál es la función {tema}?'),
        (r'uso ([^,.]+) es ([^,.]+)', '¿Cuál es el uso {tema}?'),
    ]
    
    for patron, pregunta in patrones:
        match = re.search(patron, oracion, re.IGNORECASE)
        if match:
            tema = match.group(1).strip()
            respuesta_correcta = match.group(2).strip()
            opciones = [respuesta_correcta]
            
            # Generar distractores aleatorios
            palabras = re.findall(r'\b\w+\b', oracion)
            distractores = [w.strip() for w in palabras if w.lower() not in tema.lower() and len(w) > 3]
            opciones += random.sample(distractores, min(2, len(distractores)))
            
            # Rellenar si faltan opciones
            while len(opciones) < 3:
                opciones.append(random.choice(["Falso", "Incorrecto", "No aplica"]))
            
            random.shuffle(opciones)
            return {
                "texto": pregunta.format(tema=tema),
                "opciones": opciones,
                "correcta": respuesta_correcta
            }
    return None

def main():
    with open("guia_modulo2.txt.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    
    texto = limpiar_texto(texto)
    oraciones = extraer_oraciones(texto)
    
    preguntas = []
    for oracion in oraciones:
        pregunta = generar_pregunta(oracion)
        if pregunta and pregunta not in preguntas:
            preguntas.append(pregunta)
    
    # Limitar a 50 preguntas (para variedad en exámenes)
    preguntas = preguntas[:50]
    
    with open("preguntas_modulo2.json", "w", encoding="utf-8") as f:
        json.dump(preguntas, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()