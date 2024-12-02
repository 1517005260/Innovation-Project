GRAPH_TEMPLATE = {
    'award_desc': {
        'slots': ['award'],
        'question': '什么是%award%？/ %award%的具体内容是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            RETURN c.text AS RES
        """,
        'answer': '【%award%】的相关内容：%RES%',
    },
    'award_amount': {
        'slots': ['award'],
        'question': '%award%的金额是多少？/ %award%有多少钱？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            OPTIONAL MATCH (n)-[:HAS_AMOUNT]->(m:Amount) 
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%award%】的相关信息：%RES%',
    },
    'award_condition': {
        'slots': ['award'],
        'question': '获得%award%需要满足什么条件？/ %award%怎么评定？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            OPTIONAL MATCH (n)-[:REQUIRES]->(m:Condition)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%award%】的相关信息：%RES%',
    },
    'punishment_desc': {
        'slots': ['punishment'],
        'question': '什么是%punishment%？/ %punishment%的具体内容是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Punishment) 
            WHERE n.id='%punishment%'
            RETURN c.text AS RES
        """,
        'answer': '【%punishment%】的相关内容：%RES%',
    },
    'punishment_duration': {
        'slots': ['punishment'],
        'question': '%punishment%的处分期限是多久？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Punishment) 
            WHERE n.id='%punishment%'
            OPTIONAL MATCH (n)-[:HAS_DURATION]->(m:Duration)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%punishment%】的相关信息：%RES%',
    },
    'violation_desc': {
        'slots': ['violation'],
        'question': '什么是%violation%？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Violation) 
            WHERE n.id='%violation%'
            RETURN c.text AS RES
        """,
        'answer': '【%violation%】的相关内容：%RES%',
    },
    'violation_punishment': {
        'slots': ['violation'],
        'question': '%violation%会受到什么处分？/ %violation%怎么处理？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Violation) 
            WHERE n.id='%violation%'
            OPTIONAL MATCH (n)-[:LEADS_TO]->(m:Punishment)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%violation%】的相关信息：%RES%',
    },
    'department_desc': {
        'slots': ['department'],
        'question': '%department%是做什么的？/ %department%的职责是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Department) 
            WHERE n.id='%department%'
            RETURN c.text AS RES
        """,
        'answer': '【%department%】的相关内容：%RES%',
    },
    'process_desc': {
        'slots': ['process'],
        'question': '%process%的流程是什么？/ %process%怎么操作？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Process) 
            WHERE n.id='%process%'
            RETURN c.text AS RES
        """,
        'answer': '【%process%】的相关内容：%RES%',
    },
    'honor_desc': {
        'slots': ['honor'],
        'question': '什么是%honor%？/ %honor%是什么荣誉？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Honor) 
            WHERE n.id='%honor%'
            RETURN c.text AS RES
        """,
        'answer': '【%honor%】的相关内容：%RES%',
    },
    'honor_condition': {
        'slots': ['honor'],
        'question': '获得%honor%需要满足什么条件？/ 怎么才能获得%honor%？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Honor) 
            WHERE n.id='%honor%'
            OPTIONAL MATCH (n)-[:REQUIRES]->(m:Condition)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%honor%】的相关信息：%RES%',
    }
}