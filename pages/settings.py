import streamlit as st


def show_settings():
    st.title("⚙ Settings")
    st.divider()

    st.selectbox(
        "Language",
        [
            "English",
            "Hindi",
            "English + Hindi"
        ]
    )
    st.selectbox(
        "Interview Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )
    st.checkbox("Enable Camera")
    st.checkbox("Enable Microphone")
    st.checkbox("Dark Mode (Coming Soon)")
