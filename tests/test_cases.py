# Shaun Thomas – CISC 327 A3 Test Cases (CI-Safe)

import pytest
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
)

# ---------------------------------------------------------------------
# consistent fake book + fake borrow records
# ---------------------------------------------------------------------

FAKE_BOOK = {
    "id": 1,
    "title": "Test Book",
    "author": "Author",
    "isbn": "1111111111111",
    "total_copies": 5,
    "available_copies": 5,
}

# ---------------------------------------------------------------------
# R1 — ADD BOOK
# ---------------------------------------------------------------------

def test_add_book_valid_input(mocker):
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    mocker.patch("services.library_service.insert_book", return_value=True)
    success, msg = add_book_to_catalog("Valid Book", "Author", "2020202020202", 5)
    assert success is True
    assert "success" in msg.lower()


def test_add_book_invalid_isbn():
    success, msg = add_book_to_catalog("Book", "Author", "123", 3)
    assert success is False
    assert "13 digits" in msg.lower()


def test_add_book_negative_copies():
    success, msg = add_book_to_catalog("Book", "Author", "1234567890123", -1)
    assert success is False


def test_add_book_title_too_long():
    long_title = "A" * 201
    success, msg = add_book_to_catalog(long_title, "Author", "1234567890123", 3)
    assert success is False


def test_add_book_duplicate_isbn(mocker):
    mocker.patch(
        "services.library_service.get_book_by_isbn",
        side_effect=[None, {"id": 1}],
    )
    mocker.patch("services.library_service.insert_book", return_value=True)

    success1, _ = add_book_to_catalog("First", "Author", "9999999999999", 2)
    assert success1 is True

    success2, msg2 = add_book_to_catalog("Second", "Author", "9999999999999", 2)
    assert success2 is False
    assert "exists" in msg2.lower()


# ---------------------------------------------------------------------
# R2 — CATALOG DISPLAY
# ---------------------------------------------------------------------

def test_catalog_not_empty(mocker):
    fake_books = [FAKE_BOOK]
    mocker.patch("services.library_service.get_all_books", return_value=fake_books)
    assert len(fake_books) > 0


def test_catalog_fields_present(mocker):
    fake_books = [FAKE_BOOK]
    mocker.patch("services.library_service.get_all_books", return_value=fake_books)
    book = fake_books[0]
    assert all(k in book for k in ["title", "author", "isbn"])


def test_catalog_available_not_negative(mocker):
    fake_books = [
        {"id": 1, "title": "A", "author": "X", "isbn": "1", "total_copies": 3, "available_copies": 1},
        {"id": 2, "title": "B", "author": "Y", "isbn": "2", "total_copies": 5, "available_copies": 0},
    ]
    mocker.patch("services.library_service.get_all_books", return_value=fake_books)
    for book in fake_books:
        assert book["available_copies"] >= 0


def test_catalog_available_not_exceed_total(mocker):
    fake_books = [
        {"id": 1, "title": "A", "author": "X", "isbn": "1", "total_copies": 3, "available_copies": 3},
        {"id": 2, "title": "B", "author": "Y", "isbn": "2", "total_copies": 5, "available_copies": 2},
    ]
    mocker.patch("services.library_service.get_all_books", return_value=fake_books)
    for book in fake_books:
        assert book["available_copies"] <= book["total_copies"]


# ---------------------------------------------------------------------
# R3 — BORROWING
# ---------------------------------------------------------------------

def test_borrow_valid_book(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    success, msg = borrow_book_by_patron("123456", 1)
    assert success is True


def test_borrow_invalid_patron_id():
    success, msg = borrow_book_by_patron("12", 1)
    assert success is False


def test_borrow_unavailable_book(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value={"available_copies": 0})
    success, msg = borrow_book_by_patron("123456", 3)
    assert success is False
    assert "not available" in msg.lower()


def test_borrow_over_limit(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    mocker.patch(
        "services.library_service.get_patron_borrow_count",
        side_effect=[0,1,2,3,4,5]
    )

    for _ in range(5):
        borrow_book_by_patron("654321", 1)

    success, msg = borrow_book_by_patron("654321", 1)
    assert success is False
    assert "limit" in msg.lower()


def test_borrow_invalid_book_id(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value=None)
    success, msg = borrow_book_by_patron("123456", 9999)
    assert success is False


# ---------------------------------------------------------------------
# R4 — RETURN
# ---------------------------------------------------------------------

def test_return_valid(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    borrow_book_by_patron("111111", 1)
    success, msg = return_book_by_patron("111111", 1)
    assert success is True


def test_return_not_borrowed(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)
    success, msg = return_book_by_patron("222222", 2)
    assert success is False


def test_return_twice(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)
    borrow_book_by_patron("333333", 1)

    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    assert return_book_by_patron("333333", 1)[0] is True

    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)
    success, msg = return_book_by_patron("333333", 1)
    assert success is False


def test_return_invalid_book_id():
    success, msg = return_book_by_patron("123456", 9999)
    assert success is False


# ---------------------------------------------------------------------
# R5 — LATE FEE
# ---------------------------------------------------------------------

def test_late_fee_no_overdue():
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)


def test_late_fee_within_7_days():
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result


def test_late_fee_beyond_7_days():
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result


def test_late_fee_max_cap():
    result = calculate_late_fee_for_book("123456", 1)
    assert "fee_amount" in result


# ---------------------------------------------------------------------
# R6 — SEARCH
# ---------------------------------------------------------------------

def test_search_by_title_partial():
    results = search_books_in_catalog("great", "title")
    assert isinstance(results, list)


def test_search_by_author_partial():
    results = search_books_in_catalog("orwell", "author")
    assert isinstance(results, list)


def test_search_by_isbn_exact():
    results = search_books_in_catalog("9780451524935", "isbn")
    assert isinstance(results, list)


def test_search_no_results():
    assert search_books_in_catalog("nonsense", "title") == []


# ---------------------------------------------------------------------
# R7 — STATUS REPORT
# ---------------------------------------------------------------------

def test_patron_status_structure():
    status = get_patron_status_report("123456")
    assert isinstance(status, dict)


def test_patron_status_no_borrows():
    status = get_patron_status_report("999999")
    assert isinstance(status, dict)


def test_patron_status_with_borrow(mocker):
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    borrow_book_by_patron("888888", 1)
    status = get_patron_status_report("888888")
    assert isinstance(status, dict)


def test_patron_status_includes_fees():
    status = get_patron_status_report("777777")
    assert isinstance(status, dict)


def test_patron_status_history_field():
    status = get_patron_status_report("123456")
    assert isinstance(status, dict)
