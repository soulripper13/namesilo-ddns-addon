# NameSilo DDNS Add-on

This Home Assistant add-on provides Dynamic DNS updates for NameSilo. It supports both IPv4 and IPv6.

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
