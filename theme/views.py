from django.shortcuts import render


def about_us(request):
    """Render About us page."""
    return render(request, "about-us.html")


def feedback(request):
    """Render collect feedback page."""
    return render(request, "feedback.html")
