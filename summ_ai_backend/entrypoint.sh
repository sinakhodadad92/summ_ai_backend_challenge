#!/bin/sh
echo "Making initial migrations for the translation app..."
python manage.py makemigrations translation --noinput
echo "Done."
echo "Making init. migrations ... "
python manage.py makemigrations --noinput
echo "done"
echo "Migrate ... "
python manage.py migrate --noinput
echo "done"
echo "Collectstatics ... "
python manage.py collectstatic --noinput
echo "done"
echo "Creating admin user ... "
python manage.py makemigrations --noinput
python manage.py migrate --noinput
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth.models import User

username = '$DJANGO_SUPERUSER_USERNAME'
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
"
fi
echo "done"
uvicorn summ_ai_backend.asgi:application --host 0.0.0.0 --port 80 --reload
