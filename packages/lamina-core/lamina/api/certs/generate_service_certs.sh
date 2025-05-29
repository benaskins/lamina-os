#!/bin/bash

# Enhanced certificate generation for service mesh mTLS
# This script generates certificates for each service in the infrastructure

set -e

SERVICES=("assistant" "researcher" "guardian" "ollama" "loki" "grafana" "vector" "nginx" "chromadb")
CERT_DIR="$(dirname "$0")"
CA_DIR="$CERT_DIR/ca"
SERVICES_DIR="$CERT_DIR/services"

echo "Generating service certificates for mTLS..."

# Create services directory
mkdir -p "$SERVICES_DIR"

# Check if CA exists, if not generate it
if [[ ! -f "$CA_DIR/ca.crt" || ! -f "$CA_DIR/ca.key" ]]; then
    echo "CA certificates not found. Generating CA first..."
    mkdir -p "$CA_DIR"
    
    # Generate CA private key and certificate
    openssl genpkey -algorithm RSA -out "$CA_DIR/ca.key"
    openssl req -x509 -new -nodes -key "$CA_DIR/ca.key" -sha256 -days 1825 -out "$CA_DIR/ca.crt" \
        -subj "/C=US/ST=CA/L=San Francisco/O=Lamina/OU=CA/CN=Lamina Root CA"
    
    chmod 600 "$CA_DIR/ca.key"
    chmod 644 "$CA_DIR/ca.crt"
    echo "CA certificates generated."
fi

# Generate certificates for each service
for service in "${SERVICES[@]}"; do
    echo "Generating certificates for service: $service"
    
    SERVICE_DIR="$SERVICES_DIR/$service"
    mkdir -p "$SERVICE_DIR"
    
    # Generate service private key
    openssl genpkey -algorithm RSA -out "$SERVICE_DIR/$service.key"
    
    # Generate service CSR with appropriate subject and SAN
    case $service in
        "clara")
            SAN="DNS:clara,DNS:localhost,IP:127.0.0.1"
            CN="clara"
            ;;
        "luna")
            SAN="DNS:luna,DNS:localhost,IP:127.0.0.1"
            CN="luna"
            ;;
        "phi")
            SAN="DNS:phi,DNS:localhost,IP:127.0.0.1"
            CN="phi"
            ;;
        "ollama")
            SAN="DNS:ollama,DNS:localhost,IP:127.0.0.1"
            CN="ollama"
            ;;
        "loki")
            SAN="DNS:loki,DNS:localhost,IP:127.0.0.1"
            CN="loki"
            ;;
        "grafana")
            SAN="DNS:grafana,DNS:localhost,IP:127.0.0.1"
            CN="grafana"
            ;;
        "vector")
            SAN="DNS:vector,DNS:localhost,IP:127.0.0.1"
            CN="vector"
            ;;
        "nginx")
            SAN="DNS:nginx,DNS:localhost,DNS:proxy,IP:127.0.0.1"
            CN="nginx"
            ;;
    esac
    
    openssl req -new -key "$SERVICE_DIR/$service.key" -out "$SERVICE_DIR/$service.csr" \
        -subj "/C=US/ST=CA/L=San Francisco/O=Lamina/OU=Services/CN=$CN"
    
    # Sign service certificate with CA
    openssl x509 -req -in "$SERVICE_DIR/$service.csr" -CA "$CA_DIR/ca.crt" -CAkey "$CA_DIR/ca.key" -CAcreateserial \
        -out "$SERVICE_DIR/$service.crt" -days 825 -sha256 \
        -extfile <(printf "subjectAltName=$SAN\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth")
    
    # Clean up CSR
    rm "$SERVICE_DIR/$service.csr"
    
    # Set appropriate permissions
    chmod 600 "$SERVICE_DIR/$service.key"
    chmod 644 "$SERVICE_DIR/$service.crt"
    
    echo "✓ Certificates generated for $service"
done

# Copy CA certificate to each service directory for easy access
for service in "${SERVICES[@]}"; do
    cp "$CA_DIR/ca.crt" "$SERVICES_DIR/$service/"
done

echo ""
echo "🔐 Service certificates generated successfully!"
echo ""
echo "Certificate structure:"
echo "├── ca/"
echo "│   ├── ca.crt (Root CA certificate)"
echo "│   └── ca.key (Root CA private key)"
echo "└── services/"
for service in "${SERVICES[@]}"; do
    echo "    ├── $service/"
    echo "    │   ├── $service.crt (Service certificate)"
    echo "    │   ├── $service.key (Service private key)"
    echo "    │   └── ca.crt (CA certificate copy)"
done
echo ""
echo "Next steps:"
echo "1. Each service should use its own certificate for server authentication"
echo "2. Each service should use its certificate as client cert when making requests"
echo "3. All services should trust the CA certificate for validation"
echo "4. Configure nginx to enforce mTLS for all service-to-service communication" 