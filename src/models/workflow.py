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
    stage1_prompt: str = """
    Role: You are a senior Meta ads specialist, well-versed in Taiwan’s e-commerce industry, and will assist clients in developing advertising strategies for specific products or product groups.
    Context:
    Before launching ads, it’s essential to understand the product’s features and selling points. Based on the following product information, please conduct a preliminary analysis of product highlights and market research, then produce an advertising strategy report.

    **Product Information:**
    {product_info}
    Task:
    Based on the product information, write a product analysis, market analysis, and strategic report for the client.

    Output:
    **Analysis Focus:**
    1. **USP Analysis:** Identify the product’s core competitive advantages.
    2. **Market Research:** Analyze the product’s current status and competitive landscape in Taiwan.
    3. **Consumer Insights:** Explore Taiwanese consumer preferences and behaviors regarding this product category.
    4. **Positioning Recommendations:** Suggest the most suitable market positioning strategy.
    5. **Key Messaging Themes:** Provide 3-5 core communication themes.

    Please provide actionable strategic recommendations from the perspective of a professional marketing analyst.
    Note: Always write in traditional Chinese.

    Reference:
    # Stage 1 Example Reference: 智慧貓砂盆 (Smart Cat Litter Box)

    This document provides a detailed example of the output for Stage 1 of the AI-Powered Advertising Workflow, using the hypothetical product "智慧貓砂盆" (Smart Cat Litter Box) for the Taiwan market.
    
    ---
    
    ### **Product Information (Example)**
    
    *   **Product Name:** 智慧貓砂盆 (Smart Cat Litter Box)
    *   **Product Description:** 一款專為台灣家庭設計的智慧貓砂盆，具備自動清潔、除臭、健康監測功能。透過專屬APP，貓奴可隨時掌握主子如廁情況，適用於狹小居住空間，解決傳統貓砂盆的清潔困擾與異味問題。
    *   **Product Metadata:**
        *   **Price:** NT$4,500
        *   **Features:** 自動鏟砂 (Automatic Scooping), 負離子除臭 (Anion Deodorization), APP健康監測 (APP Health Monitoring - weight, frequency, duration), 適用多種貓砂 (Compatible with multiple litter types), 低噪音運作 (Low-noise operation), 簡約設計 (Minimalist Design)
        *   **Dimensions:** 50cm x 50cm x 55cm
        *   **Target Audience:** 居住在台灣都會區的年輕貓飼主，重視生活品質與寵物健康。
    
    ---
    
    ### **1. Metadata Analysis**
    
    Based on the product information, the following key themes, keywords, and emotional triggers are identified for the Taiwan market:
    
    *   **Keywords (Traditional Chinese):** 智慧貓砂盆, 自動貓砂盆, 貓砂盆除臭, 貓健康監測, 貓奴, 主子, 鏟屎官, 智能養貓, 寵物科技, 公寓養貓.
    *   **Core Themes:**
        *   **Convenience & Time-Saving:** The "自動" (automatic) aspect is a major draw for busy Taiwanese urbanites. It frees them from the daily chore of scooping litter ("鏟屎").
        *   **Health & Wellness:** The "健康監測" (health monitoring) feature taps into the deep emotional connection Taiwanese owners have with their pets, whom they often refer to as "主子" (master). It transforms a simple litter box into a proactive health tool.
        *   **Odor Control & Cleanliness:** "除臭" (deodorization) is a critical selling point in Taiwan's humid climate and smaller living spaces (apartments/"公寓"). A clean, odor-free home is highly valued.
        *   **Smart Technology & Modern Lifestyle:** The product positions itself as part of a "智能" (smart) and modern lifestyle, appealing to tech-savvy younger generations.
    *   **Emotional Triggers:**
        *   **Love & Care for Pets:** The desire to provide the best for their "主子" (master cat).
        *   **Relief from a Chore:** The liberation from the unpleasant task of cleaning the litter box.
        *   **Peace of Mind:** Knowing their cat's health is being monitored and their home is clean.
        *   **Sense of Modernity:** Owning a piece of smart pet technology that enhances their lifestyle.
    
    ### **2. Unique Selling Points (USPs) Generation**
    
    Based on the metadata analysis, the following 4 USPs are formulated for the Taiwan market:
    
    1.  **專為台灣貓奴設計的全方位健康管家 (A Comprehensive Health Butler Designed for Taiwanese Cat Lovers):** This USP goes beyond "health monitoring." It frames the product as a dedicated "管家" (butler), a term that resonates with service-oriented values. It combines the APP monitoring of weight, frequency, and duration into a single, powerful benefit: proactive health management for their beloved "主子".
    
    2.  **告別異味，小空間也能極致清新 (Say Goodbye to Odors, Ultimate Freshness Even in Small Spaces):** This USP directly addresses the pain point of living in smaller urban apartments, a common situation in Taiwan. It highlights the anion deodorization technology and promises an "極致清新" (ultimate freshness), which is a highly desirable state in a humid climate.
    
    3.  **解放雙手，每日自動鏟屎的終極自由 (Free Your Hands, The Ultimate Freedom of Automatic Daily Scooping):** This USP uses the colloquial term "鏟屎" (scooping poop) to create a relatable and humorous connection with the target audience. It emphasizes the core benefit of convenience and frames it as "終極自由" (ultimate freedom), a powerful emotional promise for busy professionals.
    
    4.  **簡約美學，完美融入你的居家風格 (Minimalist Aesthetics, Perfectly Blends into Your Home Style):** Taiwanese consumers, particularly the younger demographic, have a growing appreciation for minimalist design and home aesthetics (e.g., Muji-style). This USP positions the product not just as a utility item, but as a stylish addition to their home, justifying its premium price point.
    
    ### **3. Market Research (Taiwan)**
    
    *   **Market Size & Trends:** The pet care market in Taiwan is booming, with a significant increase in the "pet humanization" trend. Owners are willing to spend more on premium and tech-integrated products for their pets. The smart pet product category, especially for cats, is a high-growth segment.
    *   **Consumer Behavior:** Taiwanese cat owners are highly engaged online, frequently participating in Facebook groups (e.g., "貓咪也瘋狂俱樂部") and following pet-related influencers on Instagram. They rely heavily on online reviews, unboxing videos (開箱文), and word-of-mouth recommendations before making a purchase, especially for higher-priced items. They value products that offer tangible benefits in convenience, health, and cleanliness.
    *   **Competitive Landscape:**
        *   **Key Competitors:** Brands like Petkit, Catlink, and other imported smart litter boxes are present in the market, often sold through e-commerce platforms like PChome, Momo, and Shopee.
        *   **Positioning:** Competitors often focus on the technology itself. Our opportunity is to position our product with a stronger emotional connection and a focus on benefits tailored to the *Taiwanese* lifestyle (small spaces, humidity, local colloquialisms).
    *   **Cultural Considerations:** The terms "貓奴" (cat slave), "主子" (master), and "鏟屎官" (scooper officer) are terms of endearment and are widely used. Incorporating this language creates an instant cultural connection and shows that the brand understands the local cat owner community.
    
    ### **4. Business Strategy Report for Meta Ads (Taiwan)**
    
    *   **Strategic Approach:** The campaign will focus on a benefit-driven narrative rather than a feature-driven one. We will use a combination of emotional storytelling and problem-solution content to justify the premium price and drive sales conversions. The strategy is to build trust through relatable content and highlight the product as an essential upgrade for modern cat owners in Taiwan.
    *   **Key Messaging Pillars:**
        1.  **The Gift of Health:** Frame the purchase as an investment in the cat's long-term health and the owner's peace of mind.
        2.  **The Luxury of Time:** Position the product as a time-saving device that gives owners more quality time to spend with their cats, rather than on chores.
        3.  **A Cleaner, Happier Home:** Emphasize the benefit of a fresh, odor-free living environment for both the owner and the cat.
    *   **Competitive Positioning:** While competitors sell a "smart litter box," we are selling "a better life for you and your cat in Taiwan." We will differentiate by using hyper-localized copy and creative that reflects the specific living conditions and cultural nuances of our target audience.
    *   **Sales Funnel Strategy (Meta):**
        *   **Top of Funnel (Awareness):** Use video ads showcasing the problem (messy, smelly litter boxes) and the solution (our product in a clean, stylish home). Focus on broad interests like "cats," "pet lovers," and followers of major pet-related pages in Taiwan.
        *   **Middle of Funnel (Consideration):** Retarget video viewers and page engagers with carousel ads that detail the key USPs (Health Butler, Odor Control, Freedom). Use testimonials and user-generated content style creative.
        *   **Bottom of Funnel (Conversion):** Retarget website visitors and "add to cart" abandoners with direct response ads featuring a clear Call to Action ("立即購買") and potentially a limited-time offer to create urgency. The primary text will be short, direct, and focused on the final conversion.
"""

    stage2_prompt: str = """
    Role: You are a senior Meta ads specialist, well-versed in Taiwan’s e-commerce industry, and will assist clients in identifying targeting audience groups for specific products or product colletions.
    Contex: We've already had a strategy report for the specified product/collections. see: {strategy_report}
    Task: 基於前階段的策略報告，請為此產品設計3-5個精準的受眾區隔
    Output:
        **每個受眾區隔需包含：**
        1. **受眾名稱**：簡潔明確的命名
        2. **人口統計 (Demographic)**：年齡、性別、收入、教育程度等
        3. **興趣與行為**：興趣愛好、消費行為、線上行為
        4. **痛點與動機**：主要困擾與購買動機
        5. **Meta投放建議**：具體的Facebook/Instagram定向設定
        請確保每個受眾區隔有明確差異化(MECE)，以台灣市場為主，並適合 Meta 廣告平台投放。
        Note: Always write in traditional Chinese.
        Note: Show the result in table format.
    Reference:
        

"""

    stage3_prompt: str = """
        Role: You are a senior Meta ads specialist, well-versed in Taiwan’s e-commerce industry, and will assist clients in generating ad copy for targeting audience groups for specific products or product colletions.
        Context: We've already had a "audience breakdown report" for the specified product/collectinos. "audience breakdown report": {audience_targeting}
        Task: Generate ad copy for each targeting audience group based on the "audience breakdown report"
        Output: 
            **文案規格要求：**
            - **Audience Group** (受眾族群)
            - **Primary Text** (主要廣告文案)
            - **Headline** (廣告口號：顯示在創意素材下方的短句，請提供 3 個選項)
            - **CTA Text** (行動呼籲按鈕文字)
            - **Angle Used** (採用切角)
            - **Link between Angle and Motivation** (切角與動機連結)
            請確保文案符合Meta廣告規範且針對台灣消費者優化。
            Note: Always write in traditional Chinese.
            Note: Show the result in table format.
        **需求說明**：
            - **Primary Text**: 這是廣告的主要內文。請仿照以下範例的風格，撰寫一段吸引人的文案 (不限於一句話)。文案應包含表情符號（emoji）、條列式亮點、急迫感訊息、以及相關的主題標籤（hashtags）。
              範例:
              ```
              ✈️ 日韓美妝保養品，零時差直送台灣
              🔥 三友藥妝9月限定，全館5折起
              💯 官網獨家優惠，買一送一，等於75折起
              🎁 多款熱門商品：日本皇后面膜、韓國淡斑精華...
              ⏰ 限時限量，錯過不再！
            
              立即搶購 👉 [連結]
              #三友藥妝 #日韓美妝 #買一送一 #限時優惠
              ```
            - **Headline**: 這是顯示在創意下方的短標題，請提供三個不同的版本供 A/B 測試。
            - **CTA Text**: 這是行動呼籲按鈕上顯示的文字。
            - 文案策略（切角與動機）需與指定的受眾族群高度相關。
            
        """

    stage4_prompt: str = """
你是一位精通台灣電商市場的 ads creative agency ，了解台灣電商市場常見的廣告格式以及元素。
根據以下受眾輪廓與廣告文案，請為每個受眾產生 2-3 個靜態廣告創意構想。

受眾輪廓：
{audience_targeting}

廣告文案：
{ad_copy_generation}

策略報告：
{strategy_report}

Your instructions are to act as an expert art director. For each concept, provide a concise but detailed image prompt that will be given to an AI model. The AI will be given the original product image, and your prompt will guide it on how to *edit* or *recontextualize* that product image into a new scene.

請將結果以一個 JSON 陣列格式回傳，陣列中的每個物件都代表一個創意構想，並包含以下欄位：
- "concept_name_zh": (string) 概念名稱 (繁體中文)
- "target_audience_zh": (string) 目標受眾 (繁體中文)
- "image_prompt_en": (string) 可直接用於圖像生成模型的詳細英文 prompt (專為台灣市場設計，廣告圖上需要有 hooks ，也就是吸引人的廣告文案以及 CTA)

**重要**: 請僅輸出一個格式正確的 JSON 陣列，不要包含任何額外的文字或 markdown 格式（例如 ```json ... ```）。
"""
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
