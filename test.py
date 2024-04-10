# importar las bibliotecas necesarias
from resemblyzer import preprocess_wav, VoiceEncoder
from  pathlib import Path 
from tqdm import tqdm 
import numpy as np 
from itertools import groupby
import heapq

# Listar las rutas de los archivos de audio en la carpeta "assets/train" que tengan la extensión ".mp3"
wav_fpaths = list(Path("assets/train").rglob("*.mp3"))

# Extraer los nombres de los altavoces (nombre de archivo sin la extensión) de las rutas de los archivos de audio
speakers = list(map(lambda wav_fpath: wav_fpath.stem, wav_fpaths))

# Imprimir los nombres de los altavoces
print(speakers)

# Preprocesar los archivos de audio utilizando la función preprocess_wav de la biblioteca resemblyzer
# tqdm se utiliza para mostrar una barra de progreso mientras se procesan los archivos
# Se crea un arreglo numpy llamado wavs que contiene los datos preprocesados de los archivos de audio
wavs = np.array(list(map(preprocess_wav, tqdm(wav_fpaths, "Preprocessing wavs", len(wav_fpaths)))), dtype=object)

# Agrupar los datos preprocesados de los archivos de audio por altavoz
# Se crea un diccionario llamado speaker_wavs donde las claves son los nombres de los altavoces y los valores son los datos preprocesados de los archivos de audio correspondientes
speaker_wavs = {speaker: wavs[list(indices)] for speaker, indices in groupby(range(len(wavs)), lambda i: speakers[i])}

# Imprimir el diccionario de altavoces y sus datos preprocesados
print(speaker_wavs)

# compute the embeddings
encoder = VoiceEncoder("cuda")
utterance_embeds = np.array(list(map(encoder.embed_utterance, wavs)))
print(utterance_embeds)

# Create an empty list to hold the embeddings in the desired format
embeddings = []

# Iterate through each embedding in the array
for i, embedding in enumerate(utterance_embeds):
   # Create a dictionary with “id” and “vector” keys
   embedding_dict  = { "id":i+1, "vector":embedding.tolist()} # Start IDs from 1
   # Append the dictionary to the embeddings list
   embeddings.append(embedding_dict)

import qdrant_client
qdrant_uri = '' # Paste your URI
qdrant_api_key = '' # Paste your API KEY
# Create a collection
vectors_config = qdrant_client.http.models.VectorParams(
  size=256, # requires for embeddings from resemblyzer
  distance=qdrant_client.http.models.Distance.COSINE
)
client = qdrant_client.QdrantClient(url=qdrant_uri, api_key=qdrant_api_key)
# Upsert embeddings
client.create_collection('my-collection', vectors_config)

test_wav = preprocess_wav("assets/Siuu.mp3")
# Create a voice encoder object
test_embeddings = encoder.embed_utterance(test_wav)

# Search related embeddings
results = client.search("my-collection", test_embeddings)
print(results)

# Get the top two results based on scores, handling potential ties
top_two_results = heapq.nlargest(2, results, key=lambda result: result.score)

# Extract and align IDs, considering potential ties
top_two_ids = sorted({result.id - 1 for result in top_two_results}) # Remove duplicates

# Get corresponding names, checking for valid IDs
top_two_names = []
for aligned_id in top_two_ids:
 if 0 <= aligned_id < len(speakers):
  top_two_names.append(speakers[aligned_id])

 else:
  print(f"Invalid ID {aligned_id + 1} encountered.")

print("Top two speakers: ", top_two_names)