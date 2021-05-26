import streamlit as st
import post_timing_analysis
from content_analysis import content_main

def main():
    st.title("Alpha AI")


if __name__ == '__main__':
    main()

    # Sidebar
    activities = ["Home", "Yammar Post Conent Analysis",
                  "Active Engagement Index",
                  "Posts Timing Recommendation"]
    choice = st.sidebar.selectbox("Choose Activity", activities)

    if choice == "Home":
        st.header(
            'Empowering companies to jumpstart AI and generate real-world value')
        st.subheader(
            'Use exponential technologies to your advantage and lead your industry with confidence through innovation.')

    if choice == "Posts Timing Recommendation":
        post_timing_analysis.main()

    if choice == "Yammar Post Conent Analysis":
        content_main()
