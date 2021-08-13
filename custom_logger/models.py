from builtins import str
from builtins import object
from django.db import models, DatabaseError
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from custom_logger.middlewares import get_current_user

LOGGER_LEVEL = (
        (1, 'DEBUG'),
        (2, 'INFO'),
        (3, 'WARNING'),
        (4, 'ERROR'),
        (5, 'CRITICAL'),
    )


class Logger(models.Model):

    log_id = models.AutoField(primary_key=True, verbose_name='Log ID')
    level = models.IntegerField(null=True, blank=True, choices=LOGGER_LEVEL, verbose_name='logger level')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User", null=True, blank=True, default=get_current_user)
    entity = models.CharField(verbose_name='Entity',max_length=255, null=True, blank=True,)
    entity_id = models.CharField(verbose_name='Entity id',max_length=255, null=True, blank=True,)
    date = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Data')

    request = models.TextField(verbose_name='Request', null=True, blank=True,)
    exception = models.TextField(verbose_name='Exception', null=True, blank=True,)

    custom_message = models.TextField(verbose_name='Logging message', null=True, blank=True,)
    message = models.ForeignKey('LoggerMessage', on_delete=models.CASCADE, null=True, blank=True, related_name='mesasge')
    web_request = models.ForeignKey('WebRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='web_request')

    class Meta(object):
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'

    def __str__(self):
        return str(self.level) + ' - ' + str(self.user) + ' - ' + str(self.message) + ' - ' + str(self.date)


class LoggerMessage(models.Model):
    log_message_id = models.IntegerField(primary_key=True, verbose_name='Log message ID')
    message = models.TextField(verbose_name='Logging message', null=True, blank=True,)

    class Meta(object):
        verbose_name = 'Log message'
        verbose_name_plural = 'Log messages'

    def __str__(self):
        return str(self.message)


class WebRequest(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    host = models.CharField(max_length=1000)
    path = models.CharField(max_length=1000)
    method = models.CharField(max_length=50)
    uri = models.CharField(max_length=2000)
    user_agent = models.CharField(max_length=1000,blank=True,null=True)
    remote_addr = models.GenericIPAddressField()
    remote_addr_fwd = models.GenericIPAddressField(blank=True,null=True)
    meta = models.TextField()
    cookies = models.TextField(blank=True,null=True)
    get = models.TextField(blank=True,null=True)
    post = models.TextField(blank=True,null=True)
    is_secure = models.BooleanField()
    is_ajax = models.BooleanField()
    user = models.ForeignKey(User,  on_delete=models.CASCADE, blank=True,null=True)

    class Meta(object):
        verbose_name = 'Web request'
        verbose_name_plural = 'Web requests'

    def __str__(self):
        return str(self.id) + ' - ' + str(self.uri) + ' - ' + str(self.remote_addr) + ' - ' + str(self.user)
