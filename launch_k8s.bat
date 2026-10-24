@echo off
echo ========================================================
echo   Launching Assessment 7 - Kubernetes Cluster Deployment
echo   Visual Analytics Lab (VL2026270106069)
echo   Rohan Yadav (26MML0020)
echo ========================================================

echo.
echo [1/5] Checking Kubernetes Cluster Nodes...
kubectl get nodes -o wide

echo.
echo [2/5] Applying Kubernetes Manifests (Deployments, Services, ConfigMaps, Secrets, PVCs)...
kubectl apply -f k8s/

echo.
echo [3/5] Waiting for Pods to be ready...
kubectl wait --for=condition=ready pod -l app=mysql -n va-system --timeout=90s
kubectl wait --for=condition=ready pod -l app=backend -n va-system --timeout=60s
kubectl wait --for=condition=ready pod -l app=frontend -n va-system --timeout=60s

echo.
echo [4/5] Kubernetes Cluster Resources in va-system:
kubectl get all -n va-system

echo.
echo [5/5] Opening Live Kubernetes Dashboard in browser...
start http://localhost:30080/

echo.
echo ========================================================
echo   Kubernetes Deployment is LIVE:
echo   - Frontend NodePort: http://localhost:30080
echo   - Backend Service: backend-service:5000 (Internal)
echo   - SQL Service: mysql-service:3306 (Internal)
echo ========================================================
pause
