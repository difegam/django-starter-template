#!/usr/bin/env -S uv --quiet run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "cyclopts>=4,<5",
#   "InquirerPy>=0.3",
#   "rich>=13.0.0",
# ]
# ///
"""Initialize a new Django project from this starter template."""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from cyclopts import App, Parameter
from InquirerPy import inquirer
from InquirerPy.base import Choice
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

console = Console()
app = App(help='Initialize a new Django project from this starter template.')

PROJECT_NAME_PATTERN = re.compile(r'^[a-z0-9][a-z0-9_-]*$')
PROJECT_SECTION_PATTERN = re.compile(r'(^\[project\]\n)(.*?)(?=^\[|\Z)', re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class CleanupTarget:
    """A file or directory pattern that can be removed during initialization."""

    key: str
    label: str
    description: str
    default: bool
    finder: Callable[[Path], list[Path]]


@dataclass(frozen=True)
class InitOptions:
    """Resolved options for initialization."""

    project_name: str
    description: str | None
    cleanup_keys: list[str]
    force: bool
    dry_run: bool


def direct_path(relative_path: str) -> Callable[[Path], list[Path]]:
    """Return a finder for a single path relative to the project root."""

    def finder(base_dir: Path) -> list[Path]:
        path = base_dir / relative_path
        return [path] if path.exists() else []

    return finder


def glob_paths(pattern: str) -> Callable[[Path], list[Path]]:
    """Return a finder for globbed paths relative to the project root."""

    def finder(base_dir: Path) -> list[Path]:
        return sorted(base_dir.glob(pattern), key=lambda path: path.as_posix())

    return finder


CLEANUP_TARGETS = [
    CleanupTarget(
        key='git',
        label='Git repository',
        description='Remove the starter template .git directory.',
        default=True,
        finder=direct_path('.git'),
    ),
    CleanupTarget(
        key='venv',
        label='Virtual environment',
        description='Remove the local .venv directory.',
        default=True,
        finder=direct_path('.venv'),
    ),
    CleanupTarget(
        key='sqlite',
        label='SQLite database',
        description='Remove src/db.sqlite3.',
        default=True,
        finder=direct_path('src/db.sqlite3'),
    ),
    CleanupTarget(
        key='python-caches',
        label='Python caches',
        description='Remove __pycache__ directories and .pyc files.',
        default=True,
        finder=lambda base_dir: [*glob_paths('**/__pycache__')(base_dir), *glob_paths('**/*.py[co]')(base_dir)],
    ),
    CleanupTarget(
        key='tool-caches',
        label='Tool caches',
        description='Remove .cache, .pytest_cache, .mypy_cache, .ruff_cache, and .ty_cache.',
        default=True,
        finder=lambda base_dir: [
            path
            for name in ('.cache', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.ty_cache')
            if (path := base_dir / name).exists()
        ],
    ),
    CleanupTarget(
        key='macos',
        label='macOS metadata',
        description='Remove .DS_Store files.',
        default=True,
        finder=glob_paths('**/.DS_Store'),
    ),
    CleanupTarget(
        key='node-modules',
        label='Node modules',
        description='Remove node_modules if present.',
        default=True,
        finder=direct_path('node_modules'),
    ),
    CleanupTarget(
        key='env',
        label='Local environment file',
        description='Remove .env. Not selected by default because it can contain local configuration.',
        default=False,
        finder=direct_path('.env'),
    ),
    CleanupTarget(
        key='github',
        label='GitHub configuration',
        description='Remove .github workflows and Copilot instructions.',
        default=False,
        finder=direct_path('.github'),
    ),
    CleanupTarget(
        key='vscode',
        label='VS Code settings',
        description='Remove .vscode workspace settings.',
        default=False,
        finder=direct_path('.vscode'),
    ),
    CleanupTarget(
        key='docker',
        label='Docker deployment files',
        description='Remove Docker/, compose files, Caddyfiles, and Procfile.',
        default=False,
        finder=lambda base_dir: [
            path
            for relative_path in (
                'Docker',
                'docker-compose.yml',
                'docker-compose.production.yml',
                'Caddyfile.local',
                'Caddyfile.prod',
                'Procfile',
            )
            if (path := base_dir / relative_path).exists()
        ],
    ),
    CleanupTarget(
        key='docs',
        label='Template documentation',
        description='Remove docs/ if you prefer to write project-specific docs from scratch.',
        default=False,
        finder=direct_path('docs'),
    ),
    CleanupTarget(
        key='django-placeholders',
        label='Django placeholder files',
        description='Remove empty starter placeholders such as app-level tests.py files.',
        default=False,
        finder=lambda base_dir: [
            path
            for relative_path in ('src/users/tests.py', 'src/web/tests.py', 'src/static/js/ base.js')
            if (path := base_dir / relative_path).exists()
        ],
    ),
]

CLEANUP_TARGETS_BY_KEY = {target.key: target for target in CLEANUP_TARGETS}


def validate_project_name(name: str | None) -> bool:
    """Return whether a project name is safe for Python package metadata."""
    return bool(name and PROJECT_NAME_PATTERN.match(name))


def project_name_validator(_type: type[str], value: str) -> None:
    """Validate project names passed through Cyclopts."""
    if not validate_project_name(value):
        msg = 'Use lowercase letters, numbers, hyphens, and underscores. The first character must be alphanumeric.'
        raise ValueError(msg)


def validate_cleanup_keys(keys: Iterable[str]) -> list[str]:
    """Validate cleanup keys and preserve user-provided order without duplicates."""
    normalized_keys = []
    unknown_keys = []
    for key in keys:
        if key not in CLEANUP_TARGETS_BY_KEY:
            unknown_keys.append(key)
            continue
        if key not in normalized_keys:
            normalized_keys.append(key)

    if unknown_keys:
        valid_keys = ', '.join(CLEANUP_TARGETS_BY_KEY)
        msg = f'Unknown cleanup target(s): {", ".join(unknown_keys)}. Valid targets: {valid_keys}'
        raise ValueError(msg)

    return normalized_keys


def default_cleanup_keys() -> list[str]:
    """Return cleanup target keys selected by default."""
    return [target.key for target in CLEANUP_TARGETS if target.default]


def discover_cleanup_paths(base_dir: Path, cleanup_keys: Iterable[str]) -> list[Path]:
    """Return existing cleanup paths for selected target keys."""
    paths = []
    for key in validate_cleanup_keys(cleanup_keys):
        paths.extend(CLEANUP_TARGETS_BY_KEY[key].finder(base_dir))

    unique_paths = []
    seen = set()
    for path in sorted(paths, key=lambda item: (len(item.parts), item.as_posix())):
        resolved = path.resolve()
        if resolved in seen:
            continue
        if any(resolved.is_relative_to(parent) for parent in seen):
            continue
        seen.add(resolved)
        unique_paths.append(path)
    return sorted(unique_paths, key=lambda item: item.as_posix())


def is_interactive() -> bool:
    """Return whether stdin and stdout support interactive prompts."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def ask_project_name() -> str:
    """Prompt for a valid project name."""
    return inquirer.text(
        message='Project name:',
        validate=lambda value: (
            validate_project_name(value)
            or 'Use lowercase letters, numbers, hyphens, and underscores. Start with a letter or number.'
        ),
    ).execute()


def ask_description(description: str | None) -> str | None:
    """Prompt for an optional project description."""
    if description:
        return description

    should_add_description = inquirer.confirm(message='Add a custom description?', default=False).execute()
    if not should_add_description:
        return None
    result = inquirer.text(message='Project description:').execute().strip()
    return result or None


def ask_cleanup_keys() -> list[str]:
    """Prompt for cleanup targets using InquirerPy checkboxes."""
    choices = [
        Choice(target.key, name=f'{target.label} - {target.description}', enabled=target.default)
        for target in CLEANUP_TARGETS
    ]
    selected_keys = inquirer.checkbox(
        message='Select cleanup targets:',
        choices=choices,
        validate=lambda result: bool(result) or 'Select at least one cleanup target.',
        transformer=lambda result: f'{len(result)} target group(s) selected',
    ).execute()
    return validate_cleanup_keys(selected_keys)


def confirm_cleanup(paths: list[Path], base_dir: Path) -> bool:
    """Prompt for confirmation before deleting paths."""
    if not paths:
        return True

    console.print(build_cleanup_panel(paths, base_dir, title='Confirm Destructive Changes', style='yellow'))
    return inquirer.confirm(message='Continue with deletion?', default=False).execute()


def resolve_options(
    base_dir: Path,
    project_name: str | None,
    description: str | None,
    cleanup: tuple[str, ...],
    skip_git: bool,
    force: bool,
    dry_run: bool,
) -> InitOptions:
    """Resolve CLI arguments and interactive answers into initialization options."""
    if project_name and not validate_project_name(project_name):
        msg = 'Invalid project name. Use lowercase letters, numbers, hyphens, and underscores.'
        raise ValueError(msg)

    interactive = is_interactive() and project_name is None
    if project_name is None:
        if not interactive:
            msg = 'Project name is required in non-interactive mode. Pass NAME or --name.'
            raise ValueError(msg)

        console.print(Panel.fit('[bold cyan]Django Project Initialization[/bold cyan]', title='Interactive Setup'))
        resolved_project_name = ask_project_name()
        resolved_description = ask_description(description)
        cleanup_keys = ask_cleanup_keys()
    else:
        resolved_project_name = project_name
        resolved_description = description
        cleanup_keys = validate_cleanup_keys(cleanup) if cleanup else default_cleanup_keys()

    if skip_git and 'git' in cleanup_keys:
        cleanup_keys = [key for key in cleanup_keys if key != 'git']

    paths = discover_cleanup_paths(base_dir, cleanup_keys)
    if paths and not force and not dry_run:
        if project_name is None and is_interactive():
            if not confirm_cleanup(paths, base_dir):
                msg = 'Initialization cancelled before making changes.'
                raise RuntimeError(msg)
        else:
            msg = 'Refusing to delete existing project state without --force. Use --dry-run to inspect changes.'
            raise RuntimeError(msg)

    return InitOptions(
        project_name=resolved_project_name,
        description=resolved_description,
        cleanup_keys=cleanup_keys,
        force=force,
        dry_run=dry_run,
    )


def build_cleanup_panel(paths: list[Path], base_dir: Path, title: str, style: str) -> Panel:
    """Build a panel describing paths selected for deletion."""
    target_list = '\n'.join(f' - {path.relative_to(base_dir)}' for path in paths)
    message = f'Initialization will permanently delete:\n{target_list}'
    return Panel.fit(message, title=title, border_style=style)


def remove_path(path: Path) -> None:
    """Remove a file or directory."""
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return
    path.unlink()


def cleanup_paths(paths: list[Path], base_dir: Path, dry_run: bool) -> None:
    """Remove selected cleanup paths."""
    if not paths:
        console.print('[blue]i[/blue] No cleanup targets found')
        return

    for path in paths:
        relative_path = path.relative_to(base_dir)
        if dry_run:
            console.print(f'[yellow]dry-run[/yellow] Would remove [cyan]{relative_path}[/cyan]')
            continue
        remove_path(path)
        console.print(f'[green]✓[/green] Removed [cyan]{relative_path}[/cyan]')


def toml_string(value: str) -> str:
    """Return a minimal TOML double-quoted string value."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def replace_project_field(content: str, field_name: str, value: str) -> str:
    """Replace a string field inside the [project] table while preserving surrounding formatting."""
    project_match = PROJECT_SECTION_PATTERN.search(content)
    if not project_match:
        msg = '[project] section not found in pyproject.toml'
        raise ValueError(msg)

    project_section = project_match.group(2)
    field_pattern = re.compile(rf'^(?P<indent>\s*){re.escape(field_name)}\s*=\s*"(?:[^"\\]|\\.)*"\s*$', re.MULTILINE)
    updated_section, replacements = field_pattern.subn(
        lambda match: f'{match.group("indent")}{field_name} = {toml_string(value)}',
        project_section,
        count=1,
    )

    if replacements != 1:
        msg = f'Could not update [project].{field_name} in pyproject.toml'
        raise ValueError(msg)

    return f'{content[: project_match.start(2)]}{updated_section}{content[project_match.end(2) :]}'


def readme_content(project_name: str, description: str | None = None) -> str:
    """Return README content for the initialized project."""
    overview = description or 'A Django project built with the Django Starter Template.'
    return f"""# {project_name}

## Overview

{overview}

## Features

- **Django 6** - Modern Django with current security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **uv** - Fast Python package and project management
- **Just** - Task automation for development commands
- **Type Safety** - `ty` static checks with django-stubs
- **Code Quality** - Ruff linting/formatting and prek-managed Git hooks
- **Testing** - pytest with pytest-django
- **Environment Configuration** - django-environ for 12-factor configuration
- **Docker-Ready** - Optional Docker, Caddy, Traefik, and deployment examples

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Just](https://just.systems/) recommended

### Installation

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Set at minimum:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///src/db.sqlite3
```

2. Install dependencies and hooks:

```bash
just init
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

Visit http://127.0.0.1:8000.

## Available Commands

Run `just --list --list-submodules` to see all available commands.

Common commands:

- `just init` - Set up dependencies and hooks
- `just django serve` - Start the Django development server
- `just django migrate` - Create and apply migrations
- `just django add-superuser` - Create a superuser
- `just django new NAME` - Create a new Django app
- `just test` - Run tests
- `just lint` - Run Ruff checks and formatting
- `just ty` - Run type checks
- `just check` - Run linting, type checks, and hooks

## Project Structure

```text
src/
├── config/          # Django settings and configuration
├── users/           # Custom user model
├── web/             # Main web app
├── templates/       # Project-wide templates
└── static/          # Project-wide static files
```

## Development

- Python style is enforced by Ruff with 120-character lines and single quotes.
- Tests live under `tests/` and run with pytest.
- Configuration is loaded from environment variables via django-environ.

## License

This project is open source and available under the [MIT License](LICENSE).
"""


def create_readme(base_dir: Path, project_name: str, description: str | None, dry_run: bool) -> None:
    """Create README.md for the initialized project."""
    readme_path = base_dir / 'README.md'
    if dry_run:
        console.print(f'[yellow]dry-run[/yellow] Would write [cyan]{readme_path.relative_to(base_dir)}[/cyan]')
        return
    readme_path.write_text(readme_content(project_name, description), encoding='utf-8')
    console.print('[green]✓[/green] README.md created')


def update_pyproject_toml(base_dir: Path, project_name: str, description: str | None, dry_run: bool) -> None:
    """Update project name and description in pyproject.toml."""
    pyproject_path = base_dir / 'pyproject.toml'
    if not pyproject_path.exists():
        msg = 'pyproject.toml not found'
        raise FileNotFoundError(msg)

    content = pyproject_path.read_text(encoding='utf-8')
    new_description = description or f'{project_name} - A Django project'
    updated_content = replace_project_field(content, 'name', project_name)
    updated_content = replace_project_field(updated_content, 'description', new_description)

    if dry_run:
        console.print(f'[yellow]dry-run[/yellow] Would update [cyan]{pyproject_path.relative_to(base_dir)}[/cyan]')
        return
    pyproject_path.write_text(updated_content, encoding='utf-8')
    console.print('[green]✓[/green] pyproject.toml updated')


def print_next_steps(project_name: str) -> None:
    """Print recommended next steps after initialization."""
    next_steps = Text()
    next_steps.append('\n1. Remove this script: ', style='bold')
    next_steps.append('rm init.py', style='cyan')
    next_steps.append('\n2. Initialize a new git repository: ', style='bold')
    next_steps.append('git init', style='cyan')
    next_steps.append('\n3. Create and edit your environment file: ', style='bold')
    next_steps.append('cp .env.example .env', style='cyan')
    next_steps.append('\n4. Set up the environment: ', style='bold')
    next_steps.append('just init', style='cyan')
    next_steps.append('\n5. Run migrations: ', style='bold')
    next_steps.append('just django migrate', style='cyan')
    next_steps.append('\n6. Start coding!\n', style='bold green')

    console.print(Panel(next_steps, title=f'Next Steps for {project_name}', border_style='yellow'))


def run_initialization(base_dir: Path, options: InitOptions) -> None:
    """Run cleanup and metadata updates for project initialization."""
    cleanup_targets = discover_cleanup_paths(base_dir, options.cleanup_keys)

    if options.dry_run:
        console.print(build_cleanup_panel(cleanup_targets, base_dir, title='Dry Run Cleanup Plan', style='yellow'))

    console.print(Panel.fit(f'[bold cyan]{options.project_name}[/bold cyan]', title='Initializing New Project'))

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task('[cyan]Setting up project...', total=3)

        progress.update(task, description='[cyan]Cleaning template state...')
        cleanup_paths(cleanup_targets, base_dir, options.dry_run)
        progress.advance(task)

        progress.update(task, description='[cyan]Creating README.md...')
        create_readme(base_dir, options.project_name, options.description, options.dry_run)
        progress.advance(task)

        progress.update(task, description='[cyan]Updating pyproject.toml...')
        update_pyproject_toml(base_dir, options.project_name, options.description, options.dry_run)
        progress.advance(task)

        progress.update(task, description='[green]Setup complete!')

    if options.dry_run:
        console.print(Panel.fit('[yellow]Dry run complete. No files were changed.[/yellow]', border_style='yellow'))
        return

    console.print(
        Panel.fit(
            f'[bold green]✓[/bold green] Project [cyan]{options.project_name}[/cyan] initialized successfully!',
            border_style='green',
        )
    )
    print_next_steps(options.project_name)


@app.default
def main(
    project_name: Annotated[
        str | None,
        Parameter(name=['project_name', '--name'], validator=project_name_validator, help='New project name.'),
    ] = None,
    *,
    description: Annotated[str | None, Parameter(name=['--description', '-d'], help='Project description.')] = None,
    cleanup: Annotated[
        tuple[str, ...],
        Parameter(name='--cleanup', help='Cleanup target key. Repeat to select multiple optional targets.'),
    ] = (),
    skip_git: Annotated[bool, Parameter(name='--skip-git', help='Do not remove the .git directory.')] = False,
    force: Annotated[
        bool,
        Parameter(name=['--force', '--yes'], help='Allow deletion without an interactive confirmation.'),
    ] = False,
    dry_run: Annotated[bool, Parameter(name='--dry-run', help='Show planned changes without modifying files.')] = False,
) -> None:
    """Initialize a Django project from this starter template.

    Parameters
    ----------
    project_name
        New project name. If omitted in a TTY, an interactive wizard is shown.
    description
        Optional project description written to README.md and pyproject.toml.
    cleanup
        Cleanup target key. Defaults to safe generated/local state. Repeat to customize non-interactive cleanup.
    skip_git
        Keep the starter template .git directory.
    force
        Allow deletion without an interactive confirmation.
    dry_run
        Show planned changes without modifying files.
    """
    base_dir = Path(__file__).parent.resolve()
    try:
        options = resolve_options(base_dir, project_name, description, cleanup, skip_git, force, dry_run)
        run_initialization(base_dir, options)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        console.print(f'[red]✗[/red] {error}')
        raise SystemExit(1) from error
    except KeyboardInterrupt as error:
        console.print('\n[red]✗[/red] Initialization cancelled.')
        raise SystemExit(130) from error


if __name__ == '__main__':
    app()
