import streamlit as st
import pandas as pd
import os

# Zugriff auf die Secrets
username_secrets = st.secrets["credentials"]["username"]
password_secrets = st.secrets["credentials"]["password"]

# Funktion zur Verarbeitung der eBKP-H Excel-Datei
def process_ebkph_file(file):
    
    """
    Diese Funktion liest die hochgeladene eBKP-H Excel-Datei, hebt die Header an und
    konvertiert die Spalten zu den richtigen Datentypen.
    """

    # Fortschrittsbalken initialisieren
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. Schritt: Excel-Datei laden
        status_text.text("Lade Excel-Datei...")
        xls = pd.ExcelFile(file)
        df = pd.read_excel(xls, sheet_name='eBKP-H')
        progress_bar.progress(20)
        st.success("Schritt 1: Excel-Datei erfolgreich geladen")

        # 2. Schritt: Header um eine Zeile nach oben verschieben
        status_text.text("Verschiebe Header...")
        df.columns = df.iloc[0]  # Verschiebe nur eine Zeile
        df = df[1:]  # Entferne die erste Zeile, die nun die Header ist
        progress_bar.progress(40)
        st.success("Schritt 2: Header erfolgreich verschoben")

        # 3. Schritt: Ersetze "<Nicht definiert>" und "---" durch leere Strings
        status_text.text('Ersetze "<Nicht definiert>" und "---"...')
        df.replace({"<Nicht definiert>": "", "---": ""}, inplace=True)
        progress_bar.progress(60)
        st.success('Schritt 3: "<Nicht definiert>" und "---" erfolgreich ersetzt')

        # 4. Schritt: Entferne leere Zeilen
        status_text.text("Entferne leere Zeilen...")
        df.dropna(how='all', inplace=True)
        progress_bar.progress(80)
        st.success("Schritt 4: Leere Zeilen erfolgreich entfernt")

        # 5. Schritt: Datentypen konvertieren (hier mit einfachen Beispielen)
        status_text.text("Konvertiere Datentypen...")
        dtype_conversion = {
            "Teilprojekt": str,
            "Geschoss": str,
            "eBKP-H": str,
            "Ergänzung": str,
            "Klassifizierung": str,
            "Baustoffe": str,
            "Bauteilname": str,
            "Unter Terrain": 'boolean',
            "Schichtdicke": float,
            "Fläche": float,
            "Länge": float,
            "Volumen": float,
            "Höhe": float,
            "Breite": float,
            "Menge": 'Int64',  # Null-fähige Ganzzahlen
            "Erdverbunden": 'boolean',
            "Spezialeigenschaft": str,
            "Türtyp": str,
            "Tortyp": str,
            "Geländerart": str,
            "Flügelanzahl": str,
            "Überhöhe (über 3m)": 'boolean',
            "Oberfläche oben": str,
            "Oberfläche unten": str,
            "Oberfläche Aussenseite": str,
            "Oberfläche Innenseite": str,
            "Stützenform": str,
            "Stützenbreite": float,
            "Stützentiefe": float,
            "Stützenhöhe": float,
            "Vorhangschiene": float,
            "Sonnenschutz": 'boolean',
            "Verschattung": str,
            "Schallschutzanforderung": str,
            "Anzahl der Trittstufen (gesamt)": float,
            "Standard-Steigungshöhe": float,
            "Standard-Auftrittstiefe": float,
            "Standard-Treppenbreite": float,
            "Bauteildicke": float
        }

        # Konvertiere die Datentypen für die definierten Spalten
        for column, dtype in dtype_conversion.items():
            if column in df.columns:
                try:
                    df[column] = df[column].astype(dtype)
                except ValueError:
                    st.warning(f"Fehler bei der Konvertierung der Spalte {column}.")
        progress_bar.progress(100)
        st.success("Schritt 5: Datentypen erfolgreich konvertiert")

        # Rückgabe des DataFrames
        return df

    except Exception as e:
        st.error(f"Fehler bei der Verarbeitung: {e}")
        return None

# Funktion für das Login-Formular
def login():
    """
    Zeigt das Login-Formular an und überprüft den eingegebenen Benutzernamen und das Passwort.
    Wenn die Anmeldedaten korrekt sind, wird der Benutzer als eingeloggt markiert.
    """
    st.session_state["logged_in"] = False

    st.write("Bitte einloggen")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == username_secrets and password == password_secrets:
            st.success("Login erfolgreich")
            st.session_state["logged_in"] = True
        else:
            st.error("Falscher Username oder Passwort. Wenden Sie sich an Ihren Systemadministrator")

# Hauptanwendung, wenn der Benutzer eingeloggt ist
def main_app():
    """
    Hauptfunktion der App, die nach erfolgreichem Login angezeigt wird.
    Bietet die Möglichkeit, eine Excel-Datei hochzuladen, temporär zu speichern und zu verarbeiten.
    """
    st.write(f"Willkommen, {username_secrets}!")
    
    # Datei-Upload-Funktion
    uploaded_file = st.file_uploader("Lade deine eBKP-H-Datei hoch", type=["xlsx"])

    if uploaded_file:
        # Datei direkt aus dem hochgeladenen Stream verarbeiten
        df = process_ebkph_file(uploaded_file)
        
        # Zeige die verarbeiteten Daten an
        st.write("Verarbeitete Daten:")
        st.dataframe(df)

# Hauptfunktion der App
def app():
    """
    Stellt sicher, dass der Benutzer eingeloggt ist, bevor die Hauptanwendung gestartet wird.
    Wenn der Benutzer nicht eingeloggt ist, wird das Login-Formular angezeigt.
    """
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login()
    else:
        main_app()

# Ausführen der App
if __name__ == "__main__":
    app()
