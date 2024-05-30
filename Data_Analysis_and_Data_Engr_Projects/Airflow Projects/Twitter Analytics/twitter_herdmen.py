from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
import pandas as pd
import tweepy
import re
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import preprocessor as p
nltk.download('punkt')
from PIL import Image
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from collections import Counter

#define the function to extract twitter data
def extract_tweet():
    # Authenticate to Twitter
    consumer_key = 'your_consumer_key'
    consumer_secret = 'your_consumer_secret'
    access_key= 'your_access_key'
    access_secret = 'your_access_secret'

    
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=False)
    # Enter the search words/trends to extract from twitter
    search_words = "Herdsmen" or 'Killer Herdsmen' or 'Pastoralists' or 'Pastoralist' or 'Fulani Herdsmen' or 'Fulani Pastoralist' or 'Fulani killer' or 'Miyetti' or 'Miyetti Allah' or 'MACBAN'or 'Cattle Breeders' or 'Cattle Rustlers'
    new_search = search_words + " -filter:retweets"
    tweets = tweepy.Cursor(api.search_tweets,q=new_search,count=200,lang="en",since_id=0).items()

    list_tweets = []
    for tweet in tweets:
        refined_tweet = {"id": tweet.id,
			            "created_at":tweet.created_at,
                        'tweet' : tweet.text.encode('utf-8'),
                        'location' : tweet.user.location.encode('utf-8')
                        }
        
        list_tweets.append(refined_tweet)

    df = pd.DataFrame(list_tweets)
    df.to_csv('extract_twitter_data/herds.csv',index = False)

# Function to clean tweet
def clean_tweet():
    df = pd.read_csv('data/temp/tweets.csv')
    text = df['Tweet']
    text = text.astype(str)
    text = text.apply(p.clean)
    text = text.str.replace(r"^b'", "", regex=True)
    text = text.str.replace(r"\?|\_|\-|\!|\,|\...|\&|\:|\;|\'s|\(|\)|\.", '', regex=True)
    text = text.str.replace(r"\\n", '', regex=True)
    text = text.str.lower()
    df['Tweet'] = text
    df.to_csv('data/temp/cleaned_tweets.csv', index=False)
    

