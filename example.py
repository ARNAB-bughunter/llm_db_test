
class ExampleData:
    FEW_SHOT_EXAMPLE_1 = [
                            {
                                "$group": {
                                "_id": None,
                                "total_commitment": { "$sum": "$metrics.total_commitment" },
                                "total_planned_commitment": { "$sum": "$metrics.total_planned_commitment" },
                                "total_commitment_gap": { "$sum": "$metrics.total_commitment_gap" }
                                }
                            }
                        ]


    FEW_SHOT_EXAMPLE_2 = [
                            {
                                "$group": {
                                "_id": "$document_type",
                                "count": { "$sum": 1 }
                                }
                            }
                        ]
    
    FEW_SHOT_EXAMPLE_3 = [
                            {
                                "$sort": { "metrics.total_commitment": -1 }
                            },
                            {
                                "$limit": 5
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "document_name": 1,
                                "purchase_order_id": "$attributes.purchase_order_id",
                                "total_commitment": "$metrics.total_commitment"
                                }
                            }
                        ]

    
    FEW_SHOT_EXAMPLE_4 = [
                            {
                                "$match": { "metrics.total_commitment_gap": { "$lt": 0 } }
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "purchase_order_id": "$attributes.purchase_order_id",
                                "document_name": 1,
                                "total_commitment_gap": 1
                                }
                            }
                        ]


