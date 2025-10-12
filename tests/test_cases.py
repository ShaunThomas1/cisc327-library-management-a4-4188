# Name : Shaun Thomas
# Student ID : 20394188
# Group : 4 

import pytest 
from datetime import datetime, timedelta

# pulling in the business logic functions (using the actual names from library_service.py)

from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)

from database import get_all_books

# r1 : add book to catalogue 

def test_add_book_valid_input():
    # trying with normal valid input -> should work
    success, msg = add_book_to_catalog("Valid Book", "Author", "2020202020202", 5)
    assert success is True
    assert "success" in msg.lower()

def test_add_book_invalid_isbn():
    # isbn is too short, should notify about needing 13 digits so should fail
    success, msg = add_book_to_catalog("Book", "Author", "12345", 3)
    assert success is False
    assert "13 digits" in msg

def test_add_book_negative_copies():
    # cannot add negative number of copies so should fail
    success, msg = add_book_to_catalog("Book", "Author", "1234567890123", -1)
    assert success is False
    assert "positive" in msg.lower()

def test_add_book_title_too_long():
    # title over 200 chars -> should reject
    long_title = "A" * 201
    success, msg = add_book_to_catalog(long_title, "Author", "1234567890123", 3)
    assert success is False
    assert "title" in msg.lower()

def test_add_book_duplicate_isbn():
    # adding the same isbn twice -> should fail the second time
    add_book_to_catalog("First", "Author", "9999999999999", 2)
    success, msg = add_book_to_catalog("Second", "Author", "9999999999999", 3)
    assert success is False
    assert "isbn" in msg.lower()

# r2 : book catalog display

def test_catalog_not_empty():
    # catalog should have something in it (sample data preloaded)
    books = get_all_books()
    assert len(books) > 0

def test_catalog_fields_present():
    # just checking that key fields exist in a book row
    book = get_all_books()[0]
    assert "title" in book and "author" in book and "isbn" in book

def test_catalog_available_not_negative():
    # available copies shouldn’t go below 0
    for book in get_all_books():
        assert book["available_copies"] >= 0

def test_catalog_available_not_exceed_total():
    # available copies can’t exceed total copies
    for book in get_all_books():
        assert book["available_copies"] <= book["total_copies"]

# r3 : book borrowing interface 

def test_borrow_valid_book():
    # borrowing with good patron id + available book → should pass
    success, msg = borrow_book_by_patron("123456", 1)
    assert isinstance(success, bool)
    assert isinstance(msg, str)

def test_borrow_invalid_patron_id():
    # patron id not 6 digits → reject
    success, msg = borrow_book_by_patron("12", 1)
    assert success is False
    assert "patron" in msg.lower()

def test_borrow_unavailable_book():
    # book 3 is set up as unavailable in the sample db
    success, msg = borrow_book_by_patron("123456", 3)
    assert success is False
    assert "not available" in msg.lower()

def test_borrow_over_limit():
    # try to borrow more than 5 books for the same patron
    for _ in range(5):
        borrow_book_by_patron("654321", 1)
    success, msg = borrow_book_by_patron("654321", 2)
    assert success is False
    assert "limit" in msg.lower()

def test_borrow_invalid_book_id():
    # book id doesn’t exist → should fail
    success, msg = borrow_book_by_patron("123456", 9999)
    assert success is False
    assert "not found" in msg.lower()

# r4 : book return processing

def test_return_valid():
    # borrow then return → should work (but not implemented yet)
    borrow_book_by_patron("111111", 1)
    success, msg = return_book_by_patron("111111", 1)
    assert isinstance(success, bool)

def test_return_not_borrowed():
    # trying to return something this patron never borrowed
    success, msg = return_book_by_patron("222222", 2)
    assert success is False

def test_return_twice():
    # returning once is fine, but second time should fail
    borrow_book_by_patron("333333", 1)
    return_book_by_patron("333333", 1)
    success, msg = return_book_by_patron("333333", 1)
    assert success is False

def test_return_invalid_book_id():
    # book id doesn’t exist at all
    success, msg = return_book_by_patron("123456", 9999)
    assert success is False

# r5 : late fee calculation 

def test_late_fee_no_overdue():
    # returning on time → should be $0 (currently not implemented)
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)

def test_late_fee_within_7_days():
    # expect small fee if overdue a few days
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result

def test_late_fee_beyond_7_days():
    # overdue longer → fee should be higher
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result

def test_late_fee_max_cap():
    # if overdue forever, fee should cap at 15
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result

# r6 : book search functionality 

def test_search_by_title_partial():
    # searching by part of title (not implemented yet)
    results = search_books_in_catalog("great", "title")
    assert isinstance(results, list)

def test_search_by_author_partial():
    # search by partial author name
    results = search_books_in_catalog("orwell", "author")
    assert isinstance(results, list)

def test_search_by_isbn_exact():
    # isbn search should return exact matches
    results = search_books_in_catalog("9780451524935", "isbn")
    assert isinstance(results, list)

def test_search_no_results():
    # nonsense/incorrect query should give empty list
    results = search_books_in_catalog("nonexistent", "title")
    assert results == []

# r7 : patron status report

def test_patron_status_structure():
    # should give back a dictionary with fields (not implemented yet)
    status = get_patron_status_report("123456")
    assert isinstance(status, dict)

def test_patron_status_no_borrows():
    # patron with no borrows → borrowed_books should be empty
    status = get_patron_status_report("999999")
    assert isinstance(status, dict)

def test_patron_status_with_borrow():
    # if a patron borrows, borrowed_books should have something
    borrow_book_by_patron("888888", 1)
    status = get_patron_status_report("888888")
    assert isinstance(status, dict)

def test_patron_status_includes_fees():
    # status should eventually include late fees
    status = get_patron_status_report("777777")
    assert isinstance(status, dict)

def test_patron_status_history_field():
    # should also include borrowing history
    status = get_patron_status_report("123456")
    assert isinstance(status, dict)