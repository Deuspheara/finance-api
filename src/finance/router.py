from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import get_current_active_user
from src.finance.dependencies import get_portfolio_analyzer
from src.finance.schemas import PortfolioRequest, PortfolioResponse
from src.finance.tools.portfolio_analyzer import PortfolioAnalyzer
from src.users.models import User

router = APIRouter()


@router.post("/portfolio/analyze", response_model=PortfolioResponse)
async def analyze_portfolio(
    request: PortfolioRequest,
    current_user: User = Depends(get_current_active_user),
    analyzer: PortfolioAnalyzer = Depends(get_portfolio_analyzer),
):
    # Set the user_id for the analyzer
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="User ID is required")
    analyzer.user_id = current_user.id

    try:
        # Run the analysis (this will check usage limit and log usage)
        result = await analyzer.run(request)
        return result
    except Exception as e:
        if "Usage limit exceeded" in str(e):
            raise HTTPException(status_code=500, detail="Usage limit exceeded")
        raise
