from crewai import Agent

class ScoringAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Quantitative Financial Analyst",
            goal="Compute proprietary investment scores from raw financial data.",
            backstory=(
                "As a quantitative analyst, you are adept at implementing scoring "
                "models and financial algorithms. You take raw financial data and "
                "transform it into meaningful scores like the Piotroski F-Score, "
                "Value, and Growth investor scores, providing a clear quantitative "
                "picture of a company's health."
            ),
            allow_delegation=False,
            verbose=True
        )