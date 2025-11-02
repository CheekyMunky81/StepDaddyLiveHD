import base64
import binascii
import json
import os
import re
from typing import Any, Dict

key_bytes = os.urandom(64)


def encrypt(value: str) -> str:
    """Return an obfuscated, URL-safe representation of ``value``."""

    input_bytes = value.encode("utf-8")
    result = xor(input_bytes)
    return base64.urlsafe_b64encode(result).decode("utf-8").rstrip("=")


def decrypt(value: str) -> str:
    """Reverse :func:`encrypt` and return the original string."""

    padding_needed = (-len(value)) % 4
    padded = value + ("=" * padding_needed)
    try:
        input_bytes = base64.b64decode(
            padded,
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Encrypted value is not valid base64") from exc
    result = xor(input_bytes)
    return result.decode("utf-8")


def xor(input_bytes: bytes) -> bytes:
    """Apply a repeating XOR mask to ``input_bytes``."""

    return bytes(
        input_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(input_bytes))
    )


def urlsafe_base64(value: str) -> str:
    """Encode ``value`` as a URL-safe base64 string."""

    input_bytes = value.encode("utf-8")
    return base64.urlsafe_b64encode(input_bytes).decode("utf-8")


def urlsafe_base64_decode(value: str) -> str:
    """Decode a URL-safe base64 encoded string."""

    padding = "=" * (-len(value) % 4)
    try:
        decoded_bytes = base64.b64decode(
            (value + padding).encode("utf-8"),
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Input is not valid base64") from exc
    return decoded_bytes.decode("utf-8")


def extract_and_decode_var(var_name: str, response: str) -> str:
    """Extract an ``atob`` encoded JavaScript variable from ``response``."""

    pattern = rf'var\s+{re.escape(var_name)}\s*=\s*atob\("([^"]+)"\);'
    matches = re.findall(pattern, response)
    if not matches:
        raise ValueError(f"Variable '{var_name}' not found in response")
    try:
        return base64.b64decode(matches[-1], validate=True).decode("utf-8")
    except (ValueError, binascii.Error) as exc:
        raise ValueError(f"Variable '{var_name}' is not valid base64") from exc

def decode_bundle(response_text: str) -> dict:



    candidates = set()


    candidates.update(re.findall(r'JSON\.parse\s*\(\s*atob\s*\(\s*["\']([^"\']{40,})["\']\s*\)\s*\)', response_text))


    candidates.update(re.findall(r'atob\s*\(\s*["\'](eyJ[A-Za-z0-9+/=]{40,})["\']\s*\)', response_text))


    candidates.update(re.findall(r'(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*["\'](eyJ[A-Za-z0-9+/=]{40,})["\']', response_text))


    candidates.update(re.findall(r'["\'](eyJ[A-Za-z0-9+/=]{40,})["\']', response_text))


    candidates.update(re.findall(r'["\']([A-Za-z0-9+/=]{80,})["\']', response_text))





    for candidate in candidates:


        try:


            decoded_candidate = base64.b64decode(candidate).decode("utf-8")


            data = json.loads(decoded_candidate)


            if not all(key in data for key in ['b_ts', 'b_sig', 'b_rnd', 'b_host']):


                continue


            decoded = {}


            for k, v in data.items():


                if isinstance(v, str):


                    try:


                        pad = '=' * (-len(v) % 4)


                        decoded[k] = base64.b64decode(v + pad).decode("utf-8")


                    except Exception:


                        decoded[k] = v


                else:


                    decoded[k] = v


            return decoded


        except Exception:


            continue


    return {}
