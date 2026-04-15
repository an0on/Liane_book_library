import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

OPEN_LIBRARY_URL = "https://openlibrary.org"

def get_cover_url(isbn: str, size: str = "M") -> str:
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"



def read_db(engine, table):
    query = f"SELECT * FROM {table};"
    return pd.read_sql(query, con=engine)

def insert_db(engine, table, query_dict):
    filtered_keys = [k for k, v in query_dict.items() if v is not None and str(v).strip() != ""]
    if not filtered_keys:
        st.warning("Keine Daten zum Einfügen vorhanden.")
        return False
        
    columns = ", ".join(filtered_keys)
    placeholders = ", ".join([f":{k}" for k in filtered_keys])

    query = f"""
        INSERT INTO {table} ({columns})
        VALUES ({placeholders});
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(query), query_dict)
            transaction.commit()
            return True
        except Exception as e:
            transaction.rollback()
            st.error(f"Fehler beim Speichern in der Datenbank: {e}")
            return False

def create_book(engine):
    """Das Formular zum Erstellen eines neuen Buches."""
    with st.form("create_book"):
        title = st.text_input("Titel (Pflichtfeld):")
        author = st.text_input("Autor:")
        genre = st.text_input("Genre:")
        isbn = st.text_input("ISBN:")
        
        check_form = st.form_submit_button("Buch eintragen")

        if check_form:
            if not title:
                st.warning("Der Titel darf nicht leer sein!")
            else:
                query_dict = {
                    "Title": title,
                    "Author": author,
                    "Genre": genre,
                    "Isbn": isbn
                }
                if insert_db(engine, "books", query_dict):
                    st.success(f"Buch '{title}' erfolgreich hinzugefügt!")

def add_borrower(engine):
    """Das Formular zum Hinzufügen eines neuen Freundes/Ausleihers."""
    with st.form("add_borrower"):
        first_name = st.text_input("Vorname:")
        last_name = st.text_input("Nachname:")
        email = st.text_input("E-Mail:")
        phone = st.text_input("Telefonnummer:")
        
        check_form = st.form_submit_button("Freund hinzufügen")
        
        if check_form:
            if not first_name or not last_name:
                st.warning("Vorname und Nachname sind Pflichtfelder!")
            else:
                query_dict = {
                    "FirstName": first_name,
                    "LastName": last_name,
                    "Email": email,
                    "PhoneNumber": phone
                }
                if insert_db(engine, "borrowers", query_dict):
                    st.success(f"{first_name} {last_name} wurde als Freund angelegt!")

def loan_book(engine):
    """Das Formular zum Ausleihen eines Buches."""
    # Lade aktuelle Bücher und Freunde für die Dropdowns
    try:
        books_df = pd.read_sql("SELECT BookID, Title FROM books", con=engine)
        borrowers_df = pd.read_sql("SELECT BorrowerID, FirstName, LastName FROM borrowers", con=engine)
    except Exception as e:
        st.error(f"Datenbankfehler beim Laden der Daten: {e}")
        return

    if books_df.empty or borrowers_df.empty:
        st.warning("Es müssen zuerst Bücher und Freunde angelegt werden, bevor man etwas ausleihen kann.")
        return

    # Optionen für Dropdowns vorbereiten
    book_options = {row['Title']: row['BookID'] for _, row in books_df.iterrows()}
    borrower_options = {f"{row['FirstName']} {row['LastName']}": row['BorrowerID'] for _, row in borrowers_df.iterrows()}

    with st.form("loan_book"):
        selected_book = st.selectbox("Welches Buch soll ausgeliehen werden?", list(book_options.keys()))
        selected_borrower = st.selectbox("An wen?", list(borrower_options.keys()))
        
        scheduled_return = st.date_input("Geplante Rückgabe am:", datetime.date.today() + datetime.timedelta(days=60))
        
        check_form = st.form_submit_button("Buch verleihen")
        
        if check_form:
            query_dict = {
                "BookID": book_options[selected_book],
                "BorrowerID": borrower_options[selected_borrower],
                "ScheduledReturnDate": scheduled_return
            }
            if insert_db(engine, "loans", query_dict):
                st.success(f"'{selected_book}' wurde erfolgreich an {selected_borrower} verliehen!")

def render_admin_bereich(engine):
    """Diese Funktion baut die komplette Seite für den Admin-Bereich auf."""
    st.title("Verwaltung ⚙️")
    st.write("Dieser Bereich ist später passwortgeschützt.")
    
    # Auswahlmenü, was im Adminbereich gemacht werden soll
    display = st.radio(
        "Was möchtest du tun?",
        options=[
            "📘 Neues Buch registrieren",
            "📖 Buch ausleihen",
            "🧑 Freund hinzufügen"
        ],
        horizontal=True
    )
    
    if display == "📘 Neues Buch registrieren":
        with st.expander("➕ Neues Buch hinzufügen", expanded=True):
            create_book(engine)
            
    elif display == "📖 Buch ausleihen":
        with st.expander("🤝 Buch verleihen", expanded=True):
            loan_book(engine)
        
    elif display == "🧑 Freund hinzufügen":
        with st.expander("👤 Neuen Freund anlegen", expanded=True):
            add_borrower(engine)

from sqlalchemy import text
import pandas as pd
import streamlit as st

def return_book(engine):
    """Das Formular zur Rückgabe eines Buches."""
    st.write("Wähle ein verliehenes Buch aus, um es wieder in die Bibliothek aufzunehmen.")
    
    # 1. Alle aktuell verliehenen Bücher suchen (ReturnDate IS NULL)
    # Wir verknüpfen (JOIN) die Tabellen, damit wir echte Namen und Titel sehen, nicht nur IDs.
    query = """
        SELECT l.LoanID, b.Title, br.FirstName, br.LastName 
        FROM loans l
        JOIN books b ON l.BookID = b.BookID
        JOIN borrowers br ON l.BorrowerID = br.BorrowerID
        WHERE l.ReturnDate IS NULL
    """
    
    try:
        active_loans_df = pd.read_sql(query, con=engine)
    except Exception as e:
        st.error(f"Datenbankfehler beim Laden der aktiven Ausleihen: {e}")
        return

    # 2. Prüfen, ob überhaupt Bücher verliehen sind
    if active_loans_df.empty:
        st.info("Aktuell sind keine Bücher verliehen. Alles steht sicher im Regal!")
        return

    # 3. Optionen für das Dropdown vorbereiten
    # Das Format wird z.B.: "Harry Potter - ausgeliehen an Peter Pan" -> LoanID
    loan_options = {}
    for _, row in active_loans_df.iterrows():
        label = f"{row['Title']} - ausgeliehen an {row['FirstName']} {row['LastName']}"
        loan_options[label] = row['LoanID']

    # 4. Das Formular
    with st.form("return_book_form"):
        selected_loan_label = st.selectbox("Welches Buch hast du zurückbekommen?", list(loan_options.keys()))
        
        submit_return = st.form_submit_button("✅ Buch als zurückgegeben markieren")
        
        if submit_return:
            loan_id_to_return = loan_options[selected_loan_label]
            
            # 5. Datenbank-Update: Wir setzen das Rückgabedatum auf den heutigen Tag
            update_query = text("""
                UPDATE loans 
                SET ReturnDate = CURRENT_DATE 
                WHERE LoanID = :loan_id
            """)
            
            with engine.connect() as conn:
                transaction = conn.begin()
                try:
                    conn.execute(update_query, {"loan_id": loan_id_to_return})
                    transaction.commit()
                    
                    # Den reinen Buchtitel aus dem String extrahieren für die Erfolgsmeldung
                    book_title = selected_loan_label.split(" - ")[0]
                    st.success(f"Super! '{book_title}' ist wieder da und verfügbar.")
                    
                    # WICHTIG: Die Seite neu laden, damit das Buch aus dem Dropdown verschwindet!
                    st.rerun() 
                    
                except Exception as e:
                    transaction.rollback()
                    st.error(f"Fehler bei der Rückgabe: {e}")