# NameSilo DDNS Add-on
[![Support Development](https://img.shields.io/badge/Support-Development-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/soulripper13)

<div align="center">
  <img src="https://dummyimage.com/800x60/0d1117/ffffff&text=NameSilo%20DDNS%20Add-on+-+-%20Update%20IPv4%20%28A%20record%29%20and%20IPv6%20%28AAAA%20record%29." alt="Hero Banner">
  <br><br>
  <strong>- Update IPv4 (A record) and IPv6 (AAAA record).</strong> 
  <br><br> 
  <a href="https://ko-fi.com/soulripper13">
    <img src="https://storage.ko-fi.com/cdn/kofi5.png?v=6" alt="Support NameSilo DDNS Add-on on Ko-fi" width="220">
  </a>
</div>

---

## Features
- Update IPv4 (A record) and IPv6 (AAAA record).
- Supports multiple hostnames (subdomains).
- Configurable check interval.
- Fully local and secure.
## Configuration
Example configuration:
```yaml
api_key: "your_namesilo_api_key"
domain: "example.com"
hosts:
  - "@"
  - "www"
update_ipv4: true
update_ipv6: false
check_interval: 300
```
- `api_key`: Your NameSilo API Key.
- `domain`: Your domain name (e.g., `example.com`).
- `hosts`: A list of hostnames to update. Use `@` for the root domain.
- `update_ipv4`: Set to `true` to update A records.
- `update_ipv6`: Set to `true` to update AAAA records.
- `check_interval`: How often to check for IP changes (in seconds). Minimum is 60.
## Note
The records must already exist in NameSilo. This add-on does not create new records.
Make sure your IP is whitelisted in NameSilo API settings (or leave it blank to allow all IPs).

---
## Support the Project

This project is developed and maintained in spare time and is provided free to the community.

If you find it useful and would like to support ongoing development, maintenance, and improvements, any contribution is appreciated — but never required ❤️

### Ways to Support

* **Ko-fi**
  [https://ko-fi.com/soulripper13](https://ko-fi.com/soulripper13)

* **PayPal**
  [https://paypal.me/SKatoaroo](https://paypal.me/SKatoaroo)

* **Bitcoin (BTC)**
  `bc1qvu8a9gdy3dcxa94jge7d3rd7claapsydjsjxn0`

* **Solana (SOL)**
  `4jvCR2YFQLqguoyz9qAMPzVbaEcDsG5nzRHFG8SeaeBK`

You can also help by:

* Reporting bugs
* Submitting pull requests
* Suggesting features
* Helping other users
* Starring the repository ⭐

Thank you for being part of the community.
