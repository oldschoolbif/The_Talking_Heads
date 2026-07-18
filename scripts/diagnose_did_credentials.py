"""
D-ID Credential Diagnostic Tool

This script helps diagnose what type of credentials you have and what type D-ID expects.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.utils.console_output import safe_print

def diagnose_credentials():
    """Diagnose D-ID credentials."""
    safe_print("="*60)
    safe_print("D-ID Credential Diagnostic Tool")
    safe_print("="*60)
    safe_print()
    
    # Check for different credential formats
    did_api_key = os.getenv("DID_API_KEY")
    did_aws_access_key = os.getenv("DID_AWS_ACCESS_KEY_ID")
    did_aws_secret_key = os.getenv("DID_AWS_SECRET_ACCESS_KEY")
    did_bearer_token = os.getenv("DID_BEARER_TOKEN")
    did_api_token = os.getenv("DID_API_TOKEN")
    
    safe_print("[STEP 1] Checking .env file for credentials...")
    safe_print()
    
    credentials_found = []
    
    # Check DID_API_KEY
    if did_api_key:
        safe_print("[OK] Found: DID_API_KEY")
        safe_print(f"     Format: {'username:password' if ':' in did_api_key else 'single string'}")
        safe_print(f"     Length: {len(did_api_key)} characters")
        
        if ":" in did_api_key:
            parts = did_api_key.split(":")
            safe_print(f"     Parts: {len(parts)} (username: {len(parts[0])} chars, password: {len(parts[1])} chars)")
        
        # Check if it looks like AWS credentials
        if did_api_key.startswith("AKIA"):
            safe_print("     [!] Looks like AWS Access Key ID")
        elif did_api_key.startswith("sk-"):
            safe_print("     [!] Looks like API token (OpenAI-style)")
        elif did_api_key.startswith("eyJ"):
            safe_print("     [!] Looks like JWT token")
        else:
            safe_print("     [!] Custom format - may need conversion")
        
        safe_print()
        credentials_found.append("DID_API_KEY")
    else:
        safe_print("[X] DID_API_KEY not found")
        safe_print()
    
    # Check AWS credentials
    if did_aws_access_key:
        safe_print("[OK] Found: DID_AWS_ACCESS_KEY_ID")
        safe_print(f"     Value: {did_aws_access_key[:4]}***{did_aws_access_key[-4:]}")
        safe_print(f"     Length: {len(did_aws_access_key)} characters")
        
        if did_aws_access_key.startswith("AKIA"):
            safe_print("     [OK] Valid AWS Access Key ID format")
        else:
            safe_print("     [!] Unusual format for AWS Access Key")
        
        safe_print()
        credentials_found.append("DID_AWS_ACCESS_KEY_ID")
    else:
        safe_print("[X] DID_AWS_ACCESS_KEY_ID not found")
        safe_print()
    
    if did_aws_secret_key:
        safe_print("[OK] Found: DID_AWS_SECRET_ACCESS_KEY")
        safe_print(f"     Length: {len(did_aws_secret_key)} characters")
        safe_print("     [!] Secret key hidden for security")
        safe_print()
        credentials_found.append("DID_AWS_SECRET_ACCESS_KEY")
    else:
        safe_print("[X] DID_AWS_SECRET_ACCESS_KEY not found")
        safe_print()
    
    # Check other credential types
    if did_bearer_token:
        safe_print("[OK] Found: DID_BEARER_TOKEN")
        safe_print(f"     Length: {len(did_bearer_token)} characters")
        safe_print()
        credentials_found.append("DID_BEARER_TOKEN")
    
    if did_api_token:
        safe_print("[OK] Found: DID_API_TOKEN")
        safe_print(f"     Length: {len(did_api_token)} characters")
        safe_print()
        credentials_found.append("DID_API_TOKEN")
    
    # Summary
    safe_print("="*60)
    safe_print("DIAGNOSTIC SUMMARY")
    safe_print("="*60)
    safe_print()
    
    if not credentials_found:
        safe_print("[X] NO CREDENTIALS FOUND")
        safe_print()
        safe_print("Action Required:")
        safe_print("1. Check your .env file in the project root")
        safe_print("2. Add D-ID credentials from the dashboard")
        safe_print("3. See DID_CREDENTIAL_CHECK_GUIDE.md for help")
        safe_print()
        return False
    
    safe_print(f"Credentials found: {len(credentials_found)}")
    for cred in credentials_found:
        safe_print(f"  - {cred}")
    safe_print()
    
    # Determine what's needed
    if "DID_AWS_ACCESS_KEY_ID" in credentials_found and "DID_AWS_SECRET_ACCESS_KEY" in credentials_found:
        safe_print("[OK] AWS IAM credentials found!")
        safe_print("     This is what we need for AWS Signature V4")
        safe_print()
        safe_print("Next steps:")
        safe_print("1. Update DIDProvider to use AWS credentials")
        safe_print("2. Test with: python scripts/test_did_aws_credentials.py")
        safe_print()
        return True
    
    elif "DID_API_KEY" in credentials_found:
        safe_print("[!] Basic API key found, but D-ID requires AWS SigV4")
        safe_print()
        safe_print("What you need to do:")
        safe_print("1. Check D-ID dashboard for AWS IAM credentials")
        safe_print("2. Look for separate 'AWS Credentials' or 'Developer Credentials'")
        safe_print("3. See DID_CREDENTIAL_CHECK_GUIDE.md for detailed steps")
        safe_print()
        safe_print("Your current API key format cannot be used directly with")
        safe_print("AWS Signature V4 authentication (required by D-ID API).")
        safe_print()
        return False
    
    else:
        safe_print("[?] Found credentials but not in expected format")
        safe_print()
        safe_print("Next steps:")
        safe_print("1. Check D-ID documentation for credential format")
        safe_print("2. Contact D-ID support for clarification")
        safe_print("3. See DID_CREDENTIAL_CHECK_GUIDE.md for help")
        safe_print()
        return False

if __name__ == "__main__":
    safe_print()
    success = diagnose_credentials()
    
    if success:
        safe_print("="*60)
        safe_print("[OK] Ready to test D-ID authentication!")
        safe_print("="*60)
    else:
        safe_print("="*60)
        safe_print("[ACTION REQUIRED]")
        safe_print()
        safe_print("Follow the guide in:")
        safe_print("  docs/DID_CREDENTIAL_CHECK_GUIDE.md")
        safe_print()
        safe_print("Or use alternatives:")
        safe_print("  - MockAvatarProvider (free, immediate)")
        safe_print("  - HeyGen (paid, production-ready)")
        safe_print("="*60)
    
    safe_print()
    sys.exit(0 if success else 1)

