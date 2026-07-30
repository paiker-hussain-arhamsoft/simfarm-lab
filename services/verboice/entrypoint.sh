#!/bin/bash
set -e

cd /app

# Wait for MySQL to be ready.
for i in $(seq 1 30); do
  if curl -fsS "${DATABASE_URL//mysql2:/mysql:}" >/dev/null 2>&1 || mysqladmin ping -h"${DB_HOST:-verboice-db}" -u"${DB_USER:-verboice}" -p"${DB_PASSWORD:-verboice}" --silent 2>/dev/null; then
    break
  fi
  echo "Waiting for database..."
  sleep 2
done

# If the schema isn't loaded yet, run db:setup; otherwise migrate safely.
if ! bundle exec rails runner "exit(ActiveRecord::Base.connection.tables.include?('accounts') ? 0 : 1)" RAILS_ENV=production 2>/dev/null; then
  echo "Initializing Verboice database..."
  bundle exec rake db:setup RAILS_ENV=production
else
  echo "Migrating Verboice database..."
  bundle exec rake db:migrate RAILS_ENV=production || true
fi

# Ensure a default admin account exists for API/basic-auth use.
bundle exec rails runner "
  a = Account.where(email: 'admin@lab.local').first_or_initialize
  unless a.persisted?
    a.password = 'admin123'
    a.password_confirmation = 'admin123'
    a.skip_confirmation! if a.respond_to?(:skip_confirmation!)
    a.save!
  end
" RAILS_ENV=production

exec "$@"
