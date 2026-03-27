import random
from datetime import date, timedelta
from faker import Faker

fake = Faker('en_US') # English data for consistency with your README

NUM_BOOKS = 10000
NUM_BORROWERS = 350
NUM_LOANS = 25000 # Let's create a rich history of 25,000 loans

START_DATE = date(2000, 1, 1)
TODAY = date(2026, 3, 27)

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_sql():
    with open("massive_sample_data.sql", "w", encoding="utf-8") as f:
        f.write("USE liane_library;\n\n")
        
        # ---------------------------------------------------------
        # 1. GENERATE BOOKS
        # ---------------------------------------------------------
        print("Generating 10,000 books...")
        f.write("-- Inserting 10,000 Books\n")
        f.write("INSERT INTO books (Title, Author, Isbn) VALUES\n")
        
        for i in range(NUM_BOOKS):
            # Generating somewhat realistic book titles
            title = fake.catch_phrase().replace("'", "''").title()
            author = fake.name().replace("'", "''")
            isbn = fake.isbn13()
            
            terminator = ";\n\n" if i == NUM_BOOKS - 1 else ",\n"
            f.write(f"('{title}', '{author}', '{isbn}'){terminator}")

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
        
        # Batching inserts to prevent SQL execution errors on massive lines
        batch_size = 1000
        for batch_start in range(0, NUM_LOANS, batch_size):
            f.write("INSERT INTO loans (BookID, BorrowerID, BorrowDate, ScheduledReturnDate, ReturnDate) VALUES\n")
            
            batch_end = min(batch_start + batch_size, NUM_LOANS)
            for i in range(batch_start, batch_end):
                book_id = random.randint(1, NUM_BOOKS)
                borrower_id = random.randint(1, NUM_BORROWERS)
                
                borrow_date = random_date(START_DATE, TODAY)
                scheduled_return = borrow_date + timedelta(days=90) # 3 months roughly
                
                # Determine if returned or active
                is_active = random.random() < 0.05 # 5% of all historic loans are currently active
                
                if is_active:
                    return_date_str = "NULL"
                else:
                    # Returned between 1 and 120 days later
                    return_date = borrow_date + timedelta(days=random.randint(1, 120))
                    # Prevent return dates in the future
                    if return_date > TODAY:
                        return_date = TODAY
                    return_date_str = f"'{return_date}'"
                
                terminator = ";\n\n" if i == batch_end - 1 else ",\n"
                f.write(f"({book_id}, {borrower_id}, '{borrow_date}', '{scheduled_return}', {return_date_str}){terminator}")

        print("Done! Check massive_sample_data.sql")

if __name__ == "__main__":
    generate_sql()