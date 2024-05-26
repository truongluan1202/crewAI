import os
from common.routine import (
    get_api_key_data,
    open_db_connection,
)
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# Open database connection and retrieve API data
myOpenedDb, myOpenedClient = open_db_connection("MONGOATLAS")
apiData = get_api_key_data("data-science-team", myOpenedDb)

# Set environment variables for API keys
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = apiData["apiKey"]

# Initialize search tool
search_tool = SerperDevTool()

# Create a researcher agent
researcher = Agent(
    role="Senior Researcher",
    goal="Gather detailed financial and ESG data for {company_name}",
    verbose=True,
    memory=True,
    backstory="Expert in extracting key company metrics to inform strategic decisions.",
    tools=[search_tool],
    allow_delegation=True,
)

# Define research task to gather specific attributes
research_task = Task(
    description=(
        "Retrieve and analyze financial for {company_name}."
        "Focus on gathering Company Revenue, Net Profit Margin metrics."
        "Provide a clear summary of these metrics."
    ),
    expected_output="A concise bullet-point summary of Company Revenue, Net Profit Margin metrics.",
    tools=[search_tool],
    agent=researcher,
)

# Define writer agent to format the retrieved data
writer = Agent(
    role="Writer",
    goal="Format the data into a readable bullet-point summary for {company_name}",
    verbose=True,
    memory=True,
    backstory="Skilled in presenting complex data in an easily understandable format.",
    tools=[search_tool],
    allow_delegation=False,
)

# Define writing task
write_task = Task(
    description=(
        "Compose a concise bullet-point summary of the financial metrics for {company_name}."
        "Ensure the summary is clear and provides the values for each metric."
    ),
    expected_output="A bullet-point summary formatted as markdown.",
    tools=[search_tool],
    agent=writer,
    async_execution=False,
    output_file="company-summary.md",
)

# Form a crew with the researcher and writer agents
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True,
)

# Kickoff the process to retrieve and format data for a specific company
result = crew.kickoff(inputs={"company_name": "Microsoft"})
print(result)
