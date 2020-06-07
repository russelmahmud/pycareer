class ServiceError(Exception):
    pass


class ValidationError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class SearchError(ServiceError):
    pass


class IndexError(ServiceError):
    pass
