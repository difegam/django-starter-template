#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///
"""
Initialize a new Django project from this starter template.

This script:
- Removes the existing git repository
- Creates a new README.md with the project name
- Updates pyproject.toml with the project name
- Prepares the project for a fresh start

Usage:
    uv run init_project.py <project-name>
"""

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.text import Text

console = Console()


def remove_git_repo(base_dir: Path) -> None:
    """Remove the existing .git directory."""
    git_dir = base_dir / '.git'
    if git_dir.exists():
        console.print(f'Removing existing git repository at [cyan]{git_dir}[/cyan]')
        try:
            shutil.rmtree(git_dir)
            console.print('[green]✓[/green] Git repository removed')
        except OSError as e:
            console.print(f'[red]✗[/red] Failed to remove git repository: {e}')
            sys.exit(1)
    else:
        console.print('[blue]ℹ[/blue] No git repository found')


def remove_venv(base_dir: Path) -> None:
    """Remove the existing .venv directory."""
    venv_dir = base_dir / '.venv'
    if venv_dir.exists():
        console.print(f'Removing existing virtual environment at [cyan]{venv_dir}[/cyan]')
        try:
            shutil.rmtree(venv_dir)
            console.print('[green]✓[/green] Virtual environment removed')
        except OSError as e:
            console.print(f'[red]✗[/red] Failed to remove virtual environment: {e}')
            sys.exit(1)
    else:
        console.print('[blue]ℹ[/blue] No virtual environment found')


def remove_database(base_dir: Path) -> None:
    """Remove the existing SQLite database file."""
    db_file = base_dir / 'src' / 'db.sqlite3'
    if db_file.exists():
        console.print(f'Removing existing database at [cyan]{db_file}[/cyan]')
        try:
            db_file.unlink()
            console.print('[green]✓[/green] Database removed')
        except OSError as e:
            console.print(f'[red]✗[/red] Failed to remove database: {e}')
            sys.exit(1)
    else:
        console.print('[blue]ℹ[/blue] No database file found')


def create_readme(base_dir: Path, project_name: str, description: str | None = None) -> None:
    """Create a new README.md with the project name."""
    readme_path = base_dir / 'README.md'

    # Use custom description or default
    overview = description if description else 'A Django project built with the Django Starter Template.'

    # Create a simple README template
    readme_content = f"""# {project_name}

## Overview

{overview}

## Features

- **Django 5.2+** - Latest Django features and security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **uv** - Fast, modern Python package manager
- **Just** - Command runner for development tasks
- **Type Safety** - Full mypy strict mode with django-stubs
- **Code Quality** - Ruff for linting/formatting, pre-commit hooks
- **Testing** - pytest with pytest-django and coverage reporting
- **Environment Configuration** - django-environ for 12-factor app compliance

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [Just](https://github.com/casey/just) - Install with `brew install just` (macOS)

### Installation

1. Set up the environment:
```bash
just install
```

2. Create a `.env` file in the project root:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=UTC
DATABASE_URL=sqlite:///src/db.sqlite3
```

3. Run migrations:
```bash
just dj-migrate
```

4. Create a superuser:
```bash
uv run python src/manage.py createsuperuser
```

5. Run the development server:
```bash
just run
```

## Available Commands

Run `just` to see all available commands:

- `just install` - Set up environment (uv sync + pre-commit install)
- `just run` - Start Django dev server
- `just test` - Run pytest suite
- `just lint` - Run ruff linting and formatting
- `just check` - Run all pre-commit hooks
- `just dj-migrate` - Run migrations
- `just new-app NAME` - Create new Django app

## Project Structure

```
src/
├── config/          # Django settings and configuration
├── users/           # Custom user model
├── templates/       # Project-wide templates
└── static/          # Project-wide static files
```

## Development

This project follows strict code quality standards:

- **Python Style**: Single quotes, 120 char line length (enforced by ruff)
- **Type Checking**: Strict mypy with django-stubs
- **Pre-commit Hooks**: Automatic code quality checks on commit

## License

[Add your license here]
"""

    console.print(f'Creating new README.md for [cyan]{project_name}[/cyan]')
    try:
        readme_path.write_text(readme_content, encoding='utf-8')
        console.print('[green]✓[/green] README.md created')
    except OSError as e:
        console.print(f'[red]✗[/red] Failed to create README.md: {e}')
        sys.exit(1)


