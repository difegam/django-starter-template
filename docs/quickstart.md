# Quick Start

Get this Django starter template running locally in under 5 minutes.

______________________________________________________________________

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **[Just](https://just.systems/)** — task runner (optional, but recommended)

### Install uv

=== "macOS / Linux"

````
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
````

=== "Windows (PowerShell)"

````
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
````

=== "Windows (winget)"

````
```powershell
winget install astral-sh.uv
```
````

### Install Just

=== "macOS"

````
```bash
brew install just
```
````

=== "Linux"

````
```bash
# Debian/Ubuntu
sudo apt install just

# Or via cargo
cargo install just
```
````

=== "Windows"

````
```powershell
winget install Casey.Just
```
````

______________________________________________________________________

## Step-by-step setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd django-starter-template
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Open `.env` in your editor and set at minimum:

```env
SECRET_KEY=your-secret-key-here    # Generate with: openssl rand -base64 48
DEBUG=True
DATABASE_URL=sqlite:///src/db.sqlite3
```

> **Never commit your `.env` file.** It is listed in `.gitignore`.

### 3. Install dependencies

```bash
just init
```

This runs `uv sync --all-groups` and installs pre-commit/pre-push hooks via prek.

If you don't have Just installed, use:

```bash
uv sync --all-groups
uv run prek install --prepare-hooks --hook-type pre-commit --hook-type pre-push
```

### 4. Run database migrations

```bash
just django migrate
```

Or without Just:

```bash
uv run python src/manage.py makemigrations
uv run python src/manage.py migrate
```

### 5. Create a superuser

```bash
just django add-superuser
```

Or without Just:

```bash
uv run python src/manage.py createsuperuser
```

### 6. Start the development server

```bash
just django serve
```

Or without Just:

```bash
uv run python src/manage.py runserver
```

### 7. Open your browser

Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** — you should see the home page.

______________________________________________________________________

## Alternative: initialization script

If you're using this template as a starting point for a new project, the included `init.py` script can set everything up for you:

```bash
# Interactive mode
./init.py

# Non-interactive mode
./init.py --name my-project --force
```

Then follow steps 2–7 above.

______________________________________________________________________

## Quick command reference

| What you want to do    | Command                     |
| ---------------------- | --------------------------- |
| Install dependencies   | `just init`                 |
| Run the dev server     | `just django serve`         |
| Run migrations         | `just django migrate`       |
| Create a superuser     | `just django add-superuser` |
| Run tests              | `just test`                 |
| Lint & format          | `just lint`                 |
| Type check             | `just ty`                   |
| Run all quality checks | `just check`                |
| Update dependencies    | `just update`               |
| Clean up caches        | `just clean`                |
| Fresh start            | `just fresh`                |

See [Settings & Environment](settings.md) for the full environment variable reference.
