import os
import json
import re
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from src.models.workflow import WorkflowState
from src.services.workflow_service import WorkflowService
from src.utils.text_utils import clean_product_text, parse_markdown_table

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _get_service() -> Optional[WorkflowService]:
    api_key = st.session_state.get("api_key", GEMINI_API_KEY)
    if not api_key:
        st.error("請先在側邊欄輸入 Gemini API Key")
        return None
    return WorkflowService(api_key)


def render_table_with_markdown(table_dict: dict) -> None:
    html = "<table style='width:100%; border-collapse: collapse;'><thead><tr>"
    for col in table_dict["headers"]:
        html += f"<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>{col}</th>"
    html += "</tr></thead><tbody>"
    for row in table_dict["data"]:
        html += "<tr>"
        for cell in row:
            cell_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(cell))
            cell_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', cell_html)
            html += f"<td style='border: 1px solid #ddd; padding: 8px; vertical-align: top;'>{cell_html}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reusable dialog
# ---------------------------------------------------------------------------

def _edit_dialog_body(state_key: str, label: str) -> None:
    current = getattr(st.session_state.workflow_state, state_key)
    new_val = st.text_area(label, value=current, height=450)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 儲存", use_container_width=True, type="primary"):
            setattr(st.session_state.workflow_state, state_key, new_val)
            st.rerun()
    with col2:
        if st.button("取消", use_container_width=True):
            st.rerun()


@st.dialog("編輯提示詞", width="large")
def prompt_editor_dialog(stage_key: str, label: str):
    _edit_dialog_body(stage_key, label)


@st.dialog("編輯內容", width="large")
def result_editor_dialog(state_key: str, label: str):
    _edit_dialog_body(state_key, label)


# ---------------------------------------------------------------------------
# Reusable UI components
# ---------------------------------------------------------------------------

def render_prompt_section(stage_key: str, label: str, button_key: str) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"提示詞: {getattr(st.session_state.workflow_state, stage_key)[:80]}…")
    with col2:
        if st.button("✏️ 編輯提示詞", key=button_key, use_container_width=True):
            prompt_editor_dialog(stage_key, label)


def render_editable_result(state_key: str, subheader: str, expander_label: str,
                           edit_key: str, unsafe_allow_html: bool = False) -> None:
    result = getattr(st.session_state.workflow_state, state_key, None)
    if not result:
        return
    st.subheader(subheader)
    table_data = parse_markdown_table(result)
    if table_data is not None:
        render_table_with_markdown(table_data)
    else:
        st.markdown(result, unsafe_allow_html=unsafe_allow_html)
    with st.expander(expander_label, expanded=False):
        edited = st.text_area("編輯內容", value=result, height=300, key=f"edit_{edit_key}")
        if st.button("💾 保存編輯", key=f"save_{edit_key}"):
            setattr(st.session_state.workflow_state, state_key, edited)
            st.success("✅ 已保存編輯")
            st.rerun()


# ---------------------------------------------------------------------------
# Page-level components
# ---------------------------------------------------------------------------

def initialize_workflow_state() -> None:
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = WorkflowState()


def render_stage_progress() -> None:
    stages = ["產品分析", "受眾定向", "廣告文案", "創意設計"]
    current = st.session_state.workflow_state.current_stage
    cols = st.columns(4)
    for i, (col, stage) in enumerate(zip(cols, stages), 1):
        with col:
            if i < current:
                st.success(f"✅ {i}. {stage}")
            elif i == current:
                st.info(f"🔄 {i}. {stage}")
            else:
                st.write(f"⏳ {i}. {stage}")


