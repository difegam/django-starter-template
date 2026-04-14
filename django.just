set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set dotenv-load := true

[doc("Run the application locally")]
[group("app")]
serve:
    @echo "🚀 Starting the Django development server..."
    uv run python src/manage.py runserver

[doc("Apply database migrations")]
[group("db")]
migrate: makemigrations
    @uv run python src/manage.py migrate

[doc("Create new Django migrations based on model changes")]
[private]
makemigrations:
    @uv run python src/manage.py makemigrations

[doc("Create a Django superuser")]
[group("auth")]
add-superuser:
    @uv run python src/manage.py createsuperuser

[doc("Start Django shell")]
[group("app")]
shell:
    @uv run python src/manage.py shell

[doc("Run Django deploy check")]
[group("ops")]
deploy-check:
    @uv run python src/manage.py check --deploy

[doc("Collect static files")]
[group("ops")]
collectstatic:
    @uv run python src/manage.py collectstatic --noinput

[doc("Create a new Django app with the given NAME")]
[group("app")]
[working-directory("src")]
new NAME:
    # Use module invocation to avoid missing django-admin script issues
    @uv run python -m django startapp {{ NAME }}
    mkdir -p {{ NAME }}/templates/{{ NAME }} {{ NAME }}/static/{{ NAME }}
    echo "Remember to add '{{ NAME }}' to LOCAL_APPS in src/config/settings.py"
