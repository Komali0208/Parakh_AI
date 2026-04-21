import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

nltk.download('punkt')
nltk.download('punkt_tab')

def main():
    try:
        df = pd.read_csv('data_for_preprocessing.csv')
    except Exception as e:
        print(f"Error loading csv: {e}")
        return

    # Drop any rows where Text is null or empty after stripping whitespace.
    df = df.dropna(subset=['Text'])
    df['Text'] = df['Text'].astype(str).str.strip()
    df = df[df['Text'] != '']

    sentences = []
    labels = []
    
    for _, row in df.iterrows():
        text = row['Text']
        author = row['Author']
        sents = sent_tokenize(text)
        for s in sents:
            sentences.append(s)
            labels.append(author)
            
    filtered_sentences = []
    filtered_labels = []
    for s, l in zip(sentences, labels):
        if len(s) >= 10:
            filtered_sentences.append(s)
            filtered_labels.append(l)

    new_df = pd.DataFrame({'Text': filtered_sentences, 'Author': filtered_labels})

    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1,2), sublinear_tf=True)
    
    X = new_df['Text']
    y = new_df['Author']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    model = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
    model.fit(X_train_vec, y_train)
    
    y_pred = model.predict(X_test_vec)
    print(classification_report(y_test, y_pred))
    
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    
    print("Training complete. model.pkl and vectorizer.pkl saved.")

if __name__ == '__main__':
    main()
