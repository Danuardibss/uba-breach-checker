import subprocess
import json
import os
import asyncio
import concurrent.futures
import requests

def check_holehe_sync(email):
    """
    Module 1: Social Media Account Footprint Enumeration (Holehe)
    Di-parse otomatis agar menghasilkan list akun terdaftar secara bersih.
    """
    try:
        bat_path = os.path.join(os.getcwd(), "holehe.bat")
        if os.path.exists(bat_path):
            cmd = [bat_path, email, "--only-used"]
        else:
            cmd = [r"env\Scripts\holehe.exe", email, "--only-used"]

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        raw_output = result.stdout.strip() if result.stdout else ""

        # Parser otomatis untuk mengambil domain yang berstatus [+] (Registered)
        registered_services = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line.startswith("[+]"):
                domain = line.replace("[+]", "").strip()
                registered_services.append(domain)

        return {
            "total_registered": len(registered_services),
            "registered_accounts": registered_services
        }
    except Exception as e:
        return {"total_registered": 0, "registered_accounts": [], "error": str(e)}

def check_stealer_log_sync(email):
    """
    Module 2: Stealer Log & Malware Hijack Check (Hudson Rock API)
    """
    url = f"https://cavalier.hudsonrock.com/api/v1/osint-tools/search-by-email?email={email}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            raw_data = response.json()
            return {
                "status": "MALWARE_COMPROMISED",
                "is_breached": True,
                "stealer_logs_count": raw_data.get("stealer_logs_count", 1),
                "compromised_passwords": raw_data.get("passwords_count", 0),
                "details": raw_data
            }
        elif response.status_code == 404:
            return {
                "status": "CLEAN",
                "is_breached": False,
                "message": "Tidak terdeteksi indikator infeksi Trojan/Stealer Malware."
            }
        else:
            return {"status": "API_ERROR", "code": response.status_code}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_public_breaches_sync(email):
    """
    Module 3: Direct Data Breach Lookup (XposedOrNot Public API)
    """
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if "Error" not in data and "breaches" in data:
                breach_data = data["breaches"]
                
                if isinstance(breach_data, list) and len(breach_data) > 0:
                    detailed_breaches = breach_data[0] if isinstance(breach_data[0], list) else breach_data
                else:
                    detailed_breaches = breach_data

                return {
                    "status": "BREACHED",
                    "total_breaches": len(detailed_breaches) if isinstance(detailed_breaches, list) else 1,
                    "exposed_in_databases": detailed_breaches
                }
        return {
            "status": "CLEAN",
            "total_breaches": 0,
            "message": "Email tidak terdaftar pada riwayat kebocoran data publik."
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

async def run_full_scan_async(email):
    """
    Async Engine: Menjalankan 3 Modul secara Paralel
    """
    print("====================================================")
    print("   UBA OSINT & DATA BREACH MONITORING ENGINE        ")
    print("====================================================")
    print(f"[*] Starting 3-Way Async Parallel Scan for: {email}...\n")

    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        task_footprint = loop.run_in_executor(pool, check_holehe_sync, email)
        task_stealer = loop.run_in_executor(pool, check_stealer_log_sync, email)
        task_breach = loop.run_in_executor(pool, check_public_breaches_sync, email)
        
        footprint_res, stealer_res, breach_res = await asyncio.gather(
            task_footprint, task_stealer, task_breach
        )

    return {
        "target_email": email,
        "registered_social_accounts": footprint_res,
        "stealer_log_data": stealer_res,
        "public_breach_data": breach_res
    }

def run_full_scan(email):
    return asyncio.run(run_full_scan_async(email))

if __name__ == "__main__":
    target = input("Masukkan email target: ").strip()
    if target:
        results = run_full_scan(target)
        
        print("\n================--- [ FINAL INTEGRATED RESULT ] ---================")
        print("\n--- [1. FOOTPRINT ACCOUNTS FOUND] ---")
        print(json.dumps(results["registered_social_accounts"], indent=4))
        
        print("\n--- [2. STEALER LOG & MALWARE COMPROMISE] ---")
        print(json.dumps(results["stealer_log_data"], indent=4))
        
        print("\n--- [3. REAL DATA BREACH EXPOSURE] ---")
        print(json.dumps(results["public_breach_data"], indent=4))
        print("\n==================================================================")