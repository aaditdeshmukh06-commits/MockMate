import streamlit as st


def show_interview():

    st.title("🎤 Interview Room")

    st.info("This is where the AI interview will take place.")

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

        st.write("Camera")

        st.empty()