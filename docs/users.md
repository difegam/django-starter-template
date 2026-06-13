# Custom User Model

## Why this template ships with a custom user model

Django's own documentation [advises setting up a custom user model at the very start of a project](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project):

> If you're starting a new project, it's highly recommended to set up a custom user model, even if the default User model is sufficient for you. This model behaves identically to the default user model, but you'll be able to customise it in the future if the need arises.

Changing the user model **after** the first migration has been applied is complex. It requires either manually editing migrations or using a third-party migration tool, risks data loss, and can break foreign-key relationships across the database. By shipping `users.CustomUser` from day one, this template removes that risk entirely.

The custom user is wired up in `src/config/settings.py`:

```python
AUTH_USER_MODEL = 'users.CustomUser'
```

All Django internals and third-party packages (including django-allauth) respect this setting automatically.

---

## Current implementation

`src/users/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    def __str__(self) -> str:
        return self.email
```

`AbstractUser` preserves every field and method from Django's built-in `User` (username, email, first_name, last_name, password, is_active, is_staff, is_superuser, last_login, date_joined, groups, user_permissions). The only customisation so far is that `__str__` returns the email address, which matches the email-only login configured via django-allauth.

---

## Always reference the user model indirectly

Never import Django's default `User` class directly. Use one of the two safe patterns:

```python
# Option A — recommended for code that runs at import time (e.g. type annotations,
# model ForeignKey definitions, form Meta classes)
from django.contrib.auth import get_user_model

User = get_user_model()

# Option B — direct import is fine inside the users app itself
from users.models import CustomUser
```

Using `get_user_model()` or `settings.AUTH_USER_MODEL` ensures your code keeps working if the concrete model class is ever changed.

For model `ForeignKey` / `OneToOneField` / `ManyToManyField` relations, always use the string form:

```python
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
```

---

## Adding custom fields

Follow this checklist every time you add a new field to `CustomUser`.

### 1. Add the field to the model

Open `src/users/models.py` and add your field. The example below adds an optional biography and a required timezone preference:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, default='')
    timezone = models.CharField(
        max_length=50,
        default='UTC',
    )

    def __str__(self) -> str:
        return self.email
```

> **Tip:** Prefer `blank=True, default=''` (or a sensible default) for new fields on an existing table so that the migration can be applied without supplying a value for every existing row.

### 2. Generate and apply the migration

```bash
just django migrate
```

The recipe runs `makemigrations` automatically before applying. Check the generated file in `src/users/migrations/` before committing it.

### 3. Expose the field in Django admin

Update `src/users/admin.py` to include new fields. Add them to `fieldsets` (for the edit view) and optionally to `add_fieldsets` (for the creation form):

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    # Append a new section to the existing fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'timezone')}),
    )
```

### 4. Update the admin forms if needed

`src/users/forms.py` uses `fields` to list which columns appear in the creation and change forms. Add new fields you want editors to fill in:

```python
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # add fields here if needed during creation


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'timezone')  # add new fields here
```

### 5. Update test fixtures for required fields

If a new field is required (no `default` and not `blank`), update the `user` and `admin_user` fixtures in `tests/conftest.py`:

```python
@pytest.fixture
def user(db: None) -> CustomUser:
    return CustomUser.objects.create_user(
        username='testuser',
        email='user@example.com',
        password='ThisIsATestPassword123',  # noqa: S106
        timezone='America/New_York',  # supply value for required field
    )
```

### 6. Add or update tests

Add a test in `tests/users/test_models.py` that asserts the new field behaves as expected:

```python
@pytest.mark.django_db
def test_custom_user_has_default_timezone(user: CustomUser) -> None:
    assert user.timezone == 'UTC'
```

---

## Adding a custom manager

If you need custom queryset methods (for example, `active_users()`), add a manager rather than cluttering views with repeated filter logic:

```python
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def active(self) -> models.QuerySet['CustomUser']:
        return self.filter(is_active=True)


class CustomUser(AbstractUser):
    objects: CustomUserManager = CustomUserManager()

    def __str__(self) -> str:
        return self.email
```

Usage:

```python
from users.models import CustomUser

active = CustomUser.objects.active()
```

> **Note:** Always subclass `UserManager` (not the plain `Manager`) when replacing the default manager on a user model. `UserManager` provides `create_user()` and `create_superuser()` which are required by Django's auth infrastructure.

---

## Authentication context

This project uses django-allauth configured for **email-only login**:

| Setting | Value |
|---|---|
| `ACCOUNT_LOGIN_METHODS` | `{'email'}` |
| `ACCOUNT_UNIQUE_EMAIL` | `True` |
| `ACCOUNT_SIGNUP_FIELDS` | `['email*', 'password1*', 'password2*']` |
| Minimum password length | 12 characters |
| Login redirect | `home` URL name |

Because username-based login is disabled, `__str__` returning `self.email` (rather than `self.username`) makes log messages, admin displays, and shell output immediately readable.

---

## Common pitfalls

| Pitfall | Consequence | Fix |
|---|---|---|
| Importing `from django.contrib.auth.models import User` | Breaks if `AUTH_USER_MODEL` differs from the default | Use `get_user_model()` or `from users.models import CustomUser` |
| Adding a non-nullable field without a default | Migration fails or prompts Django to ask for a one-off default | Always provide `default=` or `blank=True` for new fields |
| Forgetting `just django migrate` after editing the model | `OperationalError: no such column` at runtime | Run `just django migrate` after every model change |
| Replacing the manager without subclassing `UserManager` | `create_superuser` / `create_user` missing or broken | Subclass `UserManager`, not `Manager` |
| Skipping fixture updates for required fields | Test suite fails with `IntegrityError` | Update `tests/conftest.py` whenever a required field is added |

---

## Further reading

- [Django docs — Customizing authentication: substituting a custom user model](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#substituting-a-custom-user-model)
- [Django docs — Using a custom user model when starting a project](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project)
- [django-allauth configuration reference](https://docs.allauth.org/en/latest/account/configuration.html)
