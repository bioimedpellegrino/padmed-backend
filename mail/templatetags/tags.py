from urllib.parse import urlparse
from django.conf import settings
from django.template import Library

register = Library()

def get_current_server_site_domain():
    public_url = urlparse(settings.FULL_URL)
    return "%s://%s" % (public_url.scheme, public_url.hostname)

def get_current_server_port():
    public_url = urlparse(settings.FULL_URL)
    port = 443 if public_url.port is None and public_url.scheme == 'https' else 80 if public_url.port is None and public_url.scheme == 'http' else public_url.port
    return port

@register.inclusion_tag('mail/mail_header.html')
def mail_header(uuid=None):
    data = {}
    url = str(get_current_server_site_domain()) + ':' + str(get_current_server_port())
    data.update({'site_name': settings.SITE_NAME})
    data.update({'url': url})
    data.update({'uuid': uuid })

    return data


@register.inclusion_tag('mail/mail_footer.html')
def mail_footer(uuid=None, unsubscribe=None):
    data = {}
    url = str(get_current_server_site_domain()) + ':' + str(get_current_server_port())
    data.update({'site_name': settings.SITE_NAME})
    data.update({'url': url})
    data.update({'uuid': uuid })
    data.update({'unsubscribe': unsubscribe })


    return data