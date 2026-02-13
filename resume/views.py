from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def resume_optimizer(request):
    return render(request, "resume/optimizer.html")
