---
description: This file describes the architectural decisions and conventions for the Django backend.
applyTo: 'src/**/*.py,tests/**/*.py,pyproject.toml,justfile,.env.example'
---

# Django Architecture Rules

Follow these rules for backend architecture and framework-level decisions. The goal is predictable project structure, clear ownership boundaries, type safety, and maintainability.

## Runtime and settings

- **Commands**: Run all Django commands via `uv run python src/manage.py <command>` to respect the virtualenv.
- **Project root**: Keep Django rooted in `src/` with `src/config/` as the settings module (not a traditional `projectname/` at the repo root).
- **Environment configuration**: Read all config from `.env` using `django-environ` (no hardcoded secrets or environment-specific defaults in code).
- **App registration**: Split `INSTALLED_APPS` into three lists—`DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS`—for clarity and searchability.
- **Settings structure**: Keep `src/config/settings.py` focused on configuration; extract reusable config helpers to `src/config/` modules as needed.

### Settings organization example

```python
# src/config/settings.py
import environ

DJANGO_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', ...]
THIRD_PARTY_APPS = ['django_htmx', 'allauth', ...]
LOCAL_APPS = ['users', 'web']
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Readability: keep DB, cache, email, middleware order consistent
DATABASES = {'default': env.db()}
CACHES = {'default': env.cache()}
```

## Authentication

- **Custom user model**: Use a custom user model extending `AbstractUser` from project start (migrations become painful if added later).
- **User references**: Always use `get_user_model()` or `settings.AUTH_USER_MODEL` in code and migrations, never import `django.contrib.auth.models.User` directly.
- **Settings registration**: Set `AUTH_USER_MODEL = 'users.CustomUser'` in `src/config/settings.py` (required for custom user models to work across the project).
- **Admin configuration**: Register custom user in admin with `UserAdmin` from `django.contrib.auth.admin` to maintain default user admin behavior.
- **Allauth integration**: Configure `django-allauth` with URLs mounted at `/accounts/` and templates in `src/templates/account/` for customization.

### Authentication pattern example

```python
# ✓ Correct
from django.contrib.auth import get_user_model
User = get_user_model()

def my_view(request):
    user = request.user  # Always AbstractUser subclass

# ✗ Avoid
from django.contrib.auth.models import User
```

### Custom user model and admin example

```python
# src/users/models.py
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Extend AbstractUser for future customization."""
    pass

# src/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

# src/config/settings.py
AUTH_USER_MODEL = 'users.CustomUser'
```

## Models and domain logic

- **Ownership**: Each app owns its models, and models define the app's domain boundaries.
- **Custom managers**: Use custom `QuerySet` and `Manager` classes for reusable query logic; prefer `QuerySet.as_manager()` or `Manager.from_queryset()` over duplicating methods.
- **Query optimization**: Use `select_related()` for ForeignKey and OneToOneField; use `prefetch_related()` for ManyToManyField and reverse ForeignKey lookups.
- **Business logic**: Keep queries and filtering in managers/querysets; move complex logic to service functions.
- **Relationships**: Use `ForeignKey(to=...)` or `ForeignKey('app.Model')` to support future model renames and cross-app flexibility.
- **Transactions**: Wrap multi-step operations in `transaction.atomic()` context manager to ensure data consistency.

### Custom manager pattern example

```python
# Using as_manager() to avoid method duplication
class ActiveUserQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def by_email(self, email):
        return self.filter(email=email)

class CustomUser(AbstractUser):
    objects = ActiveUserQuerySet.as_manager()

# Usage: CustomUser.objects.active().by_email('user@example.com')
```

### Query optimization pattern example

```python
from django.db.models import Prefetch

# Optimize ForeignKey lookups with select_related
authors = Article.objects.select_related('author').all()

# Optimize ManyToMany lookups with prefetch_related
articles = Article.objects.prefetch_related('tags').all()

# Combine for complex relationships
articles = (
    Article.objects
    .select_related('author')
    .prefetch_related('tags', 'comments')
    .all()
)
```

### Transaction pattern example

```python
from django.db import transaction

@transaction.atomic
def create_user_and_profile(email, name):
    """Atomically create user and profile, rollback both if any step fails."""
    user = CustomUser.objects.create(email=email)
    UserProfile.objects.create(user=user, name=name)
    return user

# Or as context manager
def bulk_operation():
    with transaction.atomic():
        for data in items:
            Model.objects.create(**data)
```

## Views and request handling

- **Type hints**: Add type hints to all new view functions: `def my_view(request: HttpRequest) -> HttpResponse:`.
- **View responsibility**: Views orchestrate request handling—delegate business logic to service functions or querysets.
- **Return types**: Return `HttpResponse`, `JsonResponse`, or template-based responses; use fragments for HTMX requests.
- **Error handling**: Catch known exceptions and return appropriate HTTP status codes (404, 403, 400); let unexpected errors propagate to error handlers.

### View pattern example

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

def user_detail(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), pk=pk)
    return render(request, 'users/detail.html', {'user': user})
```

## Services and reusable logic

- **Service modules**: Create `src/<app>/services.py` when logic is reused across views or complex enough to warrant extraction.
- **Naming**: Use clear, action-based names (`activate_user(user)`, `send_welcome_email(user)`) rather than generic verbs.
- **Dependencies**: Pass explicit dependencies to service functions rather than importing them inside the function to aid testing.

### Service pattern example

```python
# src/users/services.py
from django.core.mail import send_mail
from users.models import CustomUser

