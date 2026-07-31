import subprocess
import json
import requests
import os

def check_holehe(email):
    """
    Module 1: Social Media Account Footprint Enumeration (Holehe)
    """
    print(f"\n[*] 1. Running Holehe Footprint for: {email}...")
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

def check_stealer_log_and_breach(email):
    """
    Module 2: Enhanced Stealer Log & Data Breach Analysis (Hudson Rock OSINT API)
    """
    print(f"\n[*] 2. Enhancing Data Breach & Stealer Log Check for: {email}...")
    
    # --- MOCK DATA UNTUK TESTING AKURASI SCRIPT ---
    if email.lower() == "test@gmail.com":
        print("    [DEBUG] Running Mock Breach Test Mode...")
        return {
            "status": "COMPROMISED",
            "is_breached": True,
            "summary": {
                "stealer_logs_found": 12,
                "compromised_passwords": 34,
                "malware_family": "RedLine Stealer / Lumma",
                "top_domains_leaked": ["facebook.com", "binance.com", "netlfix.com"]
            },
            "raw_details": {
                "stealer_id": "ST-994812",
                "computer_name": "DESKTOP-VICTIM-01",
                "operating_system": "Windows 10 Pro"
            }
        }
    # ----------------------------------------------

    url = f"https://cavalier.hudsonrock.com/api/v1/osint-tools/search-by-email?email={email}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        
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

def run_full_scan(email):
    print("====================================================")
    print("   UBA OSINT & DATA BREACH CHECKER MODULE (DANU)   ")
    print("====================================================")
    
    footprint_res = check_holehe(email)
    breach_res = check_stealer_log_and_breach(email)
    
    return {
        "target_email": email,
        "footprint_raw": footprint_res,
        "stealer_and_breach_data": breach_res
    }

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