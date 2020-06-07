import abc


class Service(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, data):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, id_, data):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id_):
        raise NotImplementedError
