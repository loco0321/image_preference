from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.text import slugify, capfirst
from django.utils.translation import ugettext_lazy as _
from pyrebase import pyrebase

from image_preference.utilities import get_firebase


class AuthenticationFormCustom(forms.Form):
    first_name = forms.CharField(max_length=100, label=_('First name'))
    last_name = forms.CharField(max_length=100, label=_('Last name'))

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationFormCustom, self).__init__(*args, **kwargs)

    def clean(self):
        firebase = get_firebase()
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password('leon9894@gmail.com', 'Leonardo0321')
        self.request.session['firebase_user'] = user
        name = '{0} {1}'.format(self.cleaned_data.get('first_name').strip(),
                                self.cleaned_data.get('last_name').strip()).lower()
        username = slugify(name)
        password = slugify(name)
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'is_active': True,
                'first_name': self.cleaned_data.get('first_name').strip(),
                'last_name': self.cleaned_data.get('last_name').strip(),
            })
        user.set_password(password)
        user.save()
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.first_name.label},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
