import subprocess
import json
import os
import shutil
import asyncio
import concurrent.futures
import requests

# ==========================================
# CONFIGURATION: API KEYS (Opsional)
# Isikan Key jika kamu/tim sudah berlangganan
# ==========================================
DEHASHED_EMAIL = os.getenv("DEHASHED_EMAIL", "")  # Email akun DeHashed
DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY", "")  # API Key DeHashed
LEAK_LOOKUP_API_KEY = os.getenv("LEAK_LOOKUP_KEY", "")  # API Key Leak-Lookup

def check_holehe_sync(email):
    try:
        bat_path = os.path.join(os.getcwd(), "holehe.bat")
        holehe_exe = bat_path if os.path.exists(bat_path) else (shutil.which("holehe") or r"env\Scripts\holehe.exe")
        
        cmd = [holehe_exe, email, "--only-used"]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        raw_output = result.stdout.strip() if result.stdout else ""

        registered_services = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line.startswith("[+]"):
                domain = line.replace("[+]", "").strip()
                if "Email used" not in domain and "websites checked" not in domain and "Rate limit" not in domain:
                    registered_services.append(domain)

        return registered_services
    except Exception:
        return []

def check_maigret_single_user(username):
    try:
        local_exe = os.path.join(os.getcwd(), "env", "Scripts", "maigret.exe")
        maigret_cmd = local_exe if os.path.exists(local_exe) else (shutil.which("maigret") or "maigret")

        cmd = [maigret_cmd, username, "--top-sites", "100", "--no-progressbar", "--no-check-updates", "--timeout", "8"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
        
        profiles = []
        for line in (result.stdout or "").splitlines():
            if "[+]" in line and "http" in line:
                parts = line.strip().split("http")
                if len(parts) > 1:
                    profiles.append("http" + parts[1].strip())
        return profiles
    except Exception:
        return []

def check_stealer_log_sync(email):
    url = f"https://cavalier.hudsonrock.com/api/v1/osint-tools/search-by-email?email={email}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if res.status_code == 200:
            data = res.json()
            return {
                "status": "COMPROMISED",
                "stealer_logs_count": data.get("stealer_logs_count", 0),
                "compromised_passwords": data.get("passwords_count", 0)
            }
        return {"status": "CLEAN", "message": "No stealer log infection found."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_public_breaches_sync(email):
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if res.status_code == 200:
            data = res.json()
            if "breaches" in data:
                breaches = data["breaches"]
                detailed = breaches[0] if isinstance(breaches, list) and len(breaches) > 0 else breaches
                return {"status": "BREACHED", "total_breaches": len(detailed) if isinstance(detailed, list) else 1, "exposed_in": detailed}
        return {"status": "CLEAN", "total_breaches": 0, "exposed_in": []}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# ==========================================
# ADVANCED BREACH ENGINES (Leak-Lookup & DeHashed)
# ==========================================
def check_leak_lookup_sync(username):
    """Mengecek database kebocoran data berdasarkan USERNAME via Leak-Lookup API."""
    if not LEAK_LOOKUP_API_KEY:
        return {"status": "SKIPPED", "message": "API Key Leak-Lookup belum diisi."}
    
    url = "https://leak-lookup.com/api/search"
    payload = {"key": LEAK_LOOKUP_API_KEY, "type": "username", "query": username}
    try:
        res = requests.post(url, data=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if not data.get("error"):
                databases = list(data.get("message", {}).keys())
                return {"status": "BREACHED", "total": len(databases), "leaked_databases": databases}
        return {"status": "CLEAN", "total": 0, "leaked_databases": []}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_dehashed_sync(query, query_type="email"):
    """Mengecek database kebocoran data mendalam via DeHashed API (Email/Username)."""
    if not DEHASHED_EMAIL or not DEHASHED_API_KEY:
        return {"status": "SKIPPED", "message": "Credentials DeHashed (Email/API Key) belum diisi."}
    
    url = f"https://api.dehashed.com/search?query={query_type}:{query}"
    headers = {"Accept": "application/json"}
    try:
        res = requests.get(url, auth=(DEHASHED_EMAIL, DEHASHED_API_KEY), headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            entries = data.get("entries", [])
            sources = list(set([entry.get("database_name") for entry in entries if entry.get("database_name")])) if entries else []
            return {
                "status": "BREACHED" if data.get("total", 0) > 0 else "CLEAN",
                "total_records": data.get("total", 0),
                "leaked_sources": sources
            }
        return {"status": "API_ERROR", "code": res.status_code}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# ==========================================
# ASYNC PIPELINE EXECUTOR
# ==========================================
async def run_full_scan_async(email, aliases):
    print("\n====================================================")
    print("   UBA ADVANCED THREAT & BREACH INTELLIGENCE ENGINE ")
    print("====================================================")
    print(f"[*] Target Email    : {email}")
    print(f"[*] Target Aliases  : {', '.join(aliases)}")
    print(f"[*] Executing Multi-Vector OSINT Scan...\n")

    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # Footprint Scanning Tasks
        task_holehe = loop.run_in_executor(pool, check_holehe_sync, email)
        maigret_tasks = [loop.run_in_executor(pool, check_maigret_single_user, alias) for alias in aliases]
        
        # Threat & Breach Scanning Tasks
        task_stealer = loop.run_in_executor(pool, check_stealer_log_sync, email)
        task_breach_public = loop.run_in_executor(pool, check_public_breaches_sync, email)
        
        # Premium Breach Lookup Tasks
        leak_lookup_tasks = [loop.run_in_executor(pool, check_leak_lookup_sync, alias) for alias in aliases]
        task_dehashed_email = loop.run_in_executor(pool, check_dehashed_sync, email, "email")

        # Gathering Async Tasks
        holehe_res = await task_holehe
        maigret_results = await asyncio.gather(*maigret_tasks)
        stealer_res = await task_stealer
        breach_pub_res = await task_breach_public
        leak_lookup_results = await asyncio.gather(*leak_lookup_tasks)
        dehashed_res = await task_dehashed_email

    # Flatten Maigret Results
    all_profiles = []
    for res in maigret_results:
        all_profiles.extend(res)

    # Format Username Breach Results
    username_breaches = {}
    for idx, alias in enumerate(aliases):
        username_breaches[alias] = leak_lookup_results[idx]

    return {
        "target_email": email,
        "scanned_aliases": aliases,
        "results": {
            "account_enumeration": {
                "email_registered_sites": {"total": len(holehe_res), "sites": holehe_res},
                "username_profiles_found": {"total_found": len(all_profiles), "urls": all_profiles}
            },
            "malware_stealer_threat": stealer_res,
            "data_breach_intelligence": {
                "email_public_breaches": breach_pub_res,
                "email_dehashed_breaches": dehashed_res,
                "username_leak_lookup_breaches": username_breaches
            }
        }
    }

if __name__ == "__main__":
    email_input = input("Masukkan Email Target: ").strip()
    alias_input = input("Masukkan Alias Username (pisahkan koma, misal: danuarasmoro, danuar_a): ").strip()
    
    aliases = [a.strip() for a in alias_input.split(",") if a.strip()] if alias_input else [email_input.split("@")[0]]
    
    if email_input:
        output = asyncio.run(run_full_scan_async(email_input, aliases))
        print("\n================--- [ INTEGRATED OSINT REPORT ] ---================")
        print(json.dumps(output, indent=4))
        print("==================================================================")