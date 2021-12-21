# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django import template
from django.conf import settings

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'

    # html_template = loader.get_template( 'index.html' )
    return HttpResponseRedirect(reverse('live_dash'))

# @login_required(login_url="/login/")
# def pages(request):
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
        
#         load_template      = request.path.split('/')[-1]
#         context['segment'] = load_template
#         html_template = loader.get_template( load_template )
#         return HttpResponse(html_template.render(context, request))
        
#     except template.TemplateDoesNotExist:
#         if settings.DEBUG:
#             import traceback
#             traceback.print_exc()
#         html_template = loader.get_template( 'page-404.html' )
#         return HttpResponse(html_template.render(context, request))

#     except:
#         if settings.DEBUG:
#             import traceback
#             traceback.print_exc()
#         html_template = loader.get_template( 'page-500.html' )
#         return HttpResponse(html_template.render(context, request))


