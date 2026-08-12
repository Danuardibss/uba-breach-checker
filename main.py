import subprocess
import json
import os
import asyncio
import concurrent.futures
import requests

def check_holehe_sync(email):
    """
    Module 1: Social Media Account Footprint Enumeration (Holehe)
    """
    try:
        bat_path = os.path.join(os.getcwd(), "holehe.bat")
        
        if os.path.exists(bat_path):
            cmd = [bat_path, email, "--only-used"]
        else:
            cmd = [r"env\Scripts\holehe.exe", email, "--only-used"]

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip() if result.stdout else "No account found or Rate Limited."
    except Exception as e:
        return f"Error executing Holehe: {str(e)}"

def check_stealer_log_and_breach_sync(email):
    """
    Module 2: Enhanced Stealer Log & Data Breach Analysis (Hudson Rock OSINT API Live)
    """
    url = f"https://cavalier.hudsonrock.com/api/v1/osint-tools/search-by-email?email={email}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            raw_data = response.json()
            return {
                "status": "COMPROMISED",
                "is_breached": True,
                "summary": {
                    "stealer_logs_found": raw_data.get("stealer_logs_count", 1),
                    "compromised_passwords": raw_data.get("passwords_count", 0)
                },
                "raw_details": raw_data
            }
        elif response.status_code == 404:
            return {
                "status": "CLEAN",
                "is_breached": False,
                "message": "Tidak ditemukan riwayat Stealer Log / Malware Compromise pada email target."
            }
        else:
            return {
                "status": "ERROR",
                "message": f"API Error Code: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Connection/Script Error: {str(e)}"
        }

async def run_full_scan_async(email):
    """
    Async Wrapper: Menjalankan Holehe dan Hudson Rock API secara PARALEL untuk efisiensi kecepatan.
    """
    print("====================================================")
    print("   UBA OSINT & DATA BREACH CHECKER MODULE (DANU)   ")
    print("====================================================")
    print(f"[*] Starting Parallel Async Scan for: {email}...")

    loop = asyncio.get_running_loop()
    
    # Menjalankan kedua modul secara serentak di ThreadPool terpisah
    with concurrent.futures.ThreadPoolExecutor() as pool:
        task_footprint = loop.run_in_executor(pool, check_holehe_sync, email)
        task_breach = loop.run_in_executor(pool, check_stealer_log_and_breach_sync, email)
        
        # Nunggu kedua task selesai barengan
        footprint_res, breach_res = await asyncio.gather(task_footprint, task_breach)

    return {
        "target_email": email,
        "footprint_raw": footprint_res,
        "stealer_and_breach_data": breach_res
    }

def run_full_scan(email):
    """
    Fungsi Synchronous wrapper biar Fahri & Adema gampang panggilnya (main.run_full_scan(email)).
    """
    return asyncio.run(run_full_scan_async(email))

if __name__ == "__main__":
    target = input("\nMasukkan email target: ").strip()
    if target:
        results = run_full_scan(target)
        
        print("\n================--- [ FINAL RESULT ] ---================")
        print("\n--- [FOOTPRINT - HOLEHE] ---")
        print(results["footprint_raw"])
        
        print("\n--- [STEALER LOG & BREACH DATA] ---")
        print(json.dumps(results["stealer_and_breach_data"], indent=4))
        print("\n========================================================")