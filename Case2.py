from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    results = soup.find_all('div', attrs={'class':'lister-item-content'})
    records = []  
    for result in results:  
        title = result.find('a').text
        title = title.strip()
        rating = result.find('strong').text
        rating = rating.strip()
        if (result.find('span', attrs={'class':'metascore favorable'}) is not None):
            meta = result.find('span', attrs={'class':'metascore favorable'}).text
        elif (result.find('span', attrs={'class':'metascore mixed'}) is not None):
            meta = result.find('span', attrs={'class':'metascore mixed'}).text
        else:
            meta = '0'
        meta = meta.strip()
        vote = result.find('span', attrs={'name':'nv'}).text
        vote = vote.strip()
        records.append((title, rating, meta, vote))

    df = pd.DataFrame(records, columns = ('Title','Rating','MetaScore','Votes'))#creating the dataframe
    #data wranggling -  try to change the data type to right data type 
    df['Votes']=df['Votes'].str.replace(',','').astype('float64')
    df['Rating']=df['Rating'].astype('float64')
    df['MetaScore']=df['MetaScore'].astype('int64')
    df['Popularity']=df['Votes']*(df['Rating']/10)+df['MetaScore']
    df = df.pivot_table(index='Title',values='Popularity', aggfunc= sum).sort_values('Popularity',ascending=False).head(7)
   #end of data wranggling
    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,3),dpi=500)
    df.plot.bar()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table

    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run(debug=True)
