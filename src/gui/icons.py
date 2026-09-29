from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer

# Ícones em SVG, no estilo linear da referência (traço fino, cantos arredondados).
PATHS = {
    "heart-pulse": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z"/><path d="M3 12h4l2-3 3 6 2-3h7"/>',
    "home": '<path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "user-plus": '<circle cx="9" cy="8" r="4"/><path d="M3 21a6 6 0 0 1 12 0"/><path d="M19 8v6M16 11h6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="3"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "calendar-clock": '<path d="M3 4h18v17H3z"/><path d="M16 2v4M8 2v4M3 10h18"/><circle cx="16" cy="16" r="3.5"/><path d="M16 14v2l1.5 1"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "bell": '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
    "stethoscope": '<path d="M6 3v5a6 6 0 0 0 12 0V3"/><path d="M4 3h4M16 3h4"/><path d="M18 14a4 4 0 1 0 4 4"/><circle cx="22" cy="18" r="1"/>',
    "map-pin": '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.9.33 1.78.62 2.63a2 2 0 0 1-.45 2.11L8 9.73a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.85.29 1.73.5 2.63.62A2 2 0 0 1 22 16.92Z"/>',
    "trash": '<path d="M3 6h18M8 6V4h8v2M19 6l-1 15H6L5 6M10 11v6M14 11v6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2M9 9h6M9 13h6M9 17h4"/>',
    "bar-chart": '<path d="M4 19V9M10 19V5M16 19V11M22 19V3"/>',
    "settings": '<path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.7 1.7-.06-.06A1.7 1.7 0 0 0 16.16 18a1.7 1.7 0 0 0-1.03 1.56V20h-2.4v-.44A1.7 1.7 0 0 0 11.7 18a1.7 1.7 0 0 0-1.88.34l-.06.06-1.7-1.7.06-.06A1.7 1.7 0 0 0 8.46 15a1.7 1.7 0 0 0-1.56-1.03H6v-2.4h.9A1.7 1.7 0 0 0 8.46 10a1.7 1.7 0 0 0-.34-1.88l-.06-.06 1.7-1.7.06.06A1.7 1.7 0 0 0 11.7 6a1.7 1.7 0 0 0 1.03-1.56V4h2.4v.44A1.7 1.7 0 0 0 16.16 6a1.7 1.7 0 0 0 1.88-.34l.06-.06 1.7 1.7-.06.06A1.7 1.7 0 0 0 19.4 9c.14.56.57.97 1.14 1.03H21v2.4h-.46A1.7 1.7 0 0 0 19.4 15Z"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "gender": '<circle cx="9" cy="15" r="4"/><path d="M12 12l6-6M15 6h3v3"/>',
    "grid": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8h.01M12 8h.01M16 8h.01M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>',
}


def _svg(name, color):
    body = PATHS[name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'''


def pixmap(name, color="#0daf69", size=24):
    renderer = QSvgRenderer(QByteArray(_svg(name, color).encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    renderer.render(pm)
    return pm


def qicon(name, color="#0daf69", size=24):
    return QIcon(pixmap(name, color, size))
