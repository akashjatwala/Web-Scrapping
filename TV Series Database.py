# Creating a database of IMDb ID, Title, Genres, Rating, Summary, and Keywords of the contents
# User has to save the IMDb ID of the contents in a text file, for which s/he wants to create the database
# In Update Database, previous created database will be used to add new contents by the user


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from tkinter.filedialog import askopenfilename

def keywords_extraction(text):
    # setting stopwods
    stop_words = set(stopwords.words("english")) 
    
    # removing punctuations
    text = re.sub('[^a-zA-Z]', ' ', text) 
    
    # converting to lowercase
    text = text.lower() 
    
    # removing tags
    text = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ", text) 
    
    # removing digits and special characters
    text = re.sub("(\\d|\\W)+"," ", text) 
    
    # lemmatization
    text = text.split()
    lem = WordNetLemmatizer()
    text = [lem.lemmatize(word) for word in text if not word in  stop_words] 

    # keywords extraction
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(text)
    text = vectorizer.get_feature_names()
    text = " ".join(str(x) for x in text)
    
    return text

def database(title_id):
    # scrapping the webpage
    url = requests.get("https://www.imdb.com/title/tt" + title_id + "/")
    soup = BeautifulSoup(url.content, 'lxml')

    # rating of the series
    rating = soup.strong.text
    
    # genres of the series
    genres = ' '.join([item.text.strip() for item in soup.select(".canwrap a[href*='genre']")])

    # title of the series
    title = soup.find('h1').text.strip()

    # keywords from the plot
    summary = soup.find('div', class_="summary_text").text.strip()
    keywords = keywords_extraction(summary)

    return rating, genres, title, summary, keywords
    
def database_creation():
    # reading the text file containing the series imdb ids
    while(True):
        filename = askopenfilename()
        if(filename[-4:]!=".txt"):
            print("Selectd File is not a '.txt' File")
        else:
            break
    id_file = open(filename, "r")
    id_list = id_file.read().split("\n")
    id_file.close()

    rating_list=[]
    genres_list=[]
    title_list=[]
    summary_list=[]
    keywords_list=[]

    # getting the requisite data from the databse function
    for i in id_list:
        rating, genres, title, summary, keywords = database(i)
        rating_list.append(rating)
        genres_list.append(genres)
        title_list.append(title)
        summary_list.append(summary)
        keywords_list.append(keywords)
    
    df=pd.DataFrame({"IMDb ID" : id_list,
                     "Title" : title_list,
                     "Genres" : genres_list,
                     "Rating" : rating_list,
                     "Summary" : summary_list,
                     "Keywords" : keywords_list})
                 
    df = df[['IMDb ID', 'Title', 'Genres', 'Rating', 'Summary', 'Keywords']]
    
    df.to_csv("series_database.csv", index=None)
    
    return df
    
def database_updation(df):
    # getting the new imdb id from the user, and checking whether it exists in the database or not
    while(True):
        new_id = input("Please enter the IMDb ID of the Series which you want to add to the Database: ")
        if(len(new_id) < 7):
            print("You had entered an invalid ID")
        else:
            if(any(df['IMDb ID'] == int(new_id)) == True):
                print("The ID you entered already exist in the Database")
            else:
                break
    
    # appending the new id to the database           
    rating_list=[]
    genres_list=[]
    title_list=[]
    summary_list=[]
    keywords_list=[]
    
    rating, genres, title, summary, keywords = database(new_id)
    
    rating_list.append(rating)
    genres_list.append(genres)
    title_list.append(title)
    summary_list.append(summary)
    keywords_list.append(keywords)
    
    df_updated=pd.DataFrame({"IMDb ID" : new_id,
                             "Title" : title_list,
                             "Genres" : genres_list,
                             "Rating" : rating_list,
                             "Summary" : summary_list,
                             "Keywords" : keywords_list})
                    
    df_updated = df_updated[['IMDb ID', 'Title', 'Genres', 'Rating', 'Summary', 'Keywords']]
    
    df_new = df.append(df_updated)
    
    df_new.to_csv("series_database.csv", index=None)
    
    return df_new

def main():
    print("1. Create New Database")
    print("2. Update the Database")
    while(True):
        ch = (int)(input("Please enter your choice: "))
        if(ch == 1 or ch == 2):
            break
        else:
            print("You had entered an invalid key")
    if(ch == 1):
        df = database_creation()
    else:
        df = pd.read_csv("series_database.csv", encoding='windows-1252')
        df = database_updation(df)
    
    df = pd.read_csv("series_database.csv", encoding='windows-1252')
    
main()

