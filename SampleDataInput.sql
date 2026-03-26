USE liane_library;

-- ----------------------------------------------------
-- 1. Insert 10 Books
-- ----------------------------------------------------
INSERT INTO books (Title, Author, Isbn)
VALUES 
    ('The Hitchhiker''s Guide to the Galaxy', 'Douglas Adams', '978-0345391803'),
    ('1984', 'George Orwell', '978-0451524935'),
    ('To Kill a Mockingbird', 'Harper Lee', '978-0060935467'),
    ('Pride and Prejudice', 'Jane Austen', '978-0141439518'),
    ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565'),
    ('Moby-Dick', 'Herman Melville', '978-1503280786'),
    ('The Lord of the Rings', 'J.R.R. Tolkien', '978-0544003415'),
    ('The Catcher in the Rye', 'J.D. Salinger', '978-0316769488'),
    ('Fahrenheit 451', 'Ray Bradbury', '978-1451673319'),
    ('The Hobbit', 'J.R.R. Tolkien', '978-0547928227');

-- ----------------------------------------------------
-- 2. Insert 5 Borrowers
-- ----------------------------------------------------
-- Peter, John, and Bob use the default MaxToBorrow (2)
-- Sabine and Alice get custom limits
INSERT INTO borrowers (FirstName, LastName, Email, PhoneNumber, MaxToBorrow)
VALUES 
    ('Peter', 'Mueller', 'peter@example.com', '0171-123456', DEFAULT),
    ('Sabine', 'Schmidt', 'sabine@example.com', '0160-987654', 5),
    ('John', 'Doe', 'john.doe@example.com', '0151-555666', DEFAULT),
    ('Alice', 'Wonderland', 'alice@example.com', '0172-111222', 3),
    ('Bob', 'Builder', 'bob@example.com', '0152-333444', DEFAULT);

-- ----------------------------------------------------
-- 3. Insert Loans (4 currently active, 2 returned)
-- ----------------------------------------------------

-- ACTIVE LOAN: Alice borrows Book 4 (Tests default BorrowDate, ReturnDate is NULL)
INSERT INTO loans (BookID, BorrowerID, ScheduledReturnDate, ReturnDate)
VALUES (4, 4, '2026-08-10', NULL);

-- PAST LOAN: Peter borrowed Book 1 and returned it
INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate)
VALUES (1, 1, '2026-02-01', '2026-03-01', '2026-02-28');

-- PAST LOAN: Peter borrowed Book 5 and returned it on the same day
INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate)
VALUES (5, 1, '2026-03-05', '2026-04-05', '2026-03-05');

-- ACTIVE LOAN: Sabine borrows Book 10 (ReturnDate is NULL)
INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate)
VALUES (10, 2, '2026-03-10', '2026-04-10', NULL);

-- ACTIVE LOAN: Sabine borrows Book 7 (ReturnDate is NULL)
INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate)
VALUES (7, 2, '2026-03-12', '2026-04-12', NULL);

-- ACTIVE LOAN: John borrows Book 2 (ReturnDate is NULL)
INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate)
VALUES (2, 3, '2026-03-20', '2026-04-20', NULL);