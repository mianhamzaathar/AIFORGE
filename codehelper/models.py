from django.db import models
from django.conf import settings
from django.utils import timezone

class ProgrammingLanguage(models.Model):
    """Programming languages supported by CodeHelper"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class CodeAnalysis(models.Model):
    """Main model for code analysis requests"""
    
    ANALYSIS_TYPES = [
        ('explain', '📖 Explain Code'),
        ('debug', '🐛 Debug Code'),
        ('optimize', '⚡ Optimize Code'),
        ('document', '📝 Add Documentation'),
        ('convert', '🔄 Convert Language'),
        ('review', '🔍 Code Review'),
        ('security', '🛡️ Security Check'),
        ('complexity', '📊 Complexity Analysis'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '⏳ Pending'),
        ('processing', '🔄 Processing'),
        ('completed', '✅ Completed'),
        ('failed', '❌ Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='code_analyses'
    )
    
    title = models.CharField(max_length=200, blank=True)
    code = models.TextField()
    language = models.ForeignKey(
        ProgrammingLanguage, 
        on_delete=models.SET_NULL,
        null=True
    )
    analysis_type = models.CharField(
        max_length=20, 
        choices=ANALYSIS_TYPES,
        default='explain'
    )
    
    target_language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversion_targets'
    )
    
    result = models.TextField(blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    errors = models.JSONField(default=list, blank=True)
    complexity_score = models.FloatField(null=True, blank=True)
    security_score = models.FloatField(null=True, blank=True)
    
    tokens_used = models.IntegerField(default=40)
    execution_time = models.FloatField(null=True, blank=True, help_text="Time in seconds")
    lines_of_code = models.IntegerField(default=0)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['analysis_type']),
        ]
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        if self.code:
            self.lines_of_code = len(self.code.splitlines())
        if not self.title and self.code:
            preview = self.code[:50].strip()
            self.title = f"{self.get_analysis_type_display()} - {self.language} ({preview}...)"
        super().save(*args, **kwargs)
    
    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        self.status = 'failed'
        if not self.errors:
            self.errors = []
        self.errors.append({'error': error_message, 'time': str(timezone.now())})
        self.save()

class CodeSnippet(models.Model):
    """Saved code snippets for future reference"""
    
    VISIBILITY_CHOICES = [
        ('private', '🔒 Private'),
        ('public', '🌍 Public'),
        ('shared', '🔗 Shared'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='code_snippets'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    code = models.TextField()
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.SET_NULL, null=True)
    tags = models.JSONField(default=list, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='private'
    )
    share_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # Stats
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    # ✅ FIX 1: Rename 'forks' field to 'fork_count' to avoid clash
    fork_count = models.IntegerField(default=0)
    
    # ✅ FIX 2: Add related_name to avoid reverse accessor clash
    parent_snippet = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_snippets'  # Changed from 'forks' to 'child_snippets'
    )
    
    analyses = models.ManyToManyField(CodeAnalysis, blank=True, related_name='snippets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.views += 1
        self.save()
    
    def generate_share_token(self):
        import uuid
        self.share_token = uuid.uuid4().hex
        self.visibility = 'shared'
        self.save()
        return self.share_token

class CodeReview(models.Model):
    """Code review comments and feedback"""
    
    analysis = models.ForeignKey(
        CodeAnalysis,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='code_reviews'
    )
    line_number = models.IntegerField(null=True, blank=True)
    comment = models.TextField()
    suggestion = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['line_number', 'created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer} - Line {self.line_number}"

class UserPreference(models.Model):
    """User preferences for CodeHelper"""
    
    THEME_CHOICES = [
        ('light', '☀️ Light'),
        ('dark', '🌙 Dark'),
        ('system', '💻 System'),
    ]
    
    EDITOR_CHOICES = [
        ('default', 'Default'),
        ('vim', 'Vim'),
        ('emacs', 'Emacs'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codehelper_preferences'
    )
    
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    editor_mode = models.CharField(max_length=20, choices=EDITOR_CHOICES, default='default')
    font_size = models.IntegerField(default=14)
    tab_size = models.IntegerField(default=4)
    auto_complete = models.BooleanField(default=True)
    line_numbers = models.BooleanField(default=True)
    
    default_language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    default_analysis = models.CharField(
        max_length=20,
        choices=CodeAnalysis.ANALYSIS_TYPES,
        default='explain'
    )
    auto_save = models.BooleanField(default=True)
    
    email_notifications = models.BooleanField(default=True)
    analysis_completed = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

class APIKey(models.Model):
    """API keys for programmatic access"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codehelper_api_keys'
    )
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    requests_count = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def generate_key(self):
        import secrets
        self.key = secrets.token_urlsafe(32)
        self.save()
        return self.key
    
    def increment_usage(self, tokens=0):
        self.requests_count += 1
        self.tokens_used += tokens
        self.last_used = timezone.now()
        self.save()