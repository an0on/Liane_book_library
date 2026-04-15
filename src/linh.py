import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date, timedelta

# --- 1. CONNECTION ---
DB_URL = "mysql+pymysql://root:PASSWORD@localhost/liane_library"
db = create_engine(DB_URL)

def run_sql(query, variables):
    with db.connect() as conn:
        conn.execute(text(query), variables)
        conn.commit()

# --- 2. NAVIGATION ---
page = st.sidebar.radio("Go to:", ["Inventory", "Add Book", "Add Friend", "Active Loan", "Return Loan"])

# --- 3. PAGES ---

if page == "Inventory":
    st.title(":books: Inventory")
    st.subheader("Books")
    st.dataframe(pd.read_sql("SELECT * FROM books", db), use_container_width=True)
    st.subheader("Friends")
    st.dataframe(pd.read_sql("SELECT * FROM borrowers", db), use_container_width=True)

elif page == "Add Book":
    st.title(":book: Add Book")
    with st.form("book_form"):
        t, a = st.text_input("Title"), st.text_input("Author")
        if st.form_submit_button("Save"):
            run_sql("INSERT INTO books (Title, Author) VALUES (:t, :a)", {"t": t, "a": a})
            st.success("Book added!")

elif page == "Add Friend":
    st.title(":bust_in_silhouette: Add Friend")
    with st.form("friend_form"):
        fn, ln = st.text_input("First Name"), st.text_input("Last Name")
        if st.form_submit_button("Save"):
            run_sql("INSERT INTO borrowers (FirstName, LastName) VALUES (:f, :l)", {"f": fn, "l": ln})
            st.success("Friend added!")

# --- loan and return pages ---
elif page == "Active Loan":
    st.title(":handshake: Create a Loan")

    books_df = pd.read_sql("SELECT BookID, Title FROM books", db)
    friends_df = pd.read_sql("SELECT BorrowerID, FirstName FROM borrowers", db)

    with st.form("loan_form"):
        selected_book = st.selectbox("Which book?", books_df["Title"])
        selected_friend = st.selectbox("Who is borrowing it?", friends_df["FirstName"])

        # calculate today's date and a default return date (e.g., 14 days from now)
        today = date.today()
        return_date = today + timedelta(days=14) # Standard: 14 days

        st.write(f":date: **Borrow Date:** {today}")
        st.write(f":alarm_clock: **Scheduled Return:** {return_date}")

        if st.form_submit_button("Confirm Loan"):
            b_id = books_df[books_df["Title"] == selected_book]["BookID"].values[0]
            f_id = friends_df[friends_df["FirstName"] == selected_friend]["BorrowerID"].values[0]

            # Save all 4 pieces of info: Book, Friend, Start, and End
            query = """
                INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate)
                VALUES (:b, :f, :d1, :d2)
            """
            run_sql(query, {"b": int(b_id), "f": int(f_id), "d1": today, "d2": return_date})
            st.success(f"Loan created! {selected_book} is due back on {return_date}.")

elif page == "Return Loan":
    st.title(":back: Return a Book")

    # We show the names AND the return dates
    query = """
        SELECT l.LoanID, b.Title, br.FirstName, l.BorrowDate, l.ScheduledReturnDate
        FROM loans l
        JOIN books b ON l.BookID = b.BookID
        JOIN borrowers br ON l.BorrowerID = br.BorrowerID
    """
    loans_df = pd.read_sql(query, db)
    st.dataframe(loans_df, use_container_width=True)

    loan_id = st.number_input("Enter Loan ID to close", min_value=1)
    if st.button("Mark as Returned"):
        run_sql("DELETE FROM loans WHERE LoanID = :id", {"id": loan_id})
        st.warning("Book returned successfully!")