import logging
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from .unfuddle import UnfuddleClient

log = logging.getLogger(__name__)


class UnfuddleOptionsForm(forms.Form):
    instance_url = forms.CharField(
        label=_("Unfuddle Instance URL"),
        widget=forms.TextInput(attrs={'class': 'span6', 'placeholder': 'e.g. "https://yourorg.unfuddle.com"'}),
        help_text=_("It must be visible to the Sentry server"),
        required=True
    )
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'span6'}),
        help_text=_("Ensure the Unfuddle user has admin perm. on the project"),
        required=True
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'span6'}),
        help_text=_("Only enter a value if you wish to change it"),
        required=False
    )
    default_project_id = forms.ChoiceField(
        label=_("Linked Project"),
        required=True
    )
    default_reporter_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(UnfuddleOptionsForm, self).__init__(*args, **kwargs)

        initial = kwargs.get("initial")
        project_safe = False
        if initial and initial.get("instance_url"):

            # Make a connection to Unfuddle to fetch a default project.
            unfuddle = UnfuddleClient(initial["instance_url"], initial.get("username"), initial.get("password"))
            projects_response = unfuddle.get_projects_list()
            if projects_response.status_code == 200:
                projects = projects_response.json
                if projects:
                    project_choices = [(p.get('id'), "%s (%s)" % (p.get('title'), p.get('id'))) for p in projects]
                    project_safe = True
                    self.fields["default_project_id"].choices = project_choices

            current_unfuddle_user = unfuddle.get_current_user().json
            self.fields["default_reporter_id"].initial = current_unfuddle_user["id"]

        if not project_safe:
            del self.fields["default_project_id"]
            del self.fields["default_reporter_id"]

    def clean_password(self):
        """
        Don't complain if the field is empty and a password is already stored,
        no one wants to type a pw in each time they want to change it.
        """
        pw = self.cleaned_data.get("password")
        if pw:
            return pw
        else:
            old_pw = self.initial.get("password")
            if not old_pw:
                raise ValidationError("A Password is Required")
            return old_pw

    def clean_instance_url(self):
        """
        Strip forward slashes off any url passed through the form.
        """
        url = self.cleaned_data.get("instance_url")
        if url and url[-1:] == "/":
            return url[:-1]
        else:
            return url

    def clean(self):
        """
        try and build a UnfuddleClient and make a random call to make sure the
        configuration is right.
        """
        cd = self.cleaned_data

        missing_fields = False
        if not cd.get("instance_url"):
            self.errors["instance_url"] = ["Instance URL is required"]
            missing_fields = True
        if not cd.get("username"):
            self.errors["username"] = ["Username is required"]
            missing_fields = True
        if missing_fields:
            raise ValidationError("Missing Fields")

        unfuddle = UnfuddleClient(cd["instance_url"], cd["username"], cd["password"])
        sut_response = unfuddle.get_current_user()
        if sut_response.status_code == 403 or sut_response.status_code == 401:
            self.errors["username"] = ["Username might be incorrect"]
            self.errors["password"] = ["Password might be incorrect"]
            raise ValidationError("Unable to connect to Unfuddle: %s, if you have "
                                  "tried and failed multiple times you may have"
                                  " to enter a CAPTCHA in Unfuddle to re-enable API"
                                  " logins." % sut_response.status_code)
        elif sut_response.status_code == 500 or sut_response.json is None:
            raise ValidationError("Unable to connect to Unfuddle: Bad Response")
        elif sut_response.status_code > 200:
            raise ValidationError("Unable to connect to Unfuddle: %s" % sut_response.status_code)

        return cd


class UnfuddleIssueForm(forms.Form):

    project_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    reporter_id = forms.CharField(widget=forms.HiddenInput(), required=True)

    assignee_id = forms.ChoiceField(
        label=_("Assignee"),
        required=True
    )
    milestone_id = forms.ChoiceField(
        label=_("Milestone"),
        required=True
    )
    priority = forms.ChoiceField(
        label=_("Priority"),
        required=True
    )
    title = forms.CharField(
        label=_("Issue Summary"),
        widget=forms.TextInput(attrs={'class': 'span6'}),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": 'span6'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial")
        unfuddle_client = initial.pop("unfuddle_client")

        project_id = initial.get('project_id')
        priorities = unfuddle_client.get_priorities().json
        users = unfuddle_client.get_users_for_project(project_id).json
        milestones = unfuddle_client.get_upcoming_milestones_for_project(project_id).json

        # Early exit, no projects available.
        if len(milestones) is 0:
            super(UnfuddleIssueForm, self).__init__(*args, **kwargs)
            self.errors["__all__"] = [
                "Error in Unfuddle configuration, no milestones found for user %s." %
                  unfuddle_client.username]
            return

        # set back after we've played with the inital data
        kwargs["initial"] = initial

        # call the super to bind self.fields from the defaults.
        super(UnfuddleIssueForm, self).__init__(*args, **kwargs)

        # Set the choices for the dynamic fields
        self.fields["project_id"].initial = project_id
        self.fields['assignee_id'].choices = self.make_choices(
            [{'id': u['id'], 'name': '{0} {1}'.format(u['first_name'], u['last_name'])} for u in users])
        self.fields['milestone_id'].choices = self.make_choices(
            [{'id': m['id'], 'name': m['title']} for m in milestones])
        self.fields['priority'].choices = self.make_choices(priorities)
        self.fields['priority'].initial = 4

        # See if there is an email for the current user
        current_user_email = initial.get('current_user_email')

        reporter_id = initial.get('default_reporter_id')
        for u in users:
            if u['email'] == current_user_email:
                reporter_id = u['id']
                self.fields['assignee_id'].initial = u['id']

        self.fields['reporter_id'].initial = reporter_id

    make_choices = lambda self, x: [(y["id"], y["name"] if "name" in y else y["value"]) for y in x] if x else []
