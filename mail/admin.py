from django.contrib import admin
from mail.models import Mail
from mail.utils import _send
from django.utils.html import format_html

def send_selected(modeladmin, request, queryset):
    for mail in queryset:
        _send(mail)
send_selected.short_description = "Send selected mail"

class MailAdmin(admin.ModelAdmin):
    actions = [send_selected]
    list_display = ('pk', 'to_who', 'subject', 'request_date', 'sent', 'uuid', 'my_url_field')
    list_filter = ('sent', )
    ordering = ['-pk']

    def my_url_field(self, obj):
        return format_html('<a href="/mail/render/%s/" target="_blank">Open</a>' % (obj.uuid))
        
    my_url_field.short_description = 'Details'

admin.site.register(Mail, MailAdmin)
