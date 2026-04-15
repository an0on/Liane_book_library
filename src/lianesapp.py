import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from connect import connection_string
import sample  # Unsere ausgelagerte Datei "sample.py" importieren

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
st.sidebar.title("📚 Lianes 🚀 Bibliothek")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation", 
    ["🏠 Startseite", "📖 Bücherkatalog", "⚙️ Admin-Bereich"]
)

# --- 4. Seiten-Inhalte ---
if page == "🏠 Startseite":
    st.title("Willkommen in Lianes Bibliothek")
    st.write("Schlauer Text.")
    st.info("Hier bauen wir später ein paar Statistiken ein (z.B. Button 'Aktuell verfügbare Bücher' usw.).")

elif page == "📖 Bücherkatalog":
    st.title("Bücherkatalog")
    st.write("Suche nach deinem nächsten Lieblingsbuch.")
    
    # Beispiel Datenbankabruf
    try:
        query = "SELECT Title, Author, Genre, Isbn FROM books"
        df_books = pd.read_sql(query, con=engine)
        
        if not df_books.empty:
            st.dataframe(df_books, use_container_width=True, hide_index=True)
        else:
            st.warning("Die Bibliothek ist noch leer. Liane muss erst Bücher hinzufügen!")
    except Exception as e:
        st.error("Fehler bei der Datenbankverbindung oder beim Laden der Bücher.")

elif page == "⚙️ Admin-Bereich":
    # Wir rufen hier nun einfach die Funktion aus 'sample.py' auf 
    # und übergeben unsere Datenbankverbindung!
    sample.render_admin_bereich(engine)