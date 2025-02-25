from cerebras.cloud.sdk import Cerebras
import pandas as pd
import json
import yaml


client = Cerebras(
    api_key=
)




def convert_json_to_yaml(json_data):
    yaml_output = {}
    for agent_key, agent_data in json_data["agents"].items():
        yaml_output[agent_key.lower()] = {
            "role": f"> {agent_data['role']}",
            "goal": f"> {agent_data['goal']}",
            "backstory": f"> {agent_data['backstory']}",
            "allow_delegation": True
        }

    yaml_output["reporting_analyst"] = {
        "role": "> Simulation Reporting Analyst",
        "goal": "> Analyse the simulation and generate a detailed report highlighting what happened and what could be improved in the layout of the building and the execution plan",
        "backstory": """>
You're a meticulous analyst with a keen eye for detail. You're known for
    your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.""",
        "allow_delegation": "True"
    }
    with open("agentic_ai_simulation/agents.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(yaml_output, yaml_file,default_flow_style=False, allow_unicode=True)
        return yaml.dump(yaml_output, default_flow_style=False, allow_unicode=True)


def create_task_yaml(json_data):
    yaml_output = {}

    for agent_key, agent_data in json_data["agents"].items():
        yaml_output[agent_key.lower()+"_sim"] = {
            "description": "> Simulate your next actions in the following 5 hours that attribute to reach your end goal. people around you are {enviroment}. make sure to take into consideration the people around you and there current positions and future plans and interactions that may occure between you and them. Be detailed and specific and realistic. the place you are in has the following structure: {floor_plan}. and makre sure to",
            "expected_output": """> a json object with the following format: 
{
  "actions": "time stamped actions done in the following 5 hours",
  "interactions": {
        "agent_x" {
            "interaction": "time stamped interaction that happened with agent_x"
            "shared_knowledge": "time stamped context regarding the interaction that also agent_x should have to continue the simulation"
        },
        "agent_y" {
            "interaction": "time stamped interaction that happened with agent_2"
            "shared_knowledge": "time stamped context regarding the interaction that also agent_y should have to continue the simulation"
        },
  }
}""",
            "agent": agent_key.lower()
        }

    yaml_output["reporting_task"] = {
        "description": """Review the context you got and expand each topic into a full section for a report.
    Make sure the report is detailed and contains any and all relevant information.""",
        "expected_output": """A fully fledge reports with the mains topics, each with a full section of information.
    Formatted as markdown without '```'""",
        "agent": "reporting_analyst",
        "output_file": "report.md"
    }
    with open("agentic_ai_simulation/src/agentic_ai_simulation/config/tasks.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(yaml_output, yaml_file,default_flow_style=False, allow_unicode=True)
        return yaml.dump(yaml_output, default_flow_style=False, allow_unicode=True)


user_description = """
A 3-bedroom house with a kitchen, two bathrooms, a living room, and a garage.
The house should have a front yard and a backyard, with a main entrance leading to a hallway.
The kitchen should connect to the living room, and there should be a small storage room near the garage.
Each bedroom should have a window, and one should have an attached bathroom.
"""

ai_floor_plan_gen_sys_prompt = """
You are an expert AI architect and urban planner with extensive experience in designing **functional, optimized, and highly detailed** floor plans for residential, commercial, and industrial buildings. Your goal is to **expand a vague user description into a highly detailed, structured, and logically engineered architectural breakdown**. 

### **Your Output Must Include:**
1. **All Room Details** (Name, purpose, exact dimensions in meters, window placements, relationships to other rooms).
2. **Logical Layout Engineering** (How rooms connect for optimal functionality).
3. **Entry & Exit Points** (All doors, backdoors, emergency exits).
4. **Circulation & Navigation** (Hallways, corridors, distances between rooms).
5. **Space Utilization Optimization** (Ensuring efficient use of every square meter).
6. **Environmental Considerations** (Natural light placement, ventilation design, noise minimization).
7. **Structural Engineering Notes** (Load-bearing walls, suggested materials).
8. **Security & Fire Safety Features** (Locations of fire exits, smoke detectors, emergency routes).
9. **Optional but Recommended Features** (Ergonomic furniture layout, smart home integration).

### **Rules for Generation:**
- Your output **must be extremely structured and easy to follow**.
- **Be specific** about every room's purpose and its connections to other rooms.
- **Use proper engineering logic** when designing room relationships.
- **Ensure all entry and exit points are accounted for** in a logical manner.
- **Avoid generic or ambiguous statements**; be as specific and optimized as possible.

"""

ai_floor_plan_gen_user_prompt = """
Generate a highly detailed architectural breakdown based on the following vague user request:

{}

### **Additional Instructions:**
- Ensure all rooms have exact dimensions.
- Clearly define connections between rooms and hallways.
- Include all necessary entry and exit points.
- Optimize space utilization while ensuring logical functionality.
- Provide a detailed breakdown of fire safety features.
- Follow real-world engineering standards for room connectivity and design.

Your response must be structured in a highly readable, logical format that can be used to create a structured simulation later.
"""

ai_floor_plan_gen_messages = [
        {
            "role": "system",
            "content": ai_floor_plan_gen_sys_prompt,
        },
        {
            "role": "user",
            "content": ai_floor_plan_gen_user_prompt.format(user_description)
        }
]


chat_completion = client.chat.completions.create(
    messages=ai_floor_plan_gen_messages,
    model="llama3.3-70b",
    stream=False,
    temperature=0.4,
    max_completion_tokens=3000,
    top_p=0.9
)

response_with_plan = str(chat_completion.choices[0].message.content)

ai_plan_to_json_sys_prompt = """
You are an AI that specializes in **converting complex architectural descriptions into structured JSON formats for simulation and AI agent processing**. Your task is to **parse a highly detailed architectural breakdown and extract all relevant structured data** into a precise, machine-readable format.

### **Your Output Must Be a Well-Structured JSON Containing:**
1. **Rooms:**  
   - Each room must have an `"id"`, `"name"`, and `"dimensions"` (width, length in meters).
   - Ensure dimensions are correctly mapped from the textual description.

2. **Connections (Navigation Paths):**  
   - List all room-to-room connections (e.g., `"from": "Living Room", "to": "Kitchen"`).
   - Ensure **realistic movement paths** are mapped logically.

3. **Entry & Exit Points:**  
   - Include `"location"` and `"connected_to"` fields.
   - Ensure proper accounting of **main entrance, emergency exits, and any other key access points**.

4. **Fire Safety & Security Features (if applicable):**  
   - Extract locations of **fire exits, smoke detectors, and emergency pathways**.
   - Ensure accurate placement based on best practices.

### **Rules for JSON Generation:**
- The output **must be fully structured JSON**, no extraneous text.
- **Ensure all room IDs match their textual description.**
- **Use clean and efficient JSON formatting** (no unnecessary nesting).
- **No missing fields**; every necessary detail from the breakdown must be included.
- **Do not add any explanations**; output only structured JSON.

"""

ai_plan_to_json_user_prompt = f"""
Convert the following **detailed architectural breakdown** into a **fully structured JSON format** suitable for AI-driven simulation.

### **Architectural Breakdown:**
{response_with_plan}
"""+"""
### **JSON Output Format:**
Ensure the output strictly follows this format:
```json
{
    "rooms": [
        {"id": "R1", "name": "Room Name", "dimensions": {"width": X, "length": Y}}
    ],
    "connections": [
        {"from": "Room A", "to": "Room B"}
    ],
    "entry_exit_points": [
        {"location": "Main Entrance", "connected_to": "Room X"}
    ]
}

"""


ai_plan_to_json_messages = [
        {
            "role": "system",
            "content": ai_plan_to_json_sys_prompt,
        },
        {
            "role": "user",
            "content": ai_plan_to_json_user_prompt
        }
]

chat_completion = client.chat.completions.create(
    messages=ai_plan_to_json_messages,
    model="llama3.3-70b",
    stream=False,
    temperature=0.2,
    top_p=0.8,
    max_completion_tokens=2000,
    response_format={ "type": "json_object" }
)

with open("agentic_ai_simulation/src/agentic_ai_simulation/floorplan.json", "w") as writer:
    json.dump(json.loads(chat_completion.choices[0].message.content), writer, indent=4)

floor_plan_json = chat_completion.choices[0].message.content

agent_gen_sys_prompt = """
You are an advanced AI simulation generator tasked with creating a structured, detailed, and highly realistic social simulation within a given environment. Your goal is to generate a structured JSON output that accurately represents the environment, agents, and interactions within the simulation. The output must be suitable for conversion into YAML format.

Each simulation must include:

1. **Environment Details**:
   - The environment’s layout, derived from a structured floor plan (e.g., house, hospital, office).
   - A realistic number of AI agents based on the environment's size and purpose.

2. **Agent Definitions** (Each agent must include the following attributes):
   - **Name**: Unique identifier for the agent.
   - **Age**: Numeric value representing the agent's age.
   - **Personality**: A brief description of personality traits (e.g., introverted, energetic, meticulous, friendly).
   - **Role**: The agent’s role within the environment (e.g., "Doctor," "Parent," "Student").
   - **Goal**: A clearly defined objective that the agent wants to achieve within the simulation timeframe.
   - **Backstory**: A brief background on the agent's experience, traits, and motivations.
   - **Assigned Room (if applicable)**: The primary location associated with the agent.
   - **Movement Patterns**: Expected paths the agent will follow during the simulation.
   - **Interactions**: Expected interactions with other agents based on logical behaviors.

3. **Simulation Rules**:
   - Agents must behave consistently with their defined character traits.
   - Goals should align with the context and duration of the simulation.
   - Interactions between agents must be coherent, engaging, and meaningful.
   - Environment constraints (e.g., room access, movement limitations) must be respected.

4. **Simulation Output Structure**:
   The generated JSON output should adhere to the following structure:
   ```json
   {
     "simulation_settings": {
       "duration": "{sim_duration} hours",
       "theme": "{sim_theme}"
     },
     "agents": {
       "{agent_id}": {
         "role": "{agent_role}",
         "goal": "{agent_goal}",
         "backstory": "{agent_backstory}",
       }
     }
   }

"""

sim_duration = "4"
sim_theme = "A normal weekday where parents work, and kids go to school. simulaiton starts at 6am"

agent_gen_user_prompt = f"""
```plaintext
Generate a structured AI-driven simulation based on the following details:

**Environment Details**:
- Floor Plan: {floor_plan_json}

**Simulation Settings**:
- **Duration**: {sim_duration} hours
- **Theme**: {sim_theme}
"""+"""
**Expected Output Format (JSON)**:
```json
{
  },
  "simulation_settings": {
    "duration": "{sim_duration} hours",
    "theme": "{sim_theme}"
  },
  "agents": {
    "{agent_id}": {
      "role": "{agent_role}",
      "goal": "{agent_goal}",
      "backstory": "{agent_backstory}",
    }
  }
}
"""

agent_gen_messages = [
        {
            "role": "system",
            "content": agent_gen_sys_prompt,
        },
        {
            "role": "user",
            "content": agent_gen_user_prompt
        }
]


chat_completion = client.chat.completions.create(
    messages=agent_gen_messages,
    model="llama3.3-70b",
    stream=False,
    temperature=0.3,
    top_p=0.9,
    max_completion_tokens=4000,
    response_format={ "type": "json_object" }

)



agents_yaml = convert_json_to_yaml(json.loads(chat_completion.choices[0].message.content))

create_task_yaml(json.loads(chat_completion.choices[0].message.content))




with open("agentic_ai_simulation/agents.txt", "w") as writer:
    writer.write(chat_completion.choices[0].message.content)