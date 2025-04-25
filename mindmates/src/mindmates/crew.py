from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
import json

file_path = '/home/vertex_ai_service_account.json' # modify it to the actual path of vertex ai service account credential file
with open(file_path, 'r') as file:
    vertex_credentials = json.load(file)
vertex_credentials_json = json.dumps(vertex_credentials)

VERBOSE = False

@CrewBase
class Mindmates():
    """Mindmates crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml' # You might use this for static task parts

    @agent
    def checkInAgent(self) -> Agent:
        return Agent(
            llm=LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                vertex_credentials=vertex_credentials_json
            ),
            config=self.agents_config['check_in_agent'],
            verbose=VERBOSE
        )
    
    @agent
    def companionChatbotAgent(self) -> Agent:
        return Agent(
            llm=LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                vertex_credentials=vertex_credentials_json
            ),
            config=self.agents_config['companion_chatbot_agent'],
            verbose=VERBOSE,
        )
    
    @agent
    def contextSummaryAgentPatient(self) -> Agent:
        return Agent(
            llm=LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                vertex_credentials=vertex_credentials_json
            ),
            config=self.agents_config['context_summary_agent_patient'],
            verbose=VERBOSE
        )

    @agent
    def calendarEventsAgent(self) -> Agent:
        return Agent(
            llm=LLM(
                model="gemini/gemini-2.0-flash",
                temperature=0.7,
                vertex_credentials=vertex_credentials_json
            ),
            config=self.agents_config['calendar_events_agent'],
            verbose=VERBOSE,
        )

    @task
    def checkInTask(self) -> Task:
        return Task(
            config=self.tasks_config['check_in_task'],
        )
    
    @task
    def chatTask(self) -> Task:
        return Task(
            config=self.tasks_config['chat_task'],
        )

    @task
    def contextSummaryPatientTask(self) -> Task:
        return Task(
            config=self.tasks_config['context_summary_patient_task'],
        )
    
    @task
    def calendarEventTask(self) -> Task:
        return Task(
            config=self.tasks_config['calendar_event_task'],
            output_file="./knowledge/calendar.txt",
        )
    
    @crew
    def checkInCrew(self) -> Crew:
        """Creates the check-in crew"""

        return Crew(
            agents=[self.checkInAgent()],
            tasks=[self.checkInTask()],
            process=Process.sequential,
            verbose=VERBOSE,
        )
    
    @crew
    def chatCrew(self) -> Crew:
        """Creates the chat crew"""

        return Crew(
            agents=[self.companionChatbotAgent(), self.contextSummaryAgentPatient(), self.calendarEventsAgent()],
            tasks=[self.chatTask(), self.contextSummaryPatientTask(), self.calendarEventTask()],
            process=Process.sequential,
            verbose=VERBOSE,
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