
import pandas as pd
import re
from textblob import TextBlob
from meme_or_not import set_model_for_image_type,get_image_type
from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=530, timeout=(10,25), retries=3, backoff_factor=0.2)
model = set_model_for_image_type()


def question_mark_check(row):
    #print(row['text'])
    if '?' not in str(row['text']):
        val = 0
    else:
        val = 1
    return val

def hashtag_check(row):
    #print(row['text'])
    if '#' not in str(row['text']):
        val = 0
    else:
        val = str(row['text']).count('#')
    return val

def url_check(row):

    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,str(row['text']))
    if len(url)>0:
        return 1
    else:
        return 0
    
def words_count(row):
    return len(str(row['text']).split())

def lexical_diversity(row):
    return len(set(str(row['text']).split())) / len(str(row['text']).split())


def sentiment(row):
    testimonial = TextBlob(str(row['text']))
    return testimonial.sentiment.polarity


def image_check(row):
    if row['image'] ==0:
        return 0
    else:
        x = get_image_type(model,row['image'])
        return x
        
        
def image_as_boolean(row):
    if row['image'] !=0:
        if row['image_type'] == -1:
            return 0
        else:
            return 1
    else:
        return 0
    

def video_as_boolean(row):
    if row['video'] != 0:
        return 1
    else:
        return 0
    
def trend_status(row):
    
    from rake_nltk import Rake

    r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.

    r.extract_keywords_from_text(str(row['text']))
 
    words = r.get_ranked_phrases()
    
    proper_nouns = set()
    tb = TextBlob(str(row['text']))
    for i in tb.tags:
        if i[1] == 'NNP':
            proper_nouns.add(str(i[0]))
            
    proper_nouns = sorted(list(proper_nouns),key = len, reverse = True)[:5]
    
            
        
    if len(words) == 0:
        return 0
    kw_list = sorted(list(words),key = len, reverse = True)[:5] + proper_nouns
    #print(kw_list)
    try:
        pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='IN', gprop='')
        interest = pytrends.interest_over_time().tail(20)
    
        interest = interest[interest.columns[0]]
    except:
        if len(proper_nouns) < 1:
            return 0
        #print(proper_nouns)
        pytrends.build_payload(proper_nouns, cat=0, timeframe='today 5-y', geo='IN', gprop='')
        interest = pytrends.interest_over_time().tail(20)
        
        try:
            interest = interest[interest.columns[0]]
        except:
            return 0
        
    x = interest.mean()
    if x == 0:
        #print("no interest")
        if len(proper_nouns) < 1:
            return 0
        #print(proper_nouns)
        pytrends.build_payload(proper_nouns, cat=0, timeframe='today 5-y', geo='IN', gprop='')
        interest = pytrends.interest_over_time().tail(20)
        
        try:
            interest = interest[interest.columns[0]]
        except:
            print('fail')
            return 0
        return interest.mean()
    return x


def text_boolean(row):
    #print(row['text'])
    if len(str(row['text'])) > 0:
        val = 1
    else:
        val = 0
    return val
    
    

def create_dataset(df,number_of_group_members):


    df['image'] = df['image'].fillna(0)
    df['video'] = df['video'].fillna(0)

    df = df[['text', 'image', 'video', 'likes',
        'comments', 'shares']]

    

    df['engagement_score'] = (df['likes'] + df['comments'] + 2*df['shares'])/number_of_group_members

    df.drop(df[df.engagement_score == 0].index, inplace=True)

    df = df[['text', 'image', 'video','engagement_score' ]]

    df['question_mark_check'] = df.apply(question_mark_check, axis=1)
    df['hashtag_check'] = df.apply(hashtag_check, axis=1)

    df['url_check'] = df.apply(url_check, axis=1)

    df['lexical_diversity'] = df.apply(lexical_diversity, axis=1)

    df['words_count'] = df.apply(words_count, axis=1)

    df['sentiment'] = df.apply(sentiment, axis=1)

    df['image_type'] = df.apply(image_check, axis=1)


    df['image'] = df.apply(image_as_boolean, axis=1)
    df['video'] = df.apply(video_as_boolean, axis=1)
    df['image_type_bool'] = df.apply(image_check, axis=1)
    df = df.drop(['image_type'], axis=1)

    df['trend_score'] = df.apply(trend_status, axis=1)

    df['text'] = df.apply(text_boolean, axis=1)


    df = df[['text','question_mark_check',
        'hashtag_check', 'url_check', 'lexical_diversity', 'words_count',
        'sentiment', 'trend_score','image','image_type_bool','video','engagement_score']]

    return df


group_str = [45000,108900,20100,101400]

groups = ['143322019583033.csv','546588969267691.csv','InsaneTech.csv','pypcom.csv']

for i in range(len(groups)):
    
    df = pd.read_csv(groups[i])
    print(i)
    f = create_dataset(df,group_str[i])
    print(len(f))
    f.to_csv(f'{i}_processed.csv')


