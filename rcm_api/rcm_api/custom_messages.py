from djoser.constants import Messages
from django.utils.translation import gettext_lazy as _


class CustomChangePasswordMessages(Messages):
    password_changed = _("Your password was successfully changed!")
