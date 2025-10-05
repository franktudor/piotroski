from crewai import Agent

class DataAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role="Financial Data Engineer",
            goal="Extract and process financial statements and key ratios for a given company.",
            backstory=(
                "You are a data-focused engineer who specializes in sourcing, "
                "cleaning, and preparing financial data from various APIs. "
                "Your expertise lies in ensuring the data is accurate, timely, "
                "and ready for quantitative analysis."
            ),
            llm=llm,
            allow_delegation=False,
            verbose=True
        )
