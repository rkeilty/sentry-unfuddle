from __future__ import absolute_import

import logging

from sentry.http import build_session
from sentry.utils import json
from sentry.utils.cache import cache
from simplejson.decoder import JSONDecodeError
from BeautifulSoup import BeautifulStoneSoup
from django.utils.datastructures import SortedDict
from dicttoxml import dicttoxml

log = logging.getLogger(__name__)

CACHE_KEY = "SENTRY-UNFUDDLE-%s-%s"


class UnfuddleClient(object):
    """
    The Unfuddle API Client, so you don't have to.
    """

    PROJECT_URL = '/api/v1/projects'
    CREATE_TICKET_URL = '/api/v1/projects/{id}/tickets'
    PROJECT_VERSIONS_URL = '/api/v1/projects/{id}/versions'
    PROJECT_USERS_URL = '/api/v1/projects/{id}/people'
    CURRENT_USER_URL = '/api/v1/people/current'
    ALL_USERS_URL = '/api/v1/people'
    USER_INVOLVEMENTS_URL = '/api/v1/people/{id}/involvements'
    PROJECT_MILESTONES_URL = '/api/v1/projects/{id}/milestones'
    UPCOMING_MILESTONES_URL = '/api/v1/milestones/upcoming'
    UPCOMING_PROJECT_MILESTONES_URL = '/api/v1/projects/{id}/milestones/upcoming'
    ALL_MILESTONES_URL = '/api/v1/milestones'
    HTTP_TIMEOUT = 5

    def __init__(self, instance_uri, username, password):
        self.instance_url = instance_uri.rstrip('/')
        self.username = username
        self.password = password

    def get_projects_list(self):
        return self.get_cached(self.PROJECT_URL)

    def get_versions(self, project_id):
        return self.get_cached(self.PROJECT_VERSIONS_URL.format(id=project_id))

    def get_current_user(self):
        return self.get_cached(self.CURRENT_USER_URL)

    def get_involvements_for_user(self, user):
        return self.get_cached(self.USER_INVOLVEMENTS_URL.format(id=user))

    def get_priorities(self):
        # Priorities are static.
        response = UnfuddleResponse('', {}, 200)
        response.json = [{'id': 1, 'name': 'Lowest'},
                         {'id': 2, 'name': 'Low'},
                         {'id': 3, 'name': 'Normal'},
                         {'id': 4, 'name': 'High'},
                         {'id': 5, 'name': 'Highest'}]
        return response

    def get_users_for_project(self, project_id):
        return self.get_cached(self.PROJECT_USERS_URL.format(id=project_id))

    def get_all_users(self):
        return self.get_cached(self.ALL_USERS_URL)

    def get_milestones_for_project(self, project_id):
        return self.get_cached(self.PROJECT_MILESTONES_URL.format(id=project_id))

    def get_upcoming_milestones(self):
        return self.get_cached(self.UPCOMING_MILESTONES_URL)

    def get_upcoming_milestones_for_project(self, project_id):
        return self.get_cached(self.UPCOMING_PROJECT_MILESTONES_URL.format(id=project_id))

    def get_all_milestones(self):
        return self.get_cached(self.ALL_MILESTONES_URL)

    def create_issue(self, raw_form_data):

        # To keep form standards, the forms are registered with _ instead of -, so replace those in the keys we send.
        # Also, Sentry expects a "title" field to exist, but we need to send that field as "summary" to Unfuddle.
        data = {'ticket': {key.replace('_', '-'): value for key, value in raw_form_data.iteritems()}}
        if 'title' in data['ticket']:
            data['ticket']['summary'] = data['ticket']['title']
            del data['ticket']['title']
        return self.make_request('post', self.CREATE_TICKET_URL.format(id=raw_form_data['project_id']), payload=data)

    def make_request(self, method, url, payload=None):
        if url[:4] != "http":
            url = self.instance_url + url
        auth = self.username, self.password
        session = build_session()
        try:
            session.headers['Accept'] = 'application/json'
            session.headers['Content-Type'] = 'application/xml'

            if method == 'get':
                r = session.get(
                    url, params=payload, auth=auth,
                    verify=False, timeout=self.HTTP_TIMEOUT)
            else:
                # Unfuddle requires XML payloads to get sent.
                xml_payload = dicttoxml(payload, root=False, attr_type=False)
                r = session.post(
                    url, data=xml_payload, auth=auth,
                    verify=False, timeout=self.HTTP_TIMEOUT)

            return UnfuddleResponse(r.text, r.headers, r.status_code)
        except Exception, e:
            logging.error('Error in request to %s: %s', url, e.message)
            return UnfuddleResponse("There was a problem reaching %s: %s" % (url, e.message), {}, 500)

    def get_cached(self, full_url):
        """
        Basic Caching mechanism for requests and responses. It only caches responses
        based on URL
        TODO: Implement GET attr in cache as well. (see self.create_meta for example)
        """
        key = CACHE_KEY % (full_url, self.instance_url)
        cached_result = cache.get(key)
        if not cached_result:
            cached_result = self.make_request('get', full_url)
            if cached_result.status_code == 200:
                cache.set(key, cached_result, 60)

        return cached_result


class UnfuddleResponse(object):
    """
    A Slimy little wrapper around a python-requests response object that renders
    JSON from Unfuddle's ordered dicts (fields come back in order, but python obv.
    doesn't care)
    """
    def __init__(self, response_text, headers, status_code):
        self.headers = headers
        self.text = response_text
        self.xml = None
        try:
            self.json = json.loads(response_text, object_pairs_hook=SortedDict)
        except (JSONDecodeError, ValueError):
            if self.text[:5] == "<?xml":
                # perhaps it's XML?
                self.xml = BeautifulStoneSoup(self.text)
            # must be an awful code.
            self.json = None
        self.status_code = status_code

    def __repr__(self):
        return "<UnfuddleResponse<%s>, %s, %s>" % (self.status_code, self.headers, self.text[:120])
