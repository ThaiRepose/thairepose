import urllib.request
import os
from django.conf import settings
from django.core.files import File


def upload_profile_pic(user, image_url, filename, testing=False):
    """Upload profile picture to Profile model.

    Args:
        user (User): User model
        image_url (str): link of image
        location (str): path for store picture
        filename (str): file name of picture
    """
    try:
        if not testing:
            result = urllib.request.urlretrieve(image_url)
        else:
            result = None
        user.profile.profile_pic.save(
            filename,
            File(open(result[0], 'rb'))
        )
    except:
        result = os.path.join(settings.PROFILE_PIC_LOCATION,
                              "blank-profile-picture.png")
        user.profile.profile_pic.save(
            filename,
            File(open(result, 'rb'))
        )

    user.profile.save()


def pic_profile_relative_path():
    """Change from absolute path to relative path.

    Returns:
        str: relative path of profile pic
    """
    path = settings.PROFILE_PIC_LOCATION.replace('\\', '/')
    if path[0] == '/':
        return path[1:]
    return path
