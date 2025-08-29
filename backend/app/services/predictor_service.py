from __future__ import annotations
from typing import Dict, Deque, Optional
from collections import deque
from dataclasses import dataclass
from sklearn.linear_model import SGDClassifier
import numpy as np
import asyncio


@dataclass
class OnlineState:
    X: Deque[np.ndarray]
    y: Deque[int]
    clf: SGDClassifier
    lock: asyncio.Lock  # concurrency safety


class PredictorService:
    """Online logistic regression model trained on rolling sentiment mean.

    Labels: 1 if next minute price change > 0 else 0.
    """
    def __init__(self, maxlen: int = 500, warmup: int = 10):
        self.states: Dict[str, OnlineState] = {}
        self.maxlen = maxlen
        self.warmup = warmup

    def _get_state(self, symbol: str) -> OnlineState:
        if symbol not in self.states:
            self.states[symbol] = OnlineState(
                X=deque(maxlen=self.maxlen),
                y=deque(maxlen=self.maxlen),
                clf=SGDClassifier(
                    loss="log_loss",
                    max_iter=1,
                    learning_rate="optimal",
                    tol=None,
                    random_state=42,
                ),
                lock=asyncio.Lock(),
            )
        return self.states[symbol]

    async def update(self, symbol: str, sentiment_avg_5m: float, next_up: Optional[int]) -> None:
        """Update model with new sample (online learning)."""
        if next_up is None:
            return

        st = self._get_state(symbol)
        x = np.array([[sentiment_avg_5m]], dtype=np.float32)

        async with st.lock:
            st.X.append(x[0])
            st.y.append(int(next_up))

            if len(st.y) >= self.warmup:
                try:
                    # Online training with latest sample
                    st.clf.partial_fit(x, [int(next_up)], classes=np.array([0, 1], dtype=np.int32))
                except Exception as e:
                    # Model training should never block system
                    print(f"[PredictorService] Training error for {symbol}: {e}")

    async def predict_proba(self, symbol: str, sentiment_avg_5m: float) -> Optional[float]:
        """Predict probability of price going up given sentiment average."""
        st = self._get_state(symbol)

        if len(st.y) < self.warmup:
            return None

        x = np.array([[sentiment_avg_5m]], dtype=np.float32)

        async with st.lock:
            try:
                return float(st.clf.predict_proba(x)[0, 1])
            except Exception as e:
                print(f"[PredictorService] Prediction error for {symbol}: {e}")
                return None
