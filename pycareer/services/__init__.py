import importlib
from .errors import ServiceError, ValidationError, NotFoundError, SearchError

services = dict(
    job='pycareer.services.job.JobService',
    event='pycareer.services.event.EventService',
    indeed='pycareer.services.indeed.IndeedApi',
    job_search='pycareer.services.search.JobSearch',
    developer_search='pycareer.services.search.DeveloperSearch',
    email='pycareer.services.email.EmailService'
)


def import_object(name):
    module_name, object_name = name.rpartition('.')[::2]
    module = importlib.import_module(module_name)
    return getattr(module, object_name)


def get_service(name, *args):
    classname = services[name]
    return import_object(classname)(*args)
