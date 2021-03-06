import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.deconstruct import deconstructible
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey


class CategoryPlan(models.Model):
    """Class for store Category of Trip plan.

    Attributes:
        name(str): category of trip

    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@deconstructible
class UploadToPathAndRename(object):
    """Class for rename image file."""

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        # get filename
        filename = '{}/{}'.format(instance.post.pk, filename)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)


class TripPlan(models.Model):
    """Extended user model class that use for Trip plan.

    Attributes:
        title(str): title of post
        author(user): user who write post
        duration(int): all day in trip
        print(int): money to cover all trip
        body(str): descriptions
        category(str): category of trip
        post_date(datetime): datetime of trip is created
        like(User): store all use press like button
        complete(bool): bool to check blog is complete or not
    """

    title = models.CharField(max_length=200, null=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    body = RichTextUploadingField(null=True, blank=True)
    category = models.ForeignKey(
        CategoryPlan, on_delete=models.PROTECT, blank=True, null=True)
    post_date = models.DateField(auto_now_add=True)
    like = models.ManyToManyField(User, related_name='trip_like', blank=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} {self.author}'

    def get_absolute_url(self):
        """Return redirect to all trip pages."""
        return reverse("trip:tripdetail", args=((str(self.id),)))

    @property
    def total_like(self):
        """Return number of count."""
        return self.like.count()

    @property
    def get_short_description(self):
        """Return short description of post with out image"""
        description = ""
        if self.body is not None:
            body_split = self.body.split("<p>")
            for body in body_split:
                if not body.startswith("<img"):
                    description += body
        return description

    @property
    def image(self):
        """Return image of this post"""
        return UploadImage.objects.filter(post=self)


class Review(MPTTModel):
    """Extended user model class that use for Review.

    Attributes:
        post(TripPlan): trip plan that host of review
        name(str): name of who write commend
        date_added(datetime): date and time when comment writed
        like(object): file to store user to like comment
    """

    post = models.ForeignKey(
        TripPlan, related_name="review", on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, related_name='commended', blank=True)

    @property
    def total_like(self):
        """Return number of count."""
        return self.like.count()

    def __str__(self):
        return '%s - %s' % (self.post.title, self.name.username)

    def get_absolute_url(self):
        """Return redirect to detail of each commend.

        When your like comment page will refesh itseft to show all like.
        """
        return reverse("trip:tripdetail", args=((str(self.post.id),)))


class UploadImage(models.Model):
    """Extend TripPlan class to store image in blog.txt

    Attributes:
        post(TripPlan): trip plan that host of review
        image(file): image of user who uploaded
    """
    post = models.ForeignKey(TripPlan, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=UploadToPathAndRename('pic'))


class PlaceDetail(models.Model):
    """Model contains place details collected by user.

    Attributes:
        place_id: ID reference to Google Place.
    """
    name = models.TextField(default=None)
    place_id = models.TextField(null=False, blank=False)

    def __str__(self):
        """Display name for this object."""
        return self.name


class PlaceReview(models.Model):
    """Model about review information for a place."""

    place = models.ForeignKey(PlaceDetail, on_delete=models.CASCADE)
    review_text = models.TextField(null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def likes(self):
        """Get amount of likes for this review."""
        return PlaceReviewLike.objects.filter(review=self, like=True).count()

    @property
    def dislikes(self):
        """Get amount of dislikes for this review."""
        return PlaceReviewLike.objects.filter(review=self, like=False).count()


class PlaceReviewLike(models.Model):
    """Model for managing like/dislike for a place review."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(PlaceReview, on_delete=models.CASCADE)
    like = models.BooleanField(default=True)
