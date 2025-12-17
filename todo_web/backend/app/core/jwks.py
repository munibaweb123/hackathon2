"""JWKS (JSON Web Key Set) utilities for Better Auth integration."""

import logging
import httpx
import asyncio
import base64
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519
import jwt
import json
from .config import settings

logger = logging.getLogger(__name__)

# Global cache for JWKS
_cached_jwks: Optional[Dict[str, Any]] = None


async def fetch_jwks():
    """Fetch JWKS from Better Auth."""
    global _cached_jwks
    try:
        better_auth_url = settings.BETTER_AUTH_URL.rstrip('/')
        # Better Auth JWKS endpoint
        jwks_url = f"{better_auth_url}/api/auth/jwks"

        logger.info(f"Fetching JWKS from: {jwks_url}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(jwks_url)
            logger.info(f"JWKS response status: {response.status_code}")

            if response.status_code == 200:
                jwks = response.json()
                _cached_jwks = jwks
                keys = jwks.get('keys', [])
                logger.info(f"Successfully fetched JWKS with {len(keys)} keys")
                for key in keys:
                    logger.info(f"  - Key: kid={key.get('kid')}, alg={key.get('alg')}, kty={key.get('kty')}")
                return jwks
            else:
                logger.warning(f"JWKS endpoint returned status {response.status_code}: {response.text}")
                return None

    except httpx.ConnectError as e:
        logger.error(f"Could not connect to JWKS endpoint: {e}")
        return None
    except httpx.TimeoutException:
        logger.error("Timeout when fetching JWKS")
        return None
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e}")
        return None


def get_jwk_for_token(token: str) -> Optional[Dict[str, Any]]:
    """Get the appropriate JWK for the given token."""
    global _cached_jwks

    if not _cached_jwks:
        logger.warning("No cached JWKS available")
        # Note: We can't fetch JWKS synchronously in this context because it would block
        # and may not work with uvloop. The JWKS should be fetched during app startup.
        # For a hackathon solution, we'll log this and return None
        logger.warning("JWKS not available during token verification. Ensure app startup completed properly.")
        return None

    try:
        # Decode header without verification to get kid
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        alg = header.get('alg', 'unknown')

        logger.debug(f"Token header - kid: {kid}, alg: {alg}")

        # Find the key in the JWKS
        keys = _cached_jwks.get('keys', [])
        for key in keys:
            if key.get('kid') == kid:
                logger.debug(f"Found JWK with matching kid: {kid}")
                return key

        # If no kid match, try to find a key with matching algorithm
        if not kid:
            for key in keys:
                if key.get('alg') == alg or (alg == 'EdDSA' and key.get('kty') == 'OKP'):
                    # EdDSA typically uses OKP (Octet Key Pair) keys
                    logger.debug(f"Found JWK with matching algorithm: {alg}")
                    return key

        logger.warning(f"No matching JWK found for kid: {kid}, alg: {alg}")
        logger.debug(f"Available keys: {[k.get('kid') for k in keys]}")
        return None
    except Exception as e:
        logger.error(f"Error finding JWK for token: {e}")
        import traceback
        logger.debug(f"JWK lookup traceback: {traceback.format_exc()}")
        return None


def verify_eddsa_token(token: str, jwk: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Verify an EdDSA-signed JWT token using the provided JWK."""
    try:
        # Extract the public key from the JWK
        # For EdDSA with OKP (Octet Key Pair), the 'x' field contains the public key
        x_b64 = jwk.get('x')
        if not x_b64:
            logger.error("JWK does not contain 'x' parameter for EdDSA public key")
            return None

        # Add proper padding for base64 URL decoding
        x_b64 += '=' * (4 - len(x_b64) % 4)
        x_bytes = base64.urlsafe_b64decode(x_b64)

        # Create the Ed25519 public key
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(x_bytes)

        # Get the signing input (header and payload)
        parts = token.split('.')
        if len(parts) != 3:
            logger.error("Invalid JWT format")
            return None

        # The signing input is the base64url-encoded header and payload
        signing_input = f"{parts[0]}.{parts[1]}".encode('utf-8')

        # Decode the signature
        sig_b64 = parts[2]
        # Add proper padding for base64 URL decoding
        sig_b64 += '=' * (4 - len(sig_b64) % 4)
        signature = base64.urlsafe_b64decode(sig_b64)

        # Verify the signature
        public_key.verify(signature, signing_input)

        # If signature is valid, decode the payload without verification (since we already verified)
        payload_b64 = parts[1]
        # Add proper padding
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)

        logger.debug(f"Successfully verified EdDSA token for user: {payload.get('sub', 'unknown')}")
        return payload
    except Exception as e:
        logger.warning(f"EdDSA token verification failed: {e}")
        import traceback
        logger.debug(f"EdDSA verification traceback: {traceback.format_exc()}")
        return None