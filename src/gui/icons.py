from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


ICONS = {
    "heart-pulse": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M3 12h4l2-7 4 14 2-7h6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m3 10 9-7 9 7v10H5V10M9 20v-6h6v6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="9" cy="7" r="4" fill="none" stroke="{color}" stroke-width="2"/><path d="M3 21v-2a6 6 0 0 1 12 0v2M16 4a4 4 0 0 1 0 7M18 14a6 6 0 0 1 3 5v2" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="17" rx="2" fill="none" stroke="{color}" stroke-width="2"/><path d="M16 2v4M8 2v4M3 10h18" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "user-plus": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="9" cy="7" r="4" fill="none" stroke="{color}" stroke-width="2"/><path d="M3 21v-2a6 6 0 0 1 12 0v2M19 8v6M16 11h6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "clipboard": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="17" rx="2" fill="none" stroke="{color}" stroke-width="2"/><path d="M9 4V2h6v2M9 10h6M9 14h6M9 18h4" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "stethoscope": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M6 3v6a4 4 0 0 0 8 0V3M4 3h4M12 3h4M14 13a5 5 0 0 0 5 5" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/><circle cx="19" cy="20" r="2" fill="none" stroke="{color}" stroke-width="2"/></svg>',
    "bar-chart": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="none" stroke="{color}" stroke-width="2"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.1h-2.6V20a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.6-1H6v-2.6h.4A1.7 1.7 0 0 0 8 10a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V5h2.6v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.1v2.6h-.1a1.7 1.7 0 0 0-1.6 1.3Z" fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" fill="none" stroke="{color}" stroke-width="2"/><path d="m20 20-4-4" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="{color}" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "map-pin": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" fill="none" stroke="{color}" stroke-width="2"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="{color}" stroke-width="2"/></svg>',
    "phone": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M6 3h3l2 5-2 1.5a15 15 0 0 0 5.5 5.5L16 13l5 2v3a3 3 0 0 1-3 3C10.8 21 3 13.2 3 6a3 3 0 0 1 3-3Z" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 14h10l1-14M9 7V4h6v3" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow-left": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 12H5M11 6l-6 6 6 6" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" fill="none" stroke="{color}" stroke-width="2"/><path d="M4 21c0-4.2 3.6-7 8-7s8 2.8 8 7" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "logout": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M10 4H5v16h5M14 8l4 4-4 4M18 12H9" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "bell": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "sun": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" fill="none" stroke="{color}" stroke-width="2"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/></svg>',
    "chevron-down": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "chevron-up": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m6 15 6-6 6 6" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "gender": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="9" cy="15" r="5" fill="none" stroke="{color}" stroke-width="2"/><path d="m13 11 7-7M15 4h5v5" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "logo": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><path d="M24 43C10 32 4 25 4 16.5 4 10.7 8.6 6 14.3 6c3.9 0 7.4 2.1 9.7 5.4C26.300 8.100 29.800 6 33.700 6 39.400 6 44 10.700 44 16.500 44 25 38 32 24 43Z" fill="{color}"/><path d="M9 24h9l3-7 5 14 3-7h10" fill="none" stroke="#ffffff" stroke-width="2.800" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "lock": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2.5"/><path d="M8 11V7.5a4 4 0 0 1 8 0V11"/><path d="M12 15.5v1.5"/></g></svg>',
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></g></svg>',
    "eye-off": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18"/><path d="M6.6 6.7C3.9 8.5 2 12 2 12s3.6 7 10 7c1.7 0 3.2-.4 4.5-1"/><path d="M10.6 5.1A10 10 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4.1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></g></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></g></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/></g></svg>',
    "globe": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z"/></g></svg>',
}


def _svg(name, color):
    return ICONS.get(name, ICONS["heart-pulse"]).format(color=color)


ILLUSTRATIONS = {
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140"><ellipse cx="118" cy="78" rx="80" ry="56" fill="#e3f7ec"/><circle cx="44" cy="38" r="6" fill="#cdeedd"/><circle cx="198" cy="28" r="4" fill="#cdeedd"/><rect x="62" y="30" width="112" height="86" rx="12" fill="#ffffff" stroke="#7fd4ab" stroke-width="3"/><path d="M62 42a12 12 0 0 1 12-12h88a12 12 0 0 1 12 12v14H62z" fill="#4cc790"/><rect x="84" y="20" width="6" height="20" rx="3" fill="#0f9d63"/><rect x="146" y="20" width="6" height="20" rx="3" fill="#0f9d63"/><g fill="#bfe8d2"><rect x="78" y="66" width="16" height="12" rx="3"/><rect x="100" y="66" width="16" height="12" rx="3"/><rect x="122" y="66" width="16" height="12" rx="3"/><rect x="144" y="66" width="16" height="12" rx="3"/><rect x="78" y="86" width="16" height="12" rx="3"/><rect x="100" y="86" width="16" height="12" rx="3"/></g><circle cx="164" cy="104" r="26" fill="#0f9d63" stroke="#ffffff" stroke-width="5"/><path d="M164 90v15l10 6" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "user-plus": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140"><ellipse cx="112" cy="74" rx="80" ry="56" fill="#e3f7ec"/><circle cx="46" cy="40" r="6" fill="#cdeedd"/><circle cx="198" cy="30" r="4" fill="#cdeedd"/><circle cx="104" cy="52" r="24" fill="#7fd4ab"/><path d="M58 114c0-24 20-38 46-38s46 14 46 38z" fill="#4cc790"/><circle cx="158" cy="98" r="21" fill="#0f9d63" stroke="#ffffff" stroke-width="5"/><path d="M158 88v20M148 98h20" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 140"><ellipse cx="112" cy="74" rx="80" ry="56" fill="#e3f7ec"/><circle cx="46" cy="40" r="6" fill="#cdeedd"/><circle cx="198" cy="30" r="4" fill="#cdeedd"/><circle cx="84" cy="56" r="20" fill="#9ce0bd"/><path d="M44 112c0-20 16-32 40-32s40 12 40 32z" fill="#7fd4ab"/><circle cx="136" cy="50" r="24" fill="#7fd4ab"/><path d="M90 114c0-24 20-38 46-38s46 14 46 38z" fill="#4cc790"/></svg>',
}


def _render(svg, width, height):
    """Renderiza SVG em 2x (nítido em qualquer ecrã) com devicePixelRatio=2."""
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(width * 2, height * 2)
    pm.setDevicePixelRatio(2)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.end()
    return pm


def pixmap(name, color="#0daf69", size=24):
    return _render(_svg(name, color), size, size)


def qicon(name, color="#0daf69", size=24):
    return QIcon(pixmap(name, color, size))


def illustration(name, width=200, height=127):
    return _render(ILLUSTRATIONS.get(name, ILLUSTRATIONS["users"]), width, height)
