"""
Custom pagination class used by all list endpoints (GET /documents, GET /queries).

Pagination splits large datasets into pages so the API never returns
thousands of records in a single response.

Usage:
    GET /documents?page=2&page_size=5

Response shape:
    {
        "count": 42,              <- total number of records
        "next": "/documents?page=3",    <- URL of the next page (null if last page)
        "previous": "/documents?page=1",  <- URL of the previous page (null if first page)
        "results": [...]          <- the records for THIS page
    }
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    # Default records per page when ?page_size is not specified
    page_size = 10

    # Clients can override page size with ?page_size=N
    # Example: GET /documents?page_size=25
    page_size_query_param = 'page_size'

    # Upper limit — prevents clients from requesting ?page_size=10000
    max_page_size = 100

    # The URL parameter name for the page number
    # Example: GET /documents?page=3
    page_query_param = 'page'
