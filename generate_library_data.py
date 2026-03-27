import random
from datetime import date, timedelta
from faker import Faker

fake = Faker('en_US')

NUM_BOOKS = 10000
NUM_BORROWERS = 350
NUM_LOANS = 25000

START_DATE = date(2000, 1, 1)
TODAY = date(2026, 3, 27)

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_sql():
    with open("massive_sample_data.sql", "w", encoding="utf-8") as f:
        f.write("USE liane_library;\n\n")
        
        f.write("-- Reset tables to ensure AUTO_INCREMENT starts at 1\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("TRUNCATE TABLE loans;\n")
        f.write("TRUNCATE TABLE books;\n")
        f.write("TRUNCATE TABLE borrowers;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
        
        # ---------------------------------------------------------
        # 1. GENERATE BOOKS
        # ---------------------------------------------------------
        print("Generating 10,000 unique books...")
        f.write("-- Inserting 10,000 Books\n")
        f.write("INSERT INTO books (Title, Author, Isbn) VALUES\n")
        
        # We use sets to track what we've already generated
        unique_titles = set()
        unique_isbns = set()
        
        for i in range(NUM_BOOKS):
            # Generate a truly unique Title
            title = fake.catch_phrase().replace("'", "''").title()
            while title in unique_titles:
                # If duplicate, append a random edition number to make it unique
                title = f"{fake.catch_phrase().replace('\'', '\'\'').title()} (Vol. {random.randint(2, 9999)})"
            unique_titles.add(title)
            
            author = fake.name().replace("'", "''")
            
            # Generate a truly unique ISBN
            isbn = fake.isbn13()
            while isbn in unique_isbns:
                isbn = fake.isbn13()
            unique_isbns.add(isbn)
            
            terminator = ";\n\n" if i == NUM_BOOKS - 1 else ",\n"
            f.write(f"('{title}', '{author}', '{isbn}'){terminator}")

        f.write("-- Inserting 12 custom Books\n")
        f.write("INSERT INTO books (Title, Author, Isbn) VALUES\n")
        f.write("('The Golden Era of Hip-Hop', 'Stefano Sancho Agada', '978-1-84049-901-8'),\n")
        f.write("('Inside the Paint: Basketball Strategies', 'Stefano Sancho Agada', '978-0-01-297961-7'),\n")
        f.write("('Cyborgs and Intergalactic Empires', 'Stefano Sancho Agada', '978-1-967753-53-6'),\n")
        f.write("('Mastering Asian Street Food', 'Linh Nguyen', '978-0-241-65371-5'),\n")
        f.write("('Data Structures and Algorithms', 'Linh Nguyen', '978-1-00-210417-0'),\n")
        f.write("('The Art of Wok Cooking', 'Linh Nguyen', '978-0-202-47320-8'),\n")
        f.write("('Colonizing the Outer Planets', 'Juan DAAI', '978-0-7622-4523-9'),\n")
        f.write("('Graffiti Techniques and Lettering', 'Juan DAAI', '978-0-87301-813-5'),\n")
        f.write("('Spaceships and Nebula Tourism', 'Juan DAAI', '978-0-7705-0180-8'),\n")
        f.write("('Advanced Plant Nutrition and Fertilizers', 'Niels Zimmermann', '978-1-74531-713-4'),\n")
        f.write("('Skateboarding: Mastering Lifestyle on Board', 'Niels Zimmermann', '978-0-14-274848-0'),\n")
        f.write("('Rocket Science and boosting Mechanics', 'Niels Zimmermann', '978-0-00-880035-2');\n\n")

        # ---------------------------------------------------------
        # 2. GENERATE BORROWERS
        # ---------------------------------------------------------
        print("Generating 350 borrowers...")
        f.write("-- Inserting 350 Borrowers\n")
        f.write("INSERT INTO borrowers (FirstName, LastName, Email, PhoneNumber, MaxToBorrow) VALUES\n")
        
        for i in range(NUM_BORROWERS):
            first_name = fake.first_name().replace("'", "''")
            last_name = fake.last_name().replace("'", "''")
            email = fake.email()
            phone = fake.phone_number()
            max_borrow = random.choices([2, 3, 5, 10], weights=[70, 15, 10, 5])[0]
            
            terminator = ";\n\n" if i == NUM_BORROWERS - 1 else ",\n"
            f.write(f"('{first_name}', '{last_name}', '{email}', '{phone}', {max_borrow}){terminator}")

        # ---------------------------------------------------------
        # 3. GENERATE LOANS
        # ---------------------------------------------------------
        print(f"Generating {NUM_LOANS} loans since 2000...")
        f.write(f"-- Inserting {NUM_LOANS} Loans (Past, Active, Overdue)\n")
        
        batch_size = 1000
        for batch_start in range(0, NUM_LOANS, batch_size):
            f.write("INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate) VALUES\n")
            
            batch_end = min(batch_start + batch_size, NUM_LOANS)
            for i in range(batch_start, batch_end):
                book_id = random.randint(1, NUM_BOOKS)
                borrower_id = random.randint(1, NUM_BORROWERS)
                
                borrow_date = random_date(START_DATE, TODAY)
                scheduled_return = borrow_date + timedelta(days=90)
                
                is_active = random.random() < 0.05
                
                if is_active:
                    return_date_str = "NULL"
                else:
                    return_date = borrow_date + timedelta(days=random.randint(1, 120))
                    if return_date > TODAY:
                        return_date = TODAY
                    return_date_str = f"'{return_date}'"
                
                terminator = ";\n\n" if i == batch_end - 1 else ",\n"
                f.write(f"({book_id}, {borrower_id}, '{borrow_date}', '{scheduled_return}', {return_date_str}){terminator}")

        print("Done! Check massive_sample_data.sql")

if __name__ == "__main__":
    generate_sql()
