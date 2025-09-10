import os
import io
import json
import re
from typing import Optional

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

from src.models.workflow import WorkflowState, ProductMetadata
from src.services.workflow_service import WorkflowService

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def clean_product_text(text: str) -> str:
    """Clean HTML tags and format product text for better display."""
    if not text:
        return text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = text.strip()
    
    return text

def render_table_with_markdown(table_dict: dict) -> None:
    """Render table dictionary as HTML table with Markdown formatting support."""
    html = "<table style='width:100%; border-collapse: collapse;'>"
    
    # Add header
    html += "<thead><tr>"
    for col in table_dict["headers"]:
        html += f"<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>{col}</th>"
    html += "</tr></thead>"
    
    # Add rows
    html += "<tbody>"
    for row in table_dict["data"]:
        html += "<tr>"
        for cell in row:
            # Convert markdown to HTML
            cell_html = str(cell)
            # Convert **bold** to <strong>bold</strong>
            cell_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', cell_html)
            # Convert *italic* to <em>italic</em>
            cell_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', cell_html)
            # <br> tags are already HTML
            html += f"<td style='border: 1px solid #ddd; padding: 8px; vertical-align: top;'>{cell_html}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    
    st.markdown(html, unsafe_allow_html=True)

def parse_markdown_table(text: str) -> Optional[dict]:
    """Parse markdown table from text and return as pandas DataFrame."""
    if not text:
        return None
    
    # Look for markdown table patterns
    lines = text.strip().split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        # Check if line looks like a table row (contains |)
        if '|' in line:
            # Clean up the line
            clean_line = line.strip()
            if clean_line.startswith('|') and clean_line.endswith('|'):
                table_lines.append(clean_line)
                in_table = True
            elif clean_line.count('|') >= 2:  # At least 2 pipes for a valid row
                table_lines.append(clean_line)
                in_table = True
        elif in_table and line.strip() == '':
            # Empty line might end the table
            break
        elif in_table and not line.strip().startswith('-'):
            # If we were in a table and hit a non-table line (not separator), break
            break
    
    if len(table_lines) < 2:  # Need at least header and one data row
        return None
    
    try:
        # Parse the table
        data = []
        headers = None
        
        for i, line in enumerate(table_lines):
            # Skip separator lines (containing only -, |, :, and spaces)
            if re.match(r'^[\s\|\-\:]+$', line):
                continue
                
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty cells at start/end (from leading/trailing |)
            cells = [cell for cell in cells if cell]
            
            if headers is None:
                headers = cells
            else:
                if len(cells) == len(headers):
                    data.append(cells)
        
        if headers and data:
            return {"headers": headers, "data": data}
    
    except Exception:
        pass  # If parsing fails, return None
    
    return None

def initialize_workflow_state():
    """Initialize workflow state in session."""
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = WorkflowState()

def render_stage_progress():
    """Render stage progress indicator."""
    stages = ["產品分析", "受眾定向", "廣告文案", "創意設計"]
    current = st.session_state.workflow_state.current_stage
    
    cols = st.columns(4)
    for i, stage in enumerate(stages, 1):
        with cols[i-1]:
            if i < current:
                st.success(f"✅ {i}. {stage}")
            elif i == current:
                st.info(f"🔄 {i}. {stage}")
            else:
                st.write(f"⏳ {i}. {stage}")

