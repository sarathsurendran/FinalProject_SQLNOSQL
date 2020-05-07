import pandas as pd
import json
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from sklearn import preprocessing


def search():
    es = Elasticsearch([{'host': '10.134.175.251', 'port': 9200}])
    
    body={"query": {"match": {"state": "IL" } } }
    results = elasticsearch.helpers.scan(es, query=body, index="business")
    df_business = pd.DataFrame.from_dict([document['_source'] for document in results])
    print(df_business)
    df_num=df_business[["stars","review_count"]]
    names = df_num.columns
# Create the Scaler object
    scaler = preprocessing.StandardScaler()
# Fit your data on the scaler object
    scaled_df = scaler.fit_transform(df_num)
    scaled_df = pd.DataFrame(scaled_df, columns=names)
    corr_data = scaled_df.corr() 
    print (corr_data)  
    grouped_data=df_business.groupby('postal_code').mean()
    print (grouped_data['stars'].plot(kind='bar'))
    print (grouped_data['review_count'].plot(kind='bar'))
       
    
    
    
    
    



if __name__ == "__main__":
   

    search()