def send_welcome_email(user: CustomUser) -> None:
    send_mail(
        subject='Welcome',
        message=f'Hello {user.email}',
        from_email='no-reply@example.com',
        recipient_list=[user.email],
    )
```

## URL ownership

- **App boundaries**: Each app owns `urls.py`, `views.py`, templates, and static files.
- **URL namespace**: Define `app_name` in each app's `urls.py` to avoid naming conflicts.
- **Root composition**: Root URLs (`src/config/urls.py`) should only compose app routers via `include()` and mount third-party paths (e.g., allauth).
- **No cross-app imports in views**: Avoid importing views from other apps; use explicit URL reversals instead.

### URL composition pattern

```python
# src/users/urls.py
from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [path('profile/', views.profile, name='profile')]

# src/config/urls.py
from django.urls import path, include
urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
]
```

## Templates and static files

- **Shared templates**: Place global/reusable templates in `src/templates/` (e.g., `_base.html`, `partials/navbar.html`, `cotton/` components).
- **App templates**: App-specific templates live in `src/<app>/templates/<app>/` to avoid naming collisions.
- **Static files**: Shared assets in `src/static/`, app-specific assets in `src/<app>/static/<app>/`.
- **Template loading order**: Django searches `src/` directories in `INSTALLED_APPS` order, so app templates can override defaults.

### Template structure example

```
src/templates/
  _base.html           # Global page shell
  partials/
    navbar.html
    footer.html
  cotton/              # Reusable components
    button.html
    card.html
src/users/templates/users/
  detail.html          # App-specific
  list.html
```

## Middleware and frontend integration

- **HTMX integration**: Include `django_htmx.middleware.HtmxMiddleware` in `MIDDLEWARE` when HTMX is enabled (provides `request.htmx` helpers).
- **Middleware ordering**: Follow standard Django middleware order: SecurityMiddleware → SessionMiddleware → CsrfViewMiddleware → AuthenticationMiddleware → HtmxMiddleware (custom) → MessageMiddleware. CSRF middleware must come after SessionMiddleware and before any custom middleware that might rotate the CSRF token.
- **Static assets**: In development, Django serves static files automatically when `DEBUG=True`. In production, use `WhiteNoiseMiddleware` in the middleware stack coupled with `collectstatic` for efficient static file serving (no separate web server config needed).
- **CSRF for HTMX**: Set `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}''` in the base template to include CSRF token automatically in all HTMX requests. This prevents CSRF failures on form submissions via HTMX.

### Middleware configuration example

```python
# src/config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',           # CSRF must be before auth
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_htmx.middleware.HtmxMiddleware',                 # Custom HTMX support
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Base template CSRF pattern

```html
<!-- src/templates/_base.html -->
<html>
  <head>
    <!-- CSS and JS -->
  </head>
  <body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}}'>
    {% block content %}{% endblock %}
  </body>
</html>
```

## Migrations and database

- **Atomic migrations**: Each migration must be reversible and represent one logical schema change.
- **No raw SQL**: Use Django ORM and migrations; avoid raw SQL unless unavoidable (then document with comments).
- **Never edit historical migrations**: Rebase and squash during development; once committed, create new migrations for changes.
- **Migration names**: Use `python src/manage.py makemigrations --name descriptive_name` for clarity.

## Error handling and logging

- **HTTP exceptions**: Use `django.http.Http404`, `django.core.exceptions.PermissionDenied`, etc., for expected errors; catch and convert to appropriate status codes.
- **Custom exceptions**: Define app-specific exceptions in `exceptions.py` for domain errors (e.g., `UserActivationError`); catch in views and return 400 or 500 as appropriate.
- **Logging**: Use `logging.getLogger(__name__)` to log errors and important events; configure log levels in settings per environment.

### Error handling pattern example

```python
from django.core.exceptions import PermissionDenied
from users.exceptions import UserNotActivated

def protected_view(request: HttpRequest) -> HttpResponse:
    try:
        user = get_object_or_404(get_user_model(), pk=request.GET.get('id'))
        if not user.is_active:
            raise UserNotActivated(f'User {user.id} is not active')
    except UserNotActivated:
        raise PermissionDenied('User account inactive')
    return render(request, 'some.html', {'user': user})
```

## Admin customization

- **Admin registration**: Register models with appropriate `ModelAdmin` classes to enable filtering, search, and inline editing.
- **Admin readability**: Set `list_display`, `list_filter`, and `search_fields` to increase usability. Use `list_select_related` and `list_prefetch_related` to optimize admin list queries.
- **Query optimization in admin**: Use `get_queryset()` override to apply `select_related()` and `prefetch_related()` for efficient admin list views.

### Admin optimization example

```python
# src/blog/admin.py
from django.contrib import admin
from .models import Article, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date']
    list_filter = ['published_date', 'tags']
    search_fields = ['title', 'content']
    inlines = [CommentInline]
    list_select_related = ['author']  # Optimize author lookup
    list_prefetch_related = ['tags']   # Optimize tags lookup

    def get_queryset(self, request):
        # Additional optimization for the changelist
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related('tags')

admin.site.register(Article, ArticleAdmin)
```

## Validation and testing

- **Run before commit**: `just check` (lint + type check + tests + security scans).
- **Test structure**: `tests/` is flat with subdirs per app; `conftest.py` provides fixtures; run via `just test`.
- **Database isolation**: Use `@pytest.mark.django_db` decorator on test functions that access the database; leverage pytest-django fixtures like `db` for transaction rollback between tests.
