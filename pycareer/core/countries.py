from operator import itemgetter
import choices

COUNTRIES = [
    {
        'code': 'us',
        'name': 'United States',
        'slug': 'united_states'
    },
    {
        'code': 'ca',
        'name': 'Canada',
        'slug': 'canada'
    },
    {
        'code': 'za',
        'name': 'South Africa',
        'slug': 'south_africa'
    },
    {
        'code': 'ar',
        'name': 'Argentina',
        'slug': 'argentina'
    },
    {
        'code': 'br',
        'name': 'Brazil',
        'slug': 'brazil'
    },
    {
        'code': 'gb',
        'name': 'United Kingdom',
        'slug': 'united_kingdom'
    },
    {
        'code': 'nl',
        'name': 'Netherlands',
        'slug': 'netherlands'
    },
    {
        'code': 'es',
        'name': 'Spain',
        'slug': 'spain'
    },
    {
        'code': 'se',
        'name': 'Sweden',
        'slug': 'sweden'
    },
    {
        'code': 'ch',
        'name': 'Switzerland',
        'slug': 'switzerland'
    },
    {
        'code': 'in',
        'name': 'India',
        'slug': 'india'
    },
    {
        'code': 'fr',
        'name': 'France',
        'slug': 'france'
    },
    {
        'code': 'de',
        'name': 'Germany',
        'slug': 'germany'
    },
    {
        'code': 'ie',
        'name': 'Ireland',
        'slug': 'ireland'
    },
    {
        'code': 'il',
        'name': 'Israel',
        'slug': 'israel'
    },
    {
        'code': 'au',
        'name': 'Australia',
        'slug': 'australia'
    },
    {
        'code': 'nz',
        'name': 'New Zealand',
        'slug': 'new_zealand'
    },
    {
        'code': 'sg',
        'name': 'Singapore',
        'slug': 'singapore'
    },
    {
        'code': 'ru',
        'name': 'Russia',
        'slug': 'russia'
    },
    {
        'code': 'cn',
        'name': 'China',
        'slug': 'china'
    },
]

SORTED_COUNTRIES = sorted(COUNTRIES, key=itemgetter('name'))


def get_country_by_slug(slug):
    countries = filter(lambda person: person['slug'] == slug, COUNTRIES)
    return countries[0] if countries else None


def get_country_name(code):
    return dict(choices.COUNTRIES).get(code, code)
