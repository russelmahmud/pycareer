import abc


class SearchEngine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def index(self, doc):
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, search_request):
        raise NotImplemented

    @abc.abstractmethod
    def delete(self, docs):
        raise NotImplemented


class SearchService(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def index(self, fields):
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, search_request, ids_only=False):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, document):
        raise NotImplementedError

    @abc.abstractmethod
    def build_document(self, fields):
        raise NotImplementedError
