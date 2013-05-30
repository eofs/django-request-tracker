import httplib
import urllib

from django.conf import settings


class BaseBackend(object):
    host = None
    url = '/'
    method = 'POST'

    def send(self, params, headers=None):
        if self.host is None:
            return

        conn = httplib.HTTPSConnection(self.host)
        params = urllib.urlencode(params)
        conn.request(self.method, self.url, params, headers)
        conn.getresponse()

    def get_anonymous_id(self, request):
        host = request.META.get('HTTP_HOST')
        user_agent = request.META.get('HTTP_USER_AGENT')
        user_id = hash(''.join([host, user_agent]))
        return 'anon-%s' % user_id

    def page(self, request,host, path):
        # Override this method to send page views
        pass

class GoogleAnalytics(BaseBackend):
    host = 'ssl.google-analytics.com'
    url = '/collect'

    def __init__(self):
        self.analytics_key = getattr(settings, 'GOOGLE_ANALYTICS_KEY', None)

    def page(self, request, response):
        host = request.META.get('HTTP_HOST')
        user_agent = request.META.get('HTTP_USER_AGENT')
        path = request.path

        # UA does not support X-Forwarded-For yet.
        #ip = request.META.get('REMOTE_ADDR')

        if request.user.is_authenticated():
            cid = request.user.pk
        else:
            cid = self.get_anonymous_id(request)

        headers = {
            'User-Agent': user_agent,
        }
        parameters = {
            'v': 1,                         # Version
            'tid': self.analytics_key,      # UA-xxxxx
            'cid': cid,                     # Anonymous Client ID
            't': 'pageview',                # Hit type
            'dh': host,                     # Document hostname
            'dp': path,                     # Page
        }

        if request.user and request.user.is_authenticated():
            parameters['cid'] = request.user.pk

        self.send(parameters, headers)
