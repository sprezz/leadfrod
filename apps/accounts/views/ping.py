# -*- coding:utf-8 -*-
from django.http import HttpResponse, HttpResponseForbidden
from json import dumps
from accounts.models import UserSession


def ping(request):
    if request.user.is_authenticated():
        UserSession.objects.update_active_session(request.user)
        return HttpResponse(dumps({}))
    else:
        return HttpResponseForbidden()
