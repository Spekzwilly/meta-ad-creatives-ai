"""
Data models for the 4-stage Meta Ad Creatives workflow.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ProductMetadata(BaseModel):
    """Product metadata extracted from URL."""
    title: str
    description: str
    image_url: Optional[str] = None
    price: Optional[str] = None
    usps: List[str] = Field(default_factory=list)
    url: str
    extracted_at: datetime = Field(default_factory=datetime.now)


class StrategyReport(BaseModel):
    """Stage 1: Product analysis and strategy report."""
    product_metadata: ProductMetadata
    usp_analysis: str
    market_research: str
    taiwan_market_insights: str
    competitive_advantages: List[str]
    recommended_positioning: str
    key_messaging_themes: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)


class AudienceSegment(BaseModel):
    """Individual audience segment definition."""
    audience_name: str
    demographics: str
    interests_behaviors: str
    pain_points_motivations: str
    meta_targeting_suggestions: str


class AudienceTargeting(BaseModel):
    """Stage 2: Audience targeting analysis."""
    strategy_report: StrategyReport
    audience_segments: List[AudienceSegment]
    generated_at: datetime = Field(default_factory=datetime.now)


class AdCopyVersion(BaseModel):
    """Individual ad copy version."""
    headline_versions: List[str] = Field(min_items=3, max_items=3)  # 3 versions, max 40 chars
    primary_text_a: str  # 125-150 chars
    primary_text_b: str  # 80-100 chars
    description_versions: List[str] = Field(min_items=2, max_items=2)  # 2 versions, max 30 chars
    call_to_action: str  # From Meta's available options
    audience_alignment_strategy: str


class AdCopyGeneration(BaseModel):
    """Stage 3: Ad copy generation for each audience."""
    audience_targeting: AudienceTargeting
    ad_copies: Dict[str, AdCopyVersion]  # audience_name -> AdCopyVersion
    generated_at: datetime = Field(default_factory=datetime.now)


class CreativeVariant(BaseModel):
    """Individual creative variant definition."""
    creative_concept_name: str
    target_audience: str
    visual_concept: Dict[str, str]  # main_subject, composition, setting, props
    style_guidelines: Dict[str, str]  # art_style, color_palette, mood, typography
    key_message_reinforcement: str
    taiwan_market_considerations: str
    image_generation_prompt: str


class AdCreativeGeneration(BaseModel):
    """Stage 4: Ad creative generation."""
    ad_copy_generation: AdCopyGeneration
    creative_variants: List[CreativeVariant]
    generated_at: datetime = Field(default_factory=datetime.now)


class WorkflowState(BaseModel):
    """Complete workflow state."""
    current_stage: int = 1
    product_url: Optional[str] = None
    
    # Stage results
    product_metadata: Optional[ProductMetadata] = None
    strategy_report: Optional[StrategyReport] = None
    audience_targeting: Optional[AudienceTargeting] = None
    ad_copy_generation: Optional[AdCopyGeneration] = None
    ad_creative_generation: Optional[AdCreativeGeneration] = None
    
    # Prompts for each stage (user can modify these)
    stage1_prompt: str = """請根據以下產品資料，為台灣市場製作深度產品分析報告：

**分析重點：**
1. **USP分析**：識別產品的核心競爭優勢
2. **市場研究**：分析台灣市場現況與競爭環境
3. **消費者洞察**：台灣消費者對此類產品的偏好與行為
4. **定位建議**：最適合的市場定位策略
5. **關鍵訊息主題**：3-5個核心溝通主題

**產品資料：**
{product_info}

請以專業行銷分析師的角度，提供可執行的策略建議。"""

    stage2_prompt: str = """基於前階段的策略報告，請為此產品設計3-5個精準的受眾區隔：

**每個受眾區隔需包含：**
1. **受眾名稱**：簡潔明確的命名
2. **人口統計**：年齡、性別、收入、教育程度等
3. **興趣與行為**：興趣愛好、消費行為、線上行為
4. **痛點與動機**：主要困擾與購買動機
5. **Meta投放建議**：具體的Facebook/Instagram定向設定

**策略報告：**
{strategy_report}

請確保每個受眾區隔有明確差異化，並適合Meta廣告平台投放。"""

    stage3_prompt: str = """基於受眾分析，為每個受眾區隔客製化廣告文案：

**文案規格要求：**
- **標題**：3個版本，最多40字繁體中文，吸睛且強調效益
- **主要文案A**：125-150字繁體中文，完整傳達價值主張
- **主要文案B**：80-100字繁體中文，精簡有力版本
- **描述文字**：2個版本，最多30字繁體中文，補強主訊息
- **行動呼籲**：選擇最適合的CTA（立即購買、了解更多、立即訂購、馬上搶購、查看商品）
- **受眾對應策略**：說明如何針對特定受眾設計

**受眾分析：**
{audience_targeting}

請確保文案符合Meta廣告規範且針對台灣消費者優化。"""

    stage4_prompt: str = """基於前三階段資料，設計3-5個1000x1000靜態廣告創意變體：

**每個創意變體需包含：**
1. **創意概念名稱**：描述性命名
2. **目標受眾**：對應第二階段的特定受眾
3. **視覺概念**：主體、構圖、場景、道具的詳細描述
4. **風格指南**：藝術風格、色彩搭配、情緒調性、文字整合
5. **訊息強化**：如何視覺化核心訊息
6. **台灣市場考量**：文化元素與在地化視覺線索
7. **圖像生成提示詞**：完整的AI圖像生成指令

**完整專案資料：**
策略報告：{strategy_report}
受眾分析：{audience_targeting}
廣告文案：{ad_copy_generation}

請設計能引起台灣消費者共鳴且符合Meta廣告最佳實踐的創意。"""
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
