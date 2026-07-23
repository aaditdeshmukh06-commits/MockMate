import streamlit as st


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