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
                best_suggestion,score,trend_score,kw,sentiment_score,x = get_suggestions(post,group_id,image)
            elif video:
                best_suggestion,score,trend_score,kw,sentiment_score,x = get_suggestions(post,group_id,False,True)
            else:
                best_suggestion,score,trend_score,kw,sentiment_score,x = get_suggestions(post,group_id,False,False)
        elif group_id and image:
            st.write("No text in post is a bad idea. Try again")

        try:

            image_type_dict = {1:'Meme',-1:'Infographic/Graphs/Chart',0 : 'Other'}

            question_mark = 'Yes' if x[1] == 1 else "No"
            hashtag_count = x[2]
            url_check = 'Yes' if x[3] == 1 else "No"
            word_count = x[5]
            image_status = 'Yes' if x[8] == 1 else "No"
            image_type = image_type_dict[x[9]]
            video_status = 'Yes' if x[10] == 1 else "No"


            st.header(f"Current Post Score: {round(score*1000,5)}")
            c1, c2 = st.beta_columns((1, 2))
            c1.subheader(f"Suggestions :")
            for i in range(len(best_suggestion)):
                c2.subheader(f"{i+1}. {best_suggestion[i]}")
            st.markdown("***")
            c3, c4 = st.beta_columns((1, 1))
            c3.subheader(f"Question in post:  {question_mark}")
            c3.subheader(f"Number of Hashtags:  {hashtag_count}")
            c3.subheader(f"Links and URLs in post:  {url_check}")
            c3.subheader(f"Word count:  {word_count}")
            c3.subheader(f"Trend Score: {trend_score}")
            c3.subheader(f"Sentiment Score: {sentiment_score}")
            df = pd.DataFrame({'Keywords extracted for trends':kw})
            c4.dataframe(df)
            if image_status == 'Yes':
                c4.subheader(f"Image:")
                c4.image(image,width=400) # Manually Adjust the width of the image as per requirement
                c4.subheader(f"Image Type: {image_type}")
            else:
                c4.subheader(f"Image: No")
            if video_status == 'Yes':
                c4.subheader(f"Video link:")
                c4.markdown(video, unsafe_allow_html=True)

        
            #c5, c6 = st.beta_columns((1, 2))
            #c5.subheader(f"Sentiment Score: {sentiment_score}")
        except Exception as e:
            st.write(e)



