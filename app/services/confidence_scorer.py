from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import pandas as pd
import numpy as np
import spacy
import joblib
import os

nlp = spacy.load("en_core_web_sm")
nli_model = pipeline("text-classification", model="roberta-large-mnli")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

class ConfidenceScoring:
    def __init__(
        self,
        MODEL_OUT="confidence_model_lgbm.joblib",
    ):
        self.model = joblib.load(MODEL_OUT)

    def _compute_feature_relevance_density(self, news_text, keywords):
        doc = nlp(news_text)
        sentences = list(doc.sents)
        if len(sentences) == 0:
            return 0.0
        count_relevant = sum(
            1
            for sent in sentences
            if any(k.lower() in sent.text.lower() for k in keywords)
        )
        return count_relevant / len(sentences)

    def _compute_contradiction_score(self, sentences):
        contradictions = 0
        total_pairs = 0
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                total_pairs += 1
                premise = sentences[i].text
                hypothesis = sentences[j].text
                result = nli_model(f"{premise} </s> {hypothesis}")[0]
                if result["label"] == "CONTRADICTION":
                    contradictions += 1
        return contradictions / total_pairs if total_pairs > 0 else 0.0

    def _compute_consistency_score(self, news_text, reasoning_summary=None):
        doc = nlp(news_text)
        sentences = [sent.text for sent in doc.sents]

        if reasoning_summary:
            sentences.append(reasoning_summary)

        if len(sentences) < 2:
            return 1.0
        
        embeds = embed_model.encode(sentences)
        sim_matrix = cosine_similarity(embeds)
        consistency = (np.sum(sim_matrix) - len(embeds)) / (
            len(embeds) * (len(embeds) - 1)
        )
        return consistency

    def _compute_reasoning_length(self, news_text):
        doc = nlp(news_text)
        return len(list(doc.sents))

    def _compute_reasoning_specificity(self, news_text):
        doc = nlp(news_text)
        sentences = list(doc.sents)

        if len(sentences) == 0:
            return 0.0
        
        specific_count = sum(
            1
            for sent in sentences
            if any(tok.ent_type_ or tok.like_num for tok in sent)
        )

        return specific_count / len(sentences)

    def _compute_semantic_uncertainty(self, news_text):
        doc = nlp(news_text)
        sentences = list(doc.sents)
        lengths = [len(sent) for sent in sentences]

        if len(lengths) == 0:
            return 0.0
        
        return np.std(lengths) / (np.mean(lengths) + 1e-6)

    def _compute_source_overlap_score(self, sources):
        if len(sources) < 2:
            return 0.5

        all_embeds = []
        for src in sources:
            chunks = [p.strip() for p in src.split("\n") if p.strip()]
            embeds = embed_model.encode(chunks, convert_to_tensor=True)
            all_embeds.append(embeds)

        n = len(all_embeds)
        pair_scores = []

        for i in range(n):
            for j in range(i + 1, n):
                sim_matrix = util.cos_sim(all_embeds[i], all_embeds[j])
                max_per_chunk = sim_matrix.max(dim=1).values
                pair_score = max_per_chunk.mean().item()
                pair_scores.append(pair_score)

        return np.mean(pair_scores)

    def compute_all_features(
        self, news_text, keywords=None, reasoning_summary=None, sources=None
    ):
        if keywords is None:
            keywords = []
        if sources is None:
            sources = []

        doc = nlp(news_text)
        sentences = list(doc.sents)

        features = {
            "feature_relevance_density": self._compute_feature_relevance_density(
                news_text, keywords
            ),
            "contradiction_score": self._compute_contradiction_score(sentences),
            "consistency_score": self._compute_consistency_score(
                news_text, reasoning_summary
            ),
            "reasoning_length": self._compute_reasoning_length(news_text),
            "reasoning_specificity": self._compute_reasoning_specificity(news_text),
            "semantic_uncertainty": self._compute_semantic_uncertainty(news_text),
            "source_overlap_score": self._compute_source_overlap_score(sources),
        }

        return features

    def predict(
        self,
        news_text,
        keywords,
        reasoning_summary,
        sources,
        llm_confidence=0,
        confidence_weight=[0.25, 0.7, 0.05],
    ):
        features = self.compute_all_features(
            news_text,
            keywords,
            reasoning_summary,
            sources,
        )
        raw_preds = self.model["model"].predict(pd.DataFrame([features]))
        llm_predicted_confidence = self.model["isotonic"].predict(raw_preds)
        source_overlap_score = features.get("source_overlap_score")
        source_overlap_score = 0 if not source_overlap_score else source_overlap_score
        weights = np.array(confidence_weight)
        weights = weights / weights.sum()
        
        return (
            confidence_weight[0] * llm_confidence
            + confidence_weight[1] * llm_predicted_confidence
            + confidence_weight[2] * source_overlap_score
        )

if __name__ == "__main__":
    from pprint import pprint

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "confidence_model_lgbm.joblib")

    scorer = ConfidenceScoring(MODEL_OUT=MODEL_PATH)

    news_text = "The government announced a new policy to reduce air pollution."

    keywords = ["government", "air pollution"]

    reasoning_summary = "Policy aims to reduce emissions and improve air quality."

    sources = [
        "Source A: Government press release on pollution control.",
        "Source B: News report summarizing the new policy.",
    ]

    llm_confidence = 0.85

    final_confidence = scorer.predict(
        news_text=news_text,
        keywords=keywords,
        reasoning_summary=reasoning_summary,
        sources=sources,
        llm_confidence=llm_confidence,
    )

    print("Final Confidence Score:", final_confidence)

    features = scorer.compute_all_features(
        news_text=news_text,
        keywords=keywords,
        reasoning_summary=reasoning_summary,
        sources=sources,
    )
    print("\nFeature breakdown:")
    pprint(features)
