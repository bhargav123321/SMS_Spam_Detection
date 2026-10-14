
import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from utils import clean_text


# 1. Load dataset
DATA_PATH = os.path.join("data", "SMSSpamCollection")
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(
    DATA_PATH,
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

print("\nFirst five rows:")
print(df.head())

print("\nDataset shape:", df.shape)
print("\nColumn information:")
df.info()

# 2. Check data quality
print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

df = df.dropna(subset=["label", "message"]).copy()
df["label"] = df["label"].str.strip().str.lower()
df["message"] = df["message"].astype(str)

# Keep only the expected labels.
df = df[df["label"].isin(["ham", "spam"])].copy()

# Remove exact duplicate records.
df = df.drop_duplicates().reset_index(drop=True)

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nClass percentages:")
print((df["label"].value_counts(normalize=True) * 100).round(2))

# 3. Clean messages
df["clean_message"] = df["message"].apply(clean_text)

# Remove messages that become empty after cleaning.
df = df[df["clean_message"].str.strip().ne("")].copy()

X = df["clean_message"]
y = df["label"]

# 4. Stratified train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining messages:", len(X_train))
print("Testing messages:", len(X_test))

# 5. Convert text into TF-IDF features.
# Fit ONLY on the training data to prevent data leakage.
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_features=20000,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

joblib.dump(
    vectorizer,
    os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
)

# 6. Train two classifiers
models = {
    "Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )
}

results = []
trained_models = {}

for name, model in models.items():
    print(f"\n{'=' * 55}")
    print(f"Training: {name}")

    model.fit(X_train_tfidf, y_train)
    predictions = model.predict(X_test_tfidf)

    trained_models[name] = model

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test, predictions, pos_label="spam", zero_division=0
    )
    recall = recall_score(
        y_test, predictions, pos_label="spam", zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, pos_label="spam", zero_division=0
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Spam Precision": precision,
        "Spam Recall": recall,
        "Spam F1-score": f1
    })

    print(classification_report(
        y_test,
        predictions,
        labels=["ham", "spam"],
        zero_division=0
    ))

    # 7. Confusion matrix
    cm = confusion_matrix(
        y_test, predictions, labels=["ham", "spam"]
    )

    plt.figure(figsize=(6, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["ham", "spam"],
        yticklabels=["ham", "spam"]
    )
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.title(f"Confusion Matrix - {name}")
    plt.tight_layout()

    safe_name = name.lower().replace(" ", "_")
    plt.savefig(
        os.path.join(MODEL_DIR, f"confusion_{safe_name}.png")
    )
    plt.close()

    # 8. Inspect false positives and false negatives
    errors = pd.DataFrame({
        "message": df.loc[X_test.index, "message"].values,
        "actual": y_test.values,
        "predicted": predictions
    })

    false_positives = errors[
        (errors["actual"] == "ham")
        & (errors["predicted"] == "spam")
    ]

    false_negatives = errors[
        (errors["actual"] == "spam")
        & (errors["predicted"] == "ham")
    ]

    print("False positives:", len(false_positives))
    print(false_positives.head(5).to_string(index=False))

    print("\nFalse negatives:", len(false_negatives))
    print(false_negatives.head(5).to_string(index=False))

    # 9. Save the trained model
    joblib.dump(
        model,
        os.path.join(MODEL_DIR, f"{safe_name}_model.pkl")
    )

# 10. Compare metrics
results_df = pd.DataFrame(results).sort_values(
    by="F1-score" if "F1-score" in results else "Spam F1-score",
    ascending=False
)

print("\nMODEL COMPARISON")
print(results_df.to_string(index=False))

results_df.to_csv(
    os.path.join(MODEL_DIR, "model_comparison.csv"),
    index=False
)

print("\nTraining completed successfully.")
print("Models and evaluation results saved in:", MODEL_DIR)
