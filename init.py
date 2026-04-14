#!/usr/bin/env -S uv --quiet run --script
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
    ./init.py [project-name]
    ./init.py --name <project-name>

    # Alternatively, invoke via uv run:
    uv run init.py [project-name]
    uv run init.py --name <project-name>
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
        console.print('[blue]i[/blue] No git repository found')


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
        console.print('[blue]i[/blue] No virtual environment found')


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
        console.print('[blue]i[/blue] No database file found')


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
- **Type Safety** - `ty` checks plus strict mypy configuration with django-stubs
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
just init
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
just django migrate
```

4. Create a superuser:
```bash
just django add-superuser
```

5. Run the development server:
```bash
just django serve
```

## Available Commands

Run `just` to see all available commands:

- `just init` - Set up environment (uv sync + pre-commit install)
- `just django serve` - Start Django dev server
- `just test` - Run pytest suite
- `just lint` - Run ruff linting and formatting
- `just ty` - Run type checks with ty
- `just check` - Run lint, type checks, and pre-commit-stage hooks
- `just django migrate` - Run migrations
- `just django add-superuser` - Create a superuser
- `just django new NAME` - Create a new Django app

## Project Structure

```
src/
├── config/          # Django settings and configuration
├── users/           # Custom user model
├── web/             # Main web app
├── templates/       # Project-wide templates
└── static/          # Project-wide static files
```

## Development

This project follows strict code quality standards:

- **Python Style**: Single quotes, 120 char line length (enforced by ruff)
- **Type Checking**: `ty` checks plus strict mypy config with django-stubs
- **Pre-commit Hooks**: Automatic code quality checks on commit

## License

This project is open source and available under the [MIT License](LICENSE).
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

    new_description = description if description else f'{project_name} - A Django project'
    updated_content = replace_project_field(content, 'name', project_name)
    updated_content = replace_project_field(updated_content, 'description', new_description)

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


def replace_project_field(content: str, field_name: str, value: str) -> str:
    """Replace a field inside the [project] table while preserving surrounding formatting."""
    project_section_pattern = re.compile(r'(^\[project\]\n)(.*?)(?=^\[|\Z)', re.MULTILINE | re.DOTALL)
    project_match = project_section_pattern.search(content)

    if not project_match:
        console.print('[red]✗[/red] [project] section not found in pyproject.toml')
        sys.exit(1)

    project_section = project_match.group(2)
    field_pattern = re.compile(rf'^(?P<indent>\s*){re.escape(field_name)}\s*=\s*"[^"]*"\s*$', re.MULTILINE)
    updated_section, replacements = field_pattern.subn(
        rf'\g<indent>{field_name} = "{value}"',
        project_section,
        count=1,
    )

    if replacements != 1:
        console.print(f'[red]✗[/red] Could not update [project].{field_name} in pyproject.toml')
        sys.exit(1)

    return f'{content[: project_match.start(2)]}{updated_section}{content[project_match.end(2) :]}'


def cli() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Initialize a new Django project from this starter template',
        epilog='Provide a project name as a positional argument or with --name. If omitted, interactive mode is used.',
    )
    parser.add_argument(
        '--name',
        dest='project_name_flag',
        nargs='?',
        help='Name of the new project (lowercase, with hyphens or underscores)',
    )
    parser.add_argument(
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
    parser.add_argument(
        '--force',
        action='store_true',
        help='Required for non-interactive runs that delete existing project state',
    )
    return parser.parse_args()


def get_destructive_targets(base_dir: Path, skip_git: bool) -> list[Path]:
    """Return existing paths that would be deleted by initialization."""
    targets = [
        base_dir / '.venv',
        base_dir / 'src' / 'db.sqlite3',
    ]
    if not skip_git:
        targets.insert(0, base_dir / '.git')
    return [path for path in targets if path.exists()]


def confirm_destructive_actions(base_dir: Path, args: argparse.Namespace, interactive: bool) -> None:
    """Require explicit confirmation before deleting existing project state."""
    destructive_targets = get_destructive_targets(base_dir, args.skip_git)
    if not destructive_targets:
        return

    target_list = '\n'.join(f' - {path.relative_to(base_dir)}' for path in destructive_targets)
    message = (
        'Initialization will permanently delete:\n'
        f'{target_list}\n'
        'Make sure you are running this from a fresh template checkout.'
    )

    if interactive:
        console.print(Panel.fit(message, title='⚠ Confirm Destructive Changes', border_style='yellow'))
        if not Confirm.ask('[bold yellow]Continue with deletion?[/bold yellow]', default=False):
            console.print('[red]✗[/red] Initialization cancelled before making changes.')
            sys.exit(1)
        return

    if args.force:
        return

    console.print(
        '[red]✗[/red] Non-interactive initialization requires --force when existing project state will be deleted.'
    )
    console.print(Panel.fit(message, title='Force Required', border_style='red'))
    sys.exit(1)


def main() -> None:
    """Main entry point for the initialization script."""

    args = cli()

    # Interactive mode if no project name provided
    provided_name = args.project_name_flag or args.project_name

    if args.project_name_flag and args.project_name and args.project_name_flag != args.project_name:
        console.print('[red]✗[/red] Provide project name using either positional argument or --name, not both.')
        sys.exit(1)

    interactive = not bool(provided_name)

    if provided_name:
        if not validate_project_name(provided_name):
            console.print(
                '[red]✗[/red] Invalid project name. Use only lowercase letters, numbers, hyphens, and underscores.'
            )
            sys.exit(1)
        project_name = provided_name
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
            )

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
    confirm_destructive_actions(base_dir, args, interactive)

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
    next_steps.append('rm init.py', style='cyan')
    next_steps.append('\n2. Initialize a new git repository: ', style='bold')
    next_steps.append('git init', style='cyan')
    next_steps.append('\n3. Set up the environment: ', style='bold')
    next_steps.append('just init', style='cyan')
    next_steps.append('\n4. Create a .env file with your configuration', style='bold')
    next_steps.append('\n5. Run migrations: ', style='bold')
    next_steps.append('just django migrate', style='cyan')
    next_steps.append('\n6. Start coding! 🎉\n', style='bold green')

    console.print(Panel(next_steps, title='[bold]Next Steps', border_style='yellow'))


if __name__ == '__main__':
    main()
