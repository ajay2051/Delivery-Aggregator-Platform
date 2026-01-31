import hashlib
import json


def generate_idempotency_key(user_id, payload: dict, prefix="delivery"):
    """
    Generate a deterministic idempotency key.

    Same user + same payload = same key.
    Different payload or user = different key.

    Args:
        user_id (int): Authenticated user ID
        payload (dict): Request data
        prefix (str): Namespace prefix

    Returns:
        str: Idempotency key
    """
    normalized_payload = json.dumps(payload, sort_keys=True)
    raw_string = f"{prefix}:{user_id}:{normalized_payload}"

    return hashlib.sha256(raw_string.encode()).hexdigest()