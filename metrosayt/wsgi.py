"""
WSGI config for metrosayt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('Sunnat', 'sunnatsavriyev39@gmail.com', 'savriyev1123')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metrosayt.settings')

application = get_wsgi_application()
