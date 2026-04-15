OPEN_LIBRARY_URL = "https://openlibrary.org"

def get_cover_url(isbn: str, size: str = "M") -> str:
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"