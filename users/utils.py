import urllib.request
import os
from django.conf import settings
from django.core.files import File

def upload_profile_pic(user, image_url, location, filename, testing=False):
    """Upload profile picture to Profile model

    Args:
        user (User): User model
        image_url (str): link of image
        location (str): path for store picture
        filename (str): file name of picture
    """
    try:
        result = urllib.request.urlretrieve('image_url')
        user.profile.profile_pic.save(
            filename,
            File(open(result[0], 'rb'))
        )
    except:
        result = os.path.join(settings.PROFILE_PIC_LOCATION,"blank-profile-picture.png")
        user.profile.profile_pic.save(
            filename,
            File(open(result, 'rb'))
        )

    
    user.profile.save()
