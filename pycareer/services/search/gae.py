from google.appengine.api import search as GaeSearch
from pycareer.services.errors import IndexError, SearchError
from .base import SearchEngine


class GaeSearchEngine(SearchEngine):
    def __init__(self, index_name, namespace):
        self.index_name = index_name
        self.namespace = namespace

    def index(self, document):
        try:
            index = self._get_index()
            index.put(document)
        except GaeSearch.Error:
            raise IndexError('Index creation failed')

    def search(self, search_request, **kwargs):
        try:
            query = self._build_query(search_request, **kwargs)
            index = self._get_index()
            search_results = index.search(query)
        except GaeSearch.Error:
            raise SearchError('Search failed')

        return search_results

    def delete(self, document_ids):
        try:
            index = self._get_index()
            index.delete(document_ids)
        except GaeSearch.Error:
            raise IndexError('Index deletion failed')

    def clean_index(self):
        doc_index = self._get_index()

        # looping because get_range by default returns up to 100 documents at a time
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)

    def _get_index(self):
        return GaeSearch.Index(name=self.index_name, namespace=self.namespace)

    def _build_query(self, options, ids_only=False, returned_expressions=None,
                     sort_options=None, returned_fields=None):
        """Build and return a search query object."""
        search_query = GaeSearch.Query(
            query_string=options['query'],
            options=GaeSearch.QueryOptions(
                limit=options['limit'],
                offset=options['offset'],
                ids_only=ids_only,
                sort_options=sort_options,
                returned_fields=returned_fields,
                returned_expressions=returned_expressions
            ))
        return search_query
