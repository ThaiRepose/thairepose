from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class TokenGenerator(PasswordResetTokenGenerator):
    """This class contain function for generate token."""

    def _make_hash_value(self, user, timestamp: int):
        """Make hash value from user information and timestano.

        Args:
            user (Profile): user profile
            timestamp (int): timestamp

        Returns:
            str: unicode of string
        """
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.profile.is_email_verified))


generate_token = TokenGenerator()
