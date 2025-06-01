import os
import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import subprocess

# Ruta donde están los archivos de embeddings JSON
EMBEDDINGS_PATH = "embeddings"
NUM_DOCUMENTOS = 1  # Número de documentos más similares a recuperar

# Cargar modelo de embeddings
print("🔍 Cargando modelo de embeddings...")
modelo_emb = SentenceTransformer("all-MiniLM-L6-v2")

def cargar_todos_los_embeddings(carpeta_embeddings):
    documentos = []
    for nombre_archivo in os.listdir(carpeta_embeddings):
        if nombre_archivo.endswith(".json"):
            ruta_completa = os.path.join(carpeta_embeddings, nombre_archivo)
            with open(ruta_completa, "r", encoding="utf-8") as f:
                documento = json.load(f)
                documentos.append(documento)
    return documentos

def similitud_coseno(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def normalizar_vector(v):
    return v / np.linalg.norm(v)

def encontrar_documentos_similares(pregunta, documentos, modelo_emb, n=NUM_DOCUMENTOS):
    emb_pregunta = modelo_emb.encode(pregunta).tolist()
    similitudes = []
    for doc in documentos:
        emb_doc = doc.get("embedding")
        if emb_doc is None:
            continue  # Saltar si no tiene embedding
        similitud = similitud_coseno(emb_pregunta, emb_doc)
        similitudes.append((similitud, doc))
    similitudes.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in similitudes[:n]]

def construir_prompt(opcion, pregunta, documentos):
    textos = []
    sin_texto = 0
    for doc in documentos:
        # Usar "contenido" si existe, si no, usar "archivo" o "tema" para no romper el código
        if "contenido" in doc:
            textos.append(doc["contenido"][:3000])
        elif "archivo" in doc:
            textos.append(f"(Texto no disponible, archivo: {doc['archivo']})")
            sin_texto += 1
        elif "tema" in doc:
            textos.append(f"(Texto no disponible, tema: {doc['tema']})")
            sin_texto += 1
        else:
            textos.append("(Texto no disponible)")
            sin_texto += 1

    contexto = "\n\n".join(textos)
    
    if opcion == "1":
        instrucciones = "Responde defendiendo una postura a favor fundamentada:"
    elif opcion == "2":
        instrucciones = "Responde defendiendo una postura en contra fundamentada:"
    elif opcion == "3":
        instrucciones = "Compara perspectivas a favor y en contra del tema:"
    elif opcion == "4":
        instrucciones = "Simula un debate entre dos posturas opuestas sobre el tema. Cada parte debe argumentar claramente su posición:"
    else:
        instrucciones = "Responde a la siguiente pregunta con base en los textos:"

    if sin_texto > 0:
        instrucciones += f"\n\n⚠️ Nota: {sin_texto} documentos no tienen texto disponible y se usan solo como referencia."

    return f"""{instrucciones}

Contexto relevante:
{contexto}

Pregunta:
{pregunta}
"""

def ejecutar_llama(prompt):
    try:
        # Crear un archivo temporal con el prompt
        temp_file = "temp_prompt.txt"
        with open(temp_file, "w", encoding="UTF-8") as f:
            f.write(prompt)
        
        # Construir el comando
        comando = f"type {temp_file} | ollama run llama3"
        
        # Ejecutar en shell con timeout extendido
        proceso = subprocess.Popen(comando, 
                                 stdin=open(temp_file, "r", encoding="utf-8"),
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 encoding="utf-8")
        
        # Esperar con timeout más largo (5 minutos)
        salida, errores = proceso.communicate(timeout=300)
        
        # Eliminar archivo temporal
        os.remove(temp_file)
        
        if errores:
            print("⚠️ Error en Ollama:", errores)
        return salida
        
    except subprocess.TimeoutExpired:
        proceso.kill()
        return "⌛ El modelo tardó demasiado en responder. Intenta con una consulta más específica."
    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"

documentos = cargar_todos_los_embeddings(EMBEDDINGS_PATH)
print(f"📄 {len(documentos)} documentos cargados.\n")

while True:
    print("🧠 ¿Qué deseas hacer?")
    print("1. Defender postura a favor")
    print("2. Defender postura en contra")
    print("3. Comparar perspectivas")
    print("4. Simular debate")
    print("5. Salir")
    opcion = input("> ")

    if opcion == "5":
        print("👋 Saliendo del sistema.")
        break

    pregunta = input("❓ Ingresa tu pregunta:\n> ")

    documentos_similares = encontrar_documentos_similares(pregunta, documentos, modelo_emb)
    prompt = construir_prompt(opcion, pregunta, documentos_similares)

    print("\n🤖 Llamando a LLaMA 3.2...\n")
    respuesta = ejecutar_llama(prompt)
    print("🧠 Respuesta del modelo:\n")
    print(respuesta)
    print("\n---\n")
