import streamlit as st


def get_theme():

    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    return st.session_state.theme


def toggle_theme():

    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"


def get_colors():

    theme = get_theme()

    if theme == "dark":

        return {
            "background": "#0F172A",
            "card": "#1E293B",
            "text": "#F8FAFC",
            "secondary": "#94A3B8",
            "primary": "#3B82F6"
        }

    else:

        return {
            "background": "#F8FAFC",
            "card": "#FFFFFF",
            "text": "#111827",
            "secondary": "#6B7280",
            "primary": "#2563EB"
        }