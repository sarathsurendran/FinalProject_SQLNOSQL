import pandas as pd
import json
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from sklearn import preprocessing
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def search():
    es = Elasticsearch([{'host': '10.134.175.251', 'port': 9200}])
    
    body={"query": {"match": {"name": "john" } } }
    results = elasticsearch.helpers.scan(es, query=body, index="users")
    df_users = pd.DataFrame.from_dict([document['_source'] for document in results])
    print(df_users.dtypes)
    corr_users=df_users.corr(method="pearson")
    print (corr_users)
    grouped_data=df_users.groupby('yelping_since')
    print (grouped_data['average_stars'].plot(kind='bar'))
    print (grouped_data['review_count'].plot(kind='bar'))
    



if __name__ == "__main__":
   

    search()
