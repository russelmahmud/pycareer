from marshmallow import fields
import datetime


class CustomDateTime(fields.DateTime):

    def _deserialize(self, val):
        if isinstance(val, datetime.datetime):
            val = val.isoformat()
        return fields.DateTime._deserialize(self, val)
