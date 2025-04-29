from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import json

VERBOSE = True

@CrewBase
class Mindmates():
    """Mindmates crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml' # You might use this for static task parts
    
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
            config=self.agents_config['work_study_agent'],
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
            config=self.agents_config['hobby_entertainment_agent'],
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
        
    @agent
    def checkInAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['check_in_agent'],
            verbose=VERBOSE
        )
    
    @agent
    def contextSummaryAgentPatient(self) -> Agent:
        return Agent(
            config=self.agents_config['context_summary_agent_patient'],
            verbose=VERBOSE
        )

    @agent
    def calendarEventsAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['calendar_events_agent'],
            verbose=VERBOSE
        )
        
    @task
    def checkInTask(self) -> Task:
        return Task(
            config=self.tasks_config['check_in_task'],
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
            output_file="./src/memory_pool/calendar.json",
        )
    
    @crew
    def checkin_crew(self) -> Crew:
        """Creates the check-in crew"""

        return Crew(
            agents=[self.checkInAgent()],
            tasks=[self.checkInTask()],
            process=Process.sequential,
            verbose=VERBOSE,
        )
    
    @crew
    def memory_update_Crew(self) -> Crew:
        """Creates the chat crew"""
        
        from src.mindmates.utils.models import CalendarEvent
        
        return Crew(
            agents=[self.contextSummaryAgentPatient(), self.calendarEventsAgent()],
            tasks=[self.contextSummaryPatientTask(), self.calendarEventTask()],
            process=Process.sequential,
            verbose=VERBOSE,
            output_pydantic=CalendarEvent
        )

    # --- Method to get specific agents by name ---
    # This is useful for dynamically fetching agents in gram.py
    def get_agent_by_name(self, name: str) -> Agent | None:
        """Retrieves an instantiated agent by its method name."""
        if hasattr(self, name):
            method = getattr(self, name)
            # TODO: looks like there is no `_is_crew_agent` attribute, but instead
            # the `is_agent` attribute, and we don't need to pass in self?
            '''
            if callable(method) and hasattr(method, '_is_crew_agent'):
                 # Call the decorated method to get the Agent instance
                 # Pass self if the method requires it (which decorated methods do implicitly)
                return method(self)
            '''
            if callable(method) and hasattr(method, 'is_agent'):
                return method()
        return None
