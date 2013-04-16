# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def active_sessions(request):
    return render_to_response('accounts/active_sessions.html')
