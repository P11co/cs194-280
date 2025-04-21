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
    tasks_config = 'config/tasks.yaml'

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
        )
