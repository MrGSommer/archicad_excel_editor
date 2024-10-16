import streamlit as st
import pandas as pd
import io

# Zugriff auf die Secrets
username_secrets = st.secrets["credentials"]["username"]
password_secrets = st.secrets["credentials"]["password"]



# Funktion zum Konvertieren des DataFrames in Excel und Bereitstellen zum Download
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Funktion zum Hochladen, Verarbeiten und Bereitstellen der Excel-Dateien
def handle_excel_file_processing(tab_title, sheet_name, header_keys):
    st.header(f"{tab_title} Datei Verarbeitung")
    file = st.file_uploader(f"Lade deine {tab_title} Datei hoch", type=["xlsx"])

    # Checkbox für Datentyp-Konvertierung
    convert_types = st.checkbox(f"Datentypen konvertieren für {tab_title} (wenn deaktiviert, alles als String)", value=False)

    if file:
        # Verarbeite die Datei und zeige den Fortschritt
        df = process_excel_file(file, sheet_name=sheet_name, header_keys=header_keys, convert_types=convert_types)

        # Wenn die Verarbeitung erfolgreich war, zeige die Optionen für den Download und die Datenvorschau an
        if df is not None:
            excel_data = convert_df_to_excel(df)
            cleaned_filename = f"{file.name.rsplit('.', 1)[0]}_gesäubert.xlsx"
            
            st.download_button(
                label=f"Download verarbeitete {tab_title} Datei",
                data=excel_data,
                file_name=cleaned_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.write(f"Verarbeitete {tab_title} Daten:")
            st.dataframe(df)

# Funktion zur Verarbeitung von Excel-Dateien (aus den gemeinsamen Logiken)
def process_excel_file(file, sheet_name, header_keys, convert_types=True):
    """
    Diese Funktion liest eine Excel-Datei, hebt die Header an,
    prüft auf doppelte Headerzeilen und konvertiert die Datentypen, falls erforderlich.
    """
    # Fortschrittsbalken initialisieren
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. Schritt: Excel-Datei laden
        status_text.text("Lade Excel-Datei...")
        xls = pd.ExcelFile(file)
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None, keep_default_na=False)
        progress_bar.progress(20)
        st.success("Schritt 1: Excel-Datei erfolgreich geladen")

        # Überprüfen, ob die Datei genügend Zeilen hat
        if len(df) < 10:
            st.error("Die Excel-Datei enthält weniger als 10 Zeilen. Überprüfen Sie die Datei.")
            return None

        # 2. Schritt: Headerzeile identifizieren
        status_text.text("Suche nach der Headerzeile...")
        header_index = None
        for i in range(10):  # Nur die ersten 10 Zeilen durchsuchen
            if all(key in df.iloc[i].values for key in header_keys):
                header_index = i
                break

        if header_index is None:
            st.error(f"Spalten {', '.join(header_keys)} wurden in den ersten 10 Zeilen nicht gefunden.")
            return None
        
        # Header festlegen und Zeilen oberhalb entfernen
        df.columns = df.iloc[header_index]
        df = df[header_index + 1:].reset_index(drop=True)
        progress_bar.progress(40)
        st.success("Schritt 2: Header erfolgreich verschoben")

        # 3. Schritt: Überprüfen auf doppelte Headerzeilen ausserhalb der obersten 10 Zeilen
        status_text.text("Überprüfe auf doppelte Headerzeilen ausserhalb der ersten 10 Zeilen...")
        rows_to_drop = []  # Liste zum Speichern der zu löschenden Zeilen

        for i in range(10, len(df)):
            if all(key in df.iloc[i].values for key in header_keys):
                rows_to_drop.append(i)  # Markiere die Zeile zum Löschen

        df.drop(rows_to_drop, inplace=True)
        df.reset_index(drop=True, inplace=True)
        progress_bar.progress(60)
        st.success("Schritt 3: Doppelte Header ausserhalb der ersten 10 Zeilen erfolgreich entfernt")

        # 4. Schritt: Ersetze "<Nicht definiert>" und "---" durch leere Strings
        status_text.text('Ersetze "<Nicht definiert>" und "---"...')
        df.replace({"<Nicht definiert>": "", "---": ""}, inplace=True)
        progress_bar.progress(80)
        st.success('Schritt 4: "<Nicht definiert>" und "---" erfolgreich ersetzt')

        # 5. Schritt: Datentypen konvertieren (je nach Arbeitsblatt)
        if convert_types:
            status_text.text("Konvertiere Datentypen...")

            if sheet_name == "eBKP-H":
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

            elif sheet_name == "SIA416":
                dtype_conversion = {
                    # Hier die Spaltennamen aus der SIA416 Datei anpassen
                    "Spaltenname1": str,
                    "Spaltenname2": float,
                    "Spaltenname3": 'Int64',  # Beispiel: Null-fähige Ganzzahl
                    # Füge hier die korrekten Spaltennamen und Datentypen für die SIA416 Datei ein
                }

            # Konvertiere die Datentypen für die definierten Spalten
            for column, dtype in dtype_conversion.items():
                if column in df.columns:
                    try:
                        df[column] = df[column].astype(dtype)
                    except ValueError:
                        st.warning(f"Fehler bei der Konvertierung der Spalte {column}.")
            
            df.fillna("", inplace=True)
            st.success("Schritt 5: Datentypen erfolgreich konvertiert und NaN-Werte durch leere Zellen ersetzt")
        else:
            status_text.text("Alle Spalten werden als String behandelt...")
            df = df.astype(str).fillna("")
            st.info("Schritt 5: Datentyp-Konvertierung deaktiviert, alle Spalten sind Strings und NaN-Werte entfernt")

        progress_bar.progress(100)
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

# Layout mit zwei Spalten
col1, col2 = st.columns([1, 1])  # Optional kannst du die Breite der Spalten anpassen, z.B. [1, 2]

with col1:
    login()  # Hier platzierst du das Login-Formular in der ersten Spalte

# Hauptanwendung mit Tabs und zusammengefasstem Code
def main_app():
    st.write(f"Willkommen, {username_secrets}!")

    # Verwende Tabs für eine bessere Übersicht
    tab1, tab2 = st.tabs(["eBKP-H Datei", "SIA416 Datei"])

    # Tab für eBKP-H Datei-Verarbeitung
    with tab1:
        handle_excel_file_processing(tab_title="eBKP-H", sheet_name="eBKP-H", header_keys=["Teilprojekt", "Geschoss"])

    # Tab für SIA416 Datei-Verarbeitung
    with tab2:
        handle_excel_file_processing(tab_title="SIA416", sheet_name="SIA416", header_keys=["Teilprojekt", "Geschoss"])

# Hauptfunktion der App
def app():
    """
    Stellt sicher, dass der Benutzer eingeloggt ist, bevor die Hauptanwendung gestartet wird.
    Wenn der Benutzer nicht eingeloggt ist, wird das Login-Formular angezeigt.
    """
    st.set_page_config(layout="wide")  # Aktiviert den "Wide Mode"
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login()
    else:
        main_app()





# Ausführen der App
if __name__ == "__main__":
    app()
