from __future__ import print_function
from __future__ import absolute_import
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator
from custom_logger.utils import add_log
from django.urls import reverse
from .models import Mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import copy
import json

class RenderMailView(View):

    template_name = ''
 
    def get(self, request, *args, **kwargs):
        m = Mail.objects.get(uuid=kwargs.get('uuid'))
        self.template_name = 'mail/' + m.template_name + '.html'
        return HttpResponse(m.html_text)
    
class SentMailListView(View):

    template_name = 'custom_mail/sent_mail_list.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser is True:
            from .models import Mail

            mails=Mail.objects.all()

            return render(request, self.template_name, {'mails': mails })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)

class SentMailView(View):

    template_name = 'custom_mail/sent_mail.html'

    def get(self, request, *args, **kwargs):
        mail_id = kwargs.get("id", None)

        # If user in role Filters Viewer
        # 31: Dashboard email notification

        if request.user.is_superuser is True:
            from .models import Mail

            if mail_id:
                mail=Mail.objects.get(pk=mail_id)
            else:
                mail=None

            return render(request, self.template_name, {'mail': mail })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)