from django.contrib import admin
from .models import (
    ProgrammingLanguage, CodeAnalysis, CodeSnippet, 
    CodeReview, UserPreference, APIKey
)

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}

@admin.register(CodeAnalysis)
class CodeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'language', 'analysis_type', 'status', 'tokens_used', 'created_at']
    list_filter = ['analysis_type', 'status', 'language', 'created_at']
    search_fields = ['user__username', 'title', 'code']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Code Information', {
            'fields': ('title', 'code', 'language', 'analysis_type', 'target_language')
        }),
        ('Results', {
            'fields': ('result', 'suggestions', 'errors', 'complexity_score', 'security_score')
        }),
        ('Metrics', {
            'fields': ('tokens_used', 'execution_time', 'lines_of_code', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )

@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'language', 'visibility', 'views', 'likes', 'fork_count', 'created_at']
    list_filter = ['language', 'visibility', 'created_at']
    search_fields = ['title', 'description', 'code', 'user__username']
    readonly_fields = ['views', 'likes', 'fork_count', 'share_token', 'created_at', 'updated_at']  # ✅ FIXED: 'forks' hataya, 'fork_count' add kiya
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'code', 'language')
        }),
        ('Metadata', {
            'fields': ('tags', 'visibility', 'share_token')
        }),
        ('Statistics', {
            'fields': ('views', 'likes', 'fork_count')
        }),
        ('Relationships', {
            'fields': ('parent_snippet', 'analyses')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'editor_mode', 'default_language', 'updated_at']
    list_filter = ['theme', 'editor_mode', 'auto_save']
    search_fields = ['user__username']

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'last_used', 'requests_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'requests_count', 'tokens_used', 'last_used']