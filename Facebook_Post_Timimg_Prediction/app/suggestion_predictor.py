import re
import numpy as np
from textblob import TextBlob
from rake_nltk import Rake
from meme_or_not import set_model_for_image_type,get_image_type
from pytrends.request import TrendReq
import pickle
import heapq
with open('models.pickle', 'rb') as handle:
    rf_models = pickle.load(handle)

pytrends = TrendReq(hl='en-US', tz=530, timeout=(10,25), retries=3, backoff_factor=0.2)
model = set_model_for_image_type()


def get_metrics(post,image = False,video = False):

    def question_mark_check(post):
        #print(row['text'])
        #print('? done')
        if '? ' not in str(post):
            val = 0
        else:
            val = 1
        return val

    def hashtag_check(post):
        #print(row['text'])
        #print('# Done')
        if '#' not in str(post):
            val = 0
        else:
            val = str(post).count('#')
        return val

    def url_check(post):
        #print('url Done')
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex,str(post))
        if len(url)>0:
            return 1
        else:
            return 0

    def words_count(post):
        #print('wc Done')
        return len(str(post).split())

    def lexical_diversity(post):
        #print(str(post).split())
        return len(set(str(post).split())) / len(str(post).split())


    def sentiment(post):
        #print('sentiment Done')
        testimonial = TextBlob(str(post))
        return testimonial.sentiment.polarity

    def image_check(image):
        
        if not image:
            return 0
        else:
            x = get_image_type(model,image)
            return x
  
    def trend_status(post):

        r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.

        r.extract_keywords_from_text(str(post))

        words = r.get_ranked_phrases()

        proper_nouns = set()
        tb = TextBlob(str(post))
        for i in tb.tags:
            if i[1] == 'NNP':
                proper_nouns.add(str(i[0]))

        proper_nouns = sorted(list(proper_nouns),key = len, reverse = True)[:5]



        if len(words) == 0:
            return 0,[]
        kw_list = sorted(list(words),key = len, reverse = True)[:5] + proper_nouns
        #print(kw_list)
        try:
            pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='IN', gprop='')
            interest = pytrends.interest_over_time().tail(20)

            interest = interest[interest.columns[0]]
        except:
            if len(proper_nouns) < 1:
                return 0,kw_list
            #print(proper_nouns)
            pytrends.build_payload(proper_nouns, cat=0, timeframe='today 5-y', geo='IN', gprop='')
            interest = pytrends.interest_over_time().tail(20)

            try:
                interest = interest[interest.columns[0]]
            except:
                return 0,kw_list

        x = interest.mean()
        if x == 0:
            #print("no interest")
            if len(proper_nouns) < 1:
                return 0,kw_list
            #print(proper_nouns)
            pytrends.build_payload(proper_nouns, cat=0, timeframe='today 5-y', geo='IN', gprop='')
            interest = pytrends.interest_over_time().tail(20)

            try:
                interest = interest[interest.columns[0]]
            except:
                #print('fail')
                return 0,kw_list
            return interest.mean(),kw_list
        return x,kw_list


    def text_boolean(post):
        #print(row[''])
        if len(str(post)) > 0:
            val = 1
        else:
            val = 0
        return val
    
    post_clean = re.sub(r'^https?:\/\/.*[\r\n]*', '', post, flags=re.MULTILINE)
   
    trend_s, keywords = trend_status(post_clean)
    #print('Trends Done')
    if not image:
        image_status = 0
        image_type = 0
    else:
        image_status = 1
        image_type = image_check(image)
    if not video:
        video_status = 0
    else:
        video_status = 1
    sentiment_score = sentiment(post_clean)
    parameters = [1,question_mark_check(post_clean),hashtag_check(post_clean),
                  url_check(post),lexical_diversity(post_clean),words_count(post_clean),
                  sentiment_score,trend_s,image_status,image_type,video_status]
    #parameters.append(int(input("image?")))
    #parameters.append(int(input("image type?")))
    #parameters.append(int(input("video?")))
    #parameters.append(input("engagement_score ?"))
    
    return parameters,keywords,trend_s,sentiment_score
    
    
def define_best_suggestion(p):

    if p == 1:
        return 'Looks like this post is ready to go!'
    
    if p == 2:
        return 'Adding a question to your post helps increase your posts engagement score'
    elif p == 3:
        return 'Try adding a hashtag. It seems like your post might do better'
    elif p == 3:
        return 'Try adding a hashtag. It seems like your post might do better'
    elif p == 4:
        return 'Adding 3 more hashtags seems like it will make a significant difference. Your post might do better'
    elif p == 5:
        return 'Can your post include a link to an article/video? Try adding this for better engagement'
    elif p == 6:
        return 'Number of words make a difference. A 25% increase in number of words in your post seems promising'
    elif p == 7:
        return 'Number of words make a difference. A 50% increase in number of words in your post seems promising'
    elif p == 8:
        return 'Number of words make a difference and it seems your post is too small. A 75% increase in number of words in your post seems promising'
    elif p == 9:
        return 'Number of words make a difference. A 25% decrease in number of words in your post seems promising'
    elif p == 10:
        return 'Your post is a bit too lengthy. If you try reducing the length of the post to about 50% its length, it may do much better'
    elif p == 11:
        return 'Your post is a bit too lengthy. If you try reducing the length of the post to about 25% its length, it may do much better'
    elif p == 12:
        return 'Try keeping the number of words limited to around 5. It look like for this post something short seems perfect'
    elif p == 13:
        return 'If the positive sentiment conveyed in your post is increased by 10%, it will do better. Try adding a few cheerful words'
    elif p == 14:
        return 'If the positive sentiment conveyed in your post is increased by 25%, it will do better. Try adding a few cheerful words'
    elif p == 15:
        return 'Including topics in trend in your post is always a good thing. Try including a few buzzwords. A 10% increase in trend score will help'
    elif p == 16:
        return 'Including topics in trend in your post is always a good thing. Try including a few buzzwords. A 25% increase in trend score will help'
    elif p == 17:
        return 'Including images in your post is always a good idea. Adding a meme or a image conveying humour might help'
    elif p == 18:
        return 'Including images in your post is always a good idea. Adding an image of a graph or some sort of infographic seems perfect'
    elif p == 19:
        return 'Including videos in your post is helpful at times. Posting a video seems like it helps engagement score'
    
    
 
