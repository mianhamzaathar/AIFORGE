from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def image_generator(request):
    return render(request, "image/generator.html")
