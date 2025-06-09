from instagrapi import Client
import os

USERNAME = ""
PASSWORD = ""
SESSION_PATH = "session.json"

cl = Client()

# Optional: provide a custom device profile (avoid re-verification)
cl.load_settings(SESSION_PATH) if os.path.exists(SESSION_PATH) else None

# This triggers 2FA the first time
cl.login(USERNAME, PASSWORD, verification_code="")

# Save session
cl.dump_settings(SESSION_PATH)
