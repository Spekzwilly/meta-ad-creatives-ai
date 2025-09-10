import os
import io
import json
from typing import Optional

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

from src.models.workflow import WorkflowState, ProductMetadata
from src.services.workflow_service import WorkflowService

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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
            st.write(f"**標題:** {metadata.title}")
            st.write(f"**描述:** {metadata.description[:200]}...")
            st.write(f"**價格:** {metadata.price}")
            if metadata.usps:
                st.write(f"**特色:** {', '.join(metadata.usps[:3])}")
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
        with st.expander("🎯 受眾分析結果", expanded=True):
            st.markdown(st.session_state.workflow_state.audience_targeting)
            
            # Edit button
            if st.button("✏️ 編輯受眾分析"):
                edited_audience = st.text_area(
                    "編輯受眾分析",
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
        with st.expander("📝 廣告文案結果", expanded=True):
            st.markdown(st.session_state.workflow_state.ad_copy_generation)
            
            # Edit button
            if st.button("✏️ 編輯廣告文案"):
                edited_copy = st.text_area(
                    "編輯廣告文案",
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎨 生成創意概念", use_container_width=True):
            try:
                api_key = st.session_state.get("api_key", GEMINI_API_KEY)
                workflow_service = WorkflowService(api_key)
                
                with st.spinner("正在生成創意概念..."):
                    result = workflow_service.generate_creative_concepts(
                        st.session_state.workflow_state.strategy_report,
                        st.session_state.workflow_state.audience_targeting,
                        st.session_state.workflow_state.ad_copy_generation,
                        prompt
                    )
                    st.session_state.workflow_state.ad_creative_generation = result
                st.success("✅ 創意概念完成！")
            except Exception as e:
                st.error(f"生成失敗: {e}")
    
    with col2:
        if st.button("🖼️ 生成創意圖片", use_container_width=True):
            if hasattr(st.session_state.workflow_state, 'ad_creative_generation') and st.session_state.workflow_state.ad_creative_generation:
                try:
                    api_key = st.session_state.get("api_key", GEMINI_API_KEY)
                    workflow_service = WorkflowService(api_key)
                    
                    # Use the creative concepts as image generation prompt
                    image_prompt = f"基於以下創意概念，生成1000x1000的Meta廣告創意圖片：\n\n{st.session_state.workflow_state.ad_creative_generation}"
                    
                    with st.spinner("正在生成創意圖片..."):
                        result_img = workflow_service.generate_image_from_prompt(
                            st.session_state.workflow_state.product_metadata.image_url,
                            image_prompt
                        )
                        if result_img:
                            st.session_state.generated_image = result_img
                            st.success("✅ 創意圖片完成！")
                        else:
                            st.warning("圖片生成失敗")
                except Exception as e:
                    st.error(f"圖片生成失敗: {e}")
            else:
                st.warning("請先生成創意概念")
    
    # Display creative concepts
    if hasattr(st.session_state.workflow_state, 'ad_creative_generation') and st.session_state.workflow_state.ad_creative_generation:
        with st.expander("🎨 創意概念結果", expanded=True):
            st.markdown(st.session_state.workflow_state.ad_creative_generation)
    
    # Display generated image
    if "generated_image" in st.session_state and st.session_state.generated_image:
        st.subheader("🖼️ 生成的創意圖片")
        st.image(st.session_state.generated_image, caption="Generated Creative", use_container_width=True)
        
        # Download button
        buf = io.BytesIO()
        st.session_state.generated_image.save(buf, format="PNG")
        st.download_button(
            label="📥 下載 PNG",
            data=buf.getvalue(),
            file_name="meta_ad_creative.png",
            mime="image/png",
            use_container_width=True
        )

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

