from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import urllib.request
from django.core.files import File

def upload_profile_pic(user, image_url, location, filename):
    try:
        urllib.request.urlretrieve(image_url, location+filename)
    except:
        print("Url not found")
    user.profile.profile_pic.save(
            filename,
            File(open(location+filename, 'rb'))
            )


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