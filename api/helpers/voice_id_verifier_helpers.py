import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
import hashlib

# VoiceId Verifier configuration
VOICE_ID_VERIFIER_HTTP_PROVIDER = os.environ.get("VOICE_ID_VERIFIER_HTTP_PROVIDER")
VOICE_ID_VERIFIER_CALLER_ADDRESS = os.environ.get("VOICE_ID_VERIFIER_CALLER_ADDRESS")
VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY = os.environ.get("VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY")
VOICE_ID_VERIFIER_CONTRACT_ADDRESS = os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ADDRESS")

def verifyVoiceID(user_id, voice_id):
    """
    Verify the user's voice ID against the stored voice ID hash in the smart contract.

    Parameters:
    - user_id (str): The unique identifier of the user.
    - voice_id (str): The voice ID provided by the user for verification.

    Returns:
    - bool: True if the voice ID matches the stored hash in the contract, False otherwise.
    """
    contract_abi = ""
    web3 = _connect_to_web3()
    contract = web3.eth.contract(address=VOICE_ID_VERIFIER_CONTRACT_ADDRESS, abi=contract_abi)
    user_id_hash = _sha256(user_id)
    voice_file_id_hash = _sha256(voice_id)
    result = contract.functions.verifyVoiceID(user_id_hash, voice_file_id_hash).call() 
    return result

def _sha256(data):
    """
    Calculate the SHA-256 hash of the input data.

    Parameters:
    - data (str): The input data to be hashed.

    Returns:
    - str: The hexadecimal representation of the SHA-256 hash.
    """
    hash_object = hashlib.sha256(data.encode())
    return hash_object.hexdigest()

def _connect_to_web3():
    """
    Connect to the Web3 provider and return a Web3 instance.

    Returns:
    - Web3: An instance of Web3 connected to the specified HTTP provider.
    """
    web3 = Web3(Web3.HTTPProvider(VOICE_ID_VERIFIER_HTTP_PROVIDER))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject the middleware
    return web3