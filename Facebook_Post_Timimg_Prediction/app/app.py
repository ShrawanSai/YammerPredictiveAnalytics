import streamlit as st
import post_timing_analysis
from content_analysis import content_main


def main():
    st.title("Alpha AI")


if __name__ == '__main__':
    main()

    # Sidebar
    activities = ["Home", "Yammer Post Content Analysis",
                  "Posts Timing Recommendation"]
    choice = st.sidebar.selectbox("Choose Activity", activities)

    if choice == "Home":
        st.header('Employee Engagement Solved')
        st.subheader('Having trouble deciding on what time to post your message? Or still deciding what your message should include for Better Engagement?')
        st.subheader('We\'ve got you covered!')


    if choice == "Posts Timing Recommendation":
        post_timing_analysis.main()

    if choice == "Yammer Post Content Analysis":
        content_main()
   
