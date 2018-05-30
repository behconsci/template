from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def send_email_in_template(subject, receiver, **data):
    html_content = render_to_string('email/template.html', data)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        '{{ project_name }} <info@{{ project_name }}.com>', [receiver]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