def get_suggestions(post,group_id,image = False,video = False):
    #print(post)
    x,kw,trend_score,sentiment_score = get_metrics(post,image,video)
    #print(kw)
    second = x.copy()
    second[1] = 1 #If no question add question

    third = x.copy()
    third[2] += 1 #Increase hashtag by 1

    fourth = x.copy()
    fourth[2] += 3#Increase hashtag by 3

    fifth = x.copy()
    fifth[3] = 1#If no url, add

    sixth = x.copy()
    sixth[5] += int(0.25*sixth[5]) #Increase word count by 25%

    seventh = x.copy()
    seventh[5] += int(0.5*seventh[5])#Increase word count by 50%


    eight = x.copy()
    eight[5] += int(0.75*eight[5])#Increase word count by 75% 

    ninth = x.copy()
    ninth[5] -= int(0.25*ninth[5])#Decrease word count by 25%

    tenth = x.copy()
    tenth[5] -= int(0.5*tenth[5])#Decrease word count by 50%

    eleventh = x.copy()
    eleventh[5] -= int(0.75*eleventh[5])#Decrease word count by 75%

    twelfth = x.copy()
    twelfth[5] = 5#Word count as 5

    thirteen = x.copy()
    thirteen[6] += 0.1*thirteen[6]#Increase sentiment by 10%

    fourteen = x.copy()
    fourteen[6] += 0.25*fourteen[6]#Increase sentiment by 25%

    fifteen = x.copy()
    fifteen[7] += 0.1*fifteen[7]#Increase trend score by 10%

    sixteen = x.copy()
    sixteen[7] += 0.25*sixteen[7]#Increase trend score by 25%

    seventeen = x.copy()
    seventeen[8],seventeen[9] = 1,1#Add image as meme

    eighteen = x.copy()
    eighteen[8],eighteen[9] = 1,-1#Add image as infogrphic

    nineteen = x.copy()
    nineteen[8],nineteen[9],nineteen[10] = 0,0,1#Add video


    to_predict = [x,
                 second,third,fourth,fifth,sixth,seventh,eight,ninth,tenth,eleventh,twelfth,thirteen,
                 fourteen,fifteen,sixteen,seventeen,eighteen,nineteen]
    
    sc = rf_models[group_id][0]
    regressor = rf_models[group_id][1] 
    input_ex = sc.transform(to_predict)
    y_pred = regressor.predict(input_ex)
    
    best_suggestion = np.argmax(y_pred) + 1
    best_few = heapq.nlargest(3, range(len(y_pred)), y_pred.take)
    if best_few[0] == 0:
        best_few = [0]
    best_few = [define_best_suggestion(j+1) for j in best_few]
    
    #print('--------------------------------------')
    #print(trend_score,kw,sentiment_score,y_pred[0])
    return best_few,y_pred[0],trend_score,kw,sentiment_score,x

if __name__ == '__main__':
    print(get_suggestions('''Deep learning becomes more interesting if you study matrix and tensors. It is interesting to note that scalars and vectors should be taken vis-à-vis with these two concepts for a full appreciation of their application. I love how simple ans easy it is to use! Good luck all!
https://l.facebook.com/l.php?u=https%3A%2F%2Fyoutu.be%2FwpZ11vrsRh8%3Ffbclid%3DIwAR0I9dSN5dlPJys7-NzAzP873viIvw-WEpNOQDZgHUfGefhYZtvbaHuKnrI&h=AT0i5nzR0lBmC2CKGLCc3rfNpF8N2pNusjh4yjlgrgd5sOHAlo68EoaoFBksXcx60NFT3XyCs1qWZygctPvYz5itroikOcoabJES8s4cUNX_keDgOZ5gG5BmiBcX6JpoRTQm&__tn__=%2CmH-R&c[0]=AT28N1fXrTI57_gqjBvNXdNXajRaBk4mH9qhK4M2lrSnQ5ykuMhedTcqVgDL8AF-qmTNeMm-QgpgVch0btZuPqPG4CilLyjRW87zq1Q1tVZaiz8X6p4hCTtqKIvQ5f4bWaggesVvNmBAyqYj0s4ukdWt1Mbl5Vewz_W8lLozNSoRjgxzYsOQW8UXUkVWaCXJ2Eb_DkidDzyCG3hdcQ''','InsaneTech','https://external.fhyd1-4.fna.fbcdn.net/safe_image.php?d=AQEURjHwI5wDKciO&w=500&h=261&url=https%3A%2F%2Fi.ytimg.com%2Fvi%2FwpZ11vrsRh8%2Fmaxresdefault.jpg&cfs=1&ext=jpg&ccb=3-5&_nc_hash=AQGy5aOLIwLU-kUt'))