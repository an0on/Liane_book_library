# 📚 Liane's Library Management System

Liane has a book collection that rivals the Library of Alexandria. She also has a generous heart and a lot of friends. Unfortunately, those friends have a terrible habit of treating her living room like a public library with zero late fees. 

This web application was built to solve a critical, real-world problem: **Where is my copy of *The Hitchhiker's Guide to the Galaxy*, and exactly who do I need to hunt down to get it back?**

This project is a lightweight, highly efficient library tracker designed to organize a massive personal book collection and keep a strict eye on lending history. It bridges the gap between boundless literary generosity and basic property rights.

---

## ✨ Key Features

*   **Interactive Web Dashboard:** A user-friendly, Streamlit-powered interface replacing raw SQL queries with a smooth, clickable library management experience.
*   **The Archive:** A cleanly structured catalog of books, complete with titles, authors, genres, and ISBNs.
*   **The Suspect List (Borrowers):** A directory of friends, acquaintances, and serial book-hoarders. Includes full CRUD (Create, Read, Update, Delete) capabilities.
*   **The Ledger (Loans):** A foolproof tracking system for assigning active loans and efficiently handling returns.
*   **Automated Deadlines:** Built-in logic that generously grants a standard 30-day borrowing window before quietly judging the borrower.

---

## 🛠 Under the Hood

Beneath the appealing web interface lies a rigorously normalized relational MySQL database. It relies on a robust three-table architecture (`books`, `borrowers`, `loans`) designed to eliminate data redundancy and maintain a permanent history of who returned what (and when). Python's Pandas and SQLAlchemy libraries act as the strong bridge connecting the Streamlit frontend with our MySQL backend.

---

## 🚀 Quick Start (Full Setup)

The era of raw SQL is over; we have a fully functional web app! Follow these steps to get your local environment running.

### 1. Database Setup

1. **Build the Schema:** Run `DB_setup.sql` in your database environment (like MySQL Workbench) to build the empty schema.
2. **(Optional) The Gentle Approach:** Run `SampleDataInput.sql` afterwards. This script provides you with some legendary book classics and a few shady test borrowers to see the logic in action.
3. **(Optional) THE STRESS TEST (Massive Data Generator):** Do you want to simulate a 26-year history involving 10,000 books, 350 borrowers, and 25,000 loan transactions? Of course you do.
   * Ensure you have Python installed and your environment activated (see next section).
   * Install the required fake-data library if you haven't yet: `pip install Faker`
   * Run the generator script: `python generate_SQL_for_massive_Data.py`
   * This births a heavy `generate_massive_sample_data.sql` file. Import and run that bad boy in your database environment to instantly experience the glorious chaos.

### 2. Environment Setup

This project uses a Conda environment to keep dependencies clean and isolated.

1. **Create the Conda environment:**
   Open your terminal in the project's root directory and run:
   ```bash
   conda env create -f environment.yml
   ```
2. **Activate the environment:**
   ```bash
   conda activate lianes-lib-env
   ```

### 3. Database Connection Configuration

For obvious security reasons, database credentials are not tracked by Git (`connect.py` is ignored in the `.gitignore`). You need to set this up locally so the Streamlit app can talk to your MySQL database.

1. Navigate into the `src` folder:
   ```bash
   cd src
   ```
2. Create a new file named `connect.py`.
3. Paste the following template into `connect.py` and modify the fields (`password`, etc.) to match your local MySQL configuration:

```python
schema = "liane_library"
host = "127.0.0.1"
user = "root"
password = "YOUR_DATABASE_PASSWORD"
port = 3306

connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{schema}'
```

### 4. Running the App

Once your database is ready, the conda environment is active, and the `connect.py` contains your exact credentials:

1. Ensure your terminal is still inside the `src/` directory.
2. Launch the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```
3. A browser window will automatically pop up (usually at `http://localhost:8501`) granting you glorious, administrative control over Liane's library!

---

## 🔮 The Master Plan (Coming Soon™)

This project has successfully evolved from a raw SQL foundation into a true platform. But we're not done yet. Upcoming features include:

*   **Automated Guilt Trips:** One-click integration to send increasingly passive-aggressive reminder emails to people holding your books hostage.
*   **Webcam Barcode Scanning:** Stop typing ISBNs! Just wave a book at your laptop camera, and *boom*—it's cataloged.
*   **Borrower Risk Assessment:** Advanced analytics to determine the exact probability of you ever seeing a book again based on the borrower's historical return patterns.
