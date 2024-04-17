import os
import qdrant_client
from resemblyzer import preprocess_wav, VoiceEncoder

# QDrant configuration
QDRANT_URI = os.environ.get("QDRANT_URI")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION")

def search_most_similar_audio(wav_path):
    """
    Search for the audio with the highest similarity ratio in a Qdrant collection based on the 
    embeddings of the provided WAV file.

    Parameters:
        wav_path (str): Path to the WAV file.

    Returns:
        int: ID of the most similar audio.
    """

    # Create a voice encoder object
    encoder = VoiceEncoder()

    # Preprocess the WAV file
    test_wav = preprocess_wav(wav_path)

    # Extract embeddings
    test_embeddings = encoder.embed_utterance(test_wav)

    # Initialize Qdrant client
    client = qdrant_client.QdrantClient(url=QDRANT_URI, api_key=QDRANT_API_KEY)

    # Search related embeddings
    results = client.search(QDRANT_COLLECTION, test_embeddings)

    # Get the most similar audio based on the highest score
    most_similar_audio = max(results, key=lambda result: result.score)

    return most_similar_audio.id - 1  # Adjust ID to match index