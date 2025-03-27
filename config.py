class ConfigData:
    MONGO_DB_URI = "mongodb://localhost:27017/"
    DB_NAME = "dummy_data"
    COLLECTION_NAME = "todos"
    TABLE_SCHEMA = '''
                        "_id":"int"
                        "userId":"int"
                        "title":"string"
                        "completed":"bool"
                    '''
    
    SCHEMA_DESCRIPTION = '''
                    Here is the description to determine what each key represents:
                    1. _id:
                        - Description: Unique identifier for the document.
                    2. userId:
                        - Description: ID of the user.
                    3. title:
                        - Description: Title of the task.
                    4. completed:
                        - Description: Status of the task.
                    '''