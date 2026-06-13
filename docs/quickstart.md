# Quick Start

Create a new project from this starter template and get it running locally in under 5 minutes.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **[Just](https://just.systems/)** — task runner (optional, but recommended)

### Install uv

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Windows (winget):**

```powershell
winget install astral-sh.uv
```

### Install Just

**macOS:**

```bash
brew install just
```

**Linux:**

```bash
# Debian/Ubuntu
sudo apt install just

# Or via cargo
cargo install just
```

**Windows:**

```powershell
winget install Casey.Just
```

## Create a new project from this template

Use this path when you cloned the starter and want to turn it into your own project.

### 1. Clone the template

```bash
git clone <your-repo-url> my-project
cd my-project
```

### 2. Run the one-time initializer

The initializer updates project metadata and removes selected local/template artifacts so your new project starts clean.

```bash
./init.py
```

When cleanup choices appear, use **Space** to toggle options and **Enter** to continue.

If direct execution fails, run the script through `uv`:

```bash
uv run init.py
```

Preview planned changes without modifying files:

```bash
./init.py --name my-project --dry-run
```

Run non-interactively:

```bash
./init.py --name my-project --force
```

> **Warning:** `./init.py` can remove local template state such as `.git`, `.venv`, caches, `node_modules`, `.DS_Store`, and `src/db.sqlite3`. Run with `--dry-run` first if you want to inspect planned changes before deleting anything.

What `./init.py` does:

- Prompts for a project name and optional description.
- Updates `README.md` and `pyproject.toml`.
- Removes selected local/template artifacts.
- Prints next steps for creating a fresh Git repository and starting development.

## Local development setup

Use these steps after running `./init.py`, or when working on this template repository directly.

### 1. Create your environment file

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

### 2. Install dependencies

```bash
just init
```

This runs `uv sync --all-groups` and installs pre-commit/pre-push hooks via prek.

If you don't have Just installed, use:

```bash
uv sync --all-groups
uv run prek install --prepare-hooks --hook-type pre-commit --hook-type pre-push
```

### 3. Run database migrations

```bash
just django migrate
```

Or without Just:

```bash
uv run python src/manage.py makemigrations
uv run python src/manage.py migrate
```

### 4. Create a superuser

```bash
just django add-superuser
```

Or without Just:

```bash
uv run python src/manage.py createsuperuser
```

### 5. Start the development server

```bash
just django serve
```

Or without Just:

```bash
uv run python src/manage.py runserver
```

### 6. Open your browser

Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** — you should see the home page.

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
