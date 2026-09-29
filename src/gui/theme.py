"""Carrega o style.qss e resolve tokens de ícones, p. ex. {{icon:chevron-down:#5b7387}}.

O Qt só aceita ficheiros em url(...), por isso os SVG internos de icons.py são
gravados como PNG numa pasta temporária e o token é trocado pelo caminho.
"""
import re
import tempfile
from pathlib import Path

from .icons import pixmap

_TOKEN = re.compile(r"\{\{icon:([\w-]+):(#[0-9a-fA-F]{3,8})\}\}")


def _icon_file(name, color):
    folder = Path(tempfile.gettempdir()) / "medisync_icons"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}_{color.lstrip('#')}.png"
    pixmap(name, color, 16).save(str(path), "PNG")  # 32x32 px reais (2x)
    return path.as_posix()


def load_stylesheet(qss_path):
    text = Path(qss_path).read_text(encoding="utf-8")
    return _TOKEN.sub(lambda m: _icon_file(m.group(1), m.group(2)), text)
