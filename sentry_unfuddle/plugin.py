from django import forms
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from sentry.plugins.base import Response
from sentry.plugins.bases.issue import IssuePlugin
from sentry.utils import json
from sentry.utils.http import absolute_uri

from sentry_unfuddle import VERSION as PLUGINVERSION
from sentry_unfuddle.forms import UnfuddleOptionsForm, UnfuddleIssueForm
from sentry_unfuddle.unfuddle import UnfuddleClient


class UnfuddlePlugin(IssuePlugin):
    author = "Rick Keilty"
    author_url = "https://github.com/rkeilty/sentry-unfuddle"
    version = PLUGINVERSION

    slug = "unfuddle"
    title = _("Unfuddle")
    conf_title = title
    conf_key = slug
    project_conf_form = UnfuddleOptionsForm
    project_conf_template = "sentry_unfuddle/project_conf_form.html"
    new_issue_form = UnfuddleIssueForm
    create_issue_template = 'sentry_unfuddle/create_unfuddle_issue.html'

    # Adding resource links for forward compatibility, still need to integrate
    # into existing `project_conf.html` template.
    resource_links = [
        ("Documentation", "http://sentry-unfuddle.readthedocs.org/en/latest/"),
        ("README", "https://raw.github.com/rkeilty/sentry-unfuddle/master/README.rst"),
        ("Bug Tracker", "https://github.com/rkeilty/sentry-unfuddle/issues"),
        ("Source", "http://github.com/rkeilty/sentry-unfuddle"),
    ]

    def is_configured(self, request, project, **kwargs):
        if not self.get_option('default_project_id', project):
            return False
        return True

    def get_unfuddle_client(self, project):
        instance = self.get_option('instance_url', project)
        username = self.get_option('username', project)
        pw = self.get_option('password', project)
        return UnfuddleClient(instance, username, pw)

    def get_initial_form_data(self, request, group, event, **kwargs):
        initial = {
            'title': self._get_group_title(request, group, event),
            'description': self._get_group_description(request, group, event),
            'project_id': self.get_option('default_project_id', group.project),
            'current_user_email': request.user.email if request.user and request.user.email else None,
            'default_reporter_id': self.get_option('default_reporter_id', group.project),
            'unfuddle_client': self.get_unfuddle_client(group.project)
        }

        return initial

    def get_new_issue_title(self):
        return "Create Unfuddle Issue"

    def get_issue_label(self, group, issue_id, **kwargs):
        return issue_id

    def create_issue(self, request, group, form_data, **kwargs):
        """
        Form validation errors recognized server-side raise ValidationErrors,
        but when validation errors occur in Unfuddle they are simply attached to
        the form.
        """
        unfuddle_client = self.get_unfuddle_client(group.project)
        issue_response = unfuddle_client.create_issue(form_data)

        if issue_response.status_code == 200:
            return issue_response.json.get("id"), None
        elif issue_response.status_code == 201:
            issue_url = issue_response.headers.get("location")
            issue_id = issue_url[issue_url.rfind('/') + 1:]
            return issue_id
        else:
            # return some sort of error.
            if issue_response.status_code == 500:
                raise forms.ValidationError(_('Unfuddle Internal Server Error.'))
            elif issue_response.status_code == 400:
                raise forms.ValidationError(_('\n'.join(issue_response.json)))
            else:
                raise forms.ValidationError(_('Something went wrong, Sounds like a configuration issue: code {0}'
                                              .format(issue_response.status_code)))

    def get_issue_url(self, group, issue_id, **kwargs):
        instance_url = self.get_option('instance_url', group.project)
        project_id = self.get_option('default_project_id', group.project)
        return '{0}/a#/projects/{1}/tickets/{2}'.format(instance_url, project_id, issue_id)

    def get_issue_label(self, group, issue_id, **kwargs):
        return 'Unfuddle #{0}'.format(issue_id)

    def _get_group_description(self, request, group, event):
        # XXX: Mostly yanked from bases/issue:IssueTrackingPlugin,
        # except change ``` code formatting to {code}
        output = [
            absolute_uri(group.get_absolute_url()),
        ]
        body = self._get_group_body(request, group, event)
        if body:
            output.extend(['', '    {0}'.format(body.replace('\n', '\n    '))])
        return '\n'.join(output)


class JSONResponse(Response):
    def __init__(self, context):
        self.context = context

    def respond(self, request, context=None):
        return HttpResponse(json.dumps(self.context), content_type='application/json')
