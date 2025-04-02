class ConfigData_old:
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
    


class ConfigData:
    MONGO_DB_URI = "mongodb://localhost:27017/"
    DB_NAME = "kv_rag"
    COLLECTION_NAME = "documents"
    TABLE_SCHEMA = '''
                        {
                            "_id": "object",
                            "document_id": "binary",
                            "document_name": "string",
                            "document_type": "string",
                            "purchase_order_id": "string",
                            "spend_type": "string",
                            "bf_level": "string",
                            "total_commitment": "number",
                            "total_planned_commitment": "number",
                            "total_commitment_gap": "number"
                        }


                    '''
    
    SCHEMA_DESCRIPTION = '''
                    Here is the description to determine what each key represents:
                    {
                        "_id":
                                Unique identifier for the document.
                        "document_id":
                                A unique identifier assigned to the document (usually a file ).
                        "document_name":
                                The name of the document (usually a file name).
                        "document_type":
                                The type of document (e.g., "PO" for Purchase Order).
                        
                        "purchase_order_id":
                            The purchase order ID associated with the document.
                        "spend_type":
                            The category of spending for the purchase order.
                        "bf_level":
                            The business function level related to the purchase order.
                    
                        "total_commitment":
                            The total financial commitment for this purchase order.
                        "total_planned_commitment":
                            The planned financial commitment amount.
                        "total_commitment_gap":
                            The difference between total commitment and planned commitment.
                        "commitments_by_year":
                            A breakdown of commitments by year (if available).
                        
                    }
                    '''
    
