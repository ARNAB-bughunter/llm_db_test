from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json, pymongo
from config import ConfigData
from example import ExampleData

# Load Schema and Examples
table_schema = ConfigData.TABLE_SCHEMA
schema_description = ConfigData.SCHEMA_DESCRIPTION
json_ex_1 = ExampleData.FEW_SHOT_EXAMPLE_1
json_ex_2 = ExampleData.FEW_SHOT_EXAMPLE_2
json_ex_3 = ExampleData.FEW_SHOT_EXAMPLE_3
json_ex_4 = ExampleData.FEW_SHOT_EXAMPLE_4

# MongoDB Connection
client = pymongo.MongoClient(ConfigData.MONGO_DB_URI)
db = client[ConfigData.DB_NAME]
collection_name = db[ConfigData.COLLECTION_NAME]

# Convert Examples to JSON Strings
json_ex_string_1 = json.dumps(json_ex_1)
json_ex_string_2 = json.dumps(json_ex_2)
json_ex_string_3 = json.dumps(json_ex_3)
json_ex_string_4 = json.dumps(json_ex_4)

pipeline = ""

# Initialize the Primary LLM for Query Generation
primary_llm = OllamaLLM(model="Mistral", base_url="http://140.245.5.20:11434", num_thread=20)

# Initialize the Secondary LLM for Cross-Verification (Different Model or Instance)
verification_llm = OllamaLLM(model="llama3.2", base_url="http://140.245.5.20:11434", num_thread=20)

# Prompt Template for Query Generation
query_prompt_template = ChatPromptTemplate.from_template(
    """
    You are an expert MongoDB query generator. 
    I will provide you with the table schema and a user question. 
    Your task is to generate a MongoDB aggregation pipeline query.

    Table schema: {table_schema}
    Schema Description: {schema_description}

    Here are some example queries:
    Input: find all completed tasks
    Output: {json_ex_string_1} 
    Input: find all completed tasks for userid 2, only return title
    Output: {json_ex_string_2} 
    Input: How many tasks has each user completed and not completed?
    Output: {json_ex_string_3}
    Input: What percentage of tasks has each user completed?
    Output: {json_ex_string_4}

    Return only the JSON query, nothing else.
    Input: {user_question}
    """
)

# LLM Chain for Query Generation
query_generation_chain = query_prompt_template | primary_llm

# Tool: Generate MongoDB Query
def generate_query(question: str):
    """Generates a MongoDB aggregation query from natural language input."""
    response = query_generation_chain.invoke({
        "user_question": question,
        "table_schema": table_schema,
        "schema_description": schema_description,
        "json_ex_string_1": json_ex_string_1,
        "json_ex_string_2": json_ex_string_2,
        "json_ex_string_3": json_ex_string_3,
        "json_ex_string_4": json_ex_string_4,
    })
    global pipeline
    pipeline = json.loads(response)

# Verification Prompt Template
verification_prompt_template = ChatPromptTemplate.from_template(
    """
    You are a MongoDB query validation expert. You will receive a MongoDB aggregation pipeline query, user question and the table schema along with Schema Description.
    Your task is to check if the query correctly answers the user question.

    Table schema: {table_schema}
    Schema Description: {schema_description}
    
    User Question: {user_question}
    Generated Query: {generated_query}

    If the query is correct, return "VALID".
    If the query is incorrect, return "INVALID" and explain why.
    """
)

# LLM Chain for Query Verification
query_verification_chain = verification_prompt_template | verification_llm

# Tool: Verify MongoDB Query
def verify_query(question: str):
    """Verifies if the MongoDB query correctly answers the user’s question."""
    response = query_verification_chain.invoke({
        "table_schema": table_schema,
        "schema_description": schema_description,
        "user_question": question,
        "generated_query": json.dumps(pipeline)
    })
    
    if "VALID" in response:
        return {"status": "VALID"}
    else:
        return {"status": "INVALID", "reason": response}

# Tool: Execute MongoDB Query
def execute_query(question: str):
    """Executes the given MongoDB aggregation query and returns results."""
    try:
        results = collection_name.aggregate(pipeline)
        return list(results)  # Convert cursor to a list for output
    except Exception as e:
        print("ERROER!!!!!!")
        return {"error": str(e)}

# Define Tools for Agent
tools = [
    Tool(
        name="GenerateMongoDBQuery",
        func=generate_query,
        description="Generates a MongoDB aggregation query from natural language input."
    ),
    Tool(
        name="VerifyMongoDBQuery",
        func=verify_query,
        description="Verifies if the generated MongoDB aggregation query correctly answers the user’s question."
    ),
    Tool(
        name="ExecuteMongoDBQuery",
        func=execute_query,
        description="Executes a given MongoDB aggregation query and returns results."
    )
]

# Add Memory for Conversation
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize Agent
agent = initialize_agent(
    tools=tools,
    llm=primary_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True
)


question = "Which users have completed at least 10 tasks?"
question = "find all complete task for user with userid 1"
result = agent.invoke({"input": question})