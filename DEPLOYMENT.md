# Railway deployment

Production: https://ledgerflow.up.railway.app

Project: https://railway.com/project/10c10be5-d703-475b-81cb-3cc6d3fb0c3e

The `Ledger_Flow` service deploys `ooronnoromy/Ledger_Flow` on `main` using the
root Dockerfile. Railway service settings contain these persistent commands:

- Pre-deploy: `python manage.py migrate --noinput`
- Start: `sh tools/start_production.sh`
- Health check: `/healthz/` (checks the database)
- Public target port: `8000`

Configuration is stored in Railway service settings. This project does not use
the deprecated `railway.json` / `railway.toml` configuration format.

## Environment and storage

`DJANGO_DEBUG=0`. A generated `DJANGO_SECRET_KEY` is stored in Railway variables.
Allowed hosts and trusted CSRF origins contain the production hostname.
Railway's public hostname is also detected automatically.

The five `DB_*` variables reference the `Postgres` service's `PGHOST`,
`PGDATABASE`, `PGUSER`, `PGPASSWORD` and `PGPORT`. Keep the database private.
The PostgreSQL template includes its own persistent volume.

The app volume mounts at `/data`. `DJANGO_MEDIA_ROOT=/data/media` stores uploaded
photos; authenticated media views enforce access to each record.
`WEBPUSH_KEYS_DIR=/data/webpush` stores persistent signing keys, generated once
on startup. Do not delete the volume or rotate these keys casually.
`WEBPUSH_SUBJECT` uses the production HTTPS URL as its contact URI.

`PORT=8000` and `WEB_CONCURRENCY=2` configure Gunicorn.
WhiteNoise serves static assets collected during the Docker image build.

## First account and maintenance

The production database starts empty by request. Register at `/register/` to
create a normal fleet account. Local records and credentials are not copied.
To create a separate Django superuser, use Railway's service shell and run
`python manage.py createsuperuser` interactively. Do not put passwords in Git.

Deployments apply migrations before replacing the running service. Check the
Railway deployment and runtime logs after changes. `/healthz/` should return
HTTP 200 with `ok`; login and registration should work over HTTPS.

Maintain backups of both database and app volumes through Railway's volume
backup settings. Restoring the database without its uploaded files may leave
missing photos. Changing a volume or database is not part of routine deployment.

Phone notification delivery requires enabling notifications on a real device.
For retries, run `python manage.py retry_push_notifications` in the service
shell. A periodic retry job is optional and is not configured by this deployment.
