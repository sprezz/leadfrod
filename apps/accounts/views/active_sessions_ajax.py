# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from json import dumps

from accounts.models import UserSession


@login_required
@user_passes_test(lambda u: u.is_superuser)
def active_sessions_ajax(request):
    actives = UserSession.objects.active_sessions().select_related('user__username')
    active_sesisons = []
    for s in actives:
        active_sesisons.append({
            'user': s.user.username,
            # 'logged_in': s.datetime_login,
            'duration': divmod(s.session_duration.seconds, 60)
        })

    return HttpResponse(dumps(active_sesisons))
