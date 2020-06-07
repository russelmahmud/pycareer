from lxml import html

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives


class EmailService(object):
    default_email = settings.DEFAULT_FROM_EMAIL
    no_reply = settings.NO_REPLY_EMAIL
    support_email = settings.SUPPORT_EMAIL

    def send_support(self, subject, template, ctx=None, from_email=None):
        text, html_content = self._render_template(template, ctx or {})
        self._send(subject, text, [self.support_email], html_content=html_content,
                   from_email=from_email)

    def _send(self, subject, body, recipients, html_content=None, from_email=None):
        from_email = from_email or self.no_reply
        msg = EmailMultiAlternatives(subject, body, from_email, recipients)

        if html_content:
            msg.attach_alternative(html_content, "text/html")

        msg.send()

    def _render_template(self, template, data):
        template = get_template(template)
        html_content = template.render(Context(data))
        text_content = html.fromstring(html_content).text_content()
        return text_content, html_content
