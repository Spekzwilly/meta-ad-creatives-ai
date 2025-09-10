"""
Service for handling the 4-stage Meta Ad Creatives workflow.
"""
import json
import re
from typing import Dict, List, Optional
import google.generativeai as genai
from src.models.workflow import (
    ProductMetadata, StrategyReport, AudienceTargeting, AudienceSegment,
    AdCopyGeneration, AdCopyVersion, AdCreativeGeneration, CreativeVariant,
    WorkflowState
)
from src.utils.product_extractor import ProductMetadataExtractor
from src.services.image_generation_service import ImageGenerationService
import logging

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing the 4-stage workflow."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel("gemini-1.5-pro")
        self.extractor = ProductMetadataExtractor()
        self.image_service = ImageGenerationService(api_key)
    
    def extract_product_metadata(self, url: str) -> ProductMetadata:
        """Stage 0: Extract product metadata from URL."""
        metadata = self.extractor.extract_metadata(url)
        return ProductMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            image_url=metadata.get("image", ""),
            price=metadata.get("price", ""),
            usps=metadata.get("usps", []),
            url=url
        )
    
    def generate_strategy_report(self, product_metadata: ProductMetadata, custom_prompt: str) -> str:
        """Stage 1: Generate strategy report."""
        product_info = f"""
標題: {product_metadata.title}
描述: {product_metadata.description}
價格: {product_metadata.price}
主要特色: {', '.join(product_metadata.usps[:5]) if product_metadata.usps else '未提供'}
網址: {product_metadata.url}
"""
        
        prompt = custom_prompt.format(product_info=product_info)
        response = self.text_model.generate_content(prompt)
        return response.text
    
    def generate_audience_targeting(self, strategy_report_text: str, custom_prompt: str) -> str:
        """Stage 2: Generate audience targeting analysis."""
        prompt = custom_prompt.format(strategy_report=strategy_report_text)
        response = self.text_model.generate_content(prompt)
        return response.text
    
    def generate_ad_copy(self, audience_targeting_text: str, custom_prompt: str) -> str:
        """Stage 3: Generate ad copy for each audience segment."""
        prompt = custom_prompt.format(audience_targeting=audience_targeting_text)
        response = self.text_model.generate_content(prompt)
        return response.text
    
    def generate_creative_concepts(self, strategy_report_text: str, audience_targeting_text: str, 
                                 ad_copy_text: str, custom_prompt: str) -> str:
        """Stage 4: Generate creative concepts and prompts."""
        prompt = custom_prompt.format(
            strategy_report=strategy_report_text,
            audience_targeting=audience_targeting_text,
            ad_copy_generation=ad_copy_text
        )
        response = self.text_model.generate_content(prompt)
        return response.text
    
    def generate_image_from_prompt(self, image_url: Optional[str], prompt: str):
        """Generate image from prompt using Gemini vision model."""
        return self.image_service.generate_image_from_prompt(image_url, prompt)
    
    def generate_creative_concepts_with_images(self, strategy_report_text: str, audience_targeting_text: str, 
                                             ad_copy_text: str, custom_prompt: str, 
                                             product_image_url: str) -> str:
        """Stage 4: Generate creative concepts with actual images in table format."""
        # Step 1: Generate JSON concepts
        prompt = custom_prompt.format(
            strategy_report=strategy_report_text,
            audience_targeting=audience_targeting_text,
            ad_copy_generation=ad_copy_text
        )
        response = self.text_model.generate_content(prompt)
        stage4_json_str = response.text
        
        # Step 2: Parse JSON and generate images
        table_rows = []
        try:
            # Clean JSON string
            if stage4_json_str.strip().startswith("```json"):
                stage4_json_str = stage4_json_str.strip()[7:-4]
            elif stage4_json_str.strip().startswith("```"):
                stage4_json_str = stage4_json_str.strip()[3:-3]
            
            creative_concepts = json.loads(stage4_json_str)
            
            for i, concept in enumerate(creative_concepts):
                # Generate image for this concept
                image_output_data = self.image_service.generate_creative_image(
                    product_image_url, 
                    concept['image_prompt_en']
                )
                
                table_rows.append({
                    "audience": concept['target_audience_zh'],
                    "description": concept['image_prompt_en'],
                    "image_output": image_output_data
                })
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return f"| Audience Group | Creative Description | Generated Image |\n|---|---|---|\n| Error | JSON Parse Error: {str(e)} | N/A |"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"| Audience Group | Creative Description | Generated Image |\n|---|---|---|\n| Error | {str(e)} | N/A |"
        
        # Step 3: Generate HTML table
        markdown_table = "| Audience Group | Creative Description | Generated Image |\n"
        markdown_table += "|---|---|---|\n"
        
        for row in table_rows:
            image_md = ""
            # Check if the output is a long string (likely base64) vs. a short error message
            if len(row['image_output']) > 100:
                # Use data URI with base64 to embed the image
                image_md = f"<img src='data:image/png;base64,{row['image_output']}' width='300'>"
            else:
                image_md = row['image_output']  # This will be the error message

            description_cleaned = row['description'].replace('|', '\\|')
            markdown_table += f"| {row['audience']} | {description_cleaned} | {image_md} |\n"
        
        return markdown_table
    
    def parse_audience_segments(self, audience_text: str) -> List[AudienceSegment]:
        """Parse audience targeting text into structured segments."""
        # This is a simplified parser - in production, you might want more sophisticated parsing
        segments = []
        
        # Try to extract audience segments using pattern matching
        # This is a basic implementation - you might want to use more advanced NLP
        audience_pattern = r"受眾名稱[：:](.+?)(?=人口統計|$)"
        demo_pattern = r"人口統計[：:](.+?)(?=興趣與行為|$)"
        interests_pattern = r"興趣與行為[：:](.+?)(?=痛點與動機|$)"
        pain_points_pattern = r"痛點與動機[：:](.+?)(?=Meta投放建議|$)"
        meta_pattern = r"Meta投放建議[：:](.+?)(?=受眾名稱|$)"
        
        # For now, return a placeholder structure
        # In a real implementation, you'd parse the actual text
        segments.append(AudienceSegment(
            audience_name="解析中...",
            demographics="解析中...",
            interests_behaviors="解析中...",
            pain_points_motivations="解析中...",
            meta_targeting_suggestions="解析中..."
        ))
        
        return segments
    
    def validate_stage_completion(self, stage: int, workflow_state: WorkflowState) -> bool:
        """Validate if a stage can proceed to the next."""
        if stage == 1:
            return workflow_state.product_metadata is not None
        elif stage == 2:
            return workflow_state.strategy_report is not None
        elif stage == 3:
            return workflow_state.audience_targeting is not None
        elif stage == 4:
            return workflow_state.ad_copy_generation is not None
        return False
