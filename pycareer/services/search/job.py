from datetime import datetime
from pycareer.job.models import Job
from pycareer.core.countries import get_country_name
from pycareer.services.utils import convert_to_list, get_relative_time, create_snippet
from pycareer import log
from .gae import GaeSearch, GaeSearchEngine

logger = log.get_logger('service')


class JobSearch(object):
    def __init__(self, index_name='jobs', namespace='pycareer'):
        self.engine = GaeSearchEngine(index_name, namespace)

    def index(self, fields):
        document = self.build_document(fields)
        self.engine.index(document)

    def delete(self, document):
        doc_ids = convert_to_list(document)
        self.engine.delete(doc_ids)

    def search(self, search_request, code=None, **kwargs):
        """
        :param code: country code
        """
        kwargs['sort_options'] = self._create_sort_options(search_request.get('sort'))
        returned_expressions = [
            self._snippet_expression(search_request['query'], 210)
        ]
        kwargs['returned_expressions'] = returned_expressions

        if code is not None:
            search_request['query'] += ' %s:"%s"' % ('code', code)

        logger.debug('query: %s', search_request['query'])
        results = self.engine.search(search_request, **kwargs)

        return {
            'num_found': results.number_found,
            'items': self._format_response(results)
        }

    def delete_all_in_index(self):
        self.engine.clean_index()

    @classmethod
    def build_document(cls, fields):
        return GaeSearch.Document(
            doc_id=str(fields['id']),
            fields=[
                GaeSearch.TextField(name='title', value=fields['title']),
                GaeSearch.TextField(name='description', value=fields['description']),
                GaeSearch.TextField(name='company', value=fields['company_name']),
                GaeSearch.TextField(name='city', value=fields['city']),
                GaeSearch.TextField(name='state', value=fields['state']),
                GaeSearch.TextField(name='will_sponsor', value=str(fields['will_sponsor'])),
                GaeSearch.AtomField(name='code', value=fields['country']),
                GaeSearch.TextField(name='country', value=get_country_name(fields['country'])),
                GaeSearch.DateField(name='published_at', value=fields['published_at'])
            ]
        )

    def _create_sort_options(self, sortq):
        if sortq == 'date':
            expr1 = GaeSearch.SortExpression(expression='published_at', direction=GaeSearch.SortExpression.DESCENDING,
                                             default_value=datetime(2015, 01, 01))
            sort_options = GaeSearch.SortOptions(expressions=[expr1])
        else:
            sort_options = GaeSearch.SortOptions(match_scorer=GaeSearch.MatchScorer())

        return sort_options

    def _snippet_expression(self, query, max_chars=200):
        expr = 'snippet("%s", description, %d)' % (query or 'python', max_chars)
        return GaeSearch.FieldExpression(name='snippet', expression=expr)

    def _format_response(self, docs):
        items = []

        for doc in docs:
            title = doc.field('title').value
            item = {
                'title': title,
                'will_sponsor': doc.field('will_sponsor').value,
                'company': doc.field('company').value,
                'location': Job.location(doc.field('city').value,
                                         doc.field('state').value,
                                         doc.field('country').value),
                'relative_time': get_relative_time(doc.field('published_at').value),
                'url': Job.get_full_url(doc.doc_id, title)
            }
            snippet = None
            for expr in doc.expressions:
                if expr.name == 'snippet':
                    snippet = expr.value
                    break

            if snippet is None:
                snippet = create_snippet(title, start_index=5, max_chars=220)

            item['snippet'] = snippet
            items.append(item)

        return items
