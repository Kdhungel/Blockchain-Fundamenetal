import hashlib
import json

def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()

def get_hash(block):
    """
    Creates a simple hash by joining block values.

    Args:
        block (dict): Block to hash.

    Returns:
        str: Hash string of the block.
    """
    return hash_string_256(json.dumps(block, sort_keys=True).encode())
