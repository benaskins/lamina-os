#!/bin/bash

# Create directories
mkdir -p {ca,server,client}

# Generate CA private key and certificate
openssl genpkey -algorithm RSA -out ca/ca.key
openssl req -x509 -new -nodes -key ca/ca.key -sha256 -days 1825 -out ca/ca.crt \
    -subj "/C=US/ST=CA/L=San Francisco/O=Lamina/OU=CA/CN=Lamina Root CA"

# Generate server private key and CSR
openssl genpkey -algorithm RSA -out server/server.key
openssl req -new -key server/server.key -out server/server.csr \
    -subj "/C=US/ST=CA/L=San Francisco/O=Lamina/OU=Server/CN=localhost"

# Sign server certificate with CA
openssl x509 -req -in server/server.csr -CA ca/ca.crt -CAkey ca/ca.key -CAcreateserial \
    -out server/server.crt -days 825 -sha256 \
    -extfile <(printf "subjectAltName=DNS:localhost,IP:127.0.0.1")

# Generate client private key and CSR
openssl genpkey -algorithm RSA -out client/client.key
openssl req -new -key client/client.key -out client/client.csr \
    -subj "/C=US/ST=CA/L=San Francisco/O=Lamina/OU=Client/CN=LaminaClient"

# Sign client certificate with CA
openssl x509 -req -in client/client.csr -CA ca/ca.crt -CAkey ca/ca.key -CAcreateserial \
    -out client/client.crt -days 825 -sha256

# Clean up CSR files
rm server/server.csr client/client.csr

# Set appropriate permissions
chmod 600 {ca,server,client}/*.key
chmod 644 {ca,server,client}/*.crt

echo "Certificates generated successfully!"
echo "Remember to:"
echo "1. Keep the CA private key (ca/ca.key) secure"
echo "2. Distribute ca/ca.crt to both server and client"
echo "3. Use server/server.key and server/server.crt on the server"
echo "4. Use client/client.key and client/client.crt on the client"
