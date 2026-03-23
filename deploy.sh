#!/bin/bash

set -e

PROJECT_ID="tyurome-pj"
REGION="asia-northeast1"
REPOSITORY="gakusyoku-app"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/app:latest"
SERVICE="gakusyoku-app-lite"

echo "==> Docker build"
docker build -f docker/Dockerfile -t "${IMAGE}" .

echo "==> Docker push"
docker push "${IMAGE}"

echo "==> Cloud Run deploy"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}"

echo "==> Done!"
