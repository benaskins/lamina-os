#!/bin/bash

# Export the client certificate and key to PKCS12 format
openssl pkcs12 -export \
    -in client/client.crt \
    -inkey client/client.key \
    -out client/client.p12 \
    -name "LaminaClient" \
    -passout pass:laminadev

echo "Exported client.p12 with password: laminadev"
echo "Copy this file to your iOS project and update the password in CertificateManager.swift"