# Function to replace unwanted patterns
def replace_pattern():
    df = pd.read_csv('data/temp/cleaned_tweets.csv')
    pattern = re.compile(r"^b'")
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    
    df['Location'] = df['Location'].apply(lambda x: pattern.sub('', x) if isinstance(x, str) else x)
    df['Location'] = df['Location'].replace("'", 'Nigeria')
    df['Tweet'] = df['Tweet'].apply(lambda x: ' '.join([w for w in x.split() if w not in stop_words]))
    df['Tweet'] = df['Tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 4]))
    df.to_csv('data/temp/replace_tweets.csv')

# Function to remove banned words
def remove_banned_words(matchobj):
    xwords = pd.Series(['xe2','x80','xa6','xf0' ,'x9f','x99','x99t','xa3','xa4','xc2','xe7x8fxe5x88xa9xe5xa7xac',
                        'xc2xa1nfidel','xc2xa1dxc2xa10t','x98x94x98x94',"'",'x94','b','b',"''",'','xa3i',"'m",
                        'x98x81',"n't",'x87xacx87xa7','esn','\\\\\\', 'foreve\\\\\\', '\\xc2\\xa1d\\xc2\\xa10t',
                        '\\xc2\\xa1nfidel','th\\\\\\','m','\\\\\\\\xa3I','\\xe7\\\\x8f\\xe5\\x88\\xa9\\xe5\\xa7\\xac',
                        '\\\\\\x98\\x94\\\\\\x98\\x94','xe7x8fxe5x88xa9xe5xa7xac','xc2xa1nfidel','xc2xa1dxc2xa10t',
                        'x98x94x98x94',"'",'x94','b','b',"''",'','xa3i',"'m",'x98x81',"n't",'x87xacx87xa7','esn',
                        '\\\\\\', 'foreve\\\\\\', '\\xc2\\xa1d\\xc2\\xa10t','\\xc2\\xa1nfidel','th\\\\\\','m',
                        '\\\\\\\\xa3I','...','\\xe7\\\\x8f\\xe5\\x88\\xa9\\xe5\\xa7\\xac','\\\\\\x98\\x94\\\\\\x98\\x94','x87xacx87xa7'])
    banned_words = set(word.lower() for word in xwords)
    
    word = matchobj.group(0)
    if word.lower() in banned_words:
        return ""
    else:
        return word

def apply_remove_banned_words():
    df = pd.read_csv('data/temp/replace_tweets.csv')
    word_pattern = re.compile(r'\w+')
    
    def clean_sentence(sentence):
        if isinstance(sentence, str):
            return word_pattern.sub(remove_banned_words, sentence)
        else:
            return sentence
    
    df['Tweet'] = df['Tweet'].apply(clean_sentence)
    df['Tweet'] = df['Tweet'].str.replace(r'\\', '', regex=True)
    df.to_csv('data/temp/final_tweets.csv', index=False)

# define function to visualize the top word frequency in wordcloud
#define the function to load the data
def load_data():
    data = pd.read_csv('data/temp/final_tweets.csv')
    return data

#define the function for the wordcloud
def wordcloud_draw(data, color = 'black'):
    data = [str(word) for word in data]
    words = ' '.join(data)
    unwanted_tokens = ['``', "''", "'"]
    cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and not word.startswith('#')
                                and word != 'RT'
                                and word not in unwanted_tokens
                            ])
   
    wordcloud = WordCloud(
                      background_color=color,
                          width=2500,
                      height=2000
                     ).generate(cleaned_word)
    plt.figure(1,figsize=(13, 13))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

#define the function to tokenize the tweets into unigrams
def unigram_tweets():
    df = pd.read_csv('data/temp/final_tweets.csv')
    all_words = ' '.join([str(w) for w in df['Tweet']])
    #tokenize all words
    tokens = word_tokenize(all_words)
    unwanted = ['``',"''","'"]
    tokens = [word for word in tokens if word not in unwanted]
    # create a frequency distribution of the tokens
    freq_dist = FreqDist(tokens)
    # create a dataframe from the frequency distribution
    freq_df = pd.DataFrame(list(freq_dist.items()), columns=['Word', 'Frequency'])
    freq_df = freq_df.sort_values(by='Frequency', ascending=False)
    freq_df.to_csv('data/temp/unigram.csv', index=False)

