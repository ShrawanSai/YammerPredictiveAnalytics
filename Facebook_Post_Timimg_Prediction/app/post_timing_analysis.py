import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import numpy as np
from collections import OrderedDict
from time import sleep


from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from scipy.stats import spearmanr, pearsonr
from datetime import date
from datetime import datetime, timedelta


def main():

    def file_selector(folder_path='./dataset'):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox("Select A File", filenames)
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()  # Fetching the Dataset
    #st.info("You Selected {}".format(filename))

    # Read Dataset
    df = pd.read_csv(filename, delimiter=';')

    if st.checkbox("Show Dataset"):
        number = st.number_input("Rows", 5, 100)
        st.dataframe(df.head(number))

    st.subheader("Data Visualizations")
    # Corelation Plot
    # Seaborn Plot
    # Count Plot
    # Pie Chart

    # Scatter Plot Distribution
    if st.checkbox("Select Features  to explore Relation using Pair Plot"):
        all_cols = df.columns.tolist()
        Selected_cols = st.multiselect(
            "Select", all_cols, key='col_corelation')
        fig = px.scatter_matrix(
            df, dimensions=Selected_cols, color=all_cols[1])
        st.plotly_chart(fig)

    if st.button("Genearte Weekday Analytics"):
        sns.set_style("whitegrid")

        f, ax = plt.subplots()
        sns.countplot(df['Post Weekday'], palette='viridis')
        handles = ["Su", "M", "Tu", "W", "Th", "F", 'Sa']
        labels = [0, 1, 2, 3, 4, 5, 6]
        plt.xticks(labels, handles)
        ax.set_ylabel("Frequency")
        sns.despine(offset=5, trim=True)
        st.pyplot(f)

    if st.button("Genearte Hourly Analytics"):
        sns.set_style("whitegrid")

        f, ax = plt.subplots()
        sns.countplot(df['Post Hour'], palette='viridis')
        ax.set_ylabel("Frequency")
        sns.despine(offset=5, trim=True)
        plt.title("Frequency of Posts by Hour")
        st.pyplot(f)

    if st.button("Genearte Weekday & Hourly Analytics"):
        timePivot = pd.pivot_table(df, aggfunc='median',
                                   columns='Post Hour',
                                   index='Post Weekday',
                                   values='like')
        timePivot = timePivot[[1, 2, 3, 4, 5, 6, 7,
                               8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]
        fig = plt.figure(figsize=(18, 10))
        cmap = sns.cubehelix_palette(8, start=.5, rot=-.75, as_cmap=True)
        sns.heatmap(timePivot, cbar=False, cmap=cmap, annot=True, fmt='g')
        #plt.pcolor(lnch_pivot,cmap=plt.cm.Blues, alpha=0.8)
        plt.yticks(np.arange(7), ['Sa', 'F', 'Th',
                   'W', 'Tu', 'M', 'Su'], fontsize=15)
        plt.xticks(fontsize=15)
        plt.ylabel('Post Weekay', fontsize=20)
        plt.xlabel('Post Hour', fontsize=20)
        plt.title('Median Likes Per Post by Post Weekday and Hour', fontsize=20)
        st.pyplot(fig)

    # stqdm.pandas()

    # pd.Series(range(50)).progress_map(lambda x: sleep(1))
    # pd.Dataframe({"a": range(50)}).progress_apply(lambda x: sleep(1), axis=1)

    def datapreprocess(df):
        df.drop(df.columns[7:15], axis=1, inplace=True)
        df.drop(['Paid'], axis=1, inplace=True)
        df['like'].fillna(0, inplace=True)
        df['share'].fillna(0, inplace=True)
        df['comment'].fillna(0, inplace=True)
        outlierCut = np.percentile(df['like'], 90)
        df = df[df['like'] < outlierCut]

        def Weekday(x):
            if x == 1:
                return 'Su'
            elif x == 2:
                return 'Mo'
            elif x == 3:
                return 'Tu'
            elif x == 4:
                return 'We'
            elif x == 5:
                return 'Th'
            elif x == 6:
                return 'Fr'
            elif x == 7:
                return "Sa"

        df['Weekday'] = df['Post Weekday'].apply(lambda x: Weekday(x))
        dayDf = pd.get_dummies(df['Weekday'])
        df = pd.concat([df, dayDf], axis=1)
        hours = list(range(0, 18))
        # hours
        for i in hours:
            hours[i] = str(hours[i])
            hours[i] = 'hr_' + hours[i]

        hourDf = pd.get_dummies(df['Post Hour'], prefix='hr_')
        df = pd.concat([df, hourDf], axis=1)
        monthDf = pd.get_dummies(df['Post Month'], prefix='Mo')
        df = pd.concat([df, monthDf], axis=1)
        df['Video'] = pd.get_dummies(df['Type'])['Video']
        df['Status'] = pd.get_dummies(df['Type'])['Status']
        df['Photo'] = pd.get_dummies(df['Type'])['Photo']
        df['Cat_1'] = pd.get_dummies(df['Category'])[1]
        df['Cat_2'] = pd.get_dummies(df['Category'])[2]

        return df

    if st.button("Train Modelfor suggestions"):
        df = datapreprocess(df)
        x = df[['Page total likes', 'Video', 'Status', 'Photo',
                'Cat_1', 'Cat_2', 'Mo', 'Tu', 'Sa', "We", 'Th', 'Fr',
                'hr__17', 'hr__1', 'hr__2', 'hr__3', 'hr__4', 'hr__5', 'hr__6', 'hr__7', 'hr__8',
                'hr__9', 'hr__10', 'hr__11', 'hr__12', 'hr__13', 'hr__14', 'hr__15', 'hr__16', 'Mo_1',
                'Mo_2', 'Mo_12', 'Mo_4', 'Mo_5', 'Mo_6', 'Mo_7', 'Mo_8', 'Mo_9', 'Mo_11', 'Mo_10']]
        y = df['like']

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1,
                                                            random_state=42)

        rf = RandomForestRegressor(n_estimators=500, min_samples_split=10)
        rf.fit(x_train, y_train)
        predicted_train = rf.predict(x_train)
        predicted_test = rf.predict(x_test)
        test_score = r2_score(y_test, predicted_test)
        spearman = spearmanr(y_test, predicted_test)
        pearson = pearsonr(y_test, predicted_test)

    d = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
         'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    post_day = st.text_input("Enter the day", "Sunday")

    post_timing = st.text_input("Enter the time", "5:00 (24 hour format)")
    hour = int(post_timing.split(" ")[0].split(':')[0]) % 18

    st.subheader('Find you best Time for Post ::sunglasses::')
    if st.button("Post Time Analysis"):
        start = int(d[post_day] - 1)
        timePivot = pd.pivot_table(df, aggfunc='median',
                                   columns='Post Hour',
                                   index='Post Weekday',
                                   values='like')
        timePivot = timePivot[[1, 2, 3, 4, 5, 6, 7,
                               8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]
        timePivot = timePivot.fillna(0)
        post_like_ratio = np.round(
            (timePivot.iloc[start:d[post_day]][hour].values[0] / timePivot.sum().sum()), 3)
        # st.write(timePivot.iloc[start:d[post_day]][hour].values[0])
        cond = "Very Poor ! Please choose another timing." if post_like_ratio == 0 else "You can go for it."
        st.write("You post could have the like perchentage is:",
                 post_like_ratio, cond)

        # Suggestion Of next Best Time
        st.subheader("Suggestions....")

        current_date = date.today()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        day = current_date.day % 7
        hour = int(dt_string.split(" ")[1].split(":")[0])

        st.write("Current Time: ->  ", dt_string)

        best_like = 0
        best_hour = 0
        for i in range(hour, 19):
            val = timePivot.iloc[day-1:][i].values[0]
            if val > best_like:
                best_like = val
                best_hour = i

        hours = best_hour-hour

        next_time = now = datetime.now()+timedelta(hours=hours)
        next_time_string = next_time.strftime("%d/%m/%Y %H:%M:%S")

        st.write("Next Best Time to Post: ", next_time_string)
