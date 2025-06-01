from sentence_transformers import SentenceTransformer
import os
import json

# Ruta base de los textos-
DATASET_DIR = 'dataset'
OUTPUT_DIR = 'embeddings'
MODEL_NAME = 'all-MiniLM-L6-v2'  # Ligero y rápido, ideal para este tipo de tareas

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cargar modelo de embeddings
print("Cargando modelo...")
model = SentenceTransformer(MODEL_NAME)

# Recorremos carpetas y archivos
for tema in os.listdir(DATASET_DIR):
    tema_path = os.path.join(DATASET_DIR, tema)

    if os.path.isdir(tema_path):
        print(f"\nProcesando tema: {tema}")

        for archivo in os.listdir(tema_path):
            if archivo.endswith('.txt'):
                ruta_txt = os.path.join(tema_path, archivo)

                with open(ruta_txt, 'r', encoding='utf-8') as f:
                    texto = f.read()

                embedding = model.encode(texto).tolist()  # Convertir a lista para guardar en JSON

                nombre_salida = archivo.replace('.txt', '.json')
                ruta_salida = os.path.join(OUTPUT_DIR, nombre_salida)

                with open(ruta_salida, 'w', encoding='utf-8') as f:
                    json.dump({
                        'archivo': archivo,
                        'tema': tema,
                        'contenido': texto,
                        'embedding': embedding
                    }, f, ensure_ascii=False, indent=2)

                print(f"✅ Embedding generado para: {archivo}")
