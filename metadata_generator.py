from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PunjabiMetadataGenerator:
    """Generate Punjabi titles, descriptions, and hashtags"""
    
    # Punjabi translations for common content types
    CONTENT_TYPES = {
        "tech_review": "ਟੈਕ ਸਮੀਖਿਆ",
        "unboxing": "ਅਨਬੌਕਸਿੰਗ",
        "tutorial": "ਟਿਊਟੋਰਿਅਲ",
        "gadget": "ਗੈਜੇਟ",
        "reaction": "ਪ୍ਰਤਿਕ੍ਰਿਆ",
        "comedy": "ਮਜ਼ਾਕ",
        "gaming": "ਗੇਮਿੰਗ",
        "education": "ਸਿਖਿਆ",
    }
    
    # Popular Punjabi hashtags
    POPULAR_HASHTAGS = [
        "#ਪੰਜਾਬੀ",
        "#ਯੂਟਿਊਬ",
        "#ਵਾਇਰਲ",
        "#ਨਵ",
        "#ਟਾਪ",
        "#ਟ੍ਰੇਂਡਿੰਗ",
    ]
    
    def __init__(self):
        pass
    
    def generate_title(self, original_title: str, content_type: str = "reaction") -> str:
        """
        Generate engaging Punjabi title
        
        Args:
            original_title: Original video title
            content_type: Type of content
        
        Returns:
            Punjabi title
        """
        try:
            # Simple title generation - can be enhanced with AI
            content_type_punjabi = self.CONTENT_TYPES.get(content_type, "ਪ୍ਰਤਿਕ੍ਰਿਆ")
            
            # Add emoji and Punjabi prefix
            title = f"{content_type_punjabi} - {original_title}"
            
            logger.info(f"Generated Punjabi title: {title}")
            return title
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return original_title
    
    def generate_description(self, original_description: str, channel_name: str = "") -> str:
        """
        Generate Punjabi description
        
        Args:
            original_description: Original video description
            channel_name: Original channel name
        
        Returns:
            Punjabi description
        """
        try:
            desc = f"""ਇਹ ਵੀਡੀਓ ਅਸਲ ਵਿੱਚ ਇਸ ਚੈਨਲ ਤੋਂ ਹੈ: {channel_name}

ਅਸੀਂ ਇਸ ਅਸਲ ਵੀਡੀਓ ਉੱਤੇ ਪੰਜਾਬੀ ਵਿੱਚ ਆਪਣਾ ਵਿਚਾਰ ਸ਼ਾਮਲ ਕੀਤਾ ਹੈ।

ਅਸਲ ਵੀਡੀਓ:
{original_description[:200]}...

ਸਾਡੀ ਯੂਟਿਊਬ ਚੈਨਲ ਨੂੰ ਸਬਸਕ੍ਰਾਈਬ ਕਰੋ ਬਹੁਤ ਸਾਰੀ ਅਜਿਹੀ ਮਾਂ ਨਿਆਲੀ ਵੀਡੀਓ ਲਈ।

ਸ਼ੁਕਰੀਆ ਵੇਖਣ ਲਈ! 🙏"""
            
            logger.info("Generated Punjabi description")
            return desc
        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            return original_description
    
    def generate_hashtags(self, content_type: str = "reaction", custom_tags: List[str] = None) -> List[str]:
        """
        Generate Punjabi hashtags
        
        Args:
            content_type: Type of content
            custom_tags: Additional custom hashtags
        
        Returns:
            List of hashtags
        """
        try:
            hashtags = self.POPULAR_HASHTAGS.copy()
            
            # Add content-type specific hashtag
            if content_type in self.CONTENT_TYPES:
                hashtags.append(f"#{self.CONTENT_TYPES[content_type]}")
            
            # Add custom tags
            if custom_tags:
                hashtags.extend([f"#{tag}" for tag in custom_tags])
            
            logger.info(f"Generated {len(hashtags)} hashtags")
            return hashtags[:15]  # Limit to 15 hashtags
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return self.POPULAR_HASHTAGS
    
    def generate_metadata(self, original_title: str, original_description: str, 
                         channel_name: str, content_type: str = "reaction") -> Dict:
        """
        Generate complete metadata package
        
        Args:
            original_title: Original video title
            original_description: Original video description
            channel_name: Original channel name
            content_type: Type of content
        
        Returns:
            Dict with title, description, hashtags
        """
        return {
            "title": self.generate_title(original_title, content_type),
            "description": self.generate_description(original_description, channel_name),
            "hashtags": self.generate_hashtags(content_type),
            "content_type": content_type,
            "language": "pa"  # Punjabi
        }