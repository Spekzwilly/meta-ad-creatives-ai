"""
Service for handling image generation operations.
"""
import base64
import requests
import logging
from typing import Optional
from PIL import Image
from io import BytesIO
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for generating and manipulating images using AI models."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.image_model = genai.GenerativeModel("gemini-2.5-flash-image-preview")
    
    def generate_image_from_prompt(self, image_url: Optional[str], prompt: str) -> Optional[Image.Image]:
        """Generate image from prompt using Gemini vision model."""
        try:
            parts = []
            if image_url:
                resp = requests.get(image_url)
                resp.raise_for_status()
                parts.append(Image.open(BytesIO(resp.content)))
            parts.append(prompt)
            
            response = self.image_model.generate_content(parts, stream=False)
            
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return Image.open(BytesIO(part.inline_data.data))
            return None
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None
    
    def generate_creative_image(self, original_image_url: str, image_prompt: str) -> str:
        """Generate a creative image based on original product image and prompt.
        
        Returns:
            Base64 encoded image string or error message
        """
        try:
            # Load original product image
            image_response = requests.get(original_image_url)
            image_response.raise_for_status()
            original_image = Image.open(BytesIO(image_response.content))
            
            # Create editing prompt
            editing_prompt = (
                f"Using the product from the provided image as the main subject, create a new photorealistic scene based on this art direction: "
                f"{image_prompt}\n\n"
                f"Important: The final output must be only the generated image."
            )
            
            # Generate image using vision model
            response = self.image_model.generate_content(
                [editing_prompt, original_image]
            )
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_bytes = part.inline_data.data
                        return base64.b64encode(image_bytes).decode('utf-8')
            
            return "No image generated"
            
        except Exception as e:
            logger.error(f"Creative image generation failed: {e}")
            return f"Generation Failed: {str(e)}"
    
    def load_image_as_base64(self, image_url: str) -> str:
        """Load an image from URL and return as base64 string."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to load image from URL: {e}")
            return f"Load Failed: {str(e)}"