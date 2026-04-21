import os
import pickle
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Ensure punkt is downloaded for sentence splitting
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

MODEL_PATH = "model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

def get_or_train_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        return model, vectorizer

    documents = [
        "This is clearly written by a human. I can tell by the style.",
        "Furthermore, notably, researchers found that this might be AI generated.",
        "In this study we examine the effects. It is a very basic structure.",
        "Delve into the intricate tapestry of notably significant furthermore aspects.",
        "I just went to the store to get some milk.",
        "It is imperative to recognize that furthermore the framework provides a robust solution.",
    ]
    labels = ["Human", "AI", "Human", "AI", "Human", "AI"]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)
    
    model = LogisticRegression()
    model.fit(X, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    return model, vectorizer

model, vectorizer = get_or_train_model()
feature_names = vectorizer.get_feature_names_out()

def analyze_sentences(sentences):
    results = []
    if not sentences:
        return results

    X_test = vectorizer.transform(sentences)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)

    ai_idx = list(model.classes_).index("AI")

    for i, sentence in enumerate(sentences):
        label = preds[i]
        ai_prob = probs[i][ai_idx]

        sentence_vec = X_test[i].toarray()[0]
        top_indices = sentence_vec.argsort()[-3:][::-1]
        
        # Return keywords with scores to match Tooltip expectation
        top_keywords = [{"word": feature_names[idx], "score": float(sentence_vec[idx])} 
                        for idx in top_indices if sentence_vec[idx] > 0]

        # Use 0-1 confidence to match Highlight expectation
        # High AI probability = low human confidence (red)
        # Low AI probability = high human confidence (green)
        if label == "AI":
            confidence = 1.0 - ai_prob # Higher AI prob makes it redder (values close to 1 are greenest in frontend)
            # Actually frontend: hue = Math.round(confidence * 120) => 0 = red, 120 = green
            # so for AI (high AI probability) we want it red (low confidence score)
            # for Human (low AI probability) we want it green (high confidence score)
            # So confidence = (1.0 - ai_prob) is correct.
        else:
            confidence = (1.0 - ai_prob) # Also correct for human.

        results.append({
            "text": sentence, # Match Highlight expectation
            "label": label,
            "confidence": float(confidence),
            "keywords": top_keywords
        })

    return results
