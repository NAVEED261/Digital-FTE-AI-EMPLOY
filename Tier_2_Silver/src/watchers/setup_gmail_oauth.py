#!/usr/bin/env python3
"""
Gmail OAuth 2.0 Setup Script - Silver Tier
Creates credentials.json and retrieves refresh token for Gmail API
"""

import os
import json
import pickle
from pathlib import Path
from google.auth.oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def setup_gmail_oauth():
    """Setup Gmail OAuth 2.0 credentials"""

    credentials_file = Path('credentials.json')
    token_file = Path.home() / '.gmail_token.pickle'

    print("🔐 Gmail OAuth 2.0 Setup")
    print("=" * 50)
    print()

    # Step 1: Create credentials.json if not exists
    if not credentials_file.exists():
        print("❌ credentials.json not found!")
        print()
        print("📋 To set up Gmail OAuth:")
        print()
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download JSON file and save as: credentials.json")
        print()
        print("6. Then run this script again")
        return False

    # Step 2: Authenticate with Gmail API
    try:
        print("✅ credentials.json found!")
        print()
        print("🔑 Authenticating with Gmail...")
        print()

        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)

        # This will open browser for authentication
        creds = flow.run_local_server(port=0)

        # Step 3: Save token
        print()
        print("✅ Authentication successful!")
        print()

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

        print(f"✅ Token saved to: {token_file}")
        print()

        # Step 4: Update .env file
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()

            # Note: refresh token might not be available for Desktop OAuth
            # Will need to use service account or manual token refresh
            with open(env_file, 'w') as f:
                f.write(env_content)
                f.write('\n\n# Gmail OAuth - Set after first authentication\n')
                f.write('GMAIL_AUTHENTICATED=true\n')

        print("✅ Environment configured!")
        print()
        print("📊 Next steps:")
        print("1. Gmail Watcher can now fetch emails")
        print("2. Start watcher: python gmail_watcher.py <vault_path>")
        print("3. Configure email sending (Silver Tier email-mcp)")
        print()

        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == '__main__':
    setup_gmail_oauth()
