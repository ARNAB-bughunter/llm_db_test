
class ExampleData:
    FEW_SHOT_EXAMPLE_1 = [
                            {
                                "$group": {
                                "_id": None,
                                "total_commitment": { "$sum": "$total_commitment" },
                                "total_planned_commitment": { "$sum": "$total_planned_commitment" },
                                "total_commitment_gap": { "$sum": "$total_commitment_gap" }
                                }
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "total_commitment": 1,
                                "total_planned_commitment": 1,
                                "total_commitment_gap": 1
                                }
                            }
                        ]

    FEW_SHOT_EXAMPLE_2 = [
                            {
                                "$group": {
                                "_id": "$document_type",
                                "count": { "$sum": 1 }
                                }
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "document_type": "$_id",
                                "count": 1
                                }
                            }
                        ]

    
    FEW_SHOT_EXAMPLE_3 = [
                            {
                                "$sort": { "total_commitment": -1 }
                            },
                            {
                                "$limit": 5
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "purchase_order_id": 1,
                                "document_name": 1,
                                "total_commitment": 1
                                }
                            }
                        ]

    
    FEW_SHOT_EXAMPLE_4 = [
                            {
                                "$match": {
                                "total_commitment_gap": { "$lt": 0 }
                                }
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "purchase_order_id": 1,
                                "document_name": 1,
                                "total_commitment": 1,
                                "total_planned_commitment": 1,
                                "total_commitment_gap": 1
                                }
                            }
                        ]
