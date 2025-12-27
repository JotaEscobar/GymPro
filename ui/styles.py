# -*- coding: utf-8 -*-
"""
Estilos globales de la aplicación
"""

# ========== ESTILOS DE BOTONES ESTANDARIZADOS ==========

BUTTON_STYLES = {
    'primary': """
        QPushButton {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        QPushButton:disabled {
            background-color: #94a3b8;
            color: #cbd5e1;
        }
    """,
    
    'success': """
        QPushButton {
            background-color: #22c55e;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #16a34a;
        }
        QPushButton:pressed {
            background-color: #15803d;
        }
        QPushButton:disabled {
            background-color: #94a3b8;
            color: #cbd5e1;
        }
    """,
    
    'danger': """
        QPushButton {
            background-color: #ef4444;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #dc2626;
        }
        QPushButton:pressed {
            background-color: #b91c1c;
        }
        QPushButton:disabled {
            background-color: #94a3b8;
            color: #cbd5e1;
        }
    """,
    
    'secondary': """
        QPushButton {
            background-color: #64748b;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #475569;
        }
        QPushButton:pressed {
            background-color: #334155;
        }
        QPushButton:disabled {
            background-color: #94a3b8;
            color: #cbd5e1;
        }
    """,
    
    'warning': """
        QPushButton {
            background-color: #f59e0b;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #d97706;
        }
        QPushButton:pressed {
            background-color: #b45309;
        }
        QPushButton:disabled {
            background-color: #94a3b8;
            color: #cbd5e1;
        }
    """,
    
    'outline': """
        QPushButton {
            background-color: transparent;
            color: #64748b;
            border: 2px solid #cbd5e1;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #f8fafc;
            border-color: #94a3b8;
            color: #475569;
        }
        QPushButton:pressed {
            background-color: #e2e8f0;
        }
        QPushButton:disabled {
            color: #cbd5e1;
            border-color: #e2e8f0;
        }
    """,
    
    'ghost': """
        QPushButton {
            background-color: transparent;
            color: #64748b;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #f8fafc;
            color: #475569;
        }
        QPushButton:pressed {
            background-color: #e2e8f0;
        }
        QPushButton:disabled {
            color: #cbd5e1;
        }
    """,
    
    'icon_small': """
        QPushButton {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px;
            min-width: 32px;
            min-height: 32px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
    """
}

# ========== ESTILO OSCURO GLOBAL ==========

ESTILO_OSCURO = """
/* --- FONDO GENERAL --- */
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* --- PESTAÑAS (TABS) --- */
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}

/* --- CAMPOS DE TEXTO (INPUTS) --- */
QLineEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 6px;
    color: #ffffff;
    padding: 8px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 2px solid #89b4fa;
}

/* --- BOTONES (DEPRECATED - Usar BUTTON_STYLES) --- */
QPushButton {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border-radius: 6px;
    padding: 10px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #94e2d5;
}
QPushButton:pressed {
    background-color: #89dceb;
}

/* --- TABLA --- */
QTableWidget {
    background-color: #181825;
    gridline-color: #313244;
    border: none;
    border-radius: 8px;
}
QHeaderView::section {
    background-color: #313244;
    color: #ffffff;
    padding: 6px;
    border: none;
    font-weight: bold;
}

/* --- SELECCIÓN EN TABLAS --- */
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
"""
