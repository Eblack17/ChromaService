# Environment Configuration

This directory contains environment-specific configuration files for the ChromaPages AI Customer Service application.

## File Structure

- `development.env`: Development environment configuration (included in repo)
- `production.env.template`: Template for production environment (needs to be copied and configured)
- `staging.env`: (Optional) Staging environment configuration

## Setup Instructions

1. For development:
   - The `development.env` file is ready to use
   - Update values as needed for your local development

2. For production:
   - Copy `production.env.template` to `production.env`
   - Fill in all required values
   - Never commit `production.env` to version control

3. For staging (optional):
   - Copy `production.env.template` to `staging.env`
   - Adjust values for staging environment

## Configuration Variables

### Required Variables
- `SECRET_KEY`: JWT secret key (auto-generated if not set)
- `GOOGLE_API_KEY`: Google API key for Gemini model
- `DB_PASSWORD`: Database password

### Optional Variables with Defaults
All other variables have sensible defaults. See the template files for details.

## Environment Selection

The application uses the `APP_ENV` environment variable to determine which configuration to load:
- `development` (default)
- `staging`
- `production`

Example:
```bash
export APP_ENV=production
python main.py
```

## Security Notes

1. Never commit sensitive values to version control
2. Use secure values for production secrets
3. Restrict access to environment files
4. Regularly rotate sensitive credentials

## Validation

The configuration system includes validation for:
- Value types and ranges
- Required fields
- Format patterns (e.g., semantic versioning)
- Environment-specific rules

## Logging

Configuration loading is logged at:
- INFO level for successful loads
- ERROR level for configuration errors

## Adding New Variables

1. Add the variable to `Settings` class in `config.py`
2. Add it to environment templates
3. Update documentation
4. Add validation if needed 