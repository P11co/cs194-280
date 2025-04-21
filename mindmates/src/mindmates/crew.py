# crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Assuming your filter function is available (e.g., from utils)
# from mindmates.utils.llm_utils import filter_lifestyle_experts # Example import

@CrewBase
class Mindmates():
    """Mindmates crew factory/definitions"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml' # You might use this for static task parts

    # --- Agent Definitions ---
    # Define ALL potential agents using the @agent decorator
    # This allows the class to instantiate them when requested.

    @agent
    def therapy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['therapy_agent'],
            verbose=True,
            memory=True # Agent-level memory can be enabled here if needed
        )

    @agent
    def workstudy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['workstudy_agent'],
            verbose=True
        )

    @agent
    def relationship_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['relationship_agent'],
            verbose=True
        )

    @agent
    def hobby_agent(self) -> Agent: # Corrected name
        return Agent(
            config=self.agents_config['hobby_agent'],
            verbose=True
        )

    @agent
    def exercise_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['exercise_agent'],
            verbose=True
        )

    @agent
    def food_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['food_agent'],
            verbose=True
        )

    # --- Method to get specific agents by name ---
    # This is useful for dynamically fetching agents in gram.py
    def get_agent_by_name(self, name: str) -> Agent | None:
        """Retrieves an instantiated agent by its method name."""
        if hasattr(self, name):
            method = getattr(self, name)
            if callable(method) and hasattr(method, '_is_crew_agent'): # Check if it's decorated
                 # Call the decorated method to get the Agent instance
                 # Pass self if the method requires it (which decorated methods do implicitly)
                return method(self)
        return None

    # Optional: A method to create a basic crew if ever needed,
    # but we will create it dynamically in gram.py
    @crew
    def base_crew(self) -> Crew:
        """Creates a base crew - Adjust as needed if you have static tasks"""
        return Crew(
            agents=[self.therapy_agent()], # Example: Just the therapy agent
            tasks=[], # Define base tasks if any
            process=Process.sequential,
            memory=True,
            verbose=True
        )
