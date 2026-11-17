#!/usr/bin/env bash
# Copyright 2026 Google LLC
# SPDX-License-Identifier: Apache-2.0
#
# One-command deployment script for the Cotality Property Trend & AI Valuation
# Cloud Run WebApp.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-cotality-proj}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-cotality-property-demo}"
DATASET_ID="${DATASET_ID:-cotality_property}"
LOCATION="${LOCATION:-US}"
BUCKET_NAME="${BUCKET_NAME:-cotality-workshop}"
CONNECTION_ID="${CONNECTION_ID:-us.cotality-conn}"

echo "================================================================================"
echo "Deploying ${SERVICE_NAME} to Google Cloud Run"
echo "  Project ID    : ${PROJECT_ID}"
echo "  Region        : ${REGION}"
echo "  Dataset       : ${PROJECT_ID}.${DATASET_ID} (${LOCATION})"
echo "  GCS Bucket    : gs://${BUCKET_NAME}"
echo "  BQ Connection : ${CONNECTION_ID}"
echo "================================================================================"

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --allow-unauthenticated \
  --no-invoker-iam-check \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --set-env-vars="PROJECT_ID=${PROJECT_ID},DATASET_ID=${DATASET_ID},LOCATION=${LOCATION},BUCKET_NAME=${BUCKET_NAME},CONNECTION_ID=${CONNECTION_ID}"
