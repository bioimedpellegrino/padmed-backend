# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['HTTPS'] = "on"

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

application = get_wsgi_application()