import streamlit as st
import plotly.graph_objects as go


def show_reports():
    st.title("📊 Interview Reports")
    st.divider()

    st.metric("Overall Score", "89%")
    st.metric("Communication", "91%")
    st.metric("Technical", "84%")
    st.metric("Confidence", "88%")
    st.divider()

    # -------------------------------------------------
    # VISUAL SUMMARY (NEW DIAGRAMS)
    # -------------------------------------------------
    st.subheader("📈 Visual Summary")
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=89,
            delta={'reference': 84},
            title={'text': "Overall Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#22C55E'},
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 80], 'color': '#FEF9C3'},
                    {'range': [80, 100], 'color': '#DCFCE7'}
                ]
            }
        ))
        fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with chart_col2:
        categories = ["Communication", "Technical", "Confidence", "Clarity"]
        values = [91, 84, 88, 86]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.25)',
            line=dict(color='#2563EB', width=2)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=30, r=30, t=30, b=30),
            height=320,
            title="Score Breakdown"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    st.subheader("AI Suggestions")
    st.success("✔ Speak a little slower.")
    st.success("✔ Maintain eye contact.")
    st.success("✔ Give more structured answers.")
    st.button("Download Report")
