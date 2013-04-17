# -*- coding:utf-8 -*-
import datetime

from django.db import models


SESSION_EXPIRE_IN = 60

class UserSessionManager(models.Manager):
    def active_sessions(self):
        active_datetime = datetime.datetime.now() - datetime.timedelta(seconds=SESSION_EXPIRE_IN)
        return self.filter(datetime_last_activity__gte=active_datetime)

    def update_active_session(self, user):
        try:
            session = self.active_sessions().filter(user=user).order_by('-id')[0]
        except IndexError:
            session = self.create(user=user)
        session.save()


class UserSession(models.Model):
    user = models.ForeignKey('auth.User')
    datetime_login = models.DateTimeField()
    datetime_last_activity = models.DateTimeField()

    objects = UserSessionManager()

    class Meta:
        app_label = 'accounts'

    @property
    def session_duration(self):
        return self.datetime_last_activity - self.datetime_login

    @property
    def active(self):
        return self.datetime_last_activity > (datetime.datetime.now() - datetime.timedelta(seconds=SESSION_EXPIRE_IN))

    def save(self, *args, **kwargs):
        if self.id is None:
            self.datetime_login = datetime.datetime.now()
        self.datetime_last_activity = datetime.datetime.now()
        super(UserSession, self).save(*args, **kwargs)