# plot the top 20 most frequent words
def plot_unigram():
    df = pd.read_csv('data/temp/unigram.csv')
    df = df.head(20)
    plt.figure(figsize=(10, 6))
    plt.barh(df['Word'], df['Frequency'], color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title('Top 20 Most Frequent Words in Tweets')
    plt.savefig('data/temp/unigram.png')
    return plt.show()

#print the wordcloud of the top 20 most frequent words
def wordcloud_unigram():
    df = pd.read_csv('/home/dabson2020/airflow/data/temp/unigram.csv')
    plt.figure(figsize=(8,6))
    wordcloud_draw(df['Word'], color='white')
    plt.savefig('data/temp/unigram_wordcloud.png')
    return plt.show()

# define the function to get bigrams, save the top 30 word and its frequency

def bigram_tweets():
    df = df = pd.read_csv('data/temp/final_tweets.csv')
    df['tokens'] = df['Tweet'].astype(str).apply(nltk.word_tokenize)
    df['bigrams'] = df['tokens'].apply(lambda row: list(nltk.bigrams(row)))
    bigrams = [bigram for sublist in df['bigrams'] for bigram in sublist]
    # Count the frequency of each bigram
    bigram_freq = Counter(bigrams)
    # Convert the counter object to a list of tuples
    bigram_freq_list = list(bigram_freq.items())

    # Sort the list by frequency in descending order
    bigram_freq_list = sorted(bigram_freq_list, key=lambda x: x[1], reverse=True)
    top_20 = bigram_freq_list[:20]
    top_20 = [t for t in top_20 if t != (('herdsmen', "'"), 78) and t !=(('b', "''"), 49) and t != (('ca', "n't"), 42)]
    bigram_df = pd.DataFrame(top_20, columns=['Bigram', 'Frequency'])
    # Sort the dataframe by frequency in descending order
    bigram_df = bigram_df.sort_values('Frequency', ascending=False)
    bigram_df.to_csv('data/temp/bigram.csv', index=False)

# plot the top 20 most frequent bigrams
def plot_bigram():
    df = pd.read_csv('data/temp/bigram.csv')
    df = df.head(20)
    plt.figure(figsize=(10, 6))
    plt.barh(df['Bigram'], df['Frequency'], color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Bigrams')
    plt.title('Top 20 Most Frequent Bigrams in Tweets')
    plt.savefig('data/temp/bigram.png')
    return plt.show()

# print the wordcloud of the top 20 most frequent bigrams
def wordcloud_bigram():
    df = pd.read_csv('/home/dabson2020/airflow/data/temp/bigram.csv')
    bigram_dict = dict(zip(df['Bigram'], df['Frequency']))
    # create a WordCloud object
    wc = WordCloud(
        background_color="white",
        max_words=2000,
        contour_width=3,
        contour_color='steelblue',
        width=2500,
        height=2000,
        max_font_size=300,
        min_font_size=10,
        relative_scaling=0.5,
        colormap='viridis'  
    )
    
    # generate the word cloud from your data
    wc.generate_from_frequencies(bigram_dict)

    # plot the wordcloud
    plt.figure(figsize=(8,6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('data/temp/bigram_wordcloud.png', dpi=300)
    return plt.show()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'twitter_processing',
    default_args=default_args,
    description='A simple data processing DAG',
    schedule_interval=timedelta(days=1),
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_tweet,
    provide_context=True,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='clean_tweet',
    python_callable=clean_tweet,
    provide_context=True,
    dag=dag,
)

replace_task = PythonOperator(
    task_id='replace_pattern',
    python_callable=replace_pattern,
    provide_context=True,
    dag=dag,
)

remove_ban_word = PythonOperator(
    task_id='remove_banned_words',
    python_callable=apply_remove_banned_words,
    provide_context=True,
    dag=dag,
)

remove_task = PythonOperator(
    task_id='apply_remove_banned_words',
    python_callable=apply_remove_banned_words,
    provide_context=True,
    dag=dag,
)

unigram_task = PythonOperator(
    task_id='unigram_tweets',
    python_callable=unigram_tweets,
    provide_context=True,
    dag=dag,
)

plot_unigram_task = PythonOperator(
    task_id='plot_unigram',
    python_callable=plot_unigram,
    provide_context=True,
    dag=dag,
)

wordcloud_unigram_task = PythonOperator(
    task_id='wordcloud_unigram',
    python_callable=wordcloud_unigram,
    provide_context=True,
    dag=dag,
)

bigram_task = PythonOperator(
    task_id='bigram_tweets',
    python_callable=bigram_tweets,
    provide_context=True,
    dag=dag,
)

plot_bigram_task = PythonOperator(
    task_id='plot_bigram',
    python_callable=plot_bigram,
    provide_context=True,
    dag=dag,
)

wordcloud_bigram_task = PythonOperator(
    task_id='wordcloud_bigram',
    python_callable=wordcloud_bigram,
    provide_context=True,
    dag=dag,
)


extract_task >> clean_task >> replace_task >> remove_ban_word >> remove_task >> unigram_task >> plot_unigram_task
unigram_task >> wordcloud_unigram_task 
remove_task >>  bigram_task >> plot_bigram_task
bigram_task >>  wordcloud_bigram_task