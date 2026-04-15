
import streamlit as st
import pandas as pd
import time
from sqlalchemy import create_engine, text
from datetime import date

try:
    from connect import connection_string
except ImportError:
    st.error("Could not find connect.py. Please make sure the file exists and connection_string is defined.")
    st.stop()

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    # Create engine (Compatible with SQLAlchemy 2.0)
    engine = create_engine(connection_string)
    return engine

engine = init_connection()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Liane's Library", page_icon="📚", layout="wide")

# --- SIDEBAR / NAVIGATION ---
st.sidebar.title("📚 Liane's Library")
st.sidebar.markdown("Navigation")
menu_selection = st.sidebar.radio(
    "",
    ["🏠 Home", "📖 Book Catalog", "📋 Borrowed Books", "⚙️ Admin Area"]
)

# --- PAGE LOGIC ---

if menu_selection == "🏠 Home":
    st.title("Welcome to Liane's Library")
    st.write("Here is a quick overview of your library status:")

    try:
        # 1. Basis-Statistiken abfragen
        total_books = pd.read_sql("SELECT COUNT(*) AS count FROM books", con=engine).iloc[0]['count']
        total_friends = pd.read_sql("SELECT COUNT(*) AS count FROM borrowers", con=engine).iloc[0]['count']
        borrowed_books = pd.read_sql("SELECT COUNT(*) AS count FROM loans WHERE ReturnDate IS NULL", con=engine).iloc[0]['count']
        overdue_books = pd.read_sql("SELECT COUNT(*) AS count FROM loans WHERE ReturnDate IS NULL AND ScheduledReturnDate < CURRENT_DATE", con=engine).iloc[0]['count']

        # 2. Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="📚 Total Books", value=int(total_books))
        with col2:
            st.metric(label="👥 Registered Friends", value=int(total_friends))
        with col3:
            st.metric(label="📦 Currently Borrowed", value=int(borrowed_books))
        with col4:
            st.metric(
                label="⚠️ Overdue Books", 
                value=int(overdue_books), 
                delta=f"{int(overdue_books)} Action required" if overdue_books > 0 else None,
                delta_color="inverse"
            )

        st.divider()

        # 3. Rankings (2x2 Raster)
        st.subheader("🏆 Library Rankings & 🚨 Wall of Shame")
        
        # --- ERSTE REIHE ---
        rank_col1, rank_col2 = st.columns(2)

        with rank_col1:
            st.markdown("#### ⭐ Most Popular Books")
            query_popular_books = """
                SELECT b.Title, COUNT(l.LoanID) as TimesBorrowed
                FROM loans l
                JOIN books b ON l.BookID = b.BookID
                GROUP BY b.Title
                ORDER BY TimesBorrowed DESC
                LIMIT 3
            """
            df_popular = pd.read_sql(query_popular_books, con=engine)
            if not df_popular.empty:
                for i, row in df_popular.iterrows():
                    st.write(f"{i+1}. **{row['Title']}** ({row['TimesBorrowed']} times)")
            else:
                st.write("No data yet.")

        with rank_col2:
            st.markdown("#### 🥇 Top Readers")
            query_top_readers = """
                SELECT br.FirstName, br.LastName, COUNT(l.LoanID) as TotalLoans
                FROM loans l
                JOIN borrowers br ON l.BorrowerID = br.BorrowerID
                GROUP BY br.BorrowerID
                ORDER BY TotalLoans DESC
                LIMIT 3
            """
            df_readers = pd.read_sql(query_top_readers, con=engine)
            if not df_readers.empty:
                for i, row in df_readers.iterrows():
                    st.write(f"{i+1}. **{row['FirstName']} {row['LastName']}** ({row['TotalLoans']} books)")
            else:
                st.write("No data yet.")
                
        st.write("") # Ein kleiner visueller Abstand zwischen den Reihen
        
        # --- ZWEITE REIHE ---
        rank_col3, rank_col4 = st.columns(2)
        
        with rank_col3:
            st.markdown("#### 🐢 Longest Read (Returned)")
            # DATEDIFF berechnet die Tage zwischen Rückgabe und Ausleihe
            query_longest_read = """
                SELECT b.Title, DATEDIFF(l.ReturnDate, l.BorrowDate) AS DaysBorrowed
                FROM loans l
                JOIN books b ON l.BookID = b.BookID
                WHERE l.ReturnDate IS NOT NULL
                ORDER BY DaysBorrowed DESC
                LIMIT 3
            """
            df_longest = pd.read_sql(query_longest_read, con=engine)
            if not df_longest.empty:
                for i, row in df_longest.iterrows():
                    st.write(f"{i+1}. **{row['Title']}** ({row['DaysBorrowed']} days)")
            else:
                st.write("No returned books yet.")
                
        with rank_col4:
            st.markdown("#### 🚨 Wall of Shame")
            # Filtert nach Freunden, die aktuell überfällige Bücher horten
            query_shame = """
                SELECT br.FirstName, br.LastName, COUNT(l.LoanID) as UnreturnedCount
                FROM loans l
                JOIN borrowers br ON l.BorrowerID = br.BorrowerID
                WHERE l.ReturnDate IS NULL AND l.ScheduledReturnDate < CURRENT_DATE
                GROUP BY br.BorrowerID
                ORDER BY UnreturnedCount DESC
                LIMIT 3
            """
            df_shame = pd.read_sql(query_shame, con=engine)
            if not df_shame.empty:
                for i, row in df_shame.iterrows():
                    st.write(f"{i+1}. **{row['FirstName']} {row['LastName']}** ({row['UnreturnedCount']} overdue books)")
            else:
                st.success("Everyone is a good friend! No overdue books.")

        st.divider()

        # 4. Auslastungs-Balken
        if total_books > 0:
            utilization = borrowed_books / total_books
            st.write(f"**Library Utilization:** {utilization:.1%} of your books are currently reading the world.")
            st.progress(float(utilization))
            
    except Exception as e:
        st.info(f"Statistics will appear here once you add data to your database. (Error: {e})")



