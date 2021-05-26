import streamlit as st
from suggestion_predictor import get_suggestions
import pandas as pd
def content_main():


    group_id = st.selectbox("Select the group_id of the group you want to post to",
     ['143322019583033','546588969267691','InsaneTech','pypcom'])

    post = st.text_area('Input your post content here')
    image = st.text_input('Enter the URL of any image you want to add to your post') 
    video = st.text_input('Enter the URL of any video you want to add to your post') 

    if st.button("Click to get post analysis and content suggestions"):
        if group_id and post:
            if image:
                best_suggestion,score,trend_score,kw,sentiment_score = get_suggestions(post,group_id,image)
            elif video:
                best_suggestion,score,trend_score,kw,sentiment_score = get_suggestions(post,group_id,False,True)
            else:
                best_suggestion,score,trend_score,kw,sentiment_score = get_suggestions(post,group_id,False,False)
        elif group_id and image:
            st.write("No text in post is a bad idea. Try again")

        try:
            st.header(f"Current Post Score: {round(score*1000,5)}")
            c1, c2 = st.beta_columns((1, 2))
            c1.subheader(f"Suggestion :")
            c2.subheader(f"{best_suggestion}")
            st.markdown("***")
            c3, c4 = st.beta_columns((1, 2))
            c3.subheader(f"Trend Score: {trend_score}")
            c3.subheader(f"Sentiment Score: {sentiment_score}")
            df = pd.DataFrame({'Keywords extracted for trends':kw})
            c4.dataframe(df)
            #c5, c6 = st.beta_columns((1, 2))
            #c5.subheader(f"Sentiment Score: {sentiment_score}")
        except Exception as e:
            st.write(e)



