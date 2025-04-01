import pymongo, json
from pymongo_schema.extract import extract_collection_schema

# with pymongo.MongoClient("mongodb://localhost:27017/") as client:
#     schema = extract_pymongo_client_schema(client)
#     print(schema)


MONGO_DB_URI = "mongodb://localhost:27017/"
DB_NAME = "dummy_data"
COLLECTION_NAME = "users"

client = pymongo.MongoClient(MONGO_DB_URI)
db = client[DB_NAME]
collection_name = db[COLLECTION_NAME]


schema_detail = extract_collection_schema(collection_name)



def extract_keys_and_types(data, parent_key=""):
    result = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                if 'type' in value:
                    result[new_key] = value['type']
                result.update(extract_keys_and_types(value, new_key))
            elif isinstance(value, list):
                result[new_key] = "LIST"
    
    return result


# Extract keys and types
result = extract_keys_and_types(schema_detail)

# Print the result
print(json.dumps(result, indent=2))



