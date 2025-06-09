#!/bin/bash
# Test network setup for accessing k3s LoadBalancer services from macOS host

set -euo pipefail

echo "=== Testing k3s LoadBalancer Network Access ==="

# Check if we can reach k3s node from host
echo "1. Testing k3s node connectivity..."
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo "   k3s node IP: $NODE_IP"

# Test if node is reachable from host
if ping -c 1 "$NODE_IP" >/dev/null 2>&1; then
    echo "   ✓ k3s node is reachable from host"
    NODE_REACHABLE=true
else
    echo "   ✗ k3s node is NOT reachable from host"
    NODE_REACHABLE=false
fi

# Check LoadBalancer service
echo ""
echo "2. Testing LoadBalancer service..."
LB_IP=$(kubectl get svc istio-ingressgateway -n istio-gateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "   LoadBalancer IP: $LB_IP"

if [ "$NODE_REACHABLE" = true ]; then
    echo "   Testing LoadBalancer IP accessibility..."
    if curl -m 5 -s "http://$LB_IP/health" -H "Host: llm.lamina.local"; then
        echo "   ✓ LoadBalancer is accessible via cluster IP"
    else
        echo "   ✗ LoadBalancer is NOT accessible via cluster IP"
    fi
fi

# Check NodePort accessibility
echo ""
echo "3. Testing NodePort accessibility..."
NODE_PORT=$(kubectl get svc istio-ingressgateway -n istio-gateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
echo "   NodePort: $NODE_PORT"

if [ "$NODE_REACHABLE" = true ]; then
    echo "   Testing NodePort via node IP..."
    if curl -m 5 -s "http://$NODE_IP:$NODE_PORT/health" -H "Host: llm.lamina.local"; then
        echo "   ✓ NodePort is accessible via node IP"
        echo ""
        echo "SOLUTION: Use $NODE_IP:$NODE_PORT or configure port forwarding"
        echo "Your /etc/hosts should have: $NODE_IP llm.lamina.local"
        echo "Access via: http://llm.lamina.local:$NODE_PORT/health"
    else
        echo "   ✗ NodePort is NOT accessible via node IP"
    fi
fi

# Test localhost NodePort (if Colima forwards it)
echo ""
echo "4. Testing localhost NodePort..."
if curl -m 5 -s "http://localhost:$NODE_PORT/health" -H "Host: llm.lamina.local"; then
    echo "   ✓ NodePort is accessible via localhost"
    echo ""
    echo "SOLUTION: Use localhost with NodePort"
    echo "Your /etc/hosts should have: 127.0.0.1 llm.lamina.local"
    echo "Access via: http://llm.lamina.local:$NODE_PORT/health"
else
    echo "   ✗ NodePort is NOT accessible via localhost"
fi

# Check Colima VM SSH access
echo ""
echo "5. Testing Colima VM SSH access..."
if colima ssh -p production -- curl -m 5 -s "http://$LB_IP/health" -H "Host: llm.lamina.local"; then
    echo "   ✓ LoadBalancer is accessible from within Colima VM"
    echo ""
    echo "RECOMMENDATION: Configure Colima port forwarding or network address"
else
    echo "   ✗ LoadBalancer is NOT accessible from within Colima VM"
fi

echo ""
echo "=== Network Test Complete ==="