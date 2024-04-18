import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
import hashlib

# VoiceId Verifier configuration
VOICE_ID_VERIFIER_HTTP_PROVIDER = os.environ.get("VOICE_ID_VERIFIER_HTTP_PROVIDER")
VOICE_ID_VERIFIER_CALLER_ADDRESS = os.environ.get("VOICE_ID_VERIFIER_CALLER_ADDRESS")
VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY = os.environ.get("VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY")
VOICE_ID_VERIFIER_CONTRACT_ADDRESS = os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ADDRESS")

def verify_voice_id(user_id, voice_id):
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

def change_voice_id_verification_state(user_id, is_enabled):
    """
    Changes the voice identity verification state for a given user.

    Parameters:
    - user_id (str): The identifier of the user for whom the verification state will be changed.
    - is_enabled (bool): Indicates whether to enable or disable voice identity verification for the user.
                         True to enable, False to disable.

    Returns:
    - bool: True if the transaction to change the voice identity verification state was successful,
            False otherwise.

    Raises:
    - ValueError: If `user_id` is an empty string or None.
    - ValueError: If `is_enabled` is not a boolean type.
    - Exception: If any error occurs during the Ethereum transaction execution.

    Notes:
    - Requires the global variables VOICE_ID_VERIFIER_CONTRACT_ADDRESS,
      VOICE_ID_VERIFIER_CALLER_ADDRESS, and VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY to be properly defined.
    """
    contract_abi = ""  # Insert the contract ABI here
    web3 = _connect_to_web3()
    contract = web3.eth.contract(address=VOICE_ID_VERIFIER_CONTRACT_ADDRESS, abi=contract_abi)

    # Verify parameters
    if not user_id:
        raise ValueError("The 'user_id' parameter cannot be empty or None.")
    if not isinstance(is_enabled, bool):
        raise ValueError("The 'is_enabled' parameter must be a boolean.")

    # Get user hash
    user_id_hash = _sha256(user_id)

    # Get chain ID and nonce
    chain_id = _get_chain_id(web3)
    nonce = _get_nonce(web3)

    # Build contract function call
    if is_enabled:
        contract_call = contract.functions.enableVoiceIDVerification(user_id_hash)
    else:
        contract_call = contract.functions.disableVoiceIDVerification(user_id_hash)

    # Build and send transaction
    tx_data = contract_call.build_transaction({
        "chainId": chain_id, 
        "from": VOICE_ID_VERIFIER_CALLER_ADDRESS, 
        "nonce": nonce
    })
    signed_tx = web3.eth.account.sign_transaction(tx_data, private_key=VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # Log transaction details
    _log_transaction_details(tx_receipt)

    # Check if transaction was successful
    return tx_receipt['status'] == 1

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


def _get_chain_id(web3):
    """
    Get chain ID.
    """
    return web3.eth.chain_id

def _get_nonce(web3):
    """
    Get address nonce.
    """
    return web3.eth.get_transaction_count(VOICE_ID_VERIFIER_CONTRACT_ADDRESS)

def _connect_to_web3():
    """
    Connect to the Web3 provider and return a Web3 instance.

    Returns:
    - Web3: An instance of Web3 connected to the specified HTTP provider.
    """
    web3 = Web3(Web3.HTTPProvider(VOICE_ID_VERIFIER_HTTP_PROVIDER))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject the middleware
    return web3

def _log_transaction_details(tx_receipt):
    """
    Log transaction details.
    """
    print(f"Transaction hash: {tx_receipt.transactionHash}")
    print(f"Gas used: {tx_receipt.gasUsed}")
    status = 'Success' if tx_receipt.status == 1 else 'Failed'
    print(f"Status: {status}")