import os
from resemblyzer import preprocess_wav, VoiceEncoder
from qdrant_client import QdrantClient

# QDrant configuration
QDRANT_URI = os.environ.get("QDRANT_URI")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION")

def search_most_similar_audio(audio_path):
    """
    Search for the audio with the highest similarity ratio in a Qdrant collection based on the 
    embeddings of the provided Audio file.

    Parameters:
        wav_path (str): Path to the Audio file.

    Returns:
        int: UUID of the most similar audio.
    """

    # Create a voice encoder object
    encoder = VoiceEncoder()

    # Preprocess the WAV file
    audio_file = preprocess_wav(audio_path)

    # Extract embeddings
    audio_embeddings = encoder.embed_utterance(audio_file)

    # Initialize Qdrant client
    client = QdrantClient(url=QDRANT_URI, api_key=QDRANT_API_KEY)

    # Search related embeddings
    results = client.search(QDRANT_COLLECTION, audio_embeddings)

    # Get the most similar audio based on the highest score
    most_similar_audio = max(results, key=lambda result: result.score)

    return most_similar_audio.id