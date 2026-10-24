@echo off
echo ========================================================
echo   Pushing Images to Container Registry
echo   Visual Analytics Lab - Assessment 8 (Workload Containerization)
echo   Rohan Yadav (26MML0020)
echo ========================================================

echo.
echo [1/4] Tagging images for local registry (localhost:5001)...
docker tag rohanyadav26/va-frontend:v1.0.0 localhost:5001/va-frontend:v1.0.0
docker tag rohanyadav26/va-frontend:v1.0.0 localhost:5001/va-frontend:latest
docker tag rohanyadav26/va-backend:v1.0.0 localhost:5001/va-backend:v1.0.0
docker tag rohanyadav26/va-backend:v1.0.0 localhost:5001/va-backend:latest
docker tag rohanyadav26/va-mysql:v1.0.0 localhost:5001/va-mysql:v1.0.0
docker tag rohanyadav26/va-mysql:v1.0.0 localhost:5001/va-mysql:latest

echo.
echo [2/4] Pushing images to registry...
docker push localhost:5001/va-frontend:v1.0.0
docker push localhost:5001/va-backend:v1.0.0
docker push localhost:5001/va-mysql:v1.0.0

echo.
echo [3/4] Verifying Registry Catalog:
curl -s http://localhost:5001/v2/_catalog

echo.
echo.
echo [4/4] To push to Docker Hub (Optional Public Cloud Registry):
echo   1. docker login
echo   2. docker push rohanyadav26/va-frontend:v1.0.0
echo   3. docker push rohanyadav26/va-backend:v1.0.0
echo   4. docker push rohanyadav26/va-mysql:v1.0.0
echo.
echo ========================================================
echo   Registry push completed successfully!
echo ========================================================
pause
