import os
import sys
import csv
import random
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from model.naive_bayes import NaiveBayesClassifier


def load_dataset(path: str):
    X, y = [], []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append(row["text"])
            y.append(int(row["label"]))
    return X, y


def evaluate(clf: NaiveBayesClassifier, X_test, y_test):
    tp = tn = fp = fn = 0
    for text, true_label in zip(X_test, y_test):
        pred = clf.predict(text)
        if pred == 1 and true_label == 1: tp += 1
        elif pred == 0 and true_label == 0: tn += 1
        elif pred == 1 and true_label == 0: fp += 1
        else: fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy  = (tp + tn) / len(y_test)

    print("\n=== RAPPORT D'ÉVALUATION ===")
    print(f"  Accuracy  : {accuracy:.4f}")
    print(f"  Precision : {precision:.4f}  (parmi les SMS marqués fraude, combien le sont vraiment)")
    print(f"  Recall    : {recall:.4f}  (parmi les vraies fraudes, combien on détecte)")
    print(f"  F1-Score  : {f1:.4f}")
    print("\n=== MATRICE DE CONFUSION ===")
    print(f"  Vrais Négatifs (TN): {tn}  |  Faux Positifs (FP): {fp}")
    print(f"  Faux Négatifs (FN): {fn}  |  Vrais Positifs (TP): {tp}")


def train():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
    if not os.path.exists(data_path):
        print("ERREUR: dataset.csv introuvable. Lancez d'abord: python data/generate_data.py")
        sys.exit(1)

    X, y = load_dataset(data_path)
    print(f"Dataset chargé : {len(X)} exemples")
    dist = Counter(y)
    print(f"Distribution   : {dist[0]} légitimes / {dist[1]} fraudes\n")

    # Split 80/20 stratifié
    combined = list(zip(X, y))
    random.seed(42)
    random.shuffle(combined)
    split = int(len(combined) * 0.8)
    train_data, test_data = combined[:split], combined[split:]

    X_train = [x for x, _ in train_data]
    y_train = [y for _, y in train_data]
    X_test  = [x for x, _ in test_data]
    y_test  = [y for _, y in test_data]

    print("Entraînement du modèle Naive Bayes...")
    clf = NaiveBayesClassifier(alpha=1.0)
    clf.fit(X_train, y_train)
    print(f"Vocabulaire : {len(clf.vocab)} tokens")

    evaluate(clf, X_test, y_test)

    model_path = os.path.join(os.path.dirname(__file__), "fraud_detector.pkl")
    clf.save(model_path)
    print(f"\nModèle sauvegardé : {model_path}")
    return clf


if __name__ == "__main__":
    train()
