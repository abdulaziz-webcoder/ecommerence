# PowerShell Script to Deploy to Google Cloud Run

Write-Host "Starting Google Cloud Run Deployment..."
Write-Host "Make sure you have run 'gcloud auth login' and 'gcloud config set project [YOUR_PROJECT_ID]'"

# Wait for a brief moment
Start-Sleep -Seconds 2

# This command deploys the application directly from the source code.
# The source code contains the Dockerfile we need.
gcloud run deploy demoMarket `
    --source . `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8000 `
    --env-vars-file .env

Write-Host "Deployment command initiated."
