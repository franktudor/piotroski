from crewai import Crew, Process, Task
from app.agents.research_agent import ResearchAgent
from app.agents.data_agent import DataAgent
from app.agents.scoring_agent import ScoringAgent
from app.agents.writer_agent import WriterAgent
from ollama_llm import OllamaLLM

class TickerCrew:
    def __init__(self, ticker: str):
        self.ticker = ticker
        llm = OllamaLLM()
        self.research_agent = ResearchAgent(llm=llm)
        self.data_agent = DataAgent(llm=llm)
        self.scoring_agent = ScoringAgent(llm=llm)
        self.writer_agent = WriterAgent(llm=llm)

    def run(self):
        # Define tasks for each agent.
        # For now, these are placeholders with simple descriptions.
        # They will be expanded later with tools and context.

        collect_profile_task = Task(
            description=f"Collect company profile for {self.ticker}",
            agent=self.research_agent,
            expected_output=f"A dictionary containing the company profile for {self.ticker}"
        )

        collect_financials_task = Task(
            description=f"Collect financial statements and ratios for {self.ticker}",
            agent=self.data_agent,
            expected_output=f"A dictionary containing the financial data for {self.ticker}"
        )

        compute_scores_task = Task(
            description=f"Compute investment scores for {self.ticker}",
            agent=self.scoring_agent,
            expected_output=f"A dictionary containing the computed scores for {self.ticker}"
        )

        write_summary_task = Task(
            description=f"Write a summary for {self.ticker}",
            agent=self.writer_agent,
            expected_output=f"A string containing the summary for {self.ticker}"
        )

        # Assemble the crew
        crew = Crew(
            agents=[self.research_agent, self.data_agent, self.scoring_agent, self.writer_agent],
            tasks=[collect_profile_task, collect_financials_task, compute_scores_task, write_summary_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result