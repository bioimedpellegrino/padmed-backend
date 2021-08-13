from builtins import str
from django.contrib import admin
from custom_logger.models import  Logger, LoggerMessage, WebRequest

def custom_logger_delete(modeladmin, request, queryset):
    # for item in queryset.all():
    #     item.delete()
    if queryset.count() > 0:
        from django.db import connection
        cursor = connection.cursor()
        try:
            selected_items = str(list(queryset.all().values_list('log_id', flat=True)))[1:-1]
            sql = 'DELETE FROM custom_logger_logger WHERE log_id IN (%s)' % selected_items
            # cursor.execute("BEGIN")
            cursor.execute(sql)
            # cursor.execute("COMMIT")
        finally:
            cursor.close()
custom_logger_delete.short_description = "Rapid Delete Selected Items"

class LoggerAdmin(admin.ModelAdmin):
    list_filter = ('level', 'user', 'entity', 'entity_id', 'date', 'message')
    list_display = ('log_id', 'level', 'user', 'entity', 'entity_id', 'date', 'message','custom_message')
    actions = [custom_logger_delete]
    readonly_fields = ('web_request',)

class LoggerMessageAdmin(admin.ModelAdmin):
    pass

class WebRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'uri', 'remote_addr','user')

admin.site.register(Logger, LoggerAdmin)
admin.site.register(LoggerMessage, LoggerMessageAdmin)
admin.site.register(WebRequest, WebRequestAdmin)