# ChromaPages AI Customer Service API

A FastAPI-based AI customer service system using Google's Gemini API.

## Features

- AI-powered customer service agents
- Rate limiting with tier support
- JWT-based authentication
- Structured logging and monitoring
- Environment-specific configurations
- Docker containerization
- Google Cloud Run deployment

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chromapages-ai.git
cd chromapages-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp app/core/environments/development.env .env
# Edit .env with your settings
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Docker

Build and run locally:
```bash
docker build -t chromapages-ai .
docker run -p 8080:8080 chromapages-ai
```

## Deployment to Google Cloud Run

### Prerequisites

1. Google Cloud Project with billing enabled
2. Google Cloud CLI installed
3. Docker installed
4. GitHub account

### Setup

1. Create a Google Cloud project:
```bash
gcloud projects create PROJECT_ID
gcloud config set project PROJECT_ID
```

2. Enable required APIs:
```bash
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

3. Create service account for GitHub Actions:
```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"
```

4. Grant necessary permissions:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

5. Create and download service account key:
```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@PROJECT_ID.iam.gserviceaccount.com
```

### GitHub Setup

1. Add the following secrets to your GitHub repository:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Content of the downloaded `key.json` file

2. Add required secrets to Google Cloud Secret Manager:
```bash
# Create secrets
echo "your-google-api-key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo "your-jwt-secret-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding JWT_SECRET_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Deployment

1. Push to main branch to trigger deployment:
```bash
git push origin main
```

2. Monitor deployment in GitHub Actions tab

3. Get the service URL:
```bash
gcloud run services describe chromapages-ai-service \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

## Environment Variables

See `app/core/environments/` for environment-specific configurations:
- `development.env`: Local development
- `production.env.template`: Production template
- `cloud_run.env.template`: Cloud Run specific

## API Documentation

Once deployed, visit:
- Swagger UI: `https://YOUR-SERVICE-URL/docs`
- ReDoc: `https://YOUR-SERVICE-URL/redoc`

## Monitoring and Logging

- Logs are available in Google Cloud Console
- Metrics are collected using OpenTelemetry
- Custom metrics are stored in `/metrics` directory
- Structured logging with JSON format in production

## Testing

Run tests:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## License

MIT License - see LICENSE file for details 