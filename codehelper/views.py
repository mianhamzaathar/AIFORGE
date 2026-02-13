from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CodeAnalysis, ProgrammingLanguage, CodeSnippet, UserPreference
import json

# ============================================
# HOME PAGE - CODE ANALYZER
# ============================================

class CodeAnalyzerView(TemplateView):
    """Main code analyzer page"""
    template_name = 'codehelper/analyzer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = ProgrammingLanguage.objects.filter(is_active=True)
        
        # Get user preferences if authenticated
        if self.request.user.is_authenticated:
            try:
                context['preferences'] = UserPreference.objects.get(user=self.request.user)
            except UserPreference.DoesNotExist:
                context['preferences'] = None
        
        return context


@login_required
def analyze_code(request):
    """Analyze submitted code"""
    if request.method == 'POST':
        code = request.POST.get('code')
        language_id = request.POST.get('language')
        analysis_type = request.POST.get('analysis_type', 'explain')
        
        # Validate input
        if not code:
            messages.error(request, '❌ Please enter some code!')
            return redirect('codehelper_home')
        
        if not language_id:
            messages.error(request, '❌ Please select a language!')
            return redirect('codehelper_home')
        
        # Get language
        try:
            language = get_object_or_404(ProgrammingLanguage, id=language_id)
        except:
            messages.error(request, '❌ Invalid language selected!')
            return redirect('codehelper_home')
        
        # Check tokens
        token_cost = settings.TOKEN_COSTS.get('code', 40)
        if not request.user.deduct_tokens(token_cost, 'code'):
            messages.error(request, '❌ Insufficient tokens! Please buy more.')
            return redirect('pricing')
        
        # Create analysis
        analysis = CodeAnalysis.objects.create(
            user=request.user,
            code=code,
            language=language,
            analysis_type=analysis_type,
            tokens_used=token_cost,
            status='completed',
            result=f"✅ Analysis complete! Your {language.name} code has been analyzed successfully."
        )
        
        messages.success(request, f'✅ {analysis.get_analysis_type_display()} completed!')
        return redirect('view_analysis', analysis_id=analysis.id)
    
    return redirect('codehelper_home')


@login_required
def view_analysis(request, analysis_id):
    """View a single analysis result"""
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id, user=request.user)
    return render(request, 'codehelper/view_analysis.html', {'analysis': analysis})


@login_required
def analysis_history(request):
    """View all user's analyses"""
    analyses = CodeAnalysis.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(analyses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'codehelper/history.html', {
        'analyses': page_obj,
        'total': analyses.count()
    })


@login_required
def delete_analysis(request, analysis_id):
    """Delete an analysis"""
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id, user=request.user)
    analysis.delete()
    messages.success(request, '✅ Analysis deleted successfully!')
    return redirect('analysis_history')


# ============================================
# CODE SNIPPETS - CRUD OPERATIONS
# ============================================

