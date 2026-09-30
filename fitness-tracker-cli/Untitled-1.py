"""
Library Management System
========================
A beginner-friendly, menu-driven library application built with Python and SQLite.
Run with: python library_management_system.py
The program creates a local database file named library.db the first time it runs.
No third-party packages are required.
"""
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
# Keep the database beside this Python file so it is easy to find.
DATABASE_FILE = Path(__file__).with_name("library.db")
LOAN_PERIOD_DAYS = 14
class Library:
    """Contains the database operations used by the menus."""
    def __init__(self, database_file: Path = DATABASE_FILE):
        self.database_file = database_file
        self.connection = sqlite3.connect(self.database_file)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
    def create_tables(self) -> None:
        """Create all tables if this is the first run."""
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                category TEXT DEFAULT 'General',
                year INTEGER,
                total_copies INTEGER NOT NULL DEFAULT 1,
                available_copies INTEGER NOT NULL DEFAULT 1,
                created_on TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                joined_on TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issued_on TEXT NOT NULL,
                due_on TEXT NOT NULL,
                returned_on TEXT,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id)
            );
            """
        )
        self.connection.commit()
    def close(self) -> None:
        """Close the database connection cleanly."""
        self.connection.close()
    def add_book(
        self,
        title: str,
        author: str,
        isbn: Optional[str],
        category: str,
        year: Optional[int],
        copies: int,
    ) -> int:
        """Save one book title and the number of copies owned."""
        cursor = self.connection.execute(
            """INSERT INTO books
               (title, author, isbn, category, year, total_copies,
                available_copies, created_on)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, author, isbn, category, year, copies, copies, date.today().isoformat()),
        )
        self.connection.commit()
        return int(cursor.lastrowid)
    def update_book(self, book_id: int, values: dict) -> bool:
        """Update editable fields for a book; return False if it does not exist."""
        old = self.get_book(book_id)
        if old is None:
            return False
        new_total = values.get("total_copies", old["total_copies"])
        checked_out = old["total_copies"] - old["available_copies"]
        if new_total < checked_out:
            raise ValueError("Total copies cannot be less than copies currently on loan.")
        new_available = new_total - checked_out
        self.connection.execute(
            """UPDATE books SET title=?, author=?, isbn=?, category=?, year=?,
               total_copies=?, available_copies=? WHERE id=?""",
            (
                values.get("title", old["title"]),
                values.get("author", old["author"]),
                values.get("isbn", old["isbn"]),
                values.get("category", old["category"]),
                values.get("year", old["year"]),
                new_total,
                new_available,
                book_id,
            ),
        )
        self.connection.commit()
        return True
    def get_book(self, book_id: int):
        """Find one book by its numeric ID."""
        return self.connection.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
    def delete_book(self, book_id: int) -> bool:
        """Delete a book only if it has no loan history."""
        book = self.get_book(book_id)
        if book is None:
            return False
        loan = self.connection.execute(
            "SELECT id FROM loans WHERE book_id = ? LIMIT 1", (book_id,)
        ).fetchone()
        if loan:
            raise ValueError("This book has loan history and cannot be deleted.")
        self.connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.connection.commit()
        return True
    def list_books(self, available_only: bool = False):
        """Return books in a predictable title order."""
        query = "SELECT * FROM books"
        if available_only:
            query += " WHERE available_copies > 0"
        query += " ORDER BY title COLLATE NOCASE"
        return self.connection.execute(query).fetchall()
    def search_books(self, term: str):
        """Search titles, authors, ISBNs, and categories."""
        pattern = f"%{term}%"
        return self.connection.execute(
            """SELECT * FROM books
               WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
               ORDER BY title COLLATE NOCASE""",
            (pattern, pattern, pattern, pattern),
        ).fetchall()
    def add_member(self, name: str, email: Optional[str], phone: str) -> int:
        """Register a new library member."""
        cursor = self.connection.execute(
            """INSERT INTO members (name, email, phone, joined_on)
               VALUES (?, ?, ?, ?)""",
            (name, email, phone, date.today().isoformat()),
        )
        self.connection.commit()
        return int(cursor.lastrowid)
    def get_member(self, member_id: int):
        """Find one member by ID."""
        return self.connection.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()
    def update_member(self, member_id: int, name: str, email: Optional[str], phone: str):
        """Change a member's contact details."""
        cursor = self.connection.execute(
            "UPDATE members SET name=?, email=?, phone=? WHERE id=? AND active=1",
            (name, email, phone, member_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0
    def deactivate_member(self, member_id: int) -> bool:
        """Deactivate a member without removing historical loan records."""
        active_loans = self.connection.execute(
            """SELECT COUNT(*) AS count FROM loans
               WHERE member_id=? AND returned_on IS NULL""",
            (member_id,),
        ).fetchone()["count"]
        if active_loans:
            raise ValueError("This member must return all books before deactivation.")
        cursor = self.connection.execute(
            "UPDATE members SET active=0 WHERE id=? AND active=1", (member_id,)
        )
        self.connection.commit()
        return cursor.rowcount > 0
    def list_members(self, active_only: bool = True):
        """List members by name."""
        query = "SELECT * FROM members"
        if active_only:
            query += " WHERE active=1"
        query += " ORDER BY name COLLATE NOCASE"
        return self.connection.execute(query).fetchall()
    def search_members(self, term: str):
        """Search active members by name, email, or phone number."""
        pattern = f"%{term}%"
        return self.connection.execute(
            """SELECT * FROM members WHERE active=1
               AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)
               ORDER BY name COLLATE NOCASE""",
            (pattern, pattern, pattern),
        ).fetchall()
    def issue_book(self, book_id: int, member_id: int) -> int:
        """Create a loan and reduce the available copy count."""
        book = self.get_book(book_id)
        member = self.get_member(member_id)
        if book is None:
            raise ValueError("Book ID was not found.")
        if member is None or not member["active"]:
            raise ValueError("An active member with that ID was not found.")
        if book["available_copies"] < 1:
            raise ValueError("No copies of this book are currently available.")
        already_borrowed = self.connection.execute(
            """SELECT COUNT(*) AS count FROM loans
               WHERE member_id=? AND returned_on IS NULL""",
            (member_id,),
        ).fetchone()["count"]
        if already_borrowed >= 5:
            raise ValueError("A member may borrow no more than five books at a time.")
        issued = date.today()
        due = issued + timedelta(days=LOAN_PERIOD_DAYS)
        cursor = self.connection.execute(
            """INSERT INTO loans (book_id, member_id, issued_on, due_on)
               VALUES (?, ?, ?, ?)""",
            (book_id, member_id, issued.isoformat(), due.isoformat()),
        )
        self.connection.execute(
            "UPDATE books SET available_copies=available_copies-1 WHERE id=?",
            (book_id,),
        )
        self.connection.commit()
        return int(cursor.lastrowid)
    def return_book(self, loan_id: int) -> bool:
        """Mark an open loan returned and make one copy available again."""
        loan = self.connection.execute(
            "SELECT * FROM loans WHERE id=? AND returned_on IS NULL", (loan_id,)
        ).fetchone()
        if loan is None:
            return False
        self.connection.execute(
            "UPDATE loans SET returned_on=? WHERE id=?",
            (date.today().isoformat(), loan_id),
        )
        self.connection.execute(
            "UPDATE books SET available_copies=available_copies+1 WHERE id=?",
            (loan["book_id"],),
        )
        self.connection.commit()
        return True
    def list_loans(self, open_only: bool = False):
        """Return loan rows with book and member names attached."""
        query = """SELECT loans.*, books.title, members.name AS member_name
                   FROM loans
                   JOIN books ON books.id=loans.book_id
                   JOIN members ON members.id=loans.member_id"""
        if open_only:
            query += " WHERE loans.returned_on IS NULL"
        query += " ORDER BY loans.issued_on DESC, loans.id DESC"
        return self.connection.execute(query).fetchall()
    def loans_for_member(self, member_id: int):
        """Show all loans belonging to a particular member."""
        return self.connection.execute(
            """SELECT loans.*, books.title FROM loans
               JOIN books ON books.id=loans.book_id
               WHERE loans.member_id=? ORDER BY loans.issued_on DESC""",
            (member_id,),
        ).fetchall()
    def overdue_loans(self):
        """Find books that are past their due date and not yet returned."""
        return self.connection.execute(
            """SELECT loans.*, books.title, members.name AS member_name,
                      members.phone
               FROM loans JOIN books ON books.id=loans.book_id
               JOIN members ON members.id=loans.member_id
               WHERE loans.returned_on IS NULL AND loans.due_on < ?
               ORDER BY loans.due_on""",
            (date.today().isoformat(),),
        ).fetchall()
    def summary(self) -> dict:
        """Build a few totals for the dashboard."""
        books = self.connection.execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(total_copies), 0) AS copies FROM books"
        ).fetchone()
        members = self.connection.execute(
            "SELECT COUNT(*) AS count FROM members WHERE active=1"
        ).fetchone()["count"]
        loans = self.connection.execute(
            "SELECT COUNT(*) AS count FROM loans WHERE returned_on IS NULL"
        ).fetchone()["count"]
        return {
            "titles": books["count"],
            "copies": books["copies"],
            "members": members,
            "loans": loans,
            "overdue": len(self.overdue_loans()),
        }
    def popular_books(self, limit: int = 10):
        """Return titles ordered by how often they have been borrowed."""
        return self.connection.execute(
            """SELECT books.title, books.author, COUNT(loans.id) AS borrow_count
               FROM books LEFT JOIN loans ON books.id=loans.book_id
               GROUP BY books.id ORDER BY borrow_count DESC, books.title LIMIT ?""",
            (limit,),
        ).fetchall()
