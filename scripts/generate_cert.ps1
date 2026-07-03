# Generate a local self-signed certificate for Jarvis HTTPS.

New-Item -ItemType Directory -Force -Path certs | Out-Null
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=jarvis.local"
