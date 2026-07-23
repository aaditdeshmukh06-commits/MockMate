import streamlit as st


def show_reports():

    st.title("📊 Interview Reports")

    st.divider()

    st.metric("Overall Score", "89%")

    st.metric("Communication", "91%")

    st.metric("Technical", "84%")

    st.metric("Confidence", "88%")

    st.divider()

    st.subheader("AI Suggestions")

    st.success("✔ Speak a little slower.")

    st.success("✔ Maintain eye contact.")

    st.success("✔ Give more structured answers.")

    st.button("Download Report")