elif menu_selection == "📖 Book Catalog":
    st.title("Book Catalog")
    
    try:
        df_books = pd.read_sql("SELECT * FROM books", con=engine)
        
        st.write("### Filter Books")
        col1, col2, col3 = st.columns(3)
        with col1:
            search_title = st.text_input("🔍 Search by Title:")
        with col2:
            search_author = st.text_input("🔍 Search by Author:")
        with col3:
            search_genre = st.text_input("🔍 Search by Genre:")
            
        filtered_df = df_books.copy()
        
        if search_title:
            filtered_df = filtered_df[filtered_df['Title'].str.contains(search_title, case=False, na=False)]
        if search_author:
            filtered_df = filtered_df[filtered_df['Author'].str.contains(search_author, case=False, na=False)]
        if search_genre:
            filtered_df = filtered_df[filtered_df['Genre'].str.contains(search_genre, case=False, na=False)]
            
        st.write(f"**Showing {len(filtered_df)} result(s):**")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error loading books: {e}")

elif menu_selection == "📋 Borrowed Books":
    st.title("Loan Management & History")
    
    tab_active, tab_history = st.tabs(["📦 Currently Borrowed", "🕰️ Loan History"])

    with tab_active:
        st.write("### Open Loans")
        query_active = """
            SELECT l.LoanID, b.Title AS Book, br.FirstName, br.LastName, l.BorrowDate, l.ScheduledReturnDate
            FROM loans l
            JOIN books b ON l.BookID = b.BookID
            JOIN borrowers br ON l.BorrowerID = br.BorrowerID
            WHERE l.ReturnDate IS NULL
        """
        try:
            df_active = pd.read_sql(query_active, con=engine)
            search_active = st.text_input("🔍 Search active loans:")
            
            if search_active:
                mask_active = df_active.astype(str).apply(lambda col: col.str.contains(search_active, case=False, na=False)).any(axis=1)
                df_active = df_active[mask_active]
                
            st.dataframe(df_active, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading active loans: {e}")

    with tab_history:
        st.write("### Returned Books (History)")
        query_history = """
            SELECT l.LoanID, b.Title AS Book, br.FirstName, br.LastName, l.BorrowDate, l.ReturnDate
            FROM loans l
            JOIN books b ON l.BookID = b.BookID
            JOIN borrowers br ON l.BorrowerID = br.BorrowerID
            WHERE l.ReturnDate IS NOT NULL
            ORDER BY l.ReturnDate DESC
        """
        try:
            df_history = pd.read_sql(query_history, con=engine)
            search_history = st.text_input("🔍 Search history:")
            
            if search_history:
                mask_history = df_history.astype(str).apply(lambda col: col.str.contains(search_history, case=False, na=False)).any(axis=1)
                df_history = df_history[mask_history]
                
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading history: {e}")


elif menu_selection == "⚙️ Admin Area":
        st.title("Administration")
        st.write("This area will be password-protected later and is intended only for Liane.")
        
        # Prüfen, ob es eine Erfolgsmeldung aus dem vorherigen Durchlauf gibt
        if 'success_msg' in st.session_state:
            st.success(st.session_state['success_msg'])
            # Nach dem Anzeigen direkt wieder löschen
            del st.session_state['success_msg']

        # 1. Add a new book
        with st.expander("Add a new book"):
            with st.form("form_new_book", clear_on_submit=True):
                title = st.text_input("Title (Required):")
                author = st.text_input("Author:")
                genre = st.text_input("Genre:")
                isbn = st.text_input("ISBN:")
                
                submit_book = st.form_submit_button("Add Book")
                
                if submit_book:
                    if title.strip() == "":
                        st.error("Please enter a title.")
                    else:
                        # Pack data into a DataFrame and send via to_sql
                        new_book_df = pd.DataFrame([{
                            "Title": title,
                            "Author": author,
                            "Genre": genre,
                            "Isbn": isbn
                        }])
                        try:
                            new_book_df.to_sql('books', con=engine, if_exists='append', index=False)
                            st.success(f"The book '{title}' was added successfully!")
                        except Exception as e:
                            st.error(f"Error saving: {e}")

        # 2. Add a new friend
        with st.expander("Add a new friend"):
            with st.form("form_new_friend", clear_on_submit=True):
                first_name = st.text_input("First Name (Required):")
                last_name = st.text_input("Last Name (Required):")
                email = st.text_input("Email:")
                phone = st.text_input("Phone Number:")
                
                submit_friend = st.form_submit_button("Add Friend")
                
                if submit_friend:
                    if first_name.strip() == "" or last_name.strip() == "":
                        st.error("First Name and Last Name are required fields.")
                    else:
                        new_friend_df = pd.DataFrame([{
                            "FirstName": first_name,
                            "LastName": last_name,
                            "Email": email,
                            "PhoneNumber": phone
                        }])
                        try:
                            new_friend_df.to_sql('borrowers', con=engine, if_exists='append', index=False)
                            st.success(f"Friend '{first_name} {last_name}' was created successfully!")
                        except Exception as e:
                            st.error(f"Error saving: {e}")

        # 3. Create a new loan
        with st.expander("Create a new loan"):
            # Load available books and friends for the dropdowns
            try:
                books = pd.read_sql("SELECT BookID, Title FROM books", con=engine)
                friends = pd.read_sql("SELECT BorrowerID, FirstName, LastName FROM borrowers", con=engine)
                
                # Format the display for the dropdowns
                book_options = dict(zip(books.BookID, books.Title))
                friend_options = dict(zip(friends.BorrowerID, friends.FirstName + " " + friends.LastName))

                with st.form("form_loan", clear_on_submit=True):
                    # Note: list(dict.keys()) is used for Streamlit selectbox compatibility
                    selected_book = st.selectbox("Select Book:", options=list(book_options.keys()), format_func=lambda x: book_options[x])
                    selected_friend = st.selectbox("Select Friend:", options=list(friend_options.keys()), format_func=lambda x: friend_options[x])
                    
                    # Calculate the scheduled return date (e.g., in 30 days)
                    today = date.today()
                    scheduled_return = today + pd.Timedelta(days=30)
                    
                    submit_loan = st.form_submit_button("Loan Book")
                    
                    if submit_loan:
                        new_loan_df = pd.DataFrame([{
                            "BookID": selected_book,
                            "BorrowerID": selected_friend,
                            "BorrowDate": today,
                            "ScheduledReturnDate": scheduled_return
                        }])
                        try:
                            new_loan_df.to_sql('loans', con=engine, if_exists='append', index=False)
                            st.success("Book was successfully loaned!")
                        except Exception as e:
                            st.error(f"Error creating loan: {e}")
            except Exception as e:
                st.warning("Books and friends must exist in the database first.")

        # 4. Return a book
        with st.expander("Return a book"):
            try:
                # Find all open loans
                open_loans = pd.read_sql("""
                    SELECT l.LoanID, b.Title, br.FirstName, br.LastName 
                    FROM loans l
                    JOIN books b ON l.BookID = b.BookID
                    JOIN borrowers br ON l.BorrowerID = br.BorrowerID
                    WHERE l.ReturnDate IS NULL
                """, con=engine)
                
                if open_loans.empty:
                    st.info("There are currently no borrowed books.")
                else:
                    loan_options = dict(zip(
                        open_loans.LoanID, 
                        open_loans.Title + " (borrowed by " + open_loans.FirstName + " " + open_loans.LastName + ")"
                    ))
                    
                    with st.form("form_return"):
                        selected_loan = st.selectbox("Select book to return:", options=list(loan_options.keys()), format_func=lambda x: loan_options[x])
                        submit_return = st.form_submit_button("Mark as returned")
                        
                        if submit_return:
                            # For an UPDATE we use SQLAlchemy directly, as pandas.to_sql is not meant for this
                            with engine.begin() as conn:
                                query = text("UPDATE loans SET ReturnDate = CURRENT_DATE WHERE LoanID = :loan_id")
                                conn.execute(query, {"loan_id": selected_loan})
                            st.success("The book was successfully returned!")
                            st.rerun() # Refreshes the page to update the dropdown list
            except Exception as e:
                st.error(f"Error loading open loans: {e}")
        # 5. Manage Books (Edit / Delete)
        with st.expander("Manage Books (Edit / Delete)"):
            try:
                books_df = pd.read_sql("SELECT * FROM books", con=engine)
                if not books_df.empty:
                    book_options = dict(zip(books_df.BookID, books_df.Title))
                    # Add a unique key to the selectbox to avoid conflicts
                    selected_manage_book_id = st.selectbox("Select a book to manage:", options=list(book_options.keys()), format_func=lambda x: book_options[x], key="manage_book_select")

                    # Get current details of the selected book
                    current_book = books_df[books_df.BookID == selected_manage_book_id].iloc[0]

                    action_book = st.radio("Action:", ["Edit", "Delete"], horizontal=True, key="action_book")

                    if action_book == "Edit":
                        with st.form("form_edit_book"):
                            # Pre-fill inputs with current database values
                            edit_title = st.text_input("Title (Required):", value=current_book['Title'])
                            # Handle potential NULL values gracefully
                            edit_author = st.text_input("Author:", value=current_book['Author'] if pd.notna(current_book['Author']) else "")
                            edit_genre = st.text_input("Genre:", value=current_book['Genre'] if pd.notna(current_book['Genre']) else "")
                            edit_isbn = st.text_input("ISBN:", value=current_book['Isbn'] if pd.notna(current_book['Isbn']) else "")

                            submit_edit_book = st.form_submit_button("Save Changes")

                            if submit_edit_book:
                                if edit_title.strip() == "":
                                    st.error("Please enter a title.")
                                else:
                                    try:
                                        with engine.begin() as conn:
                                            query = text("""
                                                UPDATE books 
                                                SET Title = :title, Author = :author, Genre = :genre, Isbn = :isbn 
                                                WHERE BookID = :book_id
                                            """)
                                            conn.execute(query, {
                                                "title": edit_title, "author": edit_author, 
                                                "genre": edit_genre, "isbn": edit_isbn, 
                                                "book_id": selected_manage_book_id
                                            })
                                        st.session_state['success_msg'] = "Book updated successfully!"
                                        # st.success("Book updated successfully!")
                                        time.sleep(1.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating book: {e}")

                    elif action_book == "Delete":
                        st.warning(f"Are you sure you want to delete '{current_book['Title']}'?")
                        if st.button("Yes, Delete Book"):
                            try:
                                with engine.begin() as conn:
                                    query = text("DELETE FROM books WHERE BookID = :book_id")
                                    conn.execute(query, {"book_id": selected_manage_book_id})
                                st.session_state['success_msg'] = "Book deleted successfully!"
                                st.rerun()
                            except Exception as e:
                                # Usually fails here if the book is still referenced in the 'loans' table
                                st.error(f"Cannot delete this book. It might be linked to existing loan records. (Details: {e})")
                else:
                    st.info("No books available to manage.")
            except Exception as e:
                st.error(f"Error loading books: {e}")


        # 6. Manage Friends (Edit / Delete)
        with st.expander("Manage Friends (Edit / Delete)"):
            try:
                friends_df = pd.read_sql("SELECT * FROM borrowers", con=engine)
                if not friends_df.empty:
                    friend_options = dict(zip(friends_df.BorrowerID, friends_df.FirstName + " " + friends_df.LastName))
                    selected_manage_friend_id = st.selectbox("Select a friend to manage:", options=list(friend_options.keys()), format_func=lambda x: friend_options[x], key="manage_friend_select")

                    current_friend = friends_df[friends_df.BorrowerID == selected_manage_friend_id].iloc[0]

                    action_friend = st.radio("Action:", ["Edit", "Delete"], horizontal=True, key="action_friend")

                    if action_friend == "Edit":
                        with st.form("form_edit_friend"):
                            edit_first_name = st.text_input("First Name (Required):", value=current_friend['FirstName'])
                            edit_last_name = st.text_input("Last Name (Required):", value=current_friend['LastName'])
                            edit_email = st.text_input("Email:", value=current_friend['Email'] if pd.notna(current_friend['Email']) else "")
                            edit_phone = st.text_input("Phone Number:", value=current_friend['PhoneNumber'] if pd.notna(current_friend['PhoneNumber']) else "")

                            submit_edit_friend = st.form_submit_button("Save Changes")

                            if submit_edit_friend:
                                if edit_first_name.strip() == "" or edit_last_name.strip() == "":
                                    st.error("First Name and Last Name are required.")
                                else:
                                    try:
                                        with engine.begin() as conn:
                                            query = text("""
                                                UPDATE borrowers 
                                                SET FirstName = :fname, LastName = :lname, Email = :email, PhoneNumber = :phone 
                                                WHERE BorrowerID = :friend_id
                                            """)
                                            conn.execute(query, {
                                                "fname": edit_first_name, "lname": edit_last_name, 
                                                "email": edit_email, "phone": edit_phone, 
                                                "friend_id": selected_manage_friend_id
                                            })
                                        # st.success("Friend updated successfully!")
                                        st.session_state['success_msg'] = "Friend updated successfully!"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating friend: {e}")

                    elif action_friend == "Delete":
                        st.warning(f"Are you sure you want to delete '{current_friend['FirstName']} {current_friend['LastName']}'?")
                        if st.button(f"Yes, Delete {current_friend['FirstName']} {current_friend['LastName']}"):
                            try:
                                with engine.begin() as conn:
                                    query = text("DELETE FROM borrowers WHERE BorrowerID = :friend_id")
                                    conn.execute(query, {"friend_id": selected_manage_friend_id})
                                # st.success("Friend deleted successfully!")
                                st.session_state['success_msg'] = "Friend deleted successfully!"
                                st.rerun()
                            except Exception as e:
                                # Usually fails here if the friend still has loan records
                                st.error(f"Cannot delete this friend. They might have existing loan records. (Details: {e})")
                else:
                    st.info("No friends available to manage.")
            except Exception as e:
                st.error(f"Error loading friends: {e}")

