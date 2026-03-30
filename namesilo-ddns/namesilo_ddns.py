import json
import os
import time
import socket
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

OPTIONS_FILE = "/data/options.json"
_orig_getaddrinfo = socket.getaddrinfo

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)

def get_public_ip(ipv6=False, custom_url=None):
    url = custom_url if custom_url else ("https://ipv6.icanhazip.com" if ipv6 else "https://ipv4.icanhazip.com")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8").strip()
    except Exception as e:
        log(f"Error fetching {'IPv6' if ipv6 else 'IPv4'} from {url}: {e}")
        return None

def namesilo_request(operation, api_key, params):
    base_url = f"https://www.namesilo.com/api/{operation}?version=1&type=xml&key={api_key}"
    for k, v in params.items():
        base_url += f"&{k}={v}"

    # NameSilo API requires IPv4; temporarily force it
    socket.getaddrinfo = lambda host, port, family=0, type=0, proto=0, flags=0: \
        _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
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
    finally:
        socket.getaddrinfo = _orig_getaddrinfo

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
    hosts_config = options.get("hosts", [])
    
    if not api_key or not domain:
        log("API Key or Domain missing in config. Please set them in the add-on configuration.")
        return

    if not hosts_config:
        log("No hosts configured. Please add at least one host in the configuration.")
        return

    # Fetch existing records from NameSilo once
    root = namesilo_request("dnsListRecords", api_key, {"domain": domain})
    if root is None:
        return

    code_el = root.find(".//code")
    if code_el is not None and code_el.text != "300":
        detail_el = root.find(".//detail")
        log(f"API Error (List): {detail_el.text if detail_el is not None else 'Unknown error'} (Code: {code_el.text})")
        return

    records = root.findall(".//resource_record")
    
    for config in hosts_config:
        host = config.get("host", "@")
        full_host = domain if host == "@" else f"{host}.{domain}"
        update_ipv4 = config.get("update_ipv4", False)
        update_ipv6 = config.get("update_ipv6", True) # Default to true for your case
        ipv4_url = config.get("ipv4_url")
        ipv6_url = config.get("ipv6_url")

        # Process IPv4
        if update_ipv4:
            current_ipv4 = get_public_ip(False, ipv4_url)
            if current_ipv4:
                found = False
                for r in records:
                    try:
                        if r.find("host").text == full_host and r.find("type").text == "A":
                            found = True
                            if r.find("value").text != current_ipv4:
                                log(f"Updating {full_host} (A) from {r.find('value').text} to {current_ipv4}")
                                update_params = {
                                    "domain": domain,
                                    "rrid": r.find("record_id").text,
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
                    except AttributeError: continue
                if not found:
                    log(f"Record {full_host} (A) not found in NameSilo. Please create it manually.")

        # Process IPv6
        if update_ipv6:
            current_ipv6 = get_public_ip(True, ipv6_url)
            if current_ipv6:
                found = False
                for r in records:
                    try:
                        if r.find("host").text == full_host and r.find("type").text == "AAAA":
                            found = True
                            if r.find("value").text != current_ipv6:
                                log(f"Updating {full_host} (AAAA) from {r.find('value').text} to {current_ipv6}")
                                update_params = {
                                    "domain": domain,
                                    "rrid": r.find("record_id").text,
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
                    except AttributeError: continue
                if not found:
                    log(f"Record {full_host} (AAAA) not found in NameSilo. Please create it manually.")

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
