from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json, pymongo
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from config import ConfigData
from example import ExampleData
from IPython.display import Image

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

class AgentState(TypedDict):
    question: str
    pipeline: list
    query_result : str
    is_valid_query : bool
    query_error : bool
    final_result :str



# Initialize the Primary LLM for Query Generation
primary_llm = OllamaLLM(model="Mistral")

# Initialize the Secondary LLM for Cross-Verification (Different Model or Instance)
verification_llm = OllamaLLM(model="llama3.2")





def generate_query(state: AgentState):
    """Generates a MongoDB aggregation query from natural language input."""
    
    question = state['question']

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

    response = query_generation_chain.invoke({
        "user_question": question,
        "table_schema": table_schema,
        "schema_description": schema_description,
        "json_ex_string_1": json_ex_string_1,
        "json_ex_string_2": json_ex_string_2,
        "json_ex_string_3": json_ex_string_3,
        "json_ex_string_4": json_ex_string_4,
    })


    state['pipeline'] = json.dumps(response)

    print("pipeline ==>\n\n ",state['pipeline'])
    print("pipeline ==>\n\n ",type(state['pipeline']))
    
    return state



def verify_query(state: AgentState):
    """Verifies if the MongoDB query correctly answers the user’s question."""
    
    question = state['question']
    pipeline = state['pipeline']

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
    response = query_verification_chain.invoke({
        "table_schema": table_schema,
        "schema_description": schema_description,
        "user_question": question,
        "generated_query": json.dumps(pipeline)
    })
    
    if "VALID" in response:
        state["is_valid_query"] = True
    else:
        state["is_valid_query"] = False
    
    print("is_valid_query ==>\n\n", state['is_valid_query'])
    return state



def execute_query(state: AgentState):
    """Executes the given MongoDB aggregation query and returns results."""
    
    pipeline = json.loads(state['pipeline'])
    print("ARNAB ")
    print(pipeline, type(pipeline))


    
    

    try:
        text_ = ""
        results = collection_name.aggregate(pipeline)

        # return list(results)  # Convert cursor to a list for output
        for doc in results:
            text_ += str(doc)
        state['query_result'] = text_
        state['query_error'] = False
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        state['query_error'] = True
    
    print("query_error ==>\n\n", state['query_error'])
    
    return state


def generate_human_readable_answer(state: AgentState):
    """Show The Final result To The User"""

    pipeline = state["pipeline"]
    query_result = state["query_result"]



    # Human reable Prompt Template
    human_readable_answer_prompt_template = ChatPromptTemplate.from_template(
        """You are an assistant that converts MongoDB pipeline results into clear, natural language responses without including any identifiers like order userId, _Id. Start the response with a friendly greeting.
        MongoDB pipeline : {pipeline}
        results : {query_result}
        """)

    # LLM Chain for Convert Result into human readable answer
    human_readable_answer_chain = human_readable_answer_prompt_template | primary_llm

    response = human_readable_answer_chain.invoke({
      "pipeline" : pipeline,
      "query_result" : query_result
    })

    state["final_result"] = response

    print("final_result ==>\n\n", state['final_result'])

    return state


###############################################

def check_regenerate_query(state: AgentState):
    if state.get("query_error"):
        return "REGENERATE"
    else:
        return "DONE"


def execute_sql_router(state: AgentState):
    if state.get("is_valid_query"):
        return "VALID"
    else:
        return "INVALID"


################################################

workflow = StateGraph(AgentState)

workflow.add_node("generate_query", generate_query)
workflow.add_node("verify_query", verify_query)
workflow.add_node("execute_query", execute_query)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)

workflow.add_edge("generate_query","verify_query")


workflow.add_conditional_edges(
    "verify_query",
    execute_sql_router,
    {
        "VALID" : "execute_query",
        "INVALID" : "generate_query"
    }

)



workflow.add_conditional_edges(
    "execute_query",
    check_regenerate_query,
    {
        "REGENERATE" : "generate_query",
        "DONE" : "generate_human_readable_answer"
    }

)


workflow.set_entry_point("generate_query")
workflow.set_finish_point("generate_human_readable_answer")

app = workflow.compile()



user_question_1 = "What was the first and most recent task added for each user?"
result_1 = app.invoke({"question": user_question_1})
print("Result: \n\n", result_1['final_result'])



# try:
#     # Generate the Mermaid diagram image data
#     image_data = app.get_graph().draw_mermaid_png()
#     # Save to file
#     with open("my_diagram.png", "wb") as f:  # "wb" = write-binary mode
#         f.write(image_data)    
# except Exception as e:
#     print(f"Error: {str(e)}")
#     # Handle missing dependencies or other issues here