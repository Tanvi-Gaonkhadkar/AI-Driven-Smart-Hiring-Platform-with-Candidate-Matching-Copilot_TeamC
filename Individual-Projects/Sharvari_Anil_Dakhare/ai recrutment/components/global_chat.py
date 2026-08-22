"""
Global AI Assistant - a floating chat available on every page.
Includes dark-mode styles for top header buttons (Notification & Profile)
and aligns the AI chat to the bottom-right corner.
"""

import streamlit as st
import streamlit.components.v1 as components
from services import ai_service
from styles.theme import is_dark_mode

_GREETING = (
    "Hi! I'm your YourTalentPilot assistant. Ask me about hiring, resumes, candidates, or how to use any page here."
)

_CUSTOM_FAB_SCRIPT = """
<script>
(function () {
    function setupCustomFab() {
        try {
            var doc = window.parent.document;
            var body = doc.body;

            var existing = doc.getElementById('custom-ai-chat-fab');
            if (existing) existing.remove();

            var popovers = doc.querySelectorAll('div[data-testid="stPopover"]');
            var aiPopover = null;

            for (var i = 0; i < popovers.length; i++) {
                if (popovers[i].textContent.indexOf('✨ AI') !== -1) {
                    aiPopover = popovers[i];
                    break;
                }
            }

            if (!aiPopover) return;

            var nativeBtn = aiPopover.querySelector('button');
            if (nativeBtn) nativeBtn.style.setProperty('display', 'none', 'important');

            var fab = doc.createElement('button');
            fab.id = 'custom-ai-chat-fab';
            fab.innerHTML = '✨ AI';
            
            var saved = null;
            try { saved = JSON.parse(localStorage.getItem('ai_fab_pos') || 'null'); } catch (e) {}

            var defaultStyle = 
                'position: fixed !important; z-index: 999999 !important; ' +
                'width: 60px !important; height: 60px !important; border-radius: 50% !important; ' +
                'background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%) !important; ' +
                'color: #FFFFFF !important; font-weight: 800 !important; font-size: 15px !important; ' +
                'border: 1.5px solid rgba(167, 139, 250, 0.5) !important; ' +
                'box-shadow: 0 8px 24px rgba(109, 40, 217, 0.5) !important; ' +
                'cursor: grab !important; display: flex !important; align-items: center !important; justify-content: center !important;';

            fab.style.cssText = defaultStyle;

            if (saved && typeof saved.left === 'number' && typeof saved.top === 'number') {
                fab.style.left = saved.left + 'px';
                fab.style.top = saved.top + 'px';
            } else {
                fab.style.bottom = '24px';
                fab.style.right = '24px';
            }

            body.appendChild(fab);

            var dragging = false, moved = false, startX, startY, origLeft, origTop;

            fab.addEventListener('pointerdown', function (e) {
                dragging = true;
                moved = false;
                var rect = fab.getBoundingClientRect();
                origLeft = rect.left;
                origTop = rect.top;
                startX = e.clientX;
                startY = e.clientY;
                try { fab.setPointerCapture(e.pointerId); } catch (err) {}
            });

            fab.addEventListener('pointermove', function (e) {
                if (!dragging) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                if (Math.abs(dx) > 4 || Math.abs(dy) > 4) moved = true;
                if (moved) {
                    var vw = doc.defaultView.innerWidth;
                    var vh = doc.defaultView.innerHeight;
                    var newLeft = Math.max(8, Math.min(vw - 68, origLeft + dx));
                    var newTop = Math.max(8, Math.min(vh - 68, origTop + dy));
                    fab.style.left = newLeft + 'px';
                    fab.style.top = newTop + 'px';
                    fab.style.right = 'auto';
                    fab.style.bottom = 'auto';
                }
            });

            fab.addEventListener('pointerup', function (e) {
                if (!dragging) return;
                dragging = false;
                if (moved) {
                    var rect = fab.getBoundingClientRect();
                    try { localStorage.setItem('ai_fab_pos', JSON.stringify({ left: rect.left, top: rect.top })); } catch (e) {}
                } else {
                    if (nativeBtn) nativeBtn.click();
                }
            });

        } catch (err) {}
    }

    setupCustomFab();
    setTimeout(setupCustomFab, 400);
})();
</script>
"""


def _ensure_state():
    if "global_chat_messages" not in st.session_state:
        st.session_state["global_chat_messages"] = [{"role": "assistant", "content": _GREETING}]


