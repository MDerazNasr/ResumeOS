from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "starter_resume.tex"


def load_starter_resume() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")

