# 📚 Liane's Library Management System

Liane has a book collection that rivals the Library of Alexandria. She also has a generous heart and a lot of friends. Unfortunately, those friends have a terrible habit of treating her living room like a public library with zero late fees. 

This web application was built to solve a critical, real-world problem: **Where is my copy of *The Hitchhiker's Guide to the Galaxy*, and exactly who do I need to hunt down to get it back?**

This project is a lightweight, highly efficient library tracker designed to organize a massive personal book collection and keep a strict eye on lending history. It bridges the gap between boundless literary generosity and basic property rights.

---

## ✨ Key Features

*   **The Archive:** A cleanly structured catalog of books, complete with titles, authors, and ISBNs.
*   **The Suspect List (Borrowers):** A directory of friends, acquaintances, and serial book-hoarders. Includes customizable borrowing limits to prevent any single person from running off with the entire sci-fi section.
*   **The Ledger (Loans):** A foolproof tracking system for active and past loans. 
*   **Automated Deadlines:** Built-in logic that generously grants a default 3-month borrowing window before quietly judging the borrower.

---

## 🛠 Under the Hood

Beneath the user-friendly web interface lies a rigorously normalized relational database. It relies on a robust three-table architecture (`books`, `borrowers`, `loans`) designed to eliminate data redundancy, enforce strict borrowing limits, and maintain a permanent history of who returned what (and when). 

---

## 🚀 Quick Start (Database Only)

Currently, the system lives in the magical and strict realm of SQL. To get the backend running:

1. **First, run `db_setup.sql`** in your database environment (like MySQL Workbench) to build the empty schema.
2. **(Optional) The Gentle Approach:** Run `sample_data_input.sql` afterwards. If you wish to put in some sample data to see the logic in action without typing your entire physical library first, this script provides you with some legendary book classics and a few shady test borrowers.
3. **(Optional) THE STRESS TEST (Massive Data Generator):** Do you want to simulate a 26-year history involving 10,000 books, 350 borrowers, and 25,000 loan transactions? Of course you do. We built a Python script to populate the ultimate "Wall of Shame."
   * Ensure you have Python installed.
   * Open your terminal and install the required fake-data library: `pip install Faker`
   * Run the generator script: `python generate_library_data.py`
   * This will birth a heavy `massive_sample_data.sql` file. Import and run that bad boy in your database environment to instantly experience the glorious chaos of a fully operational, heavily abused library.

---

## 🔮 The Master Plan (Coming Soon™)

This database is just the foundation. The final web application will be a glorious, fully-fledged platform that promises the moon, the stars, and your books back. Upcoming features include:

*   **The Ultimate Dashboard:** A beautifully auto-generated, interactive UI showing real-time lending stats, pie charts of your most "borrowed" genres, and a literal *Wall of Shame* for overdue friends.
*   **Automated Guilt Trips:** One-click integration to send increasingly passive-aggressive reminder emails to people holding your books hostage.
*   **Webcam Barcode Scanning:** Stop typing ISBNs! Just wave a book at your laptop camera, and *boom*—it's cataloged.
*   **Borrower Risk Assessment:** Advanced analytics to determine the exact probability of you ever seeing a book again based on the borrower's historical return patterns.
