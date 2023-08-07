import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from supervised.automl import AutoML
from tqdm import tqdm
from models.cleaning import clean_text

df = pd.read_csv("C:\\Users\\Irish\\Downloads\\fakenewsproject\\train.csv")
df = df[['text', 'label']]
df = df.dropna()

df = df.iloc[:5000]

# Data preprocessing
X = df["text"]
y = df["label"]

tqdm.pandas()

X_clean = X.progress_apply(lambda x: clean_text(x)).astype(str)


vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(X_clean)

print("Shape of X array:", X.shape )

if X.shape[0] == 0:
    raise ValueError("Empty array: X does not contain any samples.")

automl = AutoML(mode="Compete", algorithms=["CatBoost"], random_state=42)
automl.fit(X_tfidf.toarray(), y)

automl.report()

print(df.head())

df_test = df.iloc[0:5000]

text_test = df_test.text
X_test = text_test.apply(lambda x: clean_text(x)).astype(str)

new_X = vectorizer.transform(X_test)

predictions = automl.predict(new_X.toarray())

df_test['predictions'] = predictions
df_test[['label', 'predictions']]
accuracy = (df_test['label'] == df_test['predictions']).mean() * 100
print("Accuracy: {:.2f}%".format(accuracy))

import pickle

# Save the trained model to a pickle file
with open("C:\\Users\\Irish\\Downloads\\fakenewsproject\\automl_model.pkl", "wb") as file:
    pickle.dump(automl, file)

automl.report('C:\\Users\\Irish\\Downloads\\fakenewsproject\\report.html')

