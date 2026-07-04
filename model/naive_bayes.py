"""
Multinomial Naive Bayes pour la détection de SMS frauduleux.
Implémentation pure Python — aucune dépendance externe.
"""
import re
import math
import pickle
from collections import defaultdict
from typing import List, Tuple


def tokenize(text: str) -> List[str]:
    text = text.lower()
    # Garde les mots et les nombres (montants FCFA, numéros)
    tokens = re.findall(r"[a-zàâäéèêëîïôùûüçœæ0-9]+", text)
    # Bigrammes pour capturer des expressions clés ("par erreur", "code pin"...)
    bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
    return tokens + bigrams


class NaiveBayesClassifier:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha          # lissage de Laplace
        self.classes: List[int] = []
        self.log_priors: dict = {}
        self.log_likelihoods: dict = {}
        self.vocab: set = set()

    def fit(self, X: List[str], y: List[int]) -> "NaiveBayesClassifier":
        self.classes = list(set(y))
        n_total = len(y)

        # Comptage par classe
        class_counts: dict[int, int] = defaultdict(int)
        word_counts: dict[int, dict[str, int]] = {c: defaultdict(int) for c in self.classes}

        for text, label in zip(X, y):
            class_counts[label] += 1
            for token in tokenize(text):
                word_counts[label][token] += 1
                self.vocab.add(token)

        vocab_size = len(self.vocab)

        # Log-probabilités a priori
        self.log_priors = {
            c: math.log(class_counts[c] / n_total)
            for c in self.classes
        }

        # Log-vraisemblances avec lissage de Laplace
        self.log_likelihoods = {}
        for c in self.classes:
            total_words = sum(word_counts[c].values()) + self.alpha * vocab_size
            self.log_likelihoods[c] = {
                word: math.log((count + self.alpha) / total_words)
                for word, count in word_counts[c].items()
            }
            # Valeur par défaut pour les mots hors vocabulaire
            self.log_likelihoods[c]["__unk__"] = math.log(self.alpha / total_words)

        return self

    def predict_proba(self, text: str) -> dict[int, float]:
        tokens = tokenize(text)
        scores = {}
        for c in self.classes:
            score = self.log_priors[c]
            unk = self.log_likelihoods[c]["__unk__"]
            for token in tokens:
                score += self.log_likelihoods[c].get(token, unk)
            scores[c] = score

        # Convertir log-scores en probabilités via softmax
        max_score = max(scores.values())
        exp_scores = {c: math.exp(s - max_score) for c, s in scores.items()}
        total = sum(exp_scores.values())
        return {c: v / total for c, v in exp_scores.items()}

    def predict(self, text: str) -> int:
        proba = self.predict_proba(text)
        return max(proba, key=lambda c: proba[c])

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str) -> "NaiveBayesClassifier":
        with open(path, "rb") as f:
            return pickle.load(f)
