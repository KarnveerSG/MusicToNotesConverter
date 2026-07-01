"""Dark theme palette for MVP."""

COLORS = {
    "bg": "#1e1e2e",
    "surface": "#252536",
    "surface_alt": "#2f2f45",
    "border": "#3d3d5c",
    "text": "#e4e4ef",
    "text_muted": "#9898b0",
    "accent": "#7c9cff",
    "accent_hover": "#9ab4ff",
    "success": "#7dcea0",
    "warning": "#f5c26b",
    "error": "#ff7b7b",
    "waveform": "#7c9cff",
    "waveform_fill": "#4a5f99",
    "note": "#c9e7ff",
    "note_border": "#7c9cff",
    "playhead": "#ff7b7b",
    "subtitle_active": "#3d5a80",
}


def stylesheet() -> str:
    c = COLORS
    return f"""
    QMainWindow, QWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: "Segoe UI", sans-serif;
        font-size: 10pt;
    }}
    QMenuBar {{
        background-color: {c['surface']};
        border-bottom: 1px solid {c['border']};
        padding: 2px;
    }}
    QMenuBar::item:selected {{
        background-color: {c['surface_alt']};
    }}
    QMenu {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
    }}
    QToolBar {{
        background-color: {c['surface']};
        border-bottom: 1px solid {c['border']};
        spacing: 6px;
        padding: 4px;
    }}
    QPushButton {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background-color: {c['accent']};
        color: #111;
    }}
    QPushButton:disabled {{
        color: {c['text_muted']};
        background-color: {c['surface']};
    }}
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        background: {c['surface']};
    }}
    QTabBar::tab {{
        background: {c['surface_alt']};
        border: 1px solid {c['border']};
        padding: 8px 16px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {c['accent']};
        color: #111;
    }}
    QListWidget {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 6px;
    }}
    QListWidget::item:selected {{
        background-color: {c['subtitle_active']};
    }}
    QProgressBar {{
        border: 1px solid {c['border']};
        border-radius: 4px;
        text-align: center;
        background: {c['surface']};
    }}
    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 3px;
    }}
    QStatusBar {{
        background-color: {c['surface']};
        border-top: 1px solid {c['border']};
    }}
    QSlider::groove:horizontal {{
        height: 6px;
        background: {c['surface_alt']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        width: 14px;
        margin: -5px 0;
        background: {c['accent']};
        border-radius: 7px;
    }}
    QLabel#meta {{
        color: {c['text_muted']};
    }}
    QLabel#dropTitle {{
        font-size: 14pt;
        font-weight: 600;
        color: {c['text']};
    }}
    QLabel#panelTitle {{
        font-size: 12pt;
        font-weight: 600;
        padding-bottom: 4px;
    }}
    QLabel#toolbarMeta {{
        color: {c['text_muted']};
        padding: 0 8px;
    }}
    QWidget#settingsPanel {{
        background-color: {c['surface']};
        border-left: 1px solid {c['border']};
        padding: 12px;
    }}
    QGroupBox {{
        border: 1px solid {c['border']};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 14px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
        color: {c['text_muted']};
    }}
    QComboBox, QSpinBox {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px 8px;
        min-height: 24px;
    }}
    QCheckBox {{
        spacing: 8px;
    }}
    """
