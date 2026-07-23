import streamlit as st
import plotly.graph_objects as go


def show_dashboard():
    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    st.title("👋 Welcome, Aadit!")
    st.caption("AI Powered Mock Interview Platform")
    st.divider()

    # -------------------------------------------------
    # DASHBOARD METRICS
    # -------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "🎤 Interviews Conducted",
            "12",
            "+2 this week"
        )
    with col2:
        st.metric(
            "⭐ Average Score",
            "87%",
            "+5%"
        )
    with col3:
        st.metric(
            "💬 Confidence",
            "91%",
            "+3%"
        )
    with col4:
        st.metric(
            "🎯 Candidate Level",
            "Intermediate",
            "Improving"
        )
    st.divider()

    # -------------------------------------------------
    # PERFORMANCE OVERVIEW (NEW DIAGRAMS)
    # -------------------------------------------------
    st.subheader("📈 Performance Overview")
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        categories = ["Technical", "Communication", "Confidence", "Problem Solving", "Body Language"]
        values = [88, 85, 91, 90, 78]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.25)',
            line=dict(color='#2563EB', width=2),
            name='Skill Score'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False,
            margin=dict(l=30, r=30, t=30, b=30),
            height=340,
            title="Skill Breakdown"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with chart_col2:
        interview_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        scores = [62, 65, 70, 68, 74, 77, 80, 79, 84, 86, 85, 87]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=interview_numbers,
            y=scores,
            mode='lines+markers',
            line=dict(color='#22C55E', width=3, shape='spline'),
            marker=dict(size=7, color='#22C55E'),
            fill='tozeroy',
            fillcolor='rgba(34, 197, 94, 0.12)'
        ))
        fig_trend.update_layout(
            margin=dict(l=30, r=30, t=30, b=30),
            height=340,
            title="Score Trend Over Time",
            xaxis_title="Interview #",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    # -------------------------------------------------
    # QUICK ACTIONS
    # -------------------------------------------------
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "🎤 Start Interview",
            use_container_width=True
        )
    with col2:
        st.button(
            "📄 View Reports",
            use_container_width=True
        )
    with col3:
        st.button(
            "⚙ Settings",
            use_container_width=True
        )
    st.divider()

    # -------------------------------------------------
    # INTERVIEW HISTORY
    # -------------------------------------------------
    st.subheader("📝 Interview History")
    interviews = [
        {
            "role": "Software Engineer",
            "score": "92%",
            "action": "🔄 Practice Again",
            "strength": "Strong problem-solving and technical knowledge.",
            "improvement": "Provide more real-world project examples."
        },
        {
            "role": "Embedded Engineer",
            "score": "88%",
            "action": "🔄 Practice Again",
            "strength": "Excellent understanding of embedded systems.",
            "improvement": "Improve confidence while explaining projects."
        },
        {
            "role": "Data Analyst",
            "score": "84%",
            "action": "🔄 Practice Again",
            "strength": "Good analytical thinking and communication.",
            "improvement": "Strengthen SQL and data visualization answers."
        },
        {
            "role": "HR Interview",
            "score": "--",
            "action": "▶ Start",
            "strength": "",
            "improvement": ""
        }
    ]
    for i, interview in enumerate(interviews, start=1):
        row1, row2, row3 = st.columns([5, 1, 2])
        with row1:
            st.markdown(
                f"**{i}. {interview['role']}**"
            )
        with row2:
            st.markdown(
                f"**{interview['score']}**"
            )
        with row3:
            st.button(
                interview["action"],
                key=f"action_{i}",
                use_container_width=True
            )
        if interview["action"] == "🔄 Practice Again":
            with st.expander("🧠 AI Summary"):
                st.markdown("### AI Performance Summary")
                st.success(
                    f"**Strength**\n\n{interview['strength']}"
                )
                st.warning(
                    f"**Needs Improvement**\n\n{interview['improvement']}"
                )
                st.info(
                    """
**AI Recommendation**
• Give more quantified achievements.
• Maintain better eye contact.
• Structure answers using the STAR method.
                    """
                )
        st.divider()
