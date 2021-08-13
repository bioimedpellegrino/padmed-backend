from builtins import str
from builtins import object
from django.db import models, DatabaseError
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from custom_logger.middlewares import get_current_user
import uuid

class Mail(models.Model):

    id = models.AutoField(primary_key=True, verbose_name='Mail ID')
    sent = models.BooleanField(default=False, verbose_name='Has sent email')
    request_date = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Data of send request')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Data of effective send')
    retry = models.IntegerField(null=True, blank=True, default=0, verbose_name='Number of retry')
    from_who = models.CharField(verbose_name='From',max_length=255, null=True, blank=True,)
    reply_to = models.CharField(verbose_name='Reply to',max_length=255, null=True, blank=True,)
    to_who = models.TextField(verbose_name='To separated with ; ', null=True, blank=True,)
    cc_who = models.TextField(verbose_name='CC separated with ; ', null=True, blank=True,)
    bcc_who = models.TextField(verbose_name='BCC separated with ; ', null=True, blank=True,)
    subject = models.TextField(verbose_name='Subject', null=True, blank=True,)
    json_message = models.TextField(verbose_name='JSON Message', null=True, blank=True,)
    template_name = models.CharField(verbose_name='Template name',max_length=255, null=True, blank=True,)
    attachments = models.TextField(verbose_name='Attachments separated with ; ', null=True, blank=True,)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    html_text = models.TextField(verbose_name='Html Text', null=True, blank=True,)
    txt_text = models.TextField(verbose_name='Txt Text', null=True, blank=True,)

    class Meta(object):
        verbose_name = 'Mail'
        verbose_name_plural = 'Mails'

    def __str__(self):
        return str(self.sent) + ' - ' + str(self.from_who) + ' - ' + str(self.subject)

    def save(self, *args, **kwargs):
        if not self.from_who:
            from django.conf import settings
            self.from_who = settings.DEFAULT_FROM_EMAIL
        if not self.reply_to:
            from django.conf import settings
            self.reply_to = settings.DEFAULT_FROM_EMAIL
        if not self.bcc_who:
            from django.conf import settings
            self.bcc_who = settings.DEFAULT_FROM_EMAIL
        super(Mail, self).save(*args, **kwargs) # Call the "real" save() method.