def render_product_input() -> None:
    st.subheader("📦 產品資料")
    product_url = st.text_input(
        "產品網址",
        placeholder="https://www.nike.com/tw/product-page",
        value=st.session_state.workflow_state.product_url or ""
    )

    col1, col2 = st.columns(2)
    with col1:
        extract_btn = st.button("📝 提取產品資料", use_container_width=True)
    with col2:
        if st.button("🔄 重置流程", use_container_width=True):
            st.session_state.workflow_state = WorkflowState()
            st.rerun()

    if extract_btn and product_url:
        svc = _get_service()
        if svc:
            try:
                with st.spinner("正在提取產品資料..."):
                    metadata = svc.extract_product_metadata(product_url)
                    st.session_state.workflow_state.product_metadata = metadata
                    st.session_state.workflow_state.product_url = product_url
                    st.session_state.workflow_state.current_stage = 1
                st.success("✅ 產品資料提取完成！")
                st.rerun()
            except Exception as e:
                st.error(f"提取失敗: {e}")

    metadata = st.session_state.workflow_state.product_metadata
    if not metadata:
        return

    with st.expander("📋 已提取的產品資料", expanded=True):
        st.markdown("""
            <style>
            .product-text {
                word-wrap: break-word; word-break: break-word;
                overflow-wrap: break-word; white-space: normal;
                max-width: 100%; line-height: 1.4;
            }
            </style>
        """, unsafe_allow_html=True)

        def md(label: str, value: str) -> None:
            st.markdown(f'<div class="product-text"><strong>{label}:</strong> {value}</div>',
                        unsafe_allow_html=True)

        md("標題", clean_product_text(metadata.title))

        clean_desc = clean_product_text(metadata.description)
        if len(clean_desc) > 200:
            md("描述", clean_desc[:200] + "...")
            with st.expander("顯示完整描述", expanded=False):
                st.markdown(f'<div class="product-text">{clean_desc}</div>', unsafe_allow_html=True)
        else:
            md("描述", clean_desc)

        md("價格", clean_product_text(metadata.price) if metadata.price else "未提供")

        if metadata.usps:
            clean_usps = [clean_product_text(u) for u in metadata.usps if u.strip()]
            if clean_usps:
                md("特色", ', '.join(clean_usps[:3]))
                if len(clean_usps) > 3:
                    with st.expander("顯示所有特色", expanded=False):
                        for i, usp in enumerate(clean_usps, 1):
                            st.markdown(f'<div class="product-text">{i}. {usp}</div>', unsafe_allow_html=True)

        if metadata.image_url:
            st.image(metadata.image_url, caption="產品圖片", width=300)


# ---------------------------------------------------------------------------
# Stage renderers
# ---------------------------------------------------------------------------

def render_stage_1() -> None:
    st.subheader("🎯 階段 1: 產品策略分析")
    if not st.session_state.workflow_state.product_metadata:
        st.warning("請先提取產品資料")
        return

    render_prompt_section("stage1_prompt", "階段 1 分析提示詞", "edit_prompt_1")

    if st.button("🚀 生成策略分析", use_container_width=True):
        svc = _get_service()
        if svc:
            try:
                with st.spinner("正在生成策略分析..."):
                    result = svc.generate_strategy_report(
                        st.session_state.workflow_state.product_metadata,
                        st.session_state.workflow_state.stage1_prompt
                    )
                    st.session_state.workflow_state.strategy_report = result
                    st.session_state.workflow_state.current_stage = max(2, st.session_state.workflow_state.current_stage)
                st.success("✅ 策略分析完成！")
            except Exception as e:
                st.error(f"生成失敗: {e}")

    if st.session_state.workflow_state.strategy_report:
        with st.expander("📊 策略分析結果", expanded=True):
            st.markdown(st.session_state.workflow_state.strategy_report)
            if st.button("✏️ 編輯結果", key="edit_result_1"):
                result_editor_dialog("strategy_report", "策略分析結果")


