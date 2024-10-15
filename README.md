# eBKP-H Excel Verarbeitungs-App

Diese Streamlit-App ermöglicht das sichere Hochladen und Verarbeiten von eBKP-H Excel-Dateien. Die App enthält ein Login-System, das durch Streamlit Secrets geschützt wird. Nach erfolgreichem Login kann eine Excel-Datei hochgeladen werden, die dann verarbeitet und die Inhalte mit den korrekten Datentypen in der App angezeigt werden.

## Features

- **Sicheres Login**: Benutzername und Passwort werden über Streamlit Secrets verwaltet.
- **Excel-Dateiverarbeitung**: Die App liest die hochgeladene eBKP-H Excel-Datei, konvertiert die Spalten in die korrekten Datentypen und zeigt die Daten an.
- **Session Management**: Der Login-Zustand wird über Streamlit Session State verwaltet.

## Voraussetzungen

Stelle sicher, dass die folgenden Voraussetzungen erfüllt sind, um die App auszuführen:

- Python 3.7 oder höher
- Abhängigkeiten in `requirements.txt`
- Streamlit installiert (`pip install streamlit`)
- Eine `.streamlit/secrets.toml` Datei, die die Anmeldedaten enthält

## Installation

1. **Repository klonen**:

   ```bash
   git clone https://github.com/yourusername/ebkph-app.git
   cd ebkph-app