def update_pyproject_toml(base_dir: Path, project_name: str, description: str | None = None) -> None:
    """Update the name in pyproject.toml."""
    pyproject_path = base_dir / 'pyproject.toml'

    if not pyproject_path.exists():
        console.print('[red]✗[/red] pyproject.toml not found')
        sys.exit(1)

    console.print(f'Updating pyproject.toml with project name: [cyan]{project_name}[/cyan]')

    try:
        content = pyproject_path.read_text(encoding='utf-8')
    except OSError as e:
        console.print(f'[red]✗[/red] Failed to read pyproject.toml: {e}')
        sys.exit(1)

    # Replace the name field
    updated_content = content.replace('name = "django-starter-template"', f'name = "{project_name}"')

    # Update description
    new_description = description if description else f'{project_name} - A Django project'
    updated_content = updated_content.replace(
        'description = "A simple way to start your Django project with a solid foundation."',
        f'description = "{new_description}"',
    )

    try:
        pyproject_path.write_text(updated_content, encoding='utf-8')
        console.print('[green]✓[/green] pyproject.toml updated')
    except OSError as e:
        console.print(f'[red]✗[/red] Failed to write pyproject.toml: {e}')
        sys.exit(1)


def validate_project_name(name: str | None) -> bool:
    """Validate that the project name is suitable for Python packages."""
    if not name:
        return False
    return bool(re.match(r'^[a-z0-9_-]+$', name))


def cli() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Initialize a new Django project from this starter template',
        epilog='If no project name is provided, the script will run in interactive mode.',
    )
    parser.add_argument(
        '--name',
        'project_name',
        nargs='?',
        help='Name of the new project (lowercase, with hyphens or underscores)',
    )
    parser.add_argument('-d', '--description', help='Project description')
    parser.add_argument(
        '--skip-git',
        action='store_true',
        help='Skip removing the git repository',
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the initialization script."""

    args = cli()

    # Interactive mode if no project name provided
    if args.project_name:
        # Validate before lowercasing for better error messages
        if not validate_project_name(args.project_name.lower()):
            console.print(
                '[red]✗[/red] Invalid project name. Use only lowercase letters, numbers, hyphens, and underscores.'
            )
            sys.exit(1)
        project_name = args.project_name.lower()
        description = args.description
    else:
        console.print(
            Panel.fit(
                '[bold cyan]Django Project Initialization[/bold cyan]',
                title='🚀 Interactive Setup',
                border_style='cyan',
            )
        )
        console.print()

        # Prompt for project name
        while True:
            project_name = Prompt.ask(
                '[bold cyan]Project name[/bold cyan] [dim](lowercase, with hyphens or underscores)[/dim]'
            ).lower()

            if validate_project_name(project_name):
                break
            console.print(
                '[red]✗[/red] Invalid project name. Use only lowercase letters, numbers, hyphens, and underscores.'
            )

        # Prompt for optional description
        if Confirm.ask('[bold cyan]Add a custom description?[/bold cyan]', default=False):
            description = Prompt.ask('[bold cyan]Project description[/bold cyan]')
        else:
            description = None

        console.print()

    # Get the base directory (where this script is located)
    base_dir = Path(__file__).parent

    console.print()
    console.print(
        Panel.fit(f'[bold cyan]{project_name}[/bold cyan]', title='🚀 Initializing New Project', border_style='cyan')
    )
    console.print()

    # Setup with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Define tasks
        total_tasks = 5 if not args.skip_git else 4
        task = progress.add_task('[cyan]Setting up project...', total=total_tasks)

        # Remove git repository
        if not args.skip_git:
            progress.update(task, description='[cyan]Removing git repository...')
            remove_git_repo(base_dir)
            time.sleep(0.3)  # Brief pause for visual feedback
            progress.advance(task)

        # Remove virtual environment
        progress.update(task, description='[cyan]Removing virtual environment...')
        remove_venv(base_dir)
        time.sleep(0.3)
        progress.advance(task)

        # Remove database file
        progress.update(task, description='[cyan]Removing database file...')
        remove_database(base_dir)
        time.sleep(0.3)
        progress.advance(task)

        # Create new README
        progress.update(task, description='[cyan]Creating README.md...')
        create_readme(base_dir, project_name, description)
        time.sleep(0.3)
        progress.advance(task)

        # Update pyproject.toml
        progress.update(task, description='[cyan]Updating pyproject.toml...')
        update_pyproject_toml(base_dir, project_name, description)
        time.sleep(0.3)
        progress.advance(task)

        progress.update(task, description='[green]✓ Setup complete!')

    console.print()
    console.print(
        Panel.fit(
            f'[bold green]✓[/bold green] Project [cyan]{project_name}[/cyan] initialized successfully!',
            border_style='green',
        )
    )

    next_steps = Text()
    next_steps.append('\n1. Remove this script: ', style='bold')
    next_steps.append('rm init_project.py', style='cyan')
    next_steps.append('\n2. Initialize a new git repository: ', style='bold')
    next_steps.append('git init', style='cyan')
    next_steps.append('\n3. Set up the environment: ', style='bold')
    next_steps.append('just install', style='cyan')
    next_steps.append('\n4. Create a .env file with your configuration', style='bold')
    next_steps.append('\n5. Run migrations: ', style='bold')
    next_steps.append('just dj-migrate', style='cyan')
    next_steps.append('\n6. Start coding! 🎉\n', style='bold green')

    console.print(Panel(next_steps, title='[bold]Next Steps', border_style='yellow'))


if __name__ == '__main__':
    main()
