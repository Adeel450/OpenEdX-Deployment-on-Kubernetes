#!/bin/bash
# Stress Test Script for OpenEdX HPA (LMS & CMS)
# This script spins up ephemeral pods to generate high internal traffic.

echo "=================================================="
echo "   Starting High-Load Generators for HPA Test  "
echo "=================================================="

# 1. Launch LMS Load Generator (Detached Mode)
echo "1️⃣  Launching LMS Load Generator..."
kubectl run load-lms \
    --image=busybox:1.28 \
    --restart=Never \
    -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://lms.openedx.svc.cluster.local:8000; done" &>/dev/null
echo "   LMS Load Pod Started."

# 2. Launch CMS Load Generator (Detached Mode)
echo "2️ Launching CMS Load Generator..."
kubectl run load-cms \
    --image=busybox:1.28 \
    --restart=Never \
    -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://cms.openedx.svc.cluster.local:8000; done" &>/dev/null
echo "   CMS Load Pod Started."

echo "=================================================="
echo "Load is now being generated on both services."
echo "Watching HPA Status (Press Ctrl+C to exit watch)..."
echo "To stop load, run: kubectl delete pod load-lms load-cms"
echo "=================================================="

# 3. Watch HPA Status
kubectl get hpa -n openedx -w
