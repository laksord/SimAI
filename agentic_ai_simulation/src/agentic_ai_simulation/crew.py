from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import sys

sys.setrecursionlimit(1500)

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AgenticAiSimulation():
	"""AgenticAiSimulation crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def kid1(self) -> Agent:
		return Agent(
			config=self.agents_config['kid1'],
			verbose=False
		)

	@agent
	def kid2(self) -> Agent:
		return Agent(
			config=self.agents_config['kid2'],
			verbose=True
		)

	@agent
	def parent1(self) -> Agent:
		return Agent(
			config=self.agents_config['parent1'],
			verbose=True
		)

	@agent
	def parent2(self) -> Agent:
		return Agent(
			config=self.agents_config['parent2'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
	    return Agent(
	      config=self.agents_config['reporting_analyst'],
	      verbose=True
	    )

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def sim1(self) -> Task:
		return Task(
			config=self.tasks_config['kid1_sim'],
		)

	@task
	def sim2(self) -> Task:
		return Task(
			config=self.tasks_config['kid2_sim'],
		)

	@task
	def psim1(self) -> Task:
		return Task(
			config=self.tasks_config['parent1_sim'],
		)

	@task
	def psim2(self) -> Task:
		return Task(
			config=self.tasks_config['parent2_sim'],
		)


	@task
	def reporting_task(self) -> Task:
	    return Task(
	      config=self.tasks_config['reporting_task'],
	      output_file='output/report.md',
	      context = [self.psim1(), self.psim2(), self.sim2(), self.sim1()]
	    )


	@crew
	def crew(self) -> Crew:
		"""Creates the AgenticAiSimulation crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
