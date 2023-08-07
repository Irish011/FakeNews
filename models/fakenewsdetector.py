
import pandas as pd
import string
import re
import nltk
from supervised import AutoML
from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
from wordcloud import WordCloud
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
# load the dataset
df = pd.read_csv("/models/train.csv")
df.head(10)

"""- The count of total data is 20,800
- Data has five features
"""

import plotly.express as px
label_count = pd.DataFrame(df.label.value_counts(normalize = True).reset_index())
fig = px.pie(label_count, values='label', names = 'index', title = "Pie chart : True and Fake news Distribition")
fig.show()

df1 = df.iloc[0:10000]
df1.dropna(inplace=True)
positive_text = ' '.join(df1[df1['label']==1]['title'])
def black_color_func(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl(0,100%, 1%)")
wordcloud = WordCloud(background_color="white", width=2000, height=1000, max_words=500).generate_from_text(positive_text)
wordcloud.recolor(color_func = black_color_func)
plt.figure(figsize=[15,10])
plt.title("WordCloud for Original News")
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

neagative_text = ' '.join(df1[df1['label']==0]['title'])
wordcloud = WordCloud(background_color="white", width=2000, height=1000, max_words=500).generate_from_text(neagative_text)
wordcloud.recolor(color_func = black_color_func)
plt.figure(figsize=[15,10])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Fake News")
plt.show()

import plotly.express as px
freq_author = pd.DataFrame(df1.author.value_counts().reset_index())
fig = px.bar(freq_author.iloc[:10,:], x="index", y = 'author', title = "Authors with most news")
fig.show()

#We use only text and label
df = df[['text','label']]

#Check null
df.isnull().sum()

#Delete null
df = df.dropna()

df.isnull().sum()

#We will use 500 data
df_new = df.iloc[0:500]

# separate the features and target variable
X = df_new["text"]
y = df_new["label"]

print(X[0:100])
print(len(X[0]))

#Define the function for cleanning and tokenizing data
def clean_text(text):
    text = "".join([word.lower() for word in text if word not in string.punctuation])
    tokens = re.split('\W+', text)
    text = [word for word in tokens if word not in stopwords]
    return text

#Call function for cleaning and tokenizing data
X_clean = X.apply(lambda x: clean_text(x)).astype(str)

X_clean[0]

len(X_clean[0])

# vectorize the text using TfidfVectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(X_clean)

# train the model using AutoML
automl = AutoML(mode="Compete",algorithms=["CatBoost"], random_state=42)

automl.fit(X.toarray(), y)

automl.report()

#Make test data
df_test = df.iloc[16000:16100]

#Data preprocessing for test data
text_teset = df_test.text
X_test = text_teset.apply(lambda x: clean_text(x)).astype(str)
new_X = vectorizer.transform(X_test)

#predict on a new dataset
predictions = automl.predict(new_X.toarray())

#Check the Accuracy
def cal_acc(predictions):
    #Make new dataset for evaluating the result
    df_test['predictions'] = predictions
    df_test[['label','predictions']]
    #Check the Accuracy
    cnt = 0
    for i in df_test['label'].index:
        if df_test['label'][i] == df_test['predictions'][i]:
            cnt += 1
    acc = cnt/len(df_test)*100
    print("Accuracy: {}".format(acc))
    return df_test, acc

import warnings
warnings.filterwarnings('ignore')
df_test, acc = cal_acc(predictions)

import pickle
with open('automl-CatBoost-Data500.pkl', 'wb') as file:
    pickle.dump(automl, file)

from google.colab import files
files.download("/content/automl-CatBoost-Data500.pkl")

# !zip -r /content/file.zip /content/AutoML_2

from google.colab import files
files.download("/content/file.zip")

import pickle
from supervised import AutoML
model = AutoML()
with open('automl-CatBoost-Data500.pkl', 'rb') as file:
    model = pickle.load(file)

prediction2 = model.predict(new_X.toarray())

df_test2, acc2 = cal_acc(prediction2)