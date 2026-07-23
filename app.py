import streamlit as st

# ==========================================
# IMPORT PAGES
# ==========================================

from pages.dashboard import show_dashboard
from pages.interview import show_interview
from pages.reports import show_reports
from pages.settings import show_settings

# ==========================================
# LOAD CSS
# ==========================================

def load_css():
    with open("styles/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MockMate",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🎤 MockMate")

    st.caption("Practice. Improve. Get Hired.")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🎤 Interview",
            "📊 Reports",
            "⚙ Settings"
        ]
    )

    st.divider()

    st.success("🟢 System Ready")

    st.caption("Version 1.0")

# ==========================================
# PAGE ROUTING
# ==========================================

if page == "🏠 Dashboard":
    show_dashboard()

elif page == "🎤 Interview":
    show_interview()

elif page == "📊 Reports":
    show_reports()

elif page == "⚙ Settings":
    show_settings()