import streamlit as st
import pandas as pd
import os

# Zugriff auf die Secrets
username_secrets = st.secrets["credentials"]["username"]
password_secrets = st.secrets["credentials"]["password"]

# Funktion zur Verarbeitung der eBKP-H Excel-Datei
def process_ebkph_file(file_path):
    """
    Diese Funktion liest die hochgeladene eBKP-H Excel-Datei, hebt die Header an und
    konvertiert die Spalten zu den richtigen Datentypen.
    """
    # Excel-Datei laden
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name='eBKP-H')

    # Header erhöhen
    df.columns = df.iloc[1]
    df = df[2:]

    # Ersetze "<Nicht definiert>" und "---" durch leere Strings
    df.replace({"<Nicht definiert>": "", "---": ""}, inplace=True)

    # Entferne leere Zeilen
    df.dropna(how='all', inplace=True)

    # Definiere Datentyp-Konvertierungen für alle Spalten
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

    # Alle Spalten, die nicht im Typen-Dictionary sind, als String behandeln
    for col in df.columns:
        if col not in dtype_conversion:
            dtype_conversion[col] = str

    # Konvertiere die Datentypen
    for column, dtype in dtype_conversion.items():
        try:
            df[column] = df[column].astype(dtype)
        except KeyError:
            st.warning(f"Spalte {column} fehlt in der Datei und wurde als String verarbeitet.")
        except ValueError:
            st.warning(f"Fehler bei der Konvertierung der Spalte {column} zu {dtype}. Einige Werte könnten unpassend sein.")

    return df

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
        # Temporäre Datei speichern
        temp_path = f"temp/{uploaded_file.name}"
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Datei {uploaded_file.name} erfolgreich hochgeladen und gespeichert.")
        
        # Datei verarbeiten
        df = process_ebkph_file(temp_path)
        
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
