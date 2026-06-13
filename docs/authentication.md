# Authentication

This project uses **[django-allauth](https://docs.allauth.org/)** for authentication with email-only login. Social login (GitHub, Google, etc.) is ready to enable.

## How it works

### Authentication backends

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # username/email via Django
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth (email-first)
]
```

Both backends are active. `ModelBackend` allows username-based login in Django admin. `AuthenticationBackend` provides allauth's email-based login and social auth flows.

### Installed apps

```python
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'allauth',
    'allauth.account',
    # Local apps
    'config',
    'users',
    'web',
]
```

### Middleware

```python
"allauth.account.middleware.AccountMiddleware"  # last in the middleware stack
```

This middleware integrates allauth's session and authentication state into every request.

## Email-only login configuration

The template ships with email-only login (no username required):

```python
ACCOUNT_SESSION_REMEMBER = True  # Remember login across sessions
ACCOUNT_UNIQUE_EMAIL = True  # One account per email address
ACCOUNT_LOGIN_METHODS = {'email'}  # Login with email, not username
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Only email at signup
```

### Custom user model

Since username-based login is disabled, the custom user model's `__str__` method returns the email:

```python
class CustomUser(AbstractUser):
    def __str__(self) -> str:
        return self.email
```

This makes log messages, admin displays, and shell output immediately readable.

## Email verification

By default, allauth sets `ACCOUNT_EMAIL_VERIFICATION = 'optional'`. This means:

- Users can sign up and log in immediately, even without verifying their email
- Verification emails are sent but not enforced

### Tightening for production

For production, strongly consider:

```python
# src/config/settings.py
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

With mandatory verification:

1. User signs up → allauth sends a verification email with a confirmation link
1. User cannot log in until they click the link
1. If the user tries to log in before verifying, allauth shows a message and resends the verification email

You can also use the `@verified_email_required` decorator on views that should only be accessible to users with verified emails:

```python
from allauth.account.decorators import verified_email_required


@verified_email_required
def sensitive_view(request):
    pass
```

### Testing email verification locally

With the console email backend (default in development), verification emails are printed to your terminal. Look for the confirmation URL in the output and open it in your browser.

## Social login setup

Social login (GitHub, Google, etc.) is ready to enable via `django-allauth[socialaccount]`.

### Step 1: Add the provider app

Add the social account provider to `INSTALLED_APPS` in `src/config/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',  # GitHub
    'allauth.socialaccount.providers.google',  # Google
    # Add more providers as needed
]
```

### Step 2: Configure the provider in Django admin

1. Run `just django serve`
1. Log in to `/admin/`
1. Go to **Sites** → set the domain to `localhost:8000` (for local dev) or your production domain
1. Go to **Social applications** → **Add Social application**:
   - **Provider**: select the provider (e.g. GitHub)
   - **Name**: a descriptive name (e.g. "GitHub OAuth")
   - **Client ID**: from the provider's developer console
   - **Secret key**: from the provider's developer console
   - **Sites**: select `localhost` (and your production domain)

### Step 3: Configure the provider's developer console

#### GitHub OAuth

1. Go to **GitHub → Settings → Developer settings → OAuth Apps → New OAuth App**
1. **Authorization callback URL**:
   - Local: `http://localhost:8000/accounts/github/login/callback/`
   - Production: `https://yourdomain.com/accounts/github/login/callback/`
1. Copy the **Client ID** and **Client Secret** into Django admin

#### Google OAuth

1. Go to **Google Cloud Console → APIs & Services → Credentials**
1. Create an **OAuth 2.0 Client ID** (Web application)
1. **Authorized redirect URIs**:
   - Local: `http://localhost:8000/accounts/google/login/callback/`
   - Production: `https://yourdomain.com/accounts/google/login/callback/`
1. Copy the **Client ID** and **Client Secret** into Django admin

### Step 4: Update settings (optional)

For social accounts, you may want different email verification behavior:

```python
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Skip verification for social logins
```

## Extending the custom user model

The template ships with `users.CustomUser` extending `AbstractUser`. See [Custom User Model](users.md) for the full guide on:

- Adding custom fields (bio, timezone, avatar, etc.)
- Updating admin forms and fieldsets
- Adding a custom manager
- Updating test fixtures
- Common pitfalls

## Custom signup adapters

If you need to customize the signup flow (e.g. restrict to certain email domains), create a custom adapter:

```python
# src/users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        """Only allow signups from company domain."""
        if not email.endswith('@company.com'):
            raise ValidationError('Only @company.com emails are allowed.')
        return email
```

Then reference it in settings:

```python
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
```

## URLs

All allauth URLs are mounted under `/accounts/`:

| URL                             | View               | Description                       |
| ------------------------------- | ------------------ | --------------------------------- |
| `/accounts/login/`              | Login              | Email + password login form       |
| `/accounts/signup/`             | Signup             | New account registration          |
| `/accounts/logout/`             | Logout             | Confirm and log out               |
| `/accounts/password/change/`    | Password change    | Change password (authenticated)   |
| `/accounts/password/reset/`     | Password reset     | Request password reset email      |
| `/accounts/email/`              | Email management   | Verify and manage email addresses |
| `/accounts/social/connections/` | Social connections | Link/unlink social accounts       |

## Template overrides

The template includes custom allauth templates using Tailwind/DaisyUI in `src/templates/account/`:

- `login.html` — custom login form
- `signup.html` — custom signup form
- `logout.html` — custom logout confirmation
- `password_change.html` — custom password change form
- `email.html` — email management
- `verification_sent.html` — verification pending notice
- `email_confirm.html` — email confirmation page

Django's template loader checks `TEMPLATES['DIRS']` (which includes `src/templates/`) before app templates, so files in `src/templates/account/` override allauth defaults automatically.

## Further reading

- [Custom User Model](users.md) — extending the user model
- [Settings & Environment](settings.md) — environment variable reference
- [django-allauth configuration](https://docs.allauth.org/en/latest/account/configuration.html)
- [django-allauth social providers](https://docs.allauth.org/en/latest/socialaccount/index.html)
