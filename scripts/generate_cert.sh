#!/usr/bin/env sh
# Generate a local self-signed certificate for Jarvis HTTPS.

set -eu

mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=jarvis.local"
