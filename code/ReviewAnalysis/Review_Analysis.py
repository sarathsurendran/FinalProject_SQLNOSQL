
"""
Created on Fri May  1 01:45:11 2020
@author: Sarath Surendran
Final Project - Review Analysis
"""

import seaborn as sns
import pandas as pd
import numpy as np

import matplotlib.pyplot as plot

from wordcloud import WordCloud
from elasticsearch import Elasticsearch


es = Elasticsearch(
        ['10.134.175.251'],
        port=9200
    ) #ES set up - high level

pd.set_option('display.max_columns', None)  # just for printing all columns

def load_review_data_from_business(business_data):
    
    print("Total businesses retrieved ::",len(business_data))
    businesses=[]
    for b in business_data:
        businesses.append(b)
    
    
#    get review data
    review_query={
            "query": {
                     "terms" : { "business_id.keyword": businesses}
                       }
            }
    
    review_data=get_review_data(query=review_query,size=10000)
    
    print("Total reviews retrieved ::",len(review_data))
    fields = {}
    for num,doc in enumerate(review_data):
        review=doc["_source"]
        # iterate review data
        for key, val in review.items():
            try:
                fields[key] = np.append(fields[key], val)
            except KeyError:
                fields[key] = np.array([val])
    
    # create and return df
    return pd.DataFrame(fields)

def load_business_df(business_data):
    fields = {}
    for num,doc in enumerate(business_data):
        review=doc["_source"]
        # iterate review data
        for key, val in review.items():
            try:
                fields[key] = np.append(fields[key], val)
            except KeyError:
                fields[key] = np.array([val])
    
    # create and return df
    return pd.DataFrame(fields)

#Gets all the data for the index..default query is match all
def get_review_data(query="",size=10):
    if(query == "" ):#default query
        query={"query":
                {
                        "match_all": {}
                }
              }

    res=es.search(
            index="reviews",
            body=query,
            size=size)
    
    return res['hits']['hits']
 
#Gets all the data for the index..default query is match all
def get_business_data(query="",size=10):
    if(query == "" ):#default query
        query={"query":
                {
                        "match_all": {}
                }
              }

    res=es.search(
            index="business",
            body=query,
            size=size)
    
    return res['hits']['hits']

 
def main():
    
    #user input
    business=str(input("\nPlease enter the business name to be analyzed (Use * to do wild card analysis): "))
    
    if (not business):#simple to check to return if not string
        print("Please enter a valid business name")
        return
    elif business == "":
        print("Please enter a valid business name")
        return
        
     #Get all business starting with name McDonalds in states Illinois and Nevada
    query_business= {
	"query": {
		"bool": {
			"must": [
				{
					"wildcard": {
						"name.keyword": business
					}
				}
			]
		}
	}
}
   
    #Get all data related to waffle house from "business" index
    business_data=get_business_data(query_business,size=1000)
    
    if(len(business_data) ==0):
        print("Unable to retrieve data for the specified business.")
        return
    
    #prepare dataframe
    df_business=load_business_df(business_data)
    
    print("\nAll the businesses included for analysis ::",df_business.name.unique(),"\n")
    
    #check the rating distribution for wafflehouse
    rating=df_business['stars'].value_counts()
    rating=rating.sort_index()
    
    #plotting graph - stars
    plot.figure(figsize=(10,5))
    sns.barplot(rating.index, rating.values)
    plot.title("Ratings Distribution")
    plot.ylabel('Number of Reviews')
    plot.xlabel('Rating')
#    
#    #state wise distribution
    state_dist=df_business['state'].value_counts()
     #plotting state dist
    plot.figure(figsize=(10,5))
    sns.barplot(state_dist.index, state_dist.values, palette="vlag")
    plot.title("State Wise Distribution")
    plot.ylabel('Number of Restruants')
    plot.xlabel('State')
    
    
    # Prepare df for reviews from the data collected from businesses
    df_review=load_review_data_from_business(df_business['business_id'])
    df_review['review_length'] = df_review['text'].apply(len)
#    
#   
#    #group by usefull reviews
    useful_reviews=df_review['useful'].value_counts()
    cool_reviews=df_review['cool'].value_counts()
    funny_reviews=df_review['funny'].value_counts()
#    print(useful_reviews)
    plot.figure(figsize=(10,5))
    sns.barplot(useful_reviews.index, useful_reviews.values)
    plot.ylabel('Count')
    plot.xlabel('Useful reviews')
    
    plot.figure(figsize=(10,5))
    sns.barplot(cool_reviews.index, cool_reviews.values,palette="husl")
    plot.ylabel('Count')
    plot.xlabel('Cool reviews')
    
    plot.figure(figsize=(10,5))
    sns.barplot(funny_reviews.index, funny_reviews.values,palette="deep")
    plot.ylabel('Count')
    plot.xlabel('Funny reviews')
#    
    stars_grp = df_review.groupby('stars').mean()
    hm_fig=plot.figure(figsize=(10,5))
    ax1 = hm_fig.add_axes([0.4,0.2,0.5,0.6])
    ax=sns.heatmap(stars_grp.corr(),ax=ax1,cmap="YlGnBu",annot=True,center=0)
    hm_fig.subplots_adjust(left=0.4)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.5, top - 0.5)
    #Concatenate all reviews into one
    cloud_text=df_review.text.str.cat(sep=' ')
    #use it in wordcloud and see what pops out
    wordcloud=WordCloud(max_font_size=75, max_words=200, background_color="white",width=800, height=400).generate(cloud_text)
    # Display the generated image:
    plot.figure( figsize=(18,7) )
    plot.imshow(wordcloud)
    plot.axis("off")
    plot.tight_layout(pad=0)
    plot.show()
 
main()