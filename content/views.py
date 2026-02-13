from django.shortcuts import render

# Create your views here.
# Create content/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import BlogPost
from .services import GeminiBlogGenerator

@login_required
def blog_writer(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        tone = request.POST.get('tone', 'professional')
        length = request.POST.get('length', 'medium')
        
        token_cost = settings.TOKEN_COSTS['blog']
        if not request.user.deduct_tokens(token_cost, 'blog'):
            messages.error(request, '❌ Insufficient tokens! Please buy more.')
            return redirect('pricing')
        
        generator = GeminiBlogGenerator()
        content = generator.generate_blog(topic, tone, length)
        
        lines = content.strip().split('\n')
        title = lines[0].replace('#', '').strip() if lines else topic
        
        blog = BlogPost.objects.create(
            user=request.user,
            title=title,
            prompt=topic,
            content=content,
            tokens_used=token_cost
        )
        
        messages.success(request, '✅ Blog generated successfully!')
        return redirect('view_blog', blog_id=blog.id)
    
    return render(request, 'content/blog_writer.html')

@login_required
def view_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id, user=request.user)
    return render(request, 'content/view_blog.html', {'blog': blog})

@login_required
def my_blogs(request):
    blogs = BlogPost.objects.filter(user=request.user)
    return render(request, 'content/my_blogs.html', {'blogs': blogs})

@login_required
def improve_blog(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id, user=request.user)
    
    if request.method == 'POST':
        token_cost = settings.TOKEN_COSTS['blog'] // 2
        if not request.user.deduct_tokens(token_cost, 'blog'):
            messages.error(request, '❌ Insufficient tokens!')
            return redirect('pricing')
        
        generator = GeminiBlogGenerator()
        improved_content = generator.improve_content(blog.content)
        blog.content = improved_content
        blog.save()
        
        messages.success(request, '✅ Blog improved successfully!')
    
    return redirect('view_blog', blog_id=blog.id)
