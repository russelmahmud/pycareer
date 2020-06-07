from django.conf import settings
from django.contrib.messages.api import get_messages
from django.contrib.messages.constants import DEFAULT_TAGS


def env_processor(request):
    return {
        'is_production': settings.IS_PRODUCTION,
        'SITE_URL': 'http://www.pycareer.com',
        'SITE_COMMON_META': 'PyCareer is a platform to build python career. Full of python jobs, python events, tutorial in python programming language and python conf information.',
        'EVENT_COMMON_META': 'Python events around the world. Find python conference, workshop, user group meeting, bar camp, sprint, local meetups or other events near to your place. Submit any python event in PyCareer to reach thousands of python developers, employers or lovers.',
        'JOB_COMMON_META': 'The leading python job board. See python, django related jobs around the world.',
        'BOOK_COMMON_META': 'Python Books. Best selling python books. Python Web, GUI, Networking Books. Find most read python programming books.'
    }


def messages(request):
    """
    Returns a lazy 'messages' context variable.
    """
    messages = []
    for msg in get_messages(request):
        messages.append({
            'message': msg.message,
            'level_tag': DEFAULT_TAGS[msg.level],
            'tags': msg.extra_tags
        })
    return {'messages': messages}
