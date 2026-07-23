import streamlit as st
import plotly.graph_objects as go


def show_interview():
    st.title("🎤 Interview Room")
    st.markdown(
        '<span class="mm-live-dot"></span> **Live Session in Progress**',
        unsafe_allow_html=True
    )
    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Question")
        st.write("Tell me about yourself.")
        st.text_area(
            "Your Answer",
            height=220
        )
        st.button("Submit Answer")

    with right:
        st.subheader("Interview Status")
        st.metric("Question", "1 / 10")
        st.metric("Time Left", "24:52")
        st.progress(10)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=10,
            number={'suffix': "%"},
            title={'text': "Interview Progress"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#2563EB'},
                'steps': [
                    {'range': [0, 40], 'color': '#DBEAFE'},
                    {'range': [40, 75], 'color': '#93C5FD'},
                    {'range': [75, 100], 'color': '#60A5FA'}
                ]
            }
        ))
        fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.write("Camera")
        st.empty()
