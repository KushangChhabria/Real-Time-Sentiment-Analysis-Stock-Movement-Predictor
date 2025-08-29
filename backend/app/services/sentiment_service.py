from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

from ..models import SentimentResult, SentimentScore
from ..utils.text import clean_text


class SentimentService:
    def __init__(self, model_name: str = "yiyanghkust/finbert-tone", device: str | None = None):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.model.to(self.device)
        self.model.eval()
        
        # Example: {0:'neutral',1:'positive',2:'negative'}
        self.id2label = {int(k): v.lower() for k, v in self.model.config.id2label.items()}

    def score_texts(
        self,
        texts: List[str],
        symbol: Optional[str] = None,
        source: Optional[str] = None,
        meta: Optional[dict] = None
    ) -> List[SentimentResult]:
        """Score a batch of texts with FinBERT"""
        if not texts:
            return []

        cleaned = [clean_text(t) for t in texts]
        enc = self.tokenizer(cleaned, padding=True, truncation=True, return_tensors="pt", max_length=128)
        enc = {k: v.to(self.device) for k, v in enc.items()}

        with torch.no_grad():
            logits = self.model(**enc).logits

        probs = F.softmax(logits, dim=-1).cpu().numpy()

        results: List[SentimentResult] = []
        ts = datetime.utcnow()
        for i, text in enumerate(cleaned):
            scores = [
                SentimentScore(label=self.id2label[j], score=float(probs[i, j]))
                for j in range(probs.shape[1])
            ]
            dominant = max(scores, key=lambda x: x.score).label
            sr = SentimentResult(
                text=text,
                timestamp=ts,
                scores=scores,
                dominant=dominant,
                symbol=symbol,
                source=source,
                meta=meta or {},
            )
            results.append(sr)

        return results

    @staticmethod
    def to_scalar(sentiment: SentimentResult) -> float:
        """Convert sentiment result to scalar value for correlation with stock price"""
        score_map: Dict[str, float] = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}
        total = 0.0
        for s in sentiment.scores:
            total += score_map.get(s.label.lower(), 0.0) * s.score
        return float(total)
