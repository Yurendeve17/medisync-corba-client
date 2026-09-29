from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


ICONS = {
    "heart-pulse": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12h4l2-6 4 12 2-6h6"/>
        </svg>
    """,
    "home": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 10 9-7 9 7"/>
            <path d="M5 9v11h14V9"/>
            <path d="M9 20v-6h6v6"/>
        </svg>
    """,
    "users": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <circle cx="9" cy="7" r="4"/>
            <path d="M3 21v-2a6 6 0 0 1 12 0v2"/>
            <path d="M16 3.5a4 4 0 0 1 0 7"/>
            <path d="M21 21v-2a6 6 0 0 0-3-5.2"/>
        </svg>
    """,
    "calendar": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="17" rx="2"/>
            <path d="M16 2v4M8 2v4M3 10h18"/>
        </svg>
    """,
    "user-plus": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <circle cx="9" cy="7" r="4"/>
            <path d="M3 21v-2a6 6 0 0 1 12 0v2"/>
            <path d="M19 8v6M16 11h6"/>
        </svg>
    """,
    "clipboard": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <rect x="5" y="4" width="14" height="17" rx="2"/>
            <path d="M9 4V2h6v2M9 10h6M9 14h6M9 18h4"/>
        </svg>
    """,
    "stethoscope": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 3v6a4 4 0 0 0 8 0V3"/>
            <path d="M4 3h4M12 3h4"/>
            <path d="M14 13a5 5 0 0 0 5 5"/>
            <circle cx="19" cy="20" r="2"/>
        </svg>
    """,
    "bar-chart": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>
        </svg>
    """,
    "settings": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.1h-2.6V20a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.6-1H6v-2.6h.4A1.7 1.7 0 0 0 8 10a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V5h2.6v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.1v2.6h-.1a1.7 1.7 0 0 0-1.6 1.3Z"/>
        </svg>
    """,
    "search": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>
    """,
    "clock": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 7v5l3 2"/>
        </svg>
    """,
    "map-pin": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/>
            <circle cx="12" cy="10" r="2.5"/>
        </svg>
    """,
    "phone": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 3h3l2 5-2 1.5a15 15 0 0 0 5.5 5.5L16 13l5 2v3a3 3 0 0 1-3 3C10.8 21 3 13.2 3 6a3 3 0 0 1 3-3Z"/>
        </svg>
    """,
    "trash": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 7h16M10 11v6M14 11v6"/>
            <path d="M6 7l1 14h10l1-14M9 7V4h6v3"/>
        </svg>
    """,
    "arrow-left": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="{color}" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M11 6l-6 6 6 6"/>
        </svg>
    """
}


def _svg(name, color):
    template = ICONS.get(name, ICONS["heart-pulse"])
    return template.format(color=color)


def pixmap(name, color="#0daf69", size=24):
    renderer = QSvgRenderer(
        QByteArray(_svg(name, color).encode("utf-8"))
    )

    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)

    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()

    return pm


def qicon(name, color="#0daf69", size=24):
    return QIcon(pixmap(name, color, size))
