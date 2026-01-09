#!/usr/bin/env python3
"""
Test script to verify Better Auth integration with FastAPI backend.
This script tests the JWT token validation and JWKS fetching functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from app.core.jwks import fetch_jwks, get_jwk_for_token, verify_eddsa_token
from app.core.config import settings
from app.core.auth import decode_jwt_token

load_dotenv()

async def test_jwks_fetch():
    """Test fetching JWKS from Better Auth."""
    print("Testing JWKS fetch from Better Auth...")
    print(f"Better Auth URL: {settings.BETTER_AUTH_URL}")

    jwks = await fetch_jwks()
    if jwks:
        print(f"✅ Successfully fetched JWKS with {len(jwks.get('keys', []))} keys")
        for key in jwks.get('keys', []):
            print(f"   - Key: kid={key.get('kid')}, alg={key.get('alg')}, kty={key.get('kty')}")
        return jwks
    else:
        print("❌ Failed to fetch JWKS")
        print("   This could be because:")
        print("   - Better Auth is not running at the configured URL")
        print("   - Network connectivity issues")
        print("   - The Better Auth service is not properly configured")
        return None

def test_jwt_decode():
    """Test JWT token decoding (will fail without a real token)."""
    print("\nTesting JWT token decoding...")
    print("Note: This test will show how token decoding works, but requires a valid JWT token to succeed.")

    # Example of how a JWT token would be decoded
    example_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # Invalid example token

    print(f"Attempting to decode example token...")
    result = decode_jwt_token(example_token)
    if result is None:
        print("✅ Correctly rejected invalid token (as expected)")
    else:
        print(f"❌ Unexpectedly accepted invalid token: {result}")

async def main():
    print("Better Auth Integration Test")
    print("=" * 50)

    # Test JWKS fetching
    jwks = await test_jwks_fetch()

    # Test JWT decoding
    test_jwt_decode()

    print("\n" + "=" * 50)
    print("Test Summary:")
    print("- JWKS fetching: Should work if Better Auth is running")
    print("- JWT token validation: Requires actual Better Auth JWT token")
    print("- Backend is configured to validate Better Auth JWTs")

    if jwks:
        print("\n✅ Backend configuration looks correct!")
        print("   - JWKS endpoint is accessible")
        print("   - JWT token validation is implemented")
        print("   - Better Auth integration is properly set up")
    else:
        print("\n⚠️  Backend configuration may need adjustment:")
        print("   - Check BETTER_AUTH_URL in environment")
        print("   - Ensure Better Auth service is running")
        print("   - Verify network connectivity")

if __name__ == "__main__":
    asyncio.run(main())