def render_product_input():
    """Render product URL input and metadata extraction."""
    st.subheader("📦 產品資料")
    
    product_url = st.text_input(
        "產品網址", 
        placeholder="https://www.nike.com/tw/product-page",
        value=st.session_state.workflow_state.product_url or ""
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        extract_btn = st.button("📝 提取產品資料", use_container_width=True)
    with col2:
        reset_btn = st.button("🔄 重置流程", use_container_width=True)
    
    if reset_btn:
        st.session_state.workflow_state = WorkflowState()
        st.rerun()
    
    if extract_btn and product_url:
        if not GEMINI_API_KEY and not st.session_state.get("api_key"):
            st.error("請先在側邊欄輸入 Gemini API Key")
            return
        
        try:
            api_key = st.session_state.get("api_key", GEMINI_API_KEY)
            workflow_service = WorkflowService(api_key)
            
            with st.spinner("正在提取產品資料..."):
                metadata = workflow_service.extract_product_metadata(product_url)
                st.session_state.workflow_state.product_metadata = metadata
                st.session_state.workflow_state.product_url = product_url
                st.session_state.workflow_state.current_stage = 1
            st.success("✅ 產品資料提取完成！")
            st.rerun()
        except Exception as e:
            st.error(f"提取失敗: {e}")
    
    # Display extracted metadata
    if st.session_state.workflow_state.product_metadata:
        metadata = st.session_state.workflow_state.product_metadata
        with st.expander("📋 已提取的產品資料", expanded=True):
            # Add CSS for better text wrapping
            st.markdown("""
                <style>
                .product-metadata {
                    word-wrap: break-word;
                    word-break: break-word;
                    overflow-wrap: break-word;
                    white-space: pre-wrap;
                    max-width: 100%;
                }
                .product-text {
                    word-wrap: break-word;
                    word-break: break-word;
                    overflow-wrap: break-word;
                    white-space: normal;
                    max-width: 100%;
                    line-height: 1.4;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Clean and display title
            clean_title = clean_product_text(metadata.title)
            st.markdown(f'<div class="product-text"><strong>標題:</strong> {clean_title}</div>', unsafe_allow_html=True)
            
            # Clean and display description with proper text wrapping
            clean_description = clean_product_text(metadata.description)
            if len(clean_description) > 200:
                short_desc = clean_description[:200] + "..."
                st.markdown(f'<div class="product-text"><strong>描述:</strong> {short_desc}</div>', unsafe_allow_html=True)
                with st.expander("顯示完整描述", expanded=False):
                    st.markdown(f'<div class="product-text">{clean_description}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="product-text"><strong>描述:</strong> {clean_description}</div>', unsafe_allow_html=True)
            
            # Clean and display price
            clean_price = clean_product_text(metadata.price) if metadata.price else "未提供"
            st.markdown(f'<div class="product-text"><strong>價格:</strong> {clean_price}</div>', unsafe_allow_html=True)
            
            # Clean and display USPs
            if metadata.usps:
                clean_usps = [clean_product_text(usp) for usp in metadata.usps if usp.strip()]
                if clean_usps:
                    usps_text = ', '.join(clean_usps[:3])
                    st.markdown(f'<div class="product-text"><strong>特色:</strong> {usps_text}</div>', unsafe_allow_html=True)
                    if len(clean_usps) > 3:
                        with st.expander("顯示所有特色", expanded=False):
                            for i, usp in enumerate(clean_usps, 1):
                                st.markdown(f'<div class="product-text">{i}. {usp}</div>', unsafe_allow_html=True)
            
            # Display image
            if metadata.image_url:
                st.image(metadata.image_url, caption="產品圖片", width=300)

def render_stage_1():
    """Render Stage 1: Product Analysis."""
    st.subheader("🎯 階段 1: 產品策略分析")
    
    if not st.session_state.workflow_state.product_metadata:
        st.warning("請先提取產品資料")
        return
    
    # Editable prompt
    prompt = st.text_area(
        "分析提示詞 (可編輯)",
        value=st.session_state.workflow_state.stage1_prompt,
        height=200
    )
    st.session_state.workflow_state.stage1_prompt = prompt
    
    if st.button("🚀 生成策略分析", use_container_width=True):
        if not st.session_state.get("api_key") and not GEMINI_API_KEY:
            st.error("請先輸入 API Key")
            return
        
        try:
            api_key = st.session_state.get("api_key", GEMINI_API_KEY)
            workflow_service = WorkflowService(api_key)
            
            with st.spinner("正在生成策略分析..."):
                result = workflow_service.generate_strategy_report(
                    st.session_state.workflow_state.product_metadata,
                    prompt
                )
                st.session_state.workflow_state.strategy_report = result
                st.session_state.workflow_state.current_stage = max(2, st.session_state.workflow_state.current_stage)
            st.success("✅ 策略分析完成！")
        except Exception as e:
            st.error(f"生成失敗: {e}")
    
    # Display result
    if hasattr(st.session_state.workflow_state, 'strategy_report') and st.session_state.workflow_state.strategy_report:
        with st.expander("📊 策略分析結果", expanded=True):
            st.markdown(st.session_state.workflow_state.strategy_report)
            
            # Edit button
            if st.button("✏️ 編輯策略分析"):
                edited_report = st.text_area(
                    "編輯策略分析",
                    value=st.session_state.workflow_state.strategy_report,
                    height=300,
                    key="edit_strategy"
                )
                if st.button("💾 保存編輯", key="save_strategy"):
                    st.session_state.workflow_state.strategy_report = edited_report
                    st.success("✅ 已保存編輯")
                    st.rerun()

def render_stage_2():
    """Render Stage 2: Audience Targeting."""
    st.subheader("👥 階段 2: 受眾定向分析")
    
    if not st.session_state.workflow_state.strategy_report:
        st.warning("請先完成產品策略分析")
        return
    
    # Editable prompt
    prompt = st.text_area(
        "受眾分析提示詞 (可編輯)",
        value=st.session_state.workflow_state.stage2_prompt,
        height=200
    )
    st.session_state.workflow_state.stage2_prompt = prompt
    
    if st.button("🎯 生成受眾分析", use_container_width=True):
        try:
            api_key = st.session_state.get("api_key", GEMINI_API_KEY)
            workflow_service = WorkflowService(api_key)
            
            with st.spinner("正在生成受眾分析..."):
                result = workflow_service.generate_audience_targeting(
                    st.session_state.workflow_state.strategy_report,
                    prompt
                )
                st.session_state.workflow_state.audience_targeting = result
                st.session_state.workflow_state.current_stage = max(3, st.session_state.workflow_state.current_stage)
            st.success("✅ 受眾分析完成！")
        except Exception as e:
            st.error(f"生成失敗: {e}")
    
    # Display result
    if hasattr(st.session_state.workflow_state, 'audience_targeting') and st.session_state.workflow_state.audience_targeting:
        st.subheader("🎯 受眾分析結果")
        
        # Try to parse as table first
        table_data = parse_markdown_table(st.session_state.workflow_state.audience_targeting)
        
        if table_data is not None:
            # Display as HTML table with Markdown formatting
            render_table_with_markdown(table_data)
        else:
            # Fallback to markdown display
            st.markdown(st.session_state.workflow_state.audience_targeting)
        
        # Collapsible edit panel
        with st.expander("✏️ 編輯受眾分析", expanded=False):
            edited_audience = st.text_area(
                "編輯內容",
                value=st.session_state.workflow_state.audience_targeting,
                height=300,
                key="edit_audience"
            )
            if st.button("💾 保存編輯", key="save_audience"):
                st.session_state.workflow_state.audience_targeting = edited_audience
                st.success("✅ 已保存編輯")
                st.rerun()

def render_stage_3():
    """Render Stage 3: Ad Copy Generation."""
    st.subheader("✍️ 階段 3: 廣告文案生成")
    
    if not st.session_state.workflow_state.audience_targeting:
        st.warning("請先完成受眾定向分析")
        return
    
    # Editable prompt
    prompt = st.text_area(
        "文案生成提示詞 (可編輯)",
        value=st.session_state.workflow_state.stage3_prompt,
        height=200
    )
    st.session_state.workflow_state.stage3_prompt = prompt
    
    if st.button("📝 生成廣告文案", use_container_width=True):
        try:
            api_key = st.session_state.get("api_key", GEMINI_API_KEY)
            workflow_service = WorkflowService(api_key)
            
            with st.spinner("正在生成廣告文案..."):
                result = workflow_service.generate_ad_copy(
                    st.session_state.workflow_state.audience_targeting,
                    prompt
                )
                st.session_state.workflow_state.ad_copy_generation = result
                st.session_state.workflow_state.current_stage = max(4, st.session_state.workflow_state.current_stage)
            st.success("✅ 廣告文案完成！")
        except Exception as e:
            st.error(f"生成失敗: {e}")
    
    # Display result
    if hasattr(st.session_state.workflow_state, 'ad_copy_generation') and st.session_state.workflow_state.ad_copy_generation:
        st.subheader("📝 廣告文案結果")
        
        # Try to parse as table first
        table_data = parse_markdown_table(st.session_state.workflow_state.ad_copy_generation)
        
        if table_data is not None:
            # Display as HTML table with Markdown formatting
            render_table_with_markdown(table_data)
        else:
            # Fallback to markdown display
            st.markdown(st.session_state.workflow_state.ad_copy_generation)
        
        # Collapsible edit panel
        with st.expander("✏️ 編輯廣告文案", expanded=False):
            edited_copy = st.text_area(
                "編輯內容",
                value=st.session_state.workflow_state.ad_copy_generation,
                height=300,
                key="edit_copy"
            )
            if st.button("💾 保存編輯", key="save_copy"):
                st.session_state.workflow_state.ad_copy_generation = edited_copy
                st.success("✅ 已保存編輯")
                st.rerun()

def render_stage_4():
    """Render Stage 4: Creative Generation."""
    st.subheader("🎨 階段 4: 創意設計生成")
    
    if not st.session_state.workflow_state.ad_copy_generation:
        st.warning("請先完成廣告文案生成")
        return
    
    # Editable prompt
    prompt = st.text_area(
        "創意設計提示詞 (可編輯)",
        value=st.session_state.workflow_state.stage4_prompt,
        height=200
    )
    st.session_state.workflow_state.stage4_prompt = prompt
    
    if st.button("🎨 生成廣告創意", use_container_width=True):
        try:
            api_key = st.session_state.get("api_key", GEMINI_API_KEY)
            workflow_service = WorkflowService(api_key)
            
            # Generate creative concepts with images in one step
            with st.spinner("正在生成創意概念與圖片..."):
                result = workflow_service.generate_creative_concepts_with_images(
                    st.session_state.workflow_state.strategy_report,
                    st.session_state.workflow_state.audience_targeting,
                    st.session_state.workflow_state.ad_copy_generation,
                    prompt,
                    st.session_state.workflow_state.product_metadata.image_url
                )
                st.session_state.workflow_state.ad_creative_generation = result
                st.success("✅ 廣告創意完成！")
                    
        except Exception as e:
            st.error(f"生成失敗: {e}")
    
    # Display creative concepts
    if hasattr(st.session_state.workflow_state, 'ad_creative_generation') and st.session_state.workflow_state.ad_creative_generation:
        st.subheader("🎨 創意概念結果")
        
        # Try to parse as table first
        table_data = parse_markdown_table(st.session_state.workflow_state.ad_creative_generation)
        
        if table_data is not None:
            # Display as HTML table with Markdown formatting
            render_table_with_markdown(table_data)
        else:
            # Fallback to markdown display
            st.markdown(st.session_state.workflow_state.ad_creative_generation, unsafe_allow_html=True)
        
        # Collapsible edit panel
        with st.expander("✏️ 編輯創意概念", expanded=False):
            edited_creative = st.text_area(
                "編輯內容",
                value=st.session_state.workflow_state.ad_creative_generation,
                height=300,
                key="edit_creative"
            )
            if st.button("💾 保存編輯", key="save_creative"):
                st.session_state.workflow_state.ad_creative_generation = edited_creative
                st.success("✅ 已保存編輯")
                st.rerun()
    

def app():
    st.set_page_config(
        page_title="Meta Ad Creatives AI - 4-Stage Workflow",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Meta Ad Creatives AI")
    st.markdown("**4階段智能廣告創意生成系統**")
    
    # Initialize workflow state
    initialize_workflow_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ 系統設定")
        api_key = st.text_input(
            "Gemini API Key",
            value=GEMINI_API_KEY,
            type="password",
            help="請輸入您的 Google Gemini API Key"
        )
        st.session_state.api_key = api_key if api_key else GEMINI_API_KEY
        
        st.markdown("---")
        st.header("📋 流程說明")
        st.markdown("""
        **階段 1:** 產品策略分析  
        **階段 2:** 受眾定向分析  
        **階段 3:** 廣告文案生成  
        **階段 4:** 創意設計生成
        """)
        
        if st.button("📄 導出完整報告"):
            # Export complete workflow as JSON
            workflow_dict = st.session_state.workflow_state.dict() if hasattr(st.session_state.workflow_state, 'dict') else {}
            st.download_button(
                "💾 下載 JSON 報告",
                data=json.dumps(workflow_dict, ensure_ascii=False, indent=2),
                file_name="meta_ad_workflow_report.json",
                mime="application/json"
            )
    
    # Progress indicator
    render_stage_progress()
    st.markdown("---")
    
    # Product input (always visible)
    render_product_input()
    st.markdown("---")
    
    # Render current and completed stages
    render_stage_1()
    st.markdown("---")
    render_stage_2()
    st.markdown("---")
    render_stage_3()
    st.markdown("---")
    render_stage_4()
    
    # Footer
    st.markdown("---")
    st.caption("🤖 Meta Ad Creatives AI · 4-Stage Workflow · Powered by Google Gemini")

if __name__ == "__main__":
    app()