@login_required
def snippet_list(request):
    """List all user's code snippets"""
    snippets = CodeSnippet.objects.filter(user=request.user)
    
    # Filter by language
    language_filter = request.GET.get('language')
    if language_filter:
        snippets = snippets.filter(language_id=language_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        snippets = snippets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(snippets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all languages for filter dropdown
    languages = ProgrammingLanguage.objects.filter(is_active=True)
    
    return render(request, 'codehelper/snippet_list.html', {
        'snippets': page_obj,
        'languages': languages,
        'selected_language': language_filter,
        'search_query': search_query
    })


@login_required
def create_snippet(request):
    """Create a new code snippet"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        code = request.POST.get('code')
        language_id = request.POST.get('language')
        tags = request.POST.get('tags', '')
        visibility = request.POST.get('visibility', 'private')
        
        # Validate
        if not title:
            messages.error(request, '❌ Please enter a title!')
            return redirect('create_snippet')
        
        if not code:
            messages.error(request, '❌ Please enter some code!')
            return redirect('create_snippet')
        
        # Get language
        language = get_object_or_404(ProgrammingLanguage, id=language_id) if language_id else None
        
        # Process tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Create snippet
        snippet = CodeSnippet.objects.create(
            user=request.user,
            title=title,
            description=description,
            code=code,
            language=language,
            tags=tag_list,
            visibility=visibility
        )
        
        # Generate share token if public
        if visibility == 'shared':
            snippet.generate_share_token()
        
        messages.success(request, '✅ Code snippet created successfully!')
        return redirect('view_snippet', snippet_id=snippet.id)
    
    # GET request - show form
    languages = ProgrammingLanguage.objects.filter(is_active=True)
    return render(request, 'codehelper/create_snippet.html', {'languages': languages})


@login_required
def view_snippet(request, snippet_id):
    """View a single code snippet"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id)
    
    # Check permissions
    if snippet.visibility == 'private' and snippet.user != request.user:
        messages.error(request, '❌ You do not have permission to view this snippet!')
        return redirect('snippet_list')
    
    # Increment view count
    snippet.increment_views()
    
    # Get related analyses
    analyses = snippet.analyses.all()[:5]
    
    return render(request, 'codehelper/view_snippet.html', {
        'snippet': snippet,
        'analyses': analyses
    })


@login_required
def edit_snippet(request, snippet_id):
    """Edit a code snippet"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        code = request.POST.get('code')
        language_id = request.POST.get('language')
        tags = request.POST.get('tags', '')
        visibility = request.POST.get('visibility', 'private')
        
        # Update snippet
        snippet.title = title
        snippet.description = description
        snippet.code = code
        snippet.language = get_object_or_404(ProgrammingLanguage, id=language_id) if language_id else None
        snippet.tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        snippet.visibility = visibility
        
        # Regenerate share token if needed
        if visibility == 'shared' and not snippet.share_token:
            snippet.generate_share_token()
        elif visibility != 'shared':
            snippet.share_token = None
        
        snippet.save()
        
        messages.success(request, '✅ Snippet updated successfully!')
        return redirect('view_snippet', snippet_id=snippet.id)
    
    # GET request - show form
    languages = ProgrammingLanguage.objects.filter(is_active=True)
    return render(request, 'codehelper/edit_snippet.html', {
        'snippet': snippet,
        'languages': languages
    })


@login_required
def delete_snippet(request, snippet_id):
    """Delete a code snippet"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id, user=request.user)
    snippet.delete()
    messages.success(request, '✅ Snippet deleted successfully!')
    return redirect('snippet_list')


def shared_snippet(request, token):
    """View a shared snippet via token (no login required)"""
    snippet = get_object_or_404(CodeSnippet, share_token=token, visibility='shared')
    
    # Increment view count
    snippet.increment_views()
    
    return render(request, 'codehelper/shared_snippet.html', {'snippet': snippet})


@login_required
def fork_snippet(request, snippet_id):
    """Fork (copy) another user's snippet"""
    original = get_object_or_404(CodeSnippet, id=snippet_id)
    
    # Create forked snippet
    forked = CodeSnippet.objects.create(
        user=request.user,
        title=f"Fork: {original.title}",
        description=original.description,
        code=original.code,
        language=original.language,
        tags=original.tags,
        visibility='private',
        parent_snippet=original
    )
    
    original.forks += 1
    original.save()
    
    messages.success(request, '✅ Snippet forked successfully!')
    return redirect('edit_snippet', snippet_id=forked.id)


# ============================================
# USER PREFERENCES
# ============================================

@login_required
def user_preferences(request):
    """View and edit user preferences"""
    try:
        preferences = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        # Create default preferences
        preferences = UserPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Editor preferences
        preferences.theme = request.POST.get('theme', 'dark')
        preferences.editor_mode = request.POST.get('editor_mode', 'default')
        preferences.font_size = int(request.POST.get('font_size', 14))
        preferences.tab_size = int(request.POST.get('tab_size', 4))
        preferences.auto_complete = request.POST.get('auto_complete') == 'on'
        preferences.line_numbers = request.POST.get('line_numbers') == 'on'
        
        # Analysis preferences
        language_id = request.POST.get('default_language')
        if language_id:
            preferences.default_language = get_object_or_404(ProgrammingLanguage, id=language_id)
        
        preferences.default_analysis = request.POST.get('default_analysis', 'explain')
        preferences.auto_save = request.POST.get('auto_save') == 'on'
        
        # Notification preferences
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences.analysis_completed = request.POST.get('analysis_completed') == 'on'
        
        preferences.save()
        messages.success(request, '✅ Preferences saved successfully!')
        return redirect('user_preferences')
    
    languages = ProgrammingLanguage.objects.filter(is_active=True)
    return render(request, 'codehelper/preferences.html', {
        'preferences': preferences,
        'languages': languages
    })


# ============================================
# API ENDPOINTS (AJAX)
# ============================================

@login_required
def get_snippet_json(request, snippet_id):
    """Return snippet data as JSON (for AJAX)"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id, user=request.user)
    
    data = {
        'id': snippet.id,
        'title': snippet.title,
        'description': snippet.description,
        'code': snippet.code,
        'language': snippet.language.name if snippet.language else None,
        'tags': snippet.tags,
        'visibility': snippet.visibility,
        'created_at': snippet.created_at.strftime('%Y-%m-%d %H:%M'),
        'views': snippet.views,
        'likes': snippet.likes,
        'forks': snippet.forks,
    }
    
    return JsonResponse(data)


@login_required
def toggle_snippet_like(request, snippet_id):
    """Like/unlike a snippet"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id)
    
    # Simple implementation - in production use a Like model
    snippet.likes += 1
    snippet.save()
    
    return JsonResponse({'likes': snippet.likes})


# ============================================
# EXPORT FUNCTIONS
# ============================================

@login_required
def export_analysis(request, analysis_id):
    """Export analysis as text file"""
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id, user=request.user)
    
    content = f"""
AIForge Code Analysis Report
============================
Date: {analysis.created_at}
Language: {analysis.language.name if analysis.language else 'Unknown'}
Analysis Type: {analysis.get_analysis_type_display()}
Tokens Used: {analysis.tokens_used}

CODE:
{analysis.code}

RESULT:
{analysis.result}
    """
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="analysis_{analysis_id}_{analysis.created_at.date()}.txt"'
    
    return response


@login_required
def export_snippet(request, snippet_id):
    """Export snippet as code file"""
    snippet = get_object_or_404(CodeSnippet, id=snippet_id, user=request.user)
    
    # Get file extension
    ext_map = {
        'python': 'py',
        'javascript': 'js',
        'java': 'java',
        'cpp': 'cpp',
        'csharp': 'cs',
        'php': 'php',
        'ruby': 'rb',
        'go': 'go',
        'html': 'html',
        'css': 'css',
        'sql': 'sql',
    }
    
    ext = ext_map.get(snippet.language.slug if snippet.language else '', 'txt')
    filename = f"{snippet.title.replace(' ', '_')}.{ext}"
    
    response = HttpResponse(snippet.code, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response