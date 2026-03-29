import json
import os
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

OPTIONS_FILE = "/data/options.json"

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)

def get_public_ip(ipv6=False):
    url = "https://api6.ipify.org" if ipv6 else "https://api.ipify.org"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8").strip()
    except Exception as e:
        log(f"Error fetching {'IPv6' if ipv6 else 'IPv4'}: {e}")
        return None

def namesilo_request(operation, api_key, params):
    base_url = f"https://www.namesilo.com/api/{operation}?version=1&type=xml&key={api_key}"
    for k, v in params.items():
        base_url += f"&{k}={v}"
    
    try:
        with urllib.request.urlopen(base_url, timeout=15) as response:
            content = response.read().decode("utf-8")
            return ET.fromstring(content)
    except urllib.error.URLError as e:
        log(f"Network error calling NameSilo ({operation}): {e}")
        return None
    except ET.ParseError as e:
        log(f"Error parsing NameSilo response ({operation}): {e}")
        return None
    except Exception as e:
        log(f"Unexpected error calling NameSilo ({operation}): {e}")
        return None

def update_dns():
    if not os.path.exists(OPTIONS_FILE):
        log(f"Config file not found: {OPTIONS_FILE}")
        return

    try:
        with open(OPTIONS_FILE, "r") as f:
            options = json.load(f)
    except Exception as e:
        log(f"Error reading options: {e}")
        return

    api_key = options.get("api_key")
    domain = options.get("domain")
    hosts = options.get("hosts", ["@"])
    update_ipv4 = options.get("update_ipv4", True)
    update_ipv6 = options.get("update_ipv6", False)
    
    if not api_key or not domain:
        log("API Key or Domain missing in config. Please set them in the add-on configuration.")
        return

    # Fetch records once
    root = namesilo_request("dnsListRecords", api_key, {"domain": domain})
    if root is None:
        return

    code_el = root.find(".//code")
    if code_el is not None and code_el.text != "300":
        detail_el = root.find(".//detail")
        log(f"API Error (List): {detail_el.text if detail_el is not None else 'Unknown error'} (Code: {code_el.text})")
        return

    records = root.findall(".//resource_record")
    
    current_ipv4 = get_public_ip(False) if update_ipv4 else None
    current_ipv6 = get_public_ip(True) if update_ipv6 else None

    for host in hosts:
        full_host = domain if host == "@" else f"{host}.{domain}"
        
        # IPv4
        if update_ipv4 and current_ipv4:
            found = False
            for r in records:
                try:
                    r_host = r.find("host").text
                    r_type = r.find("type").text
                    r_id = r.find("record_id").text
                    r_value = r.find("value").text

                    if r_host == full_host and r_type == "A":
                        found = True
                        if r_value != current_ipv4:
                            log(f"Updating {full_host} (A) from {r_value} to {current_ipv4}")
                            update_params = {
                                "domain": domain,
                                "rrid": r_id,
                                "rrhost": "" if host == "@" else host,
                                "rrvalue": current_ipv4,
                                "rrttl": "3600"
                            }
                            res = namesilo_request("dnsUpdateRecord", api_key, update_params)
                            if res is not None:
                                res_code_el = res.find(".//code")
                                if res_code_el is not None and res_code_el.text == "300":
                                    log(f"Successfully updated {full_host} (A)")
                                else:
                                    res_detail_el = res.find(".//detail")
                                    log(f"Failed to update {full_host} (A): {res_detail_el.text if res_detail_el is not None else 'Unknown error'}")
                        else:
                            log(f"{full_host} (A) is already up to date ({current_ipv4})")
                        break
                except AttributeError:
                    continue
            if not found:
                log(f"Record for {full_host} (A) not found in NameSilo for domain {domain}. Please create it manually.")

        # IPv6
        if update_ipv6 and current_ipv6:
            found = False
            for r in records:
                try:
                    r_host = r.find("host").text
                    r_type = r.find("type").text
                    r_id = r.find("record_id").text
                    r_value = r.find("value").text

                    if r_host == full_host and r_type == "AAAA":
                        found = True
                        if r_value != current_ipv6:
                            log(f"Updating {full_host} (AAAA) from {r_value} to {current_ipv6}")
                            update_params = {
                                "domain": domain,
                                "rrid": r_id,
                                "rrhost": "" if host == "@" else host,
                                "rrvalue": current_ipv6,
                                "rrttl": "3600"
                            }
                            res = namesilo_request("dnsUpdateRecord", api_key, update_params)
                            if res is not None:
                                res_code_el = res.find(".//code")
                                if res_code_el is not None and res_code_el.text == "300":
                                    log(f"Successfully updated {full_host} (AAAA)")
                                else:
                                    res_detail_el = res.find(".//detail")
                                    log(f"Failed to update {full_host} (AAAA): {res_detail_el.text if res_detail_el is not None else 'Unknown error'}")
                        else:
                            log(f"{full_host} (AAAA) is already up to date ({current_ipv6})")
                        break
                except AttributeError:
                    continue
            if not found:
                log(f"Record for {full_host} (AAAA) not found in NameSilo for domain {domain}. Please create it manually.")

def main():
    log("NameSilo DDNS starting...")
    while True:
        try:
            update_dns()
        except Exception as e:
            log(f"Unhandled exception in loop: {e}")
        
        # Load check interval from config
        interval = 300
        try:
            if os.path.exists(OPTIONS_FILE):
                with open(OPTIONS_FILE, "r") as f:
                    options = json.load(f)
                    interval = options.get("check_interval", 300)
        except:
            pass
        
        log(f"Waiting {interval} seconds...")
        time.sleep(max(60, interval))

if __name__ == "__main__":
    main()
