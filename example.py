
class ExampleData:
    FEW_SHOT_EXAMPLE_1 = [
                            {
                                "$match": {
                                    "completed": True
                                }
                            },
                        ]

    FEW_SHOT_EXAMPLE_2 = [
                            {
                                "$match": {
                                "userId": 2,
                                "completed": True
                                }
                            },
                            {
                                "$project": {
                                "_id": 0,
                                "title": 1
                                }
                            }
                        ]
    
    FEW_SHOT_EXAMPLE_3 = [
                            {
                                "$group": {
                                "_id": "$userId",
                                "completedTasks": {
                                    "$sum": { "$cond": ["$completed", 1, 0] }
                                },
                                "incompleteTasks": {
                                    "$sum": { "$cond": ["$completed", 0, 1] }
                                }
                                }
                            }
                        ]
    
    FEW_SHOT_EXAMPLE_4 = [
                            {
                                "$group": {
                                "_id": "$userId",
                                "totalTasks": { "$sum": 1 },
                                "completedTasks": {
                                    "$sum": { "$cond": ["$completed", 1, 0] }
                                }
                                }
                            },
                            {
                                "$project": {
                                "completionRate": {
                                    "$multiply": [
                                    { "$divide": ["$completedTasks", "$totalTasks"] },
                                    100
                                    ]
                                }
                                }
                            }
                        ]


