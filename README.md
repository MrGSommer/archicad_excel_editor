Diese Streamlit-App ermöglicht das sichere Hochladen und Verarbeiten von Excel-Dateien, wie **eBKP-H** und **SIA416**. Die App enthält ein Login-System, das durch Streamlit Secrets geschützt wird. Nach erfolgreichem Login können Excel-Dateien hochgeladen werden, die dann verarbeitet und deren Inhalte mit den korrekten Datentypen in der App angezeigt werden.

## Features

- **Sicheres Login**: Benutzername und Passwort werden über Streamlit Secrets verwaltet.
- **Excel-Dateiverarbeitung**: Die App liest die hochgeladene Excel-Datei, identifiziert die Header, entfernt doppelte Headerzeilen und konvertiert die Spalten in die korrekten Datentypen (optional).
- **Datenbereinigung**: Standardisierte Ersetzung von "<Nicht definiert>" und "---" durch leere Strings.
- **Download-Funktion**: Nach der Verarbeitung der Datei kann die bereinigte Excel-Datei heruntergeladen werden.
- **Fortschrittsanzeige**: Fortschrittsbalken und Statusmeldungen zeigen den Verarbeitungsstand der Datei an.
- **Tab-Ansicht für unterschiedliche Dateitypen**: Verwende Tabs, um zwischen eBKP-H und SIA416 Dateien zu wechseln.
- **Session Management**: Der Login-Zustand wird über Streamlit Session State verwaltet.

## Voraussetzungen

Stelle sicher, dass die folgenden Voraussetzungen erfüllt sind, um die App auszuführen:

- Python 3.7 oder höher
- Abhängigkeiten in `requirements.txt`
- Streamlit installiert (`pip install streamlit`)
- Eine `.streamlit/secrets.toml` Datei, die die Anmeldedaten enthält (z.B. Benutzername und Passwort).

## Installation

1. **Repository klonen**:

   ```bash
   gh repo clone username/streamlit_excel_processing_app
   cd streamlit_excel_processing_app
   ```

2. **Abhängigkeiten installieren**:

   ```bash
   pip install -r requirements.txt
   ```

3. **App ausführen**:

   ```bash
   streamlit run app.py
   ```

4. **Anmeldedaten einrichten**:

   Erstelle eine Datei `.streamlit/secrets.toml` und füge die Anmeldedaten hinzu:

   ```toml
   [credentials]
   username = "your_username"
   password = "your_password"
   ```

