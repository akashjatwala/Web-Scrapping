# Scrapping various sections of Inshorts, and saving the result in a csv file


import requests
from bs4 import BeautifulSoup
import pandas as pd

urls=["https://inshorts.com/en/read/national",
      "https://inshorts.com/en/read/business",
      "https://inshorts.com/en/read/sports",
      "https://inshorts.com/en/read/world",
      "https://inshorts.com/en/read/politics",
      "https://inshorts.com/en/read/technology",
      "https://inshorts.com/en/read/startup",
      "https://inshorts.com/en/read/entertainment",
      "https://inshorts.com/en/read/miscellaneous",
      "https://inshorts.com/en/read/hatke",
      "https://inshorts.com/en/read/science",
      "https://inshorts.com/en/read/automobile"]
      
news_data_content,news_data_title,news_data_category,news_data_source,news_data_source_url=[],[],[],[],[]

for url in urls:
  category=url.split('/')[-1]
  data=requests.get(url)
  soup=BeautifulSoup(data.content,'html.parser')
  
  news_title=[]
  news_content=[]
  news_category=[]
  news_source=[]
  news_source_url=[]
  
  for headline,article in zip(soup.find_all('div', class_=["news-card-title news-right-box"]),
                            soup.find_all('div',class_=["news-card-content news-right-box"])):
    news_title.append(headline.find('span',attrs={'itemprop':"headline"}).string)
    news_content.append(article.find('div',attrs={'itemprop':"articleBody"}).string)
    news_category.append(category)
  
  for source in soup.find_all('div', class_="read-more"):
    news_source.append(source.find('a',class_="source").text)
    news_source_url.append(source.find("a").get('href').strip())
  
  news_data_title.extend(news_title)
  news_data_content.extend(news_content)
  news_data_category.extend(news_category)  
  news_data_source.extend(news_source)
  news_data_source_url.extend(news_source_url)

df1=pd.DataFrame(news_data_title,columns=["Title"])
df2=pd.DataFrame(news_data_content,columns=["Content"])
df3=pd.DataFrame(news_data_category,columns=["Category"])
df3=df3.Category.str.title()
df4=pd.DataFrame(news_data_source,columns=["Source"])
df5=pd.DataFrame(news_data_source_url,columns=["Source URL"])
df=pd.concat([df1,df2,df3,df4,df5],axis=1)
df=df.dropna()
df.to_csv("Inshorts.csv",index=None)
