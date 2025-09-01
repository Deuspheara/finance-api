from pydantic import BaseModel
from typing import List, Dict, Any


class PortfolioRequest(BaseModel):
    assets: List[Dict[str, Any]]  # e.g., [{"symbol": "AAPL", "weight": 0.5, "price": 150.0}, ...]


class PortfolioResponse(BaseModel):
    analysis: Dict[str, Any]  # e.g., {"expected_return": 0.1, "volatility": 0.2, "sharpe_ratio": 1.5}