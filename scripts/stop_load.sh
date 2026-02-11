#!/bin/bash
# Stops the load generators
echo "Stopping Load Generators..."
kubectl delete pod load-lms load-cms --ignore-not-found=true
echo "Load test stopped."
