from typing import List, Any, Dict, Optional
from .base import BaseAgent
from datetime import datetime

class ContentManagementAgent(BaseAgent):
    """Agent responsible for handling content-related inquiries and tasks."""
    
    def __init__(self):
        super().__init__(
            name="Content Management Specialist",
            description="a specialist responsible for assisting with content creation, \
            editing, optimization, and management for ChromaPages websites."
        )
        self.content_types = {
            'landing_page': 'Main landing and sales pages',
            'blog_post': 'Blog articles and posts',
            'product_page': 'Product description pages',
            'about_page': 'About us and team pages',
            'seo_content': 'SEO-optimized content',
            'social_media': 'Social media content'
        }
    
    def _get_context_prompt(self) -> str:
        """Get the specialized context prompt for the content management agent."""
        base_prompt = super()._get_context_prompt()
        return f"""{base_prompt}

        Your primary responsibilities are:
        1. Help users create and optimize web content
        2. Provide content structure recommendations
        3. Assist with SEO optimization
        4. Guide content editing and improvements
        5. Help with content organization
        
        When handling content requests:
        - Understand the target audience and purpose
        - Consider SEO best practices
        - Maintain brand voice and style
        - Ensure content is engaging and valuable
        
        Content types you work with:
        {self._format_content_types()}
        
        For content optimization:
        - Focus on readability and engagement
        - Incorporate relevant keywords naturally
        - Ensure proper content structure
        - Optimize for search engines while maintaining quality"""
    
    def _format_content_types(self) -> str:
        """Format the content types for the prompt."""
        return "\n".join([f"- {key}: {value}" for key, value in self.content_types.items()])
    
    async def _generate_response(self, message: str) -> str:
        """Generate a response using the Content Management Agent's specialized logic.
        
        Args:
            message (str): The message to process
            
        Returns:
            str: The generated response
        """
        return await super()._generate_response(message)
    
    def analyze_content_type(self, content: str) -> str:
        """Analyze and categorize the type of content based on its characteristics.
        
        Args:
            content (str): The content to analyze
            
        Returns:
            str: The identified content type
        """
        content_lower = content.lower()
        
        # Simple keyword-based categorization
        if any(word in content_lower for word in ['buy', 'pricing', 'features', 'hero section']):
            return 'landing_page'
        elif any(word in content_lower for word in ['article', 'post', 'blog']):
            return 'blog_post'
        elif any(word in content_lower for word in ['product', 'specification', 'details']):
            return 'product_page'
        elif any(word in content_lower for word in ['about', 'team', 'mission', 'vision']):
            return 'about_page'
        elif any(word in content_lower for word in ['seo', 'keyword', 'meta']):
            return 'seo_content'
        else:
            return 'social_media'
    
    def suggest_content_improvements(self, content: str) -> Dict[str, Any]:
        """Analyze content and suggest improvements.
        
        Args:
            content (str): The content to analyze
            
        Returns:
            Dict[str, Any]: Dictionary containing improvement suggestions
        """
        suggestions = {
            'structure': [],
            'seo': [],
            'readability': [],
            'engagement': []
        }
        
        # Check content structure
        if len(content.split('\n\n')) < 3:
            suggestions['structure'].append('Add more paragraph breaks for better readability')
        if not any(char in content for char in [':', '-', '•']):
            suggestions['structure'].append('Consider using bullet points or lists')
            
        # Check SEO elements
        if len(content.split()) < 300:
            suggestions['seo'].append('Content might be too short for good SEO')
        if content.count('.') < 5:
            suggestions['readability'].append('Add more sentences for better flow')
            
        # Check engagement elements
        if '?' not in content:
            suggestions['engagement'].append('Consider adding questions to engage readers')
        if not any(word in content.lower() for word in ['you', 'your']):
            suggestions['engagement'].append('Add more direct reader address')
            
        return suggestions
    
    def get_seo_recommendations(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Get SEO recommendations for the content.
        
        Args:
            content (str): The content to analyze
            target_keyword (str): The target keyword to optimize for
            
        Returns:
            Dict[str, Any]: Dictionary containing SEO recommendations
        """
        content_lower = content.lower()
        word_count = len(content.split())
        keyword_count = content_lower.count(target_keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        return {
            'word_count': word_count,
            'keyword_count': keyword_count,
            'keyword_density': round(keyword_density, 2),
            'recommendations': {
                'density': 'Good' if 0.5 <= keyword_density <= 2.5 else 'Needs adjustment',
                'suggestions': [
                    'Add keyword to title if not present',
                    'Include keyword in first paragraph',
                    'Use keyword variations',
                    'Add relevant meta description',
                    'Optimize header tags'
                ]
            }
        } 