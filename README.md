# 🚀 Meta Ad Creatives AI - 4-Stage Workflow

A comprehensive Streamlit-based application for generating Meta (Facebook/Instagram) ad creatives through a structured 4-stage workflow with customizable prompt engineering for Taiwan market.

![Meta Ad Creatives AI](https://img.shields.io/badge/Meta_Ads-AI_Powered-1877F2?style=for-the-badge&logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

## ✨ Features

### 🎯 **Stage 1: Product Strategy Analysis**
- **USP Analysis**: Identify core competitive advantages
- **Market Research**: Analyze Taiwan market landscape and competition
- **Consumer Insights**: Taiwan consumer preferences and behaviors for this product type
- **Positioning Strategy**: Optimal market positioning recommendations
- **Key Messaging Themes**: 3-5 core communication themes

### 👥 **Stage 2: Audience Targeting**
Generate 3-5 precise audience segments with:
- **Audience Name**: Clear and concise naming
- **Demographics**: Age, gender, income, education level
- **Interests & Behaviors**: Hobbies, consumption patterns, online behaviors
- **Pain Points & Motivations**: Primary concerns and purchase motivations
- **Meta Targeting Suggestions**: Specific Facebook/Instagram targeting settings

### ✍️ **Stage 3: Ad Copy Generation**
Customized ad copy for each audience segment following Meta's format:
- **Headlines**: 3 versions, max 40 Traditional Chinese characters
- **Primary Text A**: 125-150 characters, complete value proposition
- **Primary Text B**: 80-100 characters, concise version
- **Description**: 2 versions, max 30 characters
- **Call to Action**: Optimal CTA selection (立即購買, 了解更多, etc.)
- **Audience Alignment Strategy**: How copy targets specific audience motivations

### 🎨 **Stage 4: Creative Design Generation**
Generate 3-5 distinct 1000x1000 static image ad creative variants:
- **Creative Concept Name**: Descriptive naming for each variant
- **Target Audience**: Specific audience segment alignment
- **Visual Concept**: Detailed image content description
- **Style Guidelines**: Art style, color palette, mood, typography
- **Message Reinforcement**: How visuals reinforce core messages
- **Taiwan Market Considerations**: Cultural elements and localized visual cues
- **Image Generation Prompt**: Complete AI image generation instructions

## 🎛️ **Prompt Engineering Interface**

### **Editable Prompts for Each Stage**
- Real-time prompt customization for all 4 stages
- Default Taiwan-market optimized prompts
- Quick helper buttons for common modifications
- Review and edit generated results before proceeding

### **Quick Prompt Helpers**
- ➕ **Limited Time Offers**: Add urgency and scarcity elements
- ➕ **Brand Consistency**: Ensure brand voice alignment with 3 tone variations
- ➕ **A/B Variants**: Generate A/B test variations for optimization

## 🚀 Quick Start

### 1. **Installation**
```bash
git clone <repository-url>
cd meta-ad-creatives-ai
pip install -r requirements.txt
```

### 2. **Environment Setup**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. **Run Application**
```bash
streamlit run app.py
```

### 4. **Usage Workflow**
1. **Enter your Gemini API Key** in the sidebar
2. **Paste product URL** to auto-extract metadata
3. **Stage 1**: Customize analysis prompt and generate strategy report
4. **Stage 2**: Refine audience targeting prompt and generate segments
5. **Stage 3**: Adjust copy generation prompt and create ad copy variations
6. **Stage 4**: Modify creative prompts and generate visual concepts + images
7. **Review & Edit**: Each stage allows result editing before proceeding
8. **Export**: Download complete workflow report as JSON

## 📋 Default Prompts (Customizable)

### **Stage 1: Product Analysis**
```
請根據以下產品資料，為台灣市場製作深度產品分析報告：

**分析重點：**
1. **USP分析**：識別產品的核心競爭優勢
2. **市場研究**：分析台灣市場現況與競爭環境
3. **消費者洞察**：台灣消費者對此類產品的偏好與行為
4. **定位建議**：最適合的市場定位策略
5. **關鍵訊息主題**：3-5個核心溝通主題
```

### **Stage 2: Audience Targeting**
```
基於前階段的策略報告，請為此產品設計3-5個精準的受眾區隔：

**每個受眾區隔需包含：**
1. **受眾名稱**：簡潔明確的命名
2. **人口統計**：年齡、性別、收入、教育程度等
3. **興趣與行為**：興趣愛好、消費行為、線上行為
4. **痛點與動機**：主要困擾與購買動機
5. **Meta投放建議**：具體的Facebook/Instagram定向設定
```

### **Stage 3: Ad Copy Generation**
```
基於受眾分析，為每個受眾區隔客製化廣告文案：

**文案規格要求：**
- **標題**：3個版本，最多40字繁體中文
- **主要文案A**：125-150字繁體中文，完整傳達價值主張
- **主要文案B**：80-100字繁體中文，精簡有力版本
- **描述文字**：2個版本，最多30字繁體中文
- **行動呼籲**：選擇最適合的CTA
- **受眾對應策略**：說明如何針對特定受眾設計
```

### **Stage 4: Creative Generation**
```
基於前三階段資料，設計3-5個1000x1000靜態廣告創意變體：

**每個創意變體需包含：**
1. **創意概念名稱**：描述性命名
2. **目標受眾**：對應特定受眾區隔
3. **視覺概念**：主體、構圖、場景、道具描述
4. **風格指南**：藝術風格、色彩搭配、情緒調性
5. **訊息強化**：如何視覺化核心訊息
6. **台灣市場考量**：文化元素與在地化視覺線索
7. **圖像生成提示詞**：完整AI圖像生成指令
```

## 🛠️ Technical Architecture

### **Project Structure**
```
meta-ad-creatives-ai/
├── app.py                          # Main Streamlit application
├── src/
│   ├── models/
│   │   └── workflow.py              # Data models for 4-stage workflow
│   ├── services/
│   │   └── workflow_service.py      # Business logic for workflow
│   └── utils/
│       └── product_extractor.py     # Product metadata extraction
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment variables template
└── prototype.ipynb                  # Original notebook prototype
```

### **API Requirements**
- **Google Gemini API**: Required for all stages
  - `gemini-1.5-pro`: Text analysis and generation
  - `gemini-2.5-flash-image-preview`: Image generation

### **Key Dependencies**
```txt
streamlit>=1.28.0          # UI framework
google-generativeai>=0.8.5 # Gemini AI integration
requests==2.32.3           # HTTP requests
beautifulsoup4==4.13.4     # Web scraping
Pillow>=11.3.0             # Image processing
python-dotenv==1.0.0       # Environment variables
pydantic>=2.5.0            # Data validation
```

## 🎨 UI Features

### **Progress Tracking**
- Visual progress indicator showing current stage
- Completed stages marked with ✅
- Current stage highlighted with 🔄

### **Interactive Workflow**
- Each stage can be accessed once prerequisites are met
- Results can be edited and refined before proceeding
- Real-time prompt customization

### **Export & Download**
- Download generated creative images as PNG
- Export complete workflow report as JSON
- Individual stage results available for review

## 📊 Example Output

The system generates comprehensive outputs for Taiwan market including:

1. **Strategic insights** tailored for Taiwan consumers
2. **Audience segments** with specific Meta targeting parameters
3. **Ad copy variations** in Traditional Chinese following Meta specifications
4. **Visual creative concepts** with detailed generation prompts
5. **High-quality 1000x1000 ad creative images** ready for Meta campaigns

## 🤝 Contributing

Based on the original Jupyter notebook prototype, this application provides a production-ready interface for Meta ad creative generation with enhanced prompt engineering capabilities.

## 📄 License

MIT License
