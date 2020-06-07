from pycareer import log
from pycareer.job.models import Feed
from pycareer.aggregation import JobAggregator

logger = log.get_logger('service')


class FeedAggregation(object):
    @classmethod
    def _get_active_feeds(cls):
        return Feed.objects.filter(active=True)

    @classmethod
    def aggregate(cls):
        feeds = cls._get_active_feeds()
        for feed in feeds:
            logger.info('Starting to feed aggregation %s' % feed.name)

            try:
                JobAggregator.aggregate(feed.parser)
            except Exception:
                logger.exception('Exception in feed aggregation %s' % feed.name)
                pass

            logger.info('End of feed aggregation %s' % feed.name)
