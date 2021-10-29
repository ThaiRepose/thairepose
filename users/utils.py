import urllib.request
from django.core.files import File

def upload_profile_pic(user, image_url, location, filename):
    """Upload profile picture to Profile model

    Args:
        user (User): User model
        image_url (str): link of image
        location (str): path for store picture
        filename (str): file name of picture
    """
    try:
        urllib.request.urlretrieve(image_url, location+filename)
    except:
        print("Url not found")
    user.profile.profile_pic.save(
            filename,
            File(open(location+filename, 'rb'))
            )
