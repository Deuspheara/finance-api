from typing import Any

from pydantic import BaseModel


class PortfolioRequest(BaseModel):
    assets: list[dict[str, Any]]  # e.g., [{"symbol": "AAPL", "weight": 0.5, "price": 150.0}, ...]


class PortfolioResponse(BaseModel):
    analysis: dict[str, Any]  # e.g., {"expected_return": 0.1, "volatility": 0.2, "sharpe_ratio": 1.5}
