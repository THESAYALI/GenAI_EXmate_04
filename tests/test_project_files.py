from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_ci_workflow_exists():
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_dockerfile_exists():
    assert (ROOT / "Dockerfile").exists()


def test_env_file_not_committed_template_exists():
    assert (ROOT / ".env.example").exists()
