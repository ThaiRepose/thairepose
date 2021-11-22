from django.shortcuts import render


def about_us(request):
    """Render About us page."""
    return render(request, "about-us.html")
