@echo off
echo Stopping Docker Compose containers...
docker compose down
echo Stopping Kubernetes resources in va-system...
kubectl delete -f k8s/ --ignore-not-found=true
echo All services stopped cleanly.
pause
