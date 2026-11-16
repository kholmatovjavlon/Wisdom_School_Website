#!/usr/bin/env bash
# One-time setup on cPanel after "Setup Python App" has created the virtualenv.
# Usage (inside the app folder, with the virtualenv activated):
#   bash deploy/setup.sh test.wisdomschool.uz
set -euo pipefail

DOMAIN="${1:?Usage: bash deploy/setup.sh <domain>  (e.g. test.wisdomschool.uz)}"
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
  cat > .env <<ENV
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=${SECRET}
DJANGO_ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN}
DJANGO_CSRF_TRUSTED_ORIGINS=https://${DOMAIN},http://${DOMAIN}
# Set to true once the site opens over https (needed for admin login over plain http)
DJANGO_SECURE_COOKIES=false
DB_ENGINE=sqlite
ENV
  echo "Created .env for ${DOMAIN}"
else
  echo ".env already exists, leaving it as is"
fi

pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo
mkdir -p tmp && touch tmp/restart.txt

echo
echo "Done. Now create an admin account:  python manage.py createsuperuser"
echo "Then press Restart in Setup Python App and open http://${DOMAIN}"
