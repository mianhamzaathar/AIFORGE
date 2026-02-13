# Create content/services.py

import google.generativeai as genai
from django.conf import settings

class GeminiBlogGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_blog(self, topic, tone='professional', length='medium'):
        length_map = {
            'short': '300 words',
            'medium': '600 words',
            'long': '1000 words'
        }
        
        prompt = f"""
        Write a {tone} blog post about: {topic}
        
        Requirements:
        - Length: {length_map.get(length, '600 words')}
        - Include an engaging title
        - Write in markdown format
        - Include introduction, main points, and conclusion
        - Make it SEO friendly
        
        Blog Post:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating blog: {str(e)}"
    
    def improve_content(self, content):
        prompt = f"""
        Improve and rewrite this content to make it more engaging and professional:
        
        {content}
        
        Requirements:
        - Fix grammar and spelling
        - Improve readability
        - Add relevant keywords
        - Maintain the original message
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return content
