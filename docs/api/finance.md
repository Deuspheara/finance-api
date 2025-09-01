# Finance Tools API

## Overview

The finance tools API provides portfolio analysis capabilities with usage limits based on subscription tiers. All endpoints require authentication and enforce user isolation.

## Endpoints

### Analyze Portfolio

Perform portfolio analysis on a collection of assets.

**Endpoint:** `POST /api/v1/finance/portfolio/analyze`

**Authentication:** Required (JWT token)

**Request Body:**
```json
{
  "assets": [
    {
      "symbol": "AAPL",
      "weight": 0.6,
      "price": 150.0
    },
    {
      "symbol": "GOOGL",
      "weight": 0.4,
      "price": 2500.0
    }
  ]
}
```

**Response:**
```json
{
  "analysis": {
    "expected_return": 0.085,
    "volatility": 0.15,
    "sharpe_ratio": 0.567
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid asset data or empty portfolio
- `401 Unauthorized`: Invalid or missing authentication
- `429 Too Many Requests`: Usage limit exceeded for portfolio analyses

## Usage Limits

Portfolio analysis requests are limited by subscription tier:

- **Free Tier:** 5 analyses per month
- **Premium Tier:** 100 analyses per month

Limits reset monthly based on subscription creation date.

## Analysis Features

The portfolio analyzer calculates:

- **Expected Return:** Weighted average return of all assets
- **Volatility:** Standard deviation of asset returns
- **Sharpe Ratio:** Risk-adjusted return measure

### With NumPy/Pandas (Recommended)
When available, the analyzer uses NumPy for precise mathematical calculations:
- Efficient matrix operations for large portfolios
- Statistical functions for volatility calculations
- Optimized performance for complex analyses

### Fallback Mode
Without NumPy/Pandas, provides basic analysis:
- Simple weighted average calculations
- Basic asset count reporting
- Placeholder for advanced metrics

## Data Models

### PortfolioRequest
```python
{
  "assets": List[Dict[str, Any]]  # Asset data with symbol, weight, price
}
```

**Asset Structure:**
```python
{
  "symbol": str,     # Asset symbol/ticker
  "weight": float,   # Portfolio weight (0.0 to 1.0)
  "price": float     # Current asset price
}
```

### PortfolioResponse
```python
{
  "analysis": Dict[str, Any]  # Analysis results
}
```

**Analysis Structure (with NumPy):**
```python
{
  "expected_return": float,   # Expected portfolio return
  "volatility": float,        # Portfolio volatility (standard deviation)
  "sharpe_ratio": float       # Sharpe ratio (return/volatility)
}
```

**Analysis Structure (fallback):**
```python
{
  "message": str,             # Status message
  "assets_count": int         # Number of assets analyzed
}
```

## Validation Rules

- **Assets:** Must contain at least 1 asset
- **Weights:** Must sum to 1.0 (portfolio is fully allocated)
- **Prices:** Must be positive numbers
- **Symbols:** Must be non-empty strings

## Usage Tracking

Each successful analysis:
- Logs usage in the database
- Increments user's monthly usage counter
- Enforces subscription limits before processing

## Notes

- Analysis is performed synchronously
- Results are not cached (each request recalculates)
- Large portfolios (>100 assets) may have performance implications
- All calculations assume daily returns and risk-free rate of 0 for Sharpe ratio