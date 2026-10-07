"""
Proyecto Integrador: FocusClass
Descripción: Sistema de análisis y resumen automatizado de transcripciones de clases
              para optimizar el tiempo de estudio y evitar la procrastinación.
Asignatura: Proyecto Integrador - Desarrollo de Software
"""

import os
import json
import re

# Constantes y palabras de parada (Stopwords) en español
STOP_WORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un",
    "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le",
    "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre",
    "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
    "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e",
    "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él"
}

ARCHIVOPROGRESOS = "progresos.json"

def cargar_progresos():
    """Carga el historial de clases completadas desde un archivo JSON."""
    if os.path.exists(ARCHIVOPROGRESOS):
        try:
            with open(ARCHIVOPROGRESOS, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"clases_completadas": [], "total_puntos": 0}
    return {"clases_completadas": [], "total_puntos": 0}

def guardar_progresos(datos):
    """Guarda el progreso del estudiante en el archivo JSON."""
    with open(ARCHIVOPROGRESOS, "w", encoding="utf-8") as file:
        json.dump(datos, file, ensure_ascii=False, indent=4)

def limpiar_texto(texto):
    """Limpia el texto eliminando caracteres especiales y convirtiendo a minúsculas."""
    texto_limpio = re.sub(r'[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]', '', texto)
    return texto_limpio.lower()

def calcular_frecuencias(texto):
    """Calcula la frecuencia de cada palabra relevante (descartando stopwords)."""
    palabras = limpiar_texto(texto).split()
    frecuencias = {}
    
    for palabra in palabras:
        if palabra not in STOP_WORDS and len(palabra) > 2:
            frecuencias[palabra] = frecuencias.get(palabra, 0) + 1
            
    return frecuencias

def generar_resumen(texto, cantidad_oraciones=3):
    """Genera un resumen extrayendo las oraciones con mayor puntuación según palabras clave."""
    # Separar en oraciones manteniendo puntuación básica
    oraciones = [o.strip() for o in re.split(r'[.!?]+', texto) if o.strip()]
    
    if not oraciones:
        return "El archivo está vacío o no contiene oraciones válidas."
        
    frecuencias = calcular_frecuencias(texto)
    puntuacion_oraciones = {}
    
    # Evaluar cada oración
    for i, oracion in enumerate(oraciones):
        palabras_oracion = limpiar_texto(oracion).split()
        score = sum(frecuencias.get(p, 0) for p in palabras_oracion)
        # Normalizar por la longitud de la oración para no penalizar/premiar en exceso
        puntuacion_oraciones[i] = score / (len(palabras_oracion) + 1)
        
    # Seleccionar las mejores oraciones
    oraciones_ordenadas = sorted(puntuacion_oraciones.items(), key=lambda x: x[1], reverse=True)
    indices_seleccionados = sorted([item[0] for item in oraciones_ordenadas[:cantidad_oraciones]])
    
    resumen = [oraciones[idx] + "." for idx in indices_seleccionados]
    return " ".join(resumen)

def menu_principal():
    """Interfaz principal de consola para el estudiante."""
    progreso = cargar_progresos()
    
    while True:
        print("\n" + "="*50)
        print("          FOCUSCLASS - APRENDIZAJE EFECTIVO          ")
        print("="*50)
        print(f"Puntos de Enfoque Acumulados: {progreso.get('total_puntos', 0)} pts")
        print("1. Procesar y Resumir Transcripción de Clase (.txt)")
        print("2. Marcar Clase como Completada / Ganar Puntos")
        print("3. Ver Historial de Clases Procesadas")
        print("4. Salir")
        print("="*50)
        
        opcion = input("Seleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            ruta_archivo = input("\nIngrese la ruta del archivo .txt con la transcripción: ").strip()
            if not os.path.exists(ruta_archivo):
                print("❌ Error: El archivo especificado no existe.")
                continue
                
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as file:
                    contenido = file.read()
                    
                if not contenido.strip():
                    print("⚠️ El archivo está vacío.")
                    continue
                    
                print("\n--- GENERANDO RESUMEN AUTOMATIZADO ---")
                resumen = generar_resumen(contenido, cantidad_oraciones=4)
                print("\n📌 RESUMEN DE LA CLASE:")
                print(resumen)
                
                # Guardar temporalmente la última clase procesada
                nombre_clase = os.path.basename(ruta_archivo)
                progreso["ultima_clase"] = nombre_clase
                
            except Exception as e:
                print(f"❌ Ocurrió un error al leer el archivo: {e}")
                
        elif opcion == "2":
            if "ultima_clase" in progreso:
                clase = progreso["ultima_clase"]
                if clase not in progreso["clases_completadas"]:
                    progreso["clases_completadas"].append(clase)
                    progreso["total_puntos"] = progreso.get("total_puntos", 0) + 100
                    guardar_progresos(progreso)
                    print(f"\n🎉 ¡Felicidades! Completaste '{clase}'. Ganaste +100 Puntos de Enfoque.")
                else:
                    print(f"\n⚠️ La clase '{clase}' ya fue marcada como completada anteriormente.")
            else:
                print("\n⚠️ Primero debes procesar un archivo en la Opción 1.")
                
        elif opcion == "3":
            print("\n--- HISTORIAL DE CLASES COMPLETADAS ---")
            clases = progreso.get("clases_completadas", [])
            if clases:
                for idx, c in enumerate(clases, 1):
                    print(f"{idx}. {c}")
            else:
                print("Aún no has completado ninguna clase.")
                
        elif opcion == "4":
            print("\n¡Gracias por usar FocusClass! Mantente enfocado y sin distracciones.")
            break
        else:
            print("❌ Opción inválida. Por favor seleccione entre 1 y 4.")

if __name__ == "__main__":
    menu_principal()