def render_stage_2() -> None:
    st.subheader("👥 階段 2: 受眾定向分析")
    if not st.session_state.workflow_state.strategy_report:
        st.warning("請先完成產品策略分析")
        return

    render_prompt_section("stage2_prompt", "受眾分析提示詞", "edit_prompt_2")

    if st.button("🎯 生成受眾分析", use_container_width=True):
        svc = _get_service()
        if svc:
            try:
                with st.spinner("正在生成受眾分析..."):
                    result = svc.generate_audience_targeting(
                        st.session_state.workflow_state.strategy_report,
                        st.session_state.workflow_state.stage2_prompt
                    )
                    st.session_state.workflow_state.audience_targeting = result
                    st.session_state.workflow_state.current_stage = max(3, st.session_state.workflow_state.current_stage)
                st.success("✅ 受眾分析完成！")
            except Exception as e:
                st.error(f"生成失敗: {e}")

    render_editable_result("audience_targeting", "🎯 受眾分析結果", "✏️ 編輯受眾分析", "audience")


def render_stage_3() -> None:
    st.subheader("✍️ 階段 3: 廣告文案生成")
    if not st.session_state.workflow_state.audience_targeting:
        st.warning("請先完成受眾定向分析")
        return

    render_prompt_section("stage3_prompt", "文案生成提示詞", "edit_prompt_3")

    if st.button("📝 生成廣告文案", use_container_width=True):
        svc = _get_service()
        if svc:
            try:
                with st.spinner("正在生成廣告文案..."):
                    result = svc.generate_ad_copy(
                        st.session_state.workflow_state.audience_targeting,
                        st.session_state.workflow_state.stage3_prompt
                    )
                    st.session_state.workflow_state.ad_copy_generation = result
                    st.session_state.workflow_state.current_stage = max(4, st.session_state.workflow_state.current_stage)
                st.success("✅ 廣告文案完成！")
            except Exception as e:
                st.error(f"生成失敗: {e}")

    render_editable_result("ad_copy_generation", "📝 廣告文案結果", "✏️ 編輯廣告文案", "copy")


def render_stage_4() -> None:
    st.subheader("🎨 階段 4: 創意設計生成")
    if not st.session_state.workflow_state.ad_copy_generation:
        st.warning("請先完成廣告文案生成")
        return

    render_prompt_section("stage4_prompt", "創意設計提示詞", "edit_prompt_4")

    if st.button("🎨 生成廣告創意", use_container_width=True):
        svc = _get_service()
        if svc:
            try:
                state = st.session_state.workflow_state
                with st.spinner("正在生成創意概念與圖片..."):
                    result = svc.generate_creative_concepts_with_images(
                        state.strategy_report,
                        state.audience_targeting,
                        state.ad_copy_generation,
                        state.stage4_prompt,
                        state.product_metadata.image_url
                    )
                    state.ad_creative_generation = result
                st.success("✅ 廣告創意完成！")
            except Exception as e:
                st.error(f"生成失敗: {e}")

    render_editable_result(
        "ad_creative_generation", "🎨 創意概念結果", "✏️ 編輯創意概念",
        "creative", unsafe_allow_html=True
    )


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------

def app() -> None:
    st.set_page_config(
        page_title="Meta Ad Creatives AI - 4-Stage Workflow",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🚀 Meta Ad Creatives AI")
    st.markdown("**4階段智能廣告創意生成系統**")

    initialize_workflow_state()

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
        st.markdown(
            "**階段 1:** 產品策略分析  \n"
            "**階段 2:** 受眾定向分析  \n"
            "**階段 3:** 廣告文案生成  \n"
            "**階段 4:** 創意設計生成"
        )

        if st.button("📄 導出完整報告"):
            workflow_dict = st.session_state.workflow_state.dict() if hasattr(st.session_state.workflow_state, 'dict') else {}
            st.download_button(
                "💾 下載 JSON 報告",
                data=json.dumps(workflow_dict, ensure_ascii=False, indent=2),
                file_name="meta_ad_workflow_report.json",
                mime="application/json"
            )

    render_stage_progress()
    st.markdown("---")
    render_product_input()
    st.markdown("---")
    render_stage_1()
    st.markdown("---")
    render_stage_2()
    st.markdown("---")
    render_stage_3()
    st.markdown("---")
    render_stage_4()
    st.markdown("---")
    st.caption("🤖 Meta Ad Creatives AI · 4-Stage Workflow · Powered by Google Gemini")


if __name__ == "__main__":
    app()
