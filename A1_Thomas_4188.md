CISC 327 Assignment 1
Name: Shaun Thomas
Student ID: 2O394188
Group Number: 4

--

Project Implementation Status:


Requirement | Function Name                 | Status (Complete/Partial) | What is Missing / Bug 
            |-------------------------------|-------------------------- |------------------------
R1          | `add_book_to_catalog`         |    Complete               | It works with validation. The duplicate ISBN check all works.
R2          | `get_all_books`               |    Complete               | Catalogue display is fine. No Major issues.
R3          | `borrow_book_by_patron`       |    Partial                | The borrow book function works but there is a bug as it allows 6th book to be borrowed instead of maximum 5.
R4          | `return_book_by_patron`       |    Not Implemented        | The function just returns -> False, "Book return functionality is not yet implemented". No logic implemented for borrow verfiication, fee calc, updating availability.
R5          | `calculate_late_fee_for_book` |    Not Implemented        | Function ends without return -> always 'None'. No late free rules (14 days, 0.50/day, etc) coded yet.
R6          | `search_books_in_catalog`     |    Not Implemented        | No logic for title/aurthor partial match or ISBN exact match (whihc is why my test passes structurally i.e. returns a list but is always empty)
R7          | `get_patron_status_report`    |    Not Implemented        | No patron borrwed books, fees, or history included.


--

Unit Test Summary:

pytest was the framework used for testing, as recommended in the assignment instructions. My test cases are found in the folder 'tests' and named 'test_cases.py'. 33 total test cases were written which covered all 7 requirements (R1-R7) with 4-5 test cases each.
The following below breaksdown the requirements and the test cases I implemented for it:

- R1 (Add Book): 5 tests → valid input, invalid ISBN, negative copies, long title, duplicate ISBN.  
- R2 (Catalog Display): 4 tests → catalog not empty, required fields present, available >= 0, available <= total.  
- R3 (Borrowing): 5 tests → valid borrow, invalid patron ID, unavailable book, over limit, invalid book ID.  
- R4 (Return): 4 tests → valid return, return not borrowed, double return, invalid book ID.  
- R5 (Late Fee): 4 tests → no overdue, overdue <7 days, overdue >7 days, max fee cap (all fail since not implemented).  
- R6 (Search): 4 tests → partial title, partial author, exact ISBN, no results.  
- R7 (Patron Status): 5 tests → structure, no borrows, with borrow, includes fees, includes history. 

Test results:
- Passed: 27
- Failed: 6
    - sample_test.py (test_add_book_valid_input) -> I am just adding this since I ran 'pytest -v' and would've included the sample_test.py file. It fails because it reuses a duplicate ISBN which is the sample test issue and not my code (just adding as precaution). On repeated local runs, sometimes test_add_book_valid_input also fails if the database is not reset between tests (duplicate ISBN left over). On a fresh run with a clean DB, this test passes as expected.
    - All R5 late fee tests -> it fails because calculate_late_fee_for_book is not implemented yet (and hence it just returns None)
    - test_borrow_over_limit -> fails because the borrow logic checks book availability before enforcing the 5-book limit, so the test hits 'not available' instead of 'limit reached'.

--

[Note] : I clearly identifyied the missing/buggy functionalities as per the assignment. 

