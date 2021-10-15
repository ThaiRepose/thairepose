"""Django utilitys"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self,user, timestamp: int):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.customer.is_email_verified))

generate_token = TokenGenerator()
