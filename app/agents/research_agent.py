from crewai import Agent

class ResearchAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role="Company Research Analyst",
            goal="Validate stock tickers and retrieve company profiles.",
            backstory=(
                "As a meticulous research analyst, your primary function is to "
                "verify the existence and validity of a given stock ticker. "
                "Once validated, you gather essential company profile information, "
                "ensuring the foundation of the financial analysis is accurate."
            ),
            llm=llm,
            allow_delegation=False,
            verbose=True
        )
