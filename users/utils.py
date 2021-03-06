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
        result = os.path.join(os.path.join('media', 'user', 'profile_picture'),
                              "blank-profile-picture.png")
        user.profile.profile_pic.save(
            filename,
            File(open(os.path.abspath(result), 'rb'))
        )

    user.profile.save()


def pic_profile_relative_path():
    """Change from absolute path to relative path.

    Returns:
        str: relative path of profile pic
    """
    return os.path.join('user', 'profile_picture')


def pic_profile_rename_path(pk):
    """Method for get path of profile of each user.

    Args:
        pk(int): user id.

    Returns:
        path(str): path.
    """
    new_path = os.path.join(settings.PROFILE_PIC_LOCATION,
                            f'{str(pk)}_profile_picture.jpg')
    return new_path


def pic_profile_path(path):
    """Method for get path of image that user upload.

    Args:
        pk(int): user id.

    Returns:
        path(str): path.
    """
    new_path = os.path.join(settings.PROFILE_PIC_LOCATION, str(path))
    new_path = new_path.replace('\\', '/')
    return new_path


def get_pic_profile_relate_path(pk, filename):
    """Method for get path of Profile picture image.

    Args:
        pk(int): user id.
        filename(str): filename of picture.

    Returns:
        path(str): path.
    """
    return os.path.join('user', 'profile_picture', f'{str(pk)}_{filename}')


def get_upload_pic_path(filename):
    """Method for get path of Profile picture image.

    Args:
        filename(str): profile pic relative path.

    Returns:
        path(str): path.
    """
    get_path = os.path.join(settings.MEDIA_ROOT, filename)
    return get_path


def get_rename_file_path(pk, filename):
    """Method for get path of Profile picture image.

    Args:
        pk(int): user id.
        filename(str): filename of picture.

    Returns:
        path(str): path.
    """
    return os.path.join(settings.PROFILE_PIC_LOCATION, f'{str(pk)}_{filename}')
