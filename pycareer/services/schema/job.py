from django.conf import settings
from marshmallow import Schema, fields, pre_load

from .fields import CustomDateTime


class SearchRequestSchema(Schema):
    offset = fields.Int(required=True, default=0)
    limit = fields.Int(required=True, default=settings.LIST_PAGE_SIZE)
    query = fields.String(required=False, default='')
    sort = fields.String(required=True, default='date')

    def make_object(self, in_data):
        for name, field in self.fields.items():
            if name not in in_data:
                in_data[name] = field.default
        return in_data


class JobCreateSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    will_sponsor = fields.Boolean(required=True)
    visas = fields.Str(allow_none=True)
    city = fields.Str(required=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(required=True)
    published_at = CustomDateTime(allow_none=True)
    company_name = fields.Str(required=True)
    company_description = fields.Str(allow_none=True)
    contact_email = fields.Str(required=True)
    contact_name = fields.Str(allow_none=True)
    contact_url = fields.Str(allow_none=True)
    provider_id = fields.Str(allow_none=True)
    provider_link = fields.Str(allow_none=True)
    submitted_by = fields.Integer(required=True)

    class Meta:
        strict = True


class JobUpdateSchema(Schema):
    title = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    will_sponsor = fields.Boolean(required=True)
    visas = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    published_at = CustomDateTime(allow_none=True)
    company_name = fields.Str(allow_none=True)
    company_description = fields.Str(allow_none=True)
    contact_email = fields.Str(allow_none=True)
    contact_name = fields.Str(allow_none=True)
    contact_url = fields.Str(allow_none=True)
    provider_id = fields.Str(allow_none=True)
    provider_link = fields.Str(allow_none=True)

    class Meta:
        strict = True


class IndeedJobSchema(Schema):
    title = fields.Str(load_from='jobtitle')
    snippet = fields.Str(required=True)
    company = fields.Str(required=True)
    location = fields.Str(required=True)
    relative_time = fields.Str(load_from='formattedRelativeTime')
    url = fields.Str(required=True)

    class Meta:
        strict = True

    @pre_load
    def format_location(self, in_data):
        in_data['location'] = in_data['formattedLocation'] + ', ' + in_data['country']
        return in_data


class JobListResponse(Schema):
    num_found = fields.Integer(required=True)
    items = fields.Nested(IndeedJobSchema, many=True)
