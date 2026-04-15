import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from connect import connection_string
import sample  


# --- 1. Seitenkonfiguration ---
st.set_page_config(
    page_title="Lianes Bibliothek", 
    page_icon="📚", 
    layout="wide"
)

# --- 2. Datenbankverbindung ---
@st.cache_resource
def init_connection():
    engine = create_engine(connection_string)
    return engine

engine = init_connection()


# --- 3. Navigation (Sidebar) ---
st.sidebar.title("📚 Lianes Bibliothek")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation", 
    ["🏠 Startseite", "📖 Bücherkatalog", "Ausgeliehene Bücher", "⚙️ Admin-Bereich"]
)

# --- 4. Seiten-Inhalte ---
if page == "🏠 Startseite":
    st.title("Willkommen in Lianes Bibliothek")
    st.write("Hier kannst du durch Lianes Buchsammlung stöbern.")
    st.info("Hier bauen wir später ein paar coole Statistiken ein (z.B. 'Aktuell verfügbare Bücher').")

elif page == "📖 Bücherkatalog":
    st.title("Bücherkatalog")
    st.write("Suche nach deinem nächsten Lieblingsbuch.")
    
    books_df = sample.read_db(engine, "books")
    if not books_df.empty:
        st.dataframe(books_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Die Bibliothek ist noch leer. Liane muss erst Bücher hinzufügen!")
elif page == "Ausgeliehene Bücher":
    st.title("Ausgeliehene Bücher")
    st.write("Hier siehst du, welche Bücher aktuell verliehen sind.")
    
    query = """
        SELECT b.Title, br.FirstName, br.LastName, l.ScheduledReturnDate
        FROM loans l
        JOIN books b ON l.BookID = b.BookID
        JOIN borrowers br ON l.BorrowerID = br.BorrowerID
        WHERE l.ReturnDate IS NULL;
    """
    loans_df = pd.read_sql(query, con=engine)
    
    if not loans_df.empty:
        st.dataframe(loans_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aktuell sind keine Bücher verliehen.")

elif page == "⚙️ Admin-Bereich":
    st.title("Verwaltung")
    st.write("Dieser Bereich ist später passwortgeschützt und nur für Liane gedacht.")
    
    # Platzhalter für das Formular zum Hinzufügen von Büchern
    with st.expander("➕ Neues Buch hinzufügen"):
        # st.write("Hier kommt bald das Eingabeformular hin.")
        sample.create_book(engine)
        
    with st.expander("➕ Neuen Freund anlegen"):
        # st.write("Hier kommt bald das Eingabeformular hin.")
        sample.add_borrower(engine)
        
    with st.expander("➕ Neuen Ausleihvorgang anlegen"):
        # st.write("Hier kommt bald das Eingabeformular hin.")
        sample.loan_book(engine)
        
    with st.expander("➕ Buch zurückgeben", expanded=True):
        # st.write("Hier kommt bald das Eingabeformular hin.")
        sample.return_book(engine)