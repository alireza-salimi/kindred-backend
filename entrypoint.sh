chmod +x /code/wait-for-it.sh
./wait-for-it.sh db:5432
./wait-for-it.sh redis:6379
python manage.py makemigrations users --noinput
python manage.py migrate --noinput
python manage.py compilemessages -l fa
python manage.py collectstatic --noinput
exec "$@"