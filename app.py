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

# Funktion zur Verarbeitung der eBKP-H Excel-Datei
def process_ebkph_file(file, convert_types=True):
    """
    Diese Funktion liest die hochgeladene eBKP-H Excel-Datei, hebt die Header an,
    und prüft auf doppelte Headerzeilen im gesamten Dokument ausserhalb der ersten 10 Zeilen.
    """
    # Fortschrittsbalken initialisieren
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. Schritt: Excel-Datei laden
        status_text.text("Lade Excel-Datei...")
        xls = pd.ExcelFile(file)
        df = pd.read_excel(xls, sheet_name='eBKP-H', header=None)  # Keine Header angeben
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
            if "Teilprojekt" in df.iloc[i].values and "Geschoss" in df.iloc[i].values:
                header_index = i
                break

        if header_index is None:
            st.error("Spalten 'Teilprojekt' und 'Geschoss' wurden in den ersten 10 Zeilen nicht gefunden.")
            return None
        
        # Header festlegen und Zeilen oberhalb entfernen
        df.columns = df.iloc[header_index]  # Setze die gefundene Zeile als Header
        df = df[header_index + 1:].reset_index(drop=True)  # Entferne Zeilen oberhalb
        progress_bar.progress(40)
        st.success("Schritt 2: Header erfolgreich verschoben")

        # 3. Schritt: Überprüfen auf doppelte Headerzeilen ausserhalb der obersten 10 Zeilen
        status_text.text("Überprüfe auf doppelte Headerzeilen ausserhalb der ersten 10 Zeilen...")
        rows_to_drop = []  # Liste zum Speichern der zu löschenden Zeilen

        # Überprüfen der Zeilen nach der 10. Zeile
        for i in range(10, len(df)):
            # Überprüfen, ob in Spalte 1 "Teilprojekt" und in Spalte 2 "Geschoss" steht
            if df.iloc[i, 0] == "Teilprojekt" and df.iloc[i, 1] == "Geschoss":
                rows_to_drop.append(i)  # Markiere die Zeile zum Löschen

        # Lösche die markierten Zeilen
        df.drop(rows_to_drop, inplace=True)
        df.reset_index(drop=True, inplace=True)  # Index neu setzen
        progress_bar.progress(60)
        st.success("Schritt 3: Doppelte Header ausserhalb der ersten 10 Zeilen erfolgreich entfernt")

        # 4. Schritt: Ersetze "<Nicht definiert>" und "---" durch leere Strings
        status_text.text('Ersetze "<Nicht definiert>" und "---"...')
        df.replace({"<Nicht definiert>": "", "---": ""}, inplace=True)
        progress_bar.progress(80)
        st.success('Schritt 4: "<Nicht definiert>" und "---" erfolgreich ersetzt')

        # 5. Schritt: Optional: Datentypen konvertieren oder alles als String behandeln
        if convert_types:
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
            
            # Ersetze alle NaN-Werte durch leere Strings
            df.fillna("", inplace=True)
            st.success("Schritt 5: Datentypen erfolgreich konvertiert und NaN-Werte durch leere Zellen ersetzt")
        else:
            # Falls die Konvertierung deaktiviert ist, werden alle Spalten als Strings behandelt
            status_text.text("Alle Spalten werden als String behandelt...")
            df = df.astype(str).fillna("")  # Ersetze NaN-Werte durch leere Strings
            st.info("Schritt 5: Datentyp-Konvertierung deaktiviert, alle Spalten sind Strings und NaN-Werte entfernt")

        progress_bar.progress(100)

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
    file = st.file_uploader("Lade deine eBKP-H-Datei hoch", type=["xlsx"])

    # Toggle für Datentyp-Konvertierung
    convert_types = st.checkbox("Datentypen konvertieren (wenn deaktiviert, alles als String)", value=False)

    if file:
        # Datei direkt aus dem hochgeladenen Stream verarbeiten
        df = process_ebkph_file(file, convert_types)  # Passiere den "convert_types"-Parameter
        
        # Button zum Herunterladen der verarbeiteten Datei als Excel
        if df is not None:
            excel_data = convert_df_to_excel(df)
            # Ursprünglichen Dateinamen mit der Ergänzung "_gesäubert" verwenden
            original_filename = file.name.rsplit('.', 1)[0]  # Entfernt die Dateiendung
            cleaned_filename = f"{original_filename}_gesäubert.xlsx"
            
            st.download_button(
                label="Download verarbeitete Datei",
                data=excel_data,
                file_name=cleaned_filename,  # Verwendet den modifizierten Dateinamen
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


            # Zeige die verarbeiteten Daten an
            st.write("Verarbeitete Daten:")
            st.dataframe(df)




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
