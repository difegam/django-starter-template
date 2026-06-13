import importlib.util
import sys
from pathlib import Path

import pytest

INIT_PATH = Path(__file__).resolve().parents[1] / 'init.py'
SPEC = importlib.util.spec_from_file_location('init_script', INIT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
init_script = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = init_script
SPEC.loader.exec_module(init_script)


@pytest.mark.parametrize(
    ('name', 'expected'),
    [
        ('my-project', True),
        ('my_project', True),
        ('project123', True),
        ('', False),
        ('MyProject', False),
        ('-project', False),
        ('project name', False),
    ],
)
def test_validate_project_name(name: str, expected: bool) -> None:
    assert init_script.validate_project_name(name) is expected


def test_discover_cleanup_paths_deduplicates_children(tmp_path: Path) -> None:
    (tmp_path / '.venv' / 'lib' / '__pycache__').mkdir(parents=True)
    (tmp_path / '.venv' / 'lib' / '__pycache__' / 'module.pyc').write_text('', encoding='utf-8')
    (tmp_path / 'src' / 'web' / '__pycache__').mkdir(parents=True)
    (tmp_path / 'src' / 'web' / '__pycache__' / 'views.pyc').write_text('', encoding='utf-8')

    paths = init_script.discover_cleanup_paths(tmp_path, ['venv', 'python-caches'])
    relative_paths = [path.relative_to(tmp_path).as_posix() for path in paths]

    assert '.venv' in relative_paths
    assert 'src/web/__pycache__' in relative_paths
    assert '.venv/lib/__pycache__' not in relative_paths
    assert '.venv/lib/__pycache__/module.pyc' not in relative_paths


def test_replace_project_field_escapes_toml_strings() -> None:
    content = '[project]\nname = "old"\ndescription = "old description"\n\n[tool.example]\nname = "unchanged"\n'

    updated_content = init_script.replace_project_field(content, 'description', 'A "quoted" \\ path')

    assert 'description = "A \\"quoted\\" \\\\ path"' in updated_content
    assert '[tool.example]\nname = "unchanged"' in updated_content


def test_readme_content_uses_django_6_and_project_description() -> None:
    content = init_script.readme_content('billing-api', 'Payments and billing')

    assert content.startswith('# billing-api')
    assert 'Payments and billing' in content
    assert '**Django 6**' in content
    assert 'Django 5.2' not in content


def test_dry_run_does_not_remove_or_write_files(tmp_path: Path) -> None:
    (tmp_path / '.venv').mkdir()
    (tmp_path / 'README.md').write_text('# Old README\n', encoding='utf-8')
    (tmp_path / 'pyproject.toml').write_text(
        '[project]\nname = "old"\ndescription = "old description"\n',
        encoding='utf-8',
    )

    options = init_script.InitOptions(
        project_name='new-project',
        description='New description',
        cleanup_keys=['venv'],
        force=True,
        dry_run=True,
    )

    init_script.run_initialization(tmp_path, options)

    assert (tmp_path / '.venv').exists()
    assert (tmp_path / 'README.md').read_text(encoding='utf-8') == '# Old README\n'
    assert 'name = "old"' in (tmp_path / 'pyproject.toml').read_text(encoding='utf-8')


def test_unknown_cleanup_key_raises_value_error() -> None:
    with pytest.raises(ValueError, match='Unknown cleanup target'):
        init_script.validate_cleanup_keys(['missing'])
