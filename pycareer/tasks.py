from django.http import HttpResponse
from google.appengine.ext import deferred

from pycareer import log
from pycareer.services import get_service

logger = log.get_logger()


def start_aggregation(request, deferred):
    from pycareer.services.aggregation import FeedAggregation
    logger.info('Starting aggregation cron job')
    FeedAggregation.aggregate()
    logger.info('Ending aggregation cron job')
    return HttpResponse('Success')


def archive_old_job(request, deferred):
    job_service = get_service('job')
    logger.info('Starting archiving cron job')
    job_service.archive_jobs()
    logger.info('Ending archiving cron job')
    return HttpResponse('Success')


def job_approval_post_actions(job_ids):
    job_service = get_service('job')
    logger.info('Starting deferred indexing jobs')
    deferred.defer(job_service.index_jobs, job_ids, _countdown=10)
    logger.info('Ending deferred indexing jobs')


def extract_events(request, deferred=None):
    from pycareer.aggregation import EventExtractor
    logger.info('Starting event extracting cron job')
    # Cals IDs from https://wiki.python.org/moin/PythonEventsCalendar
    event_cal_id = 'j7gov1cmnqr9tvg14k621j7t5c@group.calendar.google.com'
    group_cal_id = '3haig2m9msslkpf2tn1h56nn9g@group.calendar.google.com'
    extractor = EventExtractor()
    events = (
        (event_cal_id, 'Python Events', 'False'),
        (group_cal_id, 'User Group Events', 'True')
    )
    for event in events:
        extractor.extract(event[0], event[1], singleEvents=event[2])

    logger.info('Ending event extracting cron job')
    return HttpResponse('Success')