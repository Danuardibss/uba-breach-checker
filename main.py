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

def run_crawlee_scraper_sync(target_keyword):
    """
    Module 3: Real-Time Web & OSINT Scraper via Crawlee (Playwright Engine)
    """
    try:
        # Panggil node script crawlee_scraper.mjs
        process = subprocess.run(
            ["node", "crawlee_scraper.mjs", target_keyword],
            capture_output=True,
            text=True,
            timeout=50
        )
        
        output_str = process.stdout.strip()
        
        # Ambil baris JSON terakhir dari stdout Node.js
        json_line = [line for line in output_str.split('\n') if line.startswith('[')]
        
        if json_line:
            parsed_data = json.loads(json_line[-1])
            return {
                "status": "SUCCESS",
                "total_results": len(parsed_data),
                "crawled_data": parsed_data
            }
        else:
            return {
                "status": "EMPTY_OR_BLOCKED",
                "total_results": 0,
                "crawled_data": []
            }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Crawlee Execution Error: {str(e)}"
        }

async def run_full_scan_async(email):
    """
    Async Engine: Menjalankan Holehe, Hudson Rock API, dan Crawlee Scraper secara PARALEL.
    """
    print("====================================================")
    print("   UBA OSINT, DARKWEB & CRAWLEE ENGINE (DANU)       ")
    print("====================================================")
    print(f"[*] Executing 3-Way Parallel Async Engine for: {email}...")

    loop = asyncio.get_running_loop()
    
    # Menjalankan KETIGA modul secara serentak di ThreadPool
    with concurrent.futures.ThreadPoolExecutor() as pool:
        task_footprint = loop.run_in_executor(pool, check_holehe_sync, email)
        task_breach = loop.run_in_executor(pool, check_stealer_log_and_breach_sync, email)
        task_crawlee = loop.run_in_executor(pool, run_crawlee_scraper_sync, email)
        
        # Nunggu ketiga modul beres barengan
        footprint_res, breach_res, crawlee_res = await asyncio.gather(
            task_footprint, task_breach, task_crawlee
        )

    return {
        "target_email": email,
        "footprint_raw": footprint_res,
        "stealer_and_breach_data": breach_res,
        "crawlee_osint_scraped_data": crawlee_res
    }

def run_full_scan(email):
    """
    Fungsi Synchronous wrapper biar gampang dipanggil dari luar (main.run_full_scan(email)).
    """
    return asyncio.run(run_full_scan_async(email))

if __name__ == "__main__":
    target = input("\nMasukkan email target: ").strip()
    if target:
        results = run_full_scan(target)
        
        print("\n================--- [ FINAL INTEGRATED RESULT ] ---================")
        print("\n--- [1. FOOTPRINT - HOLEHE] ---")
        print(results["footprint_raw"])
        
        print("\n--- [2. STEALER LOG & BREACH DATA] ---")
        print(json.dumps(results["stealer_and_breach_data"], indent=4))
        
        print("\n--- [3. CRAWLEE OSINT LIVE SCRAPER DATA] ---")
        print(json.dumps(results["crawlee_osint_scraped_data"], indent=4))
        print("\n==================================================================")