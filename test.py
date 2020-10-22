import pandas as pd

file = pd.read_csv('articles1.csv')
file.head()
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
vectorizer.fit(file['title'])
X1 = vectorizer.transform(file['title'])
X1[0].shape
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer()
vectorizer.fit(file['title'])
X2= vectorizer.transform(file['title'])
X2[0].shape
from sklearn.decomposition import NMF
from sklearn.preprocessing import Normalizer, MaxAbsScaler
from sklearn.pipeline import make_pipeline
scaler = MaxAbsScaler()
nmf = NMF(n_components=50)
normalizer = Normalizer()
pipeline = make_pipeline(scaler,nmf,normalizer)
norm_features1 = pipeline.fit_transform(X1)
norm_features2 = pipeline.fit_transform(X2)

df1 = pd.DataFrame(norm_features1,index=file['title'])
df2 = pd.DataFrame(norm_features2,index=file['title'])
def similarities(article,df):
    article_index = df.loc[article]

    # Compute cosine similarities: similarities
    similarities = df.dot(article_index)

    # Display those with highest cosine similarity
    print(similarities.nlargest())
similarities('The Atlantic Daily: Passing the Presidential Mic',df1)
similarities('The Atlantic Daily: Passing the Presidential Mic',df2)