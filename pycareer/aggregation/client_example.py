from pycareer import log
from pycareer.aggregation import JobAggregator

logger = log.get_logger('parser')


class Feed(object):
    feeds = [
        {'name': 'Python.org RSS', 'parser': 'python_org_rss'},
        # {'name': 'Python.org HTML', 'parser': 'python_org_html'}
    ]

    @classmethod
    def all(cls):
        return cls.feeds

    @classmethod
    def aggregate(cls, feed):
        JobAggregator.aggregate(feed['parser'])


def run():
    for feed in Feed.all():
        logger.info('Starting to aggregate %s' % feed['name'])

        try:
            Feed.aggregate(feed)
        except Exception:
            logger.exception('Exception in aggregation %s' % feed['name'])
            pass

        logger.info('End of aggregation %s' % feed['name'])


if __name__ == '__main__':
    '''
    Example : python client_example.py
    '''
    run()