# The functions below handle keyboard input and screen output.
def line(character: str = "-", width: int = 72) -> None:
    print(character * width)
def pause() -> None:
    input("\nPress Enter to continue...")
def read_text(prompt: str, required: bool = True) -> str:
    """Read text and repeat if a required answer is blank."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please try again.")
def read_integer(prompt: str, minimum: Optional[int] = None,
                 maximum: Optional[int] = None, allow_blank: bool = False):
    """Read a whole number, checking optional limits."""
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Please enter a number of at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Please enter a number no greater than {maximum}.")
            continue
        return value
def optional_email() -> Optional[str]:
    """Return a simple email value or None when the user leaves it blank."""
    email = read_text("Email (optional): ", required=False)
    if not email:
        return None
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Please enter an email address containing @ and a domain.")
    return email
def show_books(books) -> None:
    """Print book records as a compact table."""
    if not books:
        print("No books found.")
        return
    print(f"{'ID':<5} {'Title':<27} {'Author':<20} {'Available':<10} Category")
    line()
    for book in books:
        print(
            f"{book['id']:<5} {book['title'][:26]:<27} "
            f"{book['author'][:19]:<20} "
            f"{book['available_copies']}/{book['total_copies']:<8} "
            f"{book['category']}"
        )
def show_members(members) -> None:
    """Print member records."""
    if not members:
        print("No members found.")
        return
    print(f"{'ID':<5} {'Name':<25} {'Email':<30} Phone")
    line()
    for member in members:
        print(
            f"{member['id']:<5} {member['name'][:24]:<25} "
            f"{(member['email'] or '-')[:29]:<30} {member['phone'] or '-'}"
        )
def show_loans(loans) -> None:
    """Print loan records; callers can pass open or complete loan rows."""
    if not loans:
        print("No loan records found.")
        return
    print(f"{'Loan':<6} {'Book':<25} {'Member':<20} {'Issued':<12} {'Due':<12} Returned")
    line()
    for loan in loans:
        title = loan["title"][:24]
        member_name = loan["member_name"][:19] if "member_name" in loan.keys() else ""
        returned = loan["returned_on"] or "Open"
        print(
            f"{loan['id']:<6} {title:<25} {member_name:<20} "
            f"{loan['issued_on']:<12} {loan['due_on']:<12} {returned}"
        )
def ask_book_details(existing=None) -> dict:
    """Ask for book information, keeping old values when left blank."""
    if existing is None:
        title = read_text("Title: ")
        author = read_text("Author: ")
        isbn = read_text("ISBN (optional): ", required=False) or None
        category = read_text("Category [General]: ", required=False) or "General"
        year = read_integer("Publication year (optional): ", 0, 2100, True)
        copies = read_integer("Number of copies: ", 1, 10000)
    else:
        title = read_text(f"Title [{existing['title']}]: ", False) or existing["title"]
        author = read_text(f"Author [{existing['author']}]: ", False) or existing["author"]
        old_isbn = existing["isbn"] or ""
        isbn = read_text(f"ISBN [{old_isbn}]: ", False) or old_isbn or None
        category = read_text(f"Category [{existing['category']}]: ", False) or existing["category"]
        year = read_integer(
            f"Publication year [{existing['year'] or ''}]: ", 0, 2100, True
        )
        if year is None:
            year = existing["year"]
        copies = read_integer(
            f"Total copies [{existing['total_copies']}]: ", 1, 10000, True
        )
        if copies is None:
            copies = existing["total_copies"]
    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "category": category,
        "year": year,
        "total_copies": copies,
    }
def add_book_screen(library: Library) -> None:
    """Collect and save a new book."""
    print("\nADD A BOOK")
    line()
    details = ask_book_details()
    book_id = library.add_book(
        details["title"], details["author"], details["isbn"],
        details["category"], details["year"], details["total_copies"],
    )
    print(f"Book saved with ID {book_id}.")
def edit_book_screen(library: Library) -> None:
    """Find a book by ID and update its details."""
    book_id = read_integer("Book ID to edit: ", 1)
    book = library.get_book(book_id)
    if book is None:
        print("Book not found.")
        return
    updated = ask_book_details(book)
    if library.update_book(book_id, updated):
        print("Book details updated.")
def delete_book_screen(library: Library) -> None:
    """Remove a book that has never been borrowed."""
    book_id = read_integer("Book ID to delete: ", 1)
    if library.delete_book(book_id):
        print("Book deleted.")
    else:
        print("Book not found.")
def books_menu(library: Library) -> None:
    """Book listing, search, and maintenance menu."""
    while True:
        print("\nBOOKS")
        line()
        print("1. List all books")
        print("2. List available books")
        print("3. Search books")
        print("4. Add a book")
        print("5. Edit a book")
        print("6. Delete a book")
        print("0. Back")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                show_books(library.list_books())
                pause()
            elif choice == "2":
                show_books(library.list_books(available_only=True))
                pause()
            elif choice == "3":
                term = read_text("Search title, author, ISBN, or category: ")
                show_books(library.search_books(term))
                pause()
            elif choice == "4":
                add_book_screen(library)
                pause()
            elif choice == "5":
                edit_book_screen(library)
                pause()
            elif choice == "6":
                delete_book_screen(library)
                pause()
            elif choice == "0":
                return
            else:
                print("Choose one of the listed options.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Could not complete that action: {error}")
            pause()
def add_member_screen(library: Library) -> None:
    """Register a member from answers typed at the keyboard."""
    print("\nREGISTER MEMBER")
    line()
    name = read_text("Full name: ")
    email = optional_email()
    phone = read_text("Phone (optional): ", required=False)
    member_id = library.add_member(name, email, phone)
    print(f"Member registered with ID {member_id}.")
def edit_member_screen(library: Library) -> None:
    """Change contact information for one active member."""
    member_id = read_integer("Member ID to edit: ", 1)
    member = library.get_member(member_id)
    if member is None or not member["active"]:
        print("Active member not found.")
        return
    name = read_text(f"Name [{member['name']}]: ", False) or member["name"]
    email = read_text(f"Email [{member['email'] or ''}]: ", False)
    email = email or member["email"]
    phone = read_text(f"Phone [{member['phone'] or ''}]: ", False) or member["phone"]
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        raise ValueError("Please enter a valid email address.")
    if library.update_member(member_id, name, email, phone):
        print("Member details updated.")
def deactivate_member_screen(library: Library) -> None:
    """Deactivate a member while keeping their old records."""
    member_id = read_integer("Member ID to deactivate: ", 1)
    if library.deactivate_member(member_id):
        print("Member deactivated.")
    else:
        print("Active member not found.")
def members_menu(library: Library) -> None:
    """Member registration, search, and maintenance menu."""
    while True:
        print("\nMEMBERS")
        line()
        print("1. List active members")
        print("2. Search members")
        print("3. Register member")
        print("4. Edit member")
        print("5. Deactivate member")
        print("0. Back")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                show_members(library.list_members())
                pause()
            elif choice == "2":
                term = read_text("Search name, email, or phone: ")
                show_members(library.search_members(term))
                pause()
            elif choice == "3":
                add_member_screen(library)
                pause()
            elif choice == "4":
                edit_member_screen(library)
                pause()
            elif choice == "5":
                deactivate_member_screen(library)
                pause()
            elif choice == "0":
                return
            else:
                print("Choose one of the listed options.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Could not complete that action: {error}")
            pause()
def issue_book_screen(library: Library) -> None:
    """Issue one available copy to an active member."""
    print("\nISSUE A BOOK")
    line()
    show_books(library.list_books(available_only=True))
    book_id = read_integer("Book ID: ", 1)
    show_members(library.list_members())
    member_id = read_integer("Member ID: ", 1)
    loan_id = library.issue_book(book_id, member_id)
    due = (date.today() + timedelta(days=LOAN_PERIOD_DAYS)).isoformat()
    print(f"Loan {loan_id} created. Please return by {due}.")
def return_book_screen(library: Library) -> None:
    """Show open loans and ask which one is being returned."""
    open_loans = library.list_loans(open_only=True)
    show_loans(open_loans)
    if not open_loans:
        return
    loan_id = read_integer("Loan ID to return: ", 1)
    if library.return_book(loan_id):
        print("Return recorded. Thank you!")
    else:
        print("Open loan not found. Check the loan ID and try again.")
def circulation_menu(library: Library) -> None:
    """Issue and return books, and inspect current loans."""
    while True:
        print("\nCIRCULATION")
        line()
        print("1. Issue a book")
        print("2. Return a book")
        print("3. View all open loans")
        print("4. View all loan history")
        print("0. Back")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                issue_book_screen(library)
                pause()
            elif choice == "2":
                return_book_screen(library)
                pause()
            elif choice == "3":
                show_loans(library.list_loans(open_only=True))
                pause()
            elif choice == "4":
                show_loans(library.list_loans())
                pause()
            elif choice == "0":
                return
            else:
                print("Choose one of the listed options.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Could not complete that action: {error}")
            pause()
def overdue_report(library: Library) -> None:
    """Display overdue loans and how many days late they are."""
    overdue = library.overdue_loans()
    if not overdue:
        print("There are no overdue books today.")
        return
    print(f"{'Loan':<6} {'Book':<26} {'Member':<22} {'Due':<12} Days late")
    line()
    for loan in overdue:
        due_date = date.fromisoformat(loan["due_on"])
        days_late = (date.today() - due_date).days
        print(
            f"{loan['id']:<6} {loan['title'][:25]:<26} "
            f"{loan['member_name'][:21]:<22} {loan['due_on']:<12} {days_late}"
        )
def reports_menu(library: Library) -> None:
    """Show a dashboard and a few useful library reports."""
    while True:
        print("\nREPORTS")
        line()
        print("1. Library summary")
        print("2. Overdue books")
        print("3. Most borrowed titles")
        print("4. Loan history for a member")
        print("0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            info = library.summary()
            print(f"Book titles:          {info['titles']}")
            print(f"Physical copies:      {info['copies']}")
            print(f"Active members:       {info['members']}")
            print(f"Books currently out:  {info['loans']}")
            print(f"Overdue loans:        {info['overdue']}")
            pause()
        elif choice == "2":
            overdue_report(library)
            pause()
        elif choice == "3":
            print(f"{'Title':<35} {'Author':<25} Borrowed")
            line()
            for book in library.popular_books():
                print(f"{book['title'][:34]:<35} {book['author'][:24]:<25} {book['borrow_count']}")
            pause()
        elif choice == "4":
            member_id = read_integer("Member ID: ", 1)
            member = library.get_member(member_id)
            if member is None:
                print("Member not found.")
            else:
                print(f"Loan history for {member['name']}:")
                history = library.loans_for_member(member_id)
                if history:
                    for loan in history:
                        status = loan["returned_on"] or "Still borrowed"
                        print(f"{loan['title']} | issued {loan['issued_on']} | {status}")
                else:
                    print("This member has no loan history.")
            pause()
        elif choice == "0":
            return
        else:
            print("Choose one of the listed options.")
def print_welcome(library: Library) -> None:
    """Show the application title and a quick count of library activity."""
    info = library.summary()
    print("\n" + "=" * 72)
    print("                 LIBRARY MANAGEMENT SYSTEM")
    print("=" * 72)
    print(
        f"Today: {date.today().isoformat()}  |  "
        f"Titles: {info['titles']}  |  Members: {info['members']}  |  "
        f"Books out: {info['loans']}"
    )
    line("=")
def main_menu(library: Library) -> None:
    """Keep showing the main menu until the user chooses to quit."""
    while True:
        print_welcome(library)
        print("1. Books")
        print("2. Members")
        print("3. Issue and return")
        print("4. Reports")
        print("0. Save and exit")
        choice = input("Choose a section: ").strip()
        if choice == "1":
            books_menu(library)
        elif choice == "2":
            members_menu(library)
        elif choice == "3":
            circulation_menu(library)
        elif choice == "4":
            reports_menu(library)
        elif choice == "0":
            print("Your information is saved in the database. Goodbye!")
            return
        else:
            print("Choose one of the listed options.")
            pause()
def run() -> None:
    """Open the library, run the menus, and always close the database."""
    library = Library()
    try:
        main_menu(library)
    except KeyboardInterrupt:
        print("\nProgram interrupted. Your saved information is still in the database.")
    finally:
        library.close()
if __name__ == "__main__":
    run()