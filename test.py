from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json, time, pymongo
from config import ConfigData
from example import ExampleData




table_schema = ConfigData.TABLE_SCHEMA
schema_description = ConfigData.SCHEMA_DESCRIPTION
json_ex_1 = ExampleData.FEW_SHOT_EXAMPLE_1
json_ex_2 = ExampleData.FEW_SHOT_EXAMPLE_2
json_ex_3 = ExampleData.FEW_SHOT_EXAMPLE_3
json_ex_4 = ExampleData.FEW_SHOT_EXAMPLE_4

client = pymongo.MongoClient(ConfigData.MONGO_DB_URI)
db = client[ConfigData.DB_NAME]
collection_name = db[ConfigData.COLLECTION_NAME]



prompt_template_for_creating_query = """

    You are an expert in crafting NoSQL queries for MongoDB with 10 years of experience, particularly in MongoDB. 
    I will provide you with the table_schema and schema_description in a specified format. 
    Your task is to read the user_question, which will adhere to certain guidelines or formats, and create a NOSQL MongoDb aggregation pipeline accordingly.

    Table schema:""" +  table_schema + """
    Schema Description: """ + schema_description + """

    Here are some example:
    Input: find all completed task
    Output: {json_ex_string_1} 
    Input: find all completed task for userid 2 i want title only
    Output: {json_ex_string_2} 
    Input: How many tasks has each user completed and not completed?
    Output: {json_ex_string_3}
    Input: What percentage of tasks has each user completed?
    Output: {json_ex_string_4}

    Note: You have to just return the query nothing else. Don't return any additional text with the query.
    Input: {user_question}
    
    """

json_ex_string_1 = json.dumps(json_ex_1)
json_ex_string_2 = json.dumps(json_ex_2)
json_ex_string_3 = json.dumps(json_ex_3)
json_ex_string_4 = json.dumps(json_ex_4)


model = OllamaLLM(model="mistral", base_url="http://140.245.5.20:11434", num_thread=20)


prompt = ChatPromptTemplate.from_template(prompt_template_for_creating_query)

chain = prompt | model 




def get_query(question):
    response = chain.invoke({
                                "user_question": question, 
                                "json_ex_string_1": json_ex_string_1, 
                                "json_ex_string_2": json_ex_string_2,
                                "json_ex_string_3": json_ex_string_3,
                                "json_ex_string_4": json_ex_string_4,
                            })
    return json.loads(response)

def get_result(question):
    aggregation_done = False
    query_hit = 0
    text_ = ""


    while not aggregation_done and query_hit <= 5:
        query_hit += 1
        try:
            pipeline = get_query(question)
            print("RESPONSE:: ",pipeline)
            result = collection_name.aggregate(pipeline)
            for doc in result:
                text_ += str(doc)
            aggregation_done = True
        except Exception as e:
            print(e)
            aggregation_done = False

    print("==>>",text_)

    
    


# question = "find all complete task for user with userid 1?"
question = "Which users have completed at least 10 tasks?"
s_time = time.time()
get_result(question)
print(time.time() - s_time)