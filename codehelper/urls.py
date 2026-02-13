from django.urls import path
from . import views

urlpatterns = [
    # Home / Analyzer
    path('', views.CodeAnalyzerView.as_view(), name='codehelper_home'),
    
    # Analysis
    path('analyze/', views.analyze_code, name='analyze_code'),
    path('history/', views.analysis_history, name='analysis_history'),  # ✅ YEH URL ADD KARO
    path('view/<int:analysis_id>/', views.view_analysis, name='view_analysis'),
    path('delete/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    
    # Snippets
    path('snippets/', views.snippet_list, name='snippet_list'),
    path('snippets/create/', views.create_snippet, name='create_snippet'),
    path('snippets/<int:snippet_id>/', views.view_snippet, name='view_snippet'),
    path('snippets/<int:snippet_id>/edit/', views.edit_snippet, name='edit_snippet'),
    path('snippets/<int:snippet_id>/delete/', views.delete_snippet, name='delete_snippet'),
    path('snippets/<int:snippet_id>/fork/', views.fork_snippet, name='fork_snippet'),
    
    # Shared
    path('shared/<str:token>/', views.shared_snippet, name='shared_snippet'),
    
    # API
    path('api/snippet/<int:snippet_id>/json/', views.get_snippet_json, name='get_snippet_json'),
    path('api/snippet/<int:snippet_id>/like/', views.toggle_snippet_like, name='toggle_snippet_like'),
    
    # Export
    path('export/analysis/<int:analysis_id>/', views.export_analysis, name='export_analysis'),
    path('export/snippet/<int:snippet_id>/', views.export_snippet, name='export_snippet'),
]