# Deployment Guide

This document describes how to deploy the Django application to various hosting platforms.

## 1. Google Cloud Run (Recommended)

Since this project has a `deployments/compose/backend/Dockerfile` and is already containerized, Google Cloud Run is an excellent choice for a scalable, serverless deployment.

### Prerequisites
1. Install [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install).
2. Authenticate and select your project:
   ```bash
   gcloud auth login
   gcloud config set project [YOUR_PROJECT_ID]
   ```

### Deployment Steps
1. Enable the required APIs:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com
   ```
2. Make sure your `.env` file is properly configured.
3. Use the provided deployment script to deploy the application directly from source:
   **Windows (PowerShell)**:
   ```powershell
   .\deploy_cloud_run.ps1
   ```
   *Note: This script simply runs the following command:*
   ```bash
   gcloud run deploy django-app --source . --region us-central1 --allow-unauthenticated --env-vars-file .env
   ```

## 2. Vercel

Vercel is great for stateless frontends and API backends, but it has a 15MB Serverless function limit and a strict read-only filesystem (except for `/tmp`).

### Prerequisites
1. Setup a Vercel project or login to the [Vercel CLI](https://vercel.com/cli).
2. Ensure you have a `requirements.txt` file (you can generate it using `uv export > requirements.txt` or `pip freeze > requirements.txt`).

### Deployment Steps
1. Vercel automatically detects the `vercel.json` file we've created in the root directory.
2. Ensure your `ALLOWED_HOSTS` includes `.vercel.app` or `*`.
3. Simply connect your GitHub/GitLab repository to Vercel, or run:
   ```bash
   vercel --prod
   ```
4. Configure all the environment variables from your `.env` file in the Vercel Dashboard directly.

*(Note: Background tasks like Celery require a separate worker service, as Vercel functions time out quickly and cannot run persistent background workers).*

## 3. PythonAnywhere

PythonAnywhere provides a traditional server environment, perfect for long-running processes, though it requires manual WSGI configuration.

### Prerequisites
1. Create a [PythonAnywhere account](https://www.pythonanywhere.com/).

### Deployment Steps
1. Open a Bash console in PythonAnywhere.
2. Clone your repository:
   ```bash
   git clone <your-repo-url> /home/<username>/projects
   cd /home/<username>/projects
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   mkvirtualenv --python=python3.11 django-venv
   pip install -r requirements.txt
   ```
4. Setup environment variables by creating a `.env` file in `/home/<username>/projects/.env`.
5. Run migrations and collect static files:
   ```bash
   python src/manage.py migrate
   python src/manage.py collectstatic --no-input
   ```
6. Go to the **Web** tab in PythonAnywhere Dashboard, add a new web app, and choose **Manual Configuration** (Python 3.11).
7. Set the **Source code** folder to `/home/<username>/projects`.
8. Set the **Virtualenv** folder to `/home/<username>/.virtualenvs/django-venv`.
9. Edit the **WSGI configuration file** (link found in the Web tab) to point to your Django application:
   ```python
   import os
   import sys
   from dotenv import load_dotenv

   path = '/home/<username>/projects/src'
   if path not in sys.path:
       sys.path.append(path)

   # Load environment variables
   load_dotenv('/home/<username>/projects/.env')

   os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
10. Finally, configure Static Files in the Web Tab:
    - URL: `/static/` -> Directory: `/home/<username>/projects/assets/staticfiles/`
    - URL: `/media/` -> Directory: `/home/<username>/projects/assets/media/`
11. Reload the web app from the dashboard.
