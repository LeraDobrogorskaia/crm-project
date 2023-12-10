from django.contrib.auth.forms import \
    AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import gettext_lazy as _


class AuthenticationForm(BaseAuthenticationForm):
    error_messages = {
        **BaseAuthenticationForm.error_messages,
        "invalid_login": _(
            "Please enter a correct username and password. Note that both "
            "fields may be case-sensitive."
        ),
    }
