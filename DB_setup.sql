
-- DROP SCHEMA IF EXISTS liane_library;

CREATE DATABASE liane_library;

 USE liane_library;

CREATE TABLE books (
    BookID INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
    Title VARCHAR(100) NOT NULL UNIQUE,
    Author VARCHAR(101),
    Isbn VARCHAR(30) UNIQUE
);

CREATE TABLE borrowers (
    BorrowerID INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(255),
    PhoneNumber VARCHAR(255),
    MaxToBorrow INT NOT NULL DEFAULT 2
);

CREATE TABLE loans (
	LoanID INT AUTO_INCREMENT PRIMARY KEY,
	BookID INT NOT NULL,
    BorrowerID INT NOT NULL,
    BorrowDate DATE DEFAULT (CURRENT_DATE),
    ScheduledReturnDate DATE,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES books(BookID),
    FOREIGN KEY (BorrowerID) REFERENCES borrowers(BorrowerID)
    
);


