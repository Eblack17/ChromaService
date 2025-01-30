from typing import List, Any, Dict, Optional
from .base import BaseAgent

class ProductInformationAgent(BaseAgent):
    """Agent responsible for handling product-related inquiries and information."""
    
    def __init__(self):
        super().__init__(
            name="Product Information Specialist",
            description="a specialist responsible for providing detailed information about ChromaPages \
            features, plans, capabilities, and helping users choose the right solutions."
        )
        self.product_categories = {
            'website_builder': 'Core website building features',
            'templates': 'Website templates and themes',
            'ecommerce': 'E-commerce features and capabilities',
            'hosting': 'Hosting and domain services',
            'integrations': 'Third-party integrations and plugins',
            'analytics': 'Website analytics and reporting'
        }
    
    def _get_context_prompt(self) -> str:
        """Get the specialized context prompt for the product information agent."""
        base_prompt = super()._get_context_prompt()
        return f"""{base_prompt}

        Your primary responsibilities are:
        1. Explain ChromaPages features and capabilities
        2. Help users understand our different plans
        3. Provide template recommendations
        4. Explain technical requirements
        5. Compare features with alternatives
        
        When providing product information:
        - Focus on ChromaPages' unique benefits
        - Explain features in user-friendly terms
        - Provide specific examples and use cases
        - Recommend appropriate solutions
        
        Product categories you specialize in:
        {self._format_categories()}
        
        For recommendations:
        - Understand the user's specific needs
        - Consider technical expertise level
        - Explain the reasoning behind suggestions
        - Highlight relevant features"""
    
    def _format_categories(self) -> str:
        """Format the product categories for the prompt."""
        return "\n".join([f"- {key}: {value}" for key, value in self.product_categories.items()])
    
    async def _generate_response(self, message: str) -> str:
        """Generate a response using the Product Information Agent's specialized logic.
        
        Args:
            message (str): The message to process
            
        Returns:
            str: The generated response
        """
        return await super()._generate_response(message)
    
    def categorize_product_query(self, message: str) -> str:
        """Categorize the type of product query based on the user's message.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: The category of the product query
        """
        message_lower = message.lower()
        
        # Simple keyword-based categorization
        if any(word in message_lower for word in ['builder', 'create', 'design', 'edit']):
            return 'website_builder'
        elif any(word in message_lower for word in ['template', 'theme', 'layout']):
            return 'templates'
        elif any(word in message_lower for word in ['shop', 'store', 'ecommerce', 'payment']):
            return 'ecommerce'
        elif any(word in message_lower for word in ['host', 'domain', 'ssl']):
            return 'hosting'
        elif any(word in message_lower for word in ['integrate', 'plugin', 'connect']):
            return 'integrations'
        else:
            return 'analytics'
    
    def get_feature_details(self, feature: str) -> Dict[str, Any]:
        """Get detailed information about a specific feature.
        
        Args:
            feature (str): The feature to get details for
            
        Returns:
            Dict[str, Any]: Dictionary containing feature details
        """
        features = {
            'website_builder': {
                'name': 'Drag-and-Drop Website Builder',
                'description': 'Intuitive visual website builder with real-time preview',
                'key_features': [
                    'Visual drag-and-drop interface',
                    'Real-time preview',
                    'Responsive design tools',
                    'Custom CSS/HTML support'
                ],
                'included_in_plans': ['Basic', 'Pro', 'Business']
            },
            'templates': {
                'name': 'Professional Templates',
                'description': 'Customizable templates for various industries',
                'key_features': [
                    'Industry-specific designs',
                    'Mobile-responsive layouts',
                    'Customization options',
                    'Regular updates'
                ],
                'included_in_plans': ['Basic', 'Pro', 'Business']
            },
            'ecommerce': {
                'name': 'E-commerce Suite',
                'description': 'Complete e-commerce functionality',
                'key_features': [
                    'Product management',
                    'Secure checkout',
                    'Payment gateway integration',
                    'Order tracking'
                ],
                'included_in_plans': ['Pro', 'Business']
            }
        }
        
        return features.get(feature, {
            'name': 'Feature',
            'description': 'Feature information not found',
            'key_features': [],
            'included_in_plans': []
        })
    
    def check_product_availability(self, product_id: str) -> Dict[str, Any]:
        """Check the availability of a product.
        
        Args:
            product_id (str): The ID of the product to check
            
        Returns:
            Dict[str, Any]: Dictionary containing availability information
        """
        # This is a placeholder - in a real system, you'd query a database
        return {
            'available': True,
            'stock_level': 'in_stock',
            'quantity': 10,
            'shipping_estimate': '2-3 business days'
        }
    
    def get_related_products(self, product_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related products for a given product.
        
        Args:
            product_id (str): The ID of the product
            limit (int): Maximum number of related products to return
            
        Returns:
            List[Dict[str, Any]]: List of related products
        """
        # This is a placeholder - in a real system, you'd query a recommendation engine
        return [
            {
                'id': f'RELATED-{i}',
                'name': f'Related Product {i}',
                'similarity_score': 0.9 - (i * 0.1),
                'price': 99.99
            }
            for i in range(limit)
        ] 