def render_global_chat():
    _ensure_state()

    is_dark = is_dark_mode()

    border_col = "rgba(167, 139, 250, 0.4)" if is_dark else "rgba(124, 58, 237, 0.2)"
    panel_bg = "#120C24" if is_dark else "#FFFFFF"
    title_color = "#E9D5FF" if is_dark else "#5B21B6"
    text_main = "#F8FAFC" if is_dark else "#0F172A"
    sub_text = "#C084FC" if is_dark else "#6D28D9"

    action_btn_text = "#E9D5FF" if is_dark else "#5B21B6"
    action_btn_hover = "rgba(255, 255, 255, 0.05)" if is_dark else "rgba(0, 0, 0, 0.04)"

    st.markdown(
        f"""
        <style>
            /* 1. HEADER BUTTONS STYLING (NOTIFICATION & PROFILE) */
            header div[data-testid="stPopover"] > button,
            div[data-testid="stHeader"] div[data-testid="stPopover"] > button {{
                background: {"rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.04)"} !important;
                border: 1px solid {border_col} !important;
                color: {text_main} !important;
                border-radius: 12px !important;
                padding: 6px 14px !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                box-shadow: none !important;
                transition: all 0.2s ease !important;
            }}

            header div[data-testid="stPopover"] > button:hover,
            div[data-testid="stHeader"] div[data-testid="stPopover"] > button:hover {{
                background: {"rgba(124, 58, 237, 0.25)" if is_dark else "rgba(124, 58, 237, 0.12)"} !important;
                border-color: {title_color} !important;
            }}

            header div[data-testid="stPopover"] > button *,
            div[data-testid="stHeader"] div[data-testid="stPopover"] > button * {{
                color: {text_main} !important;
                fill: {text_main} !important;
            }}

            /* 2. ALIGN EXPANDED POPOVER CHAT BOX TO BOTTOM-RIGHT */
            div[data-baseweb="popover"] {{
                position: fixed !important;
                right: 24px !important;
                left: auto !important;
                bottom: 90px !important;
                top: auto !important;
                z-index: 999998 !important;
                transform: none !important;
            }}

            div[data-testid="stPopoverBody"],
            div[data-testid="stPopoverBody"] *,
            div[data-baseweb="popover"] > div {{
                background-color: {panel_bg} !important;
                color: {text_main} !important;
            }}

            div[data-testid="stPopoverBody"] {{
                border: 1.5px solid {border_col} !important;
                border-radius: 20px !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4) !important;
                width: 380px !important;
                max-width: calc(100vw - 32px) !important;
                padding: 16px !important;
            }}

            .global-chat-title {{
                font-family: 'Space Grotesk', system-ui, sans-serif;
                font-size: 17px;
                font-weight: 800;
                color: {title_color} !important;
            }}

            .global-chat-sub {{
                font-size: 12px;
                font-weight: 600;
                color: {sub_text} !important;
            }}

            /* UNHIGHLIGHTED NEW CHAT & CLEAR BUTTONS */
            div[data-testid="stPopoverBody"] .stButton > button {{
                background: transparent !important;
                border: 1px solid {border_col} !important;
                box-shadow: none !important;
                border-radius: 10px !important;
                padding: 6px 12px !important;
                transition: background 0.2s ease !important;
            }}

            div[data-testid="stPopoverBody"] .stButton > button *,
            div[data-testid="stPopoverBody"] .stButton > button p,
            div[data-testid="stPopoverBody"] .stButton > button span {{
                color: {action_btn_text} !important;
                font-weight: 600 !important;
                font-size: 13px !important;
            }}

            div[data-testid="stPopoverBody"] .stButton > button:hover {{
                background: {action_btn_hover} !important;
                border-color: {border_col} !important;
            }}

            /* Transparent Message & Input Areas */
            div[data-testid="stChatMessage"] {{
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }}

            div[data-testid="stChatInput"] {{
                background-color: transparent !important;
                border: 1px solid {border_col} !important;
                border-radius: 12px !important;
                box-shadow: none !important;
            }}

            div[data-testid="stChatInput"] textarea {{
                color: {text_main} !important;
                background: transparent !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Inject Custom Floating Action Button
    components.html(_CUSTOM_FAB_SCRIPT, height=0, width=0)

    # Native Popover container triggered by custom Floating Button
    with st.popover("✨ AI"):
        st.markdown(
            f"""
            <div style="margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid {border_col};">
                <div class="global-chat-title">✨ AI HR Copilot</div>
                <div class="global-chat-sub">Talent & Recruitment Specialist</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Chat", key="pop_new_chat", use_container_width=True):
                st.session_state["global_chat_messages"] = [
                    {"role": "assistant", "content": "New chat started. How can I help?"}
                ]
                st.rerun()
        with col2:
            if st.button("🗑️ Clear", key="pop_clear_chat", use_container_width=True):
                st.session_state["global_chat_messages"] = []
                st.rerun()

        st.divider()

        if not ai_service.is_configured():
            st.caption("⚠️ Add a Gemini API key (or set AI_PROVIDER=ollama) in `.env` to enable the assistant.")

        for msg in st.session_state["global_chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask about hiring, resumes, roles...", key="pop_chat_input")
        if user_msg:
            question = user_msg.strip()
            prior_history = list(st.session_state["global_chat_messages"])
            st.session_state["global_chat_messages"].append({"role": "user", "content": question})

            with st.spinner("Analyzing pipeline..."):
                try:
                    reply = ai_service.global_assistant_chat(prior_history, question)
                except ai_service.AIServiceError as e:
                    reply = f"Sorry, I ran into an error: {e}"

            st.session_state["global_chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()