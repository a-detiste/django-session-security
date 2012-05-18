import datetime

from django.contrib import auth
from django.views import generic
from django import http

__all__ = ['PingView',]


class PingView(generic.View):
    """
    Return a text response with instructions for the javascript.

    3 possible return values:

    - if the session has expired, return string 'expire',
    - if the user should be warned that the session will expire, return string 'warn',
    - if the user has generated activity, return the lifetime of the session in seconds.
    """

    def get(self, request, *args, **kwargs):
        from settings import WARN_AFTER, EXPIRE_AFTER, SKEW_MARGIN

        now = datetime.datetime.now()

        if 'session_security' not in request.session.keys():
            return http.HttpResponse('-1')

        client_since_activity = int(request.GET['sinceActivity'])
        client_last_activity = now - datetime.timedelta(seconds=client_since_activity)

        server_last_activity = request.session['session_security']['last_activity']
        server_since_activity = (now - server_last_activity).seconds

        print client_since_activity, server_since_activity

        if client_since_activity < 0 or server_last_activity > client_last_activity:
            last_activity = server_last_activity
            since_activity = server_since_activity
        else:
            print 'use client since', client_since_activity
            last_activity = client_last_activity
            since_activity = client_since_activity

            request.session['session_security']['last_activity'] = client_last_activity
            request.session.save()

        if since_activity > EXPIRE_AFTER:
            auth.logout(request)

        print "RETURN:", since_activity
        return http.HttpResponse(since_activity)