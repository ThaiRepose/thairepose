from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField


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
    """

    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    duration = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    body = RichTextField(blank=True, null=True)
    category = models.CharField(max_length=255, default='Uncatagorize')
    post_date = models.DateField(auto_now_add=True)
    like = models.ManyToManyField(User, related_name='trip_like', blank=True)

    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def get_absolute_url(self):
        """Return redirect to all trip pages."""
        return reverse("trip:tripdetail", args=(str(self.id)))
    
    def total_like(self):
        """Return number of count."""
        return self.like.count()


class Review(models.Model):
    """Extended user model class that use for Review.

    Attributes:
        post(TripPlan): trip plan that host of review
        name(str): name of who write commend
        date_added(datetime): date and time when comment writed
        like(object): file to store user to like comment
    """

    post = models.ForeignKey(
        TripPlan, related_name="review", on_delete=models.CASCADE)
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
        return reverse("trip:tripdetail", args=(str(self.post.id)))


class CategoryPlan(models.Model):
    """Extended user model class that use for Category of Trip plan.

    Attributes:
        name(str): category of trip

    """

    name = models.CharField(max_length=255, default='Uncatagorize')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return redirect to all trip pages."""
        return reverse("trip:tripplan")
