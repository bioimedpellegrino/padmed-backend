from logger.models import Logger, LoggerMessage, WebRequest
from django.conf import settings
import json

def add_log(level, message=None, user=None, custom_message=None, request=None, exception=None):
    try:
        if message:
            try:
                msg = LoggerMessage.objects.get(pk=message)
            except:
                msg = LoggerMessage.objects.get(pk=1)
        else:
            msg = LoggerMessage.objects.get(pk=1)
        log = Logger(message=msg, level=level, request=request,exception=exception, custom_message=custom_message,)
        if user:
            log.user = user
        if request:
            web_request = _save_request(request)
            log.web_request = web_request
        log.save()
    except:
        pass

def _dumps(value):
    return json.dumps(value,default=lambda o:None, ensure_ascii=False)


def _save_request(request):
    from django.contrib.auth.models import User

    if hasattr(request, 'user'):
        user = request.user if type(request.user) == User else None
    else:
        user = None

    meta = request.META.copy()
    meta.pop('QUERY_STRING',None)
    meta.pop('HTTP_COOKIE',None)
    remote_addr_fwd = None

    if 'HTTP_X_FORWARDED_FOR' in meta:
        remote_addr_fwd = meta['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
        if remote_addr_fwd == meta['HTTP_X_FORWARDED_FOR']:
            meta.pop('HTTP_X_FORWARDED_FOR')

    post = None
    uri = request.build_absolute_uri()
    if request.POST:
        post = _dumps(request.POST)
    try:
        if not post and request.data:
            post = _dumps(request.data)
    except:
        pass



    web_req = WebRequest(
        host = request.get_host(),
        path = request.path,
        method = request.method,
        uri = request.build_absolute_uri(),
        #status_code = response.status_code,
        user_agent = meta.pop('HTTP_USER_AGENT',None),
        remote_addr = meta.pop('REMOTE_ADDR',None),
        remote_addr_fwd = remote_addr_fwd,
        meta = None if not meta else _dumps(meta),
        cookies = None if not request.COOKIES else _dumps(request.COOKIES),
        get = None if not request.GET else _dumps(request.GET),
        post = post,
        is_secure = request.is_secure(),
        is_ajax = request.is_ajax(),
        user = user
    )
    web_req.save()

    return web_req