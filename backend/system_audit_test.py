import httpx
import asyncio
import json
import time

BASE_URL = "https://verificai-code-quality-system-i9im.onrender.com/api/v1"
LOCAL_URL = "http://localhost:8000/api/v1"

async def run_audit():
    print("=== VERIFICAI SYSTEM AUDIT ===")
    
    # Try production first
    url = BASE_URL
    print(f"Testing PROD URL: {url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Version Check
        try:
            # Check root health first as it's guaranteed to be public
            health_resp = await client.get("https://verificai-code-quality-system-i9im.onrender.com/health")
            if health_resp.status_code == 200:
                print(f"✅ Health Check: {health_resp.json().get('status')} (Version: {health_resp.json().get('version', 'N/A')})")
            
            # Check new public version endpoint
            resp = await client.get("https://verificai-code-quality-system-i9im.onrender.com/public/version")
            if resp.status_code == 200:
                print(f"✅ Version Check: {resp.json().get('version')} - {resp.json().get('status')}")
                print(f"   Features: {', '.join(resp.json().get('features', []))}")
            else:
                print(f"❌ Version Check Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"⚠️ PROD unavailable, trying LOCAL... ({str(e)})")
            url = LOCAL_URL
            try:
                resp = await client.get(f"{url}/version")
                print(f"✅ Local Version Check: {resp.json().get('version')}")
            except:
                print("❌ Both PROD and LOCAL unavailable.")
                return

        # 2. Login Check
        print("\n--- Testing Authentication ---")
        # Trying the password from main.py /setup
        login_data = {"username": "admin", "password": "Admin@2024"}
        # Auth usually uses form data for OAuth2
        try:
            resp = await client.post(f"{url}/login", data=login_data)
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                print("✅ Login Successful")
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print(f"❌ Login Failed: {resp.status_code} - {resp.text}")
                return
        except Exception as e:
            print(f"❌ Login Error: {str(e)}")
            return

        # 3. Public Path Sync Check
        print("\n--- Testing Path IDs Fix ---")
        try:
            resp = await client.get(f"{url}/file-paths/public")
            if resp.status_code == 200:
                paths = resp.json()
                print(f"✅ Found {len(paths)} public paths")
                if len(paths) > 0 and isinstance(paths[0], dict) and "file_id" in paths[0]:
                    print(f"✅ PATH ID SYNC VALIDATED: '{paths[0]['full_path']}' has ID '{paths[0]['file_id']}'")
                else:
                    print("❌ PATH ID SYNC FAILED: Response format incorrect or missing file_id")
            else:
                print(f"❌ Path Fetch Failed: {resp.status_code}")
        except Exception as e:
            print(f"❌ Path Fetch Error: {str(e)}")

        # 4. Analysis Orchestrator Check (Status List)
        print("\n--- Testing Analysis History ---")
        try:
            resp = await client.get(f"{url}/analysis/", headers=headers)
            if resp.status_code == 200:
                analyses = resp.json()
                print(f"✅ Found {len(analyses)} analyses in history")
            else:
                print(f"❌ Analysis Fetch Failed: {resp.status_code}")
        except Exception as e:
            print(f"❌ Analysis Fetch Error: {str(e)}")

    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(run_audit())
