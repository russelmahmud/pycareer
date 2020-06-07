from pycareer.core.countries import get_country_name
from pycareer import log
from .gae import GaeSearch, GaeSearchEngine

logger = log.get_logger('service')


class DeveloperSearch(object):
    def __init__(self, index_name='developers', namespace='pycareer'):
        self.engine = GaeSearchEngine(index_name, namespace)

    def index(self, profile):
        document = self.build_document(profile)
        self.engine.index(document)

    @classmethod
    def build_document(cls, profile):
        return GaeSearch.Document(
                doc_id=str(profile.id),
                fields=[
                    GaeSearch.TextField(name='first_name', value=profile.user.first_name),
                    GaeSearch.TextField(name='last_name', value=profile.user.last_name),
                    GaeSearch.TextField(name='title', value=profile.title),
                    GaeSearch.TextField(name='skills', value=profile.skills),
                    GaeSearch.HtmlField(name='summary', value=profile.summary),
                    GaeSearch.TextField(name='city', value=profile.city),
                    GaeSearch.TextField(name='state', value=profile.state),
                    GaeSearch.TextField(name='country', value=get_country_name(profile.country)),
                    GaeSearch.DateField(name='modified_at', value=profile.modified_at)
                ]
        )
