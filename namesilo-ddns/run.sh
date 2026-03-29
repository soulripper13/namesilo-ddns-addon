#!/usr/bin/with-contenv bashio

bashio::log.info "Starting NameSilo DDNS Add-on..."

# Start the python script
python3 /namesilo_ddns.py
