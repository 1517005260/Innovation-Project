GRAPH_TEMPLATE = {
    'award_requirements': {
        'slots': ['award'],
        'question': [
            '%award%的申请条件是什么？',
            '%award%有什么要求？',
            '想要申请%award%需要满足哪些条件？',
            '申请%award%的资格要求有哪些？',
            '%award%的评选标准是什么？',
            '谁可以申请%award%？',
            '%award%的准入条件是什么？'
        ],
        'cypher': "MATCH (n:Award)-[:REQUIRES]->(m:Condition) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的申请条件：%RES%'
    },
    'award_duration': {
        'slots': ['award'],
        'question': [
            '%award%的评选时间是什么时候？',
            '%award%什么时候开始评选？',
            '%award%的申请截止日期是？',
            '%award%评选周期是多久？',
            '%award%什么时候可以申请？',
            '%award%的发放时间是什么时候？'
        ],
        'cypher': "MATCH (n:Award)-[:HAS_DURATION]->(m:Duration) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的评选时间：%RES%'
    },
    'award_amount': {
        'slots': ['award'],
        'question': [
            '%award%的金额是多少？',
            '%award%每年发多少钱？',
            '%award%的奖励金额是多少？',
            '获得%award%可以拿到多少奖金？',
            '%award%的资助标准是多少？'
        ],
        'cypher': "MATCH (n:Award)-[:HAS_AMOUNT]->(m:Amount) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的金额：%RES%'
    },
    'award_supervisor': {
        'slots': ['award'],
        'question': [
            '%award%由哪个部门负责？',
            '%award%的主管部门是哪个？',
            '谁负责管理%award%？',
            '%award%的评审工作由谁负责？',
            '申请%award%要找哪个部门？',
            '%award%的评审机构是什么？'
        ],
        'cypher': "MATCH (n:Award)-[:SUPERVISED_BY]->(m:Department) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的负责部门：%RES%'
    },
    'violation_punishment': {
        'slots': ['violation'],
        'question': [
            '因为%violation%会受到什么处分？',
            '%violation%的处罚是什么？',
            '%violation%会有什么后果？',
            '%violation%要受到什么纪律处分？',
            '如果%violation%会怎么处理？'
        ],
        'cypher': "MATCH (n:Violation)-[:LEADS_TO]->(m:Punishment) WHERE n.id='%violation%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '因【%violation%】可能受到的处分：%RES%'
    },
    'punishment_duration': {
        'slots': ['punishment'],
        'question': [
            '%punishment%的期限是多久？',
            '%punishment%要多长时间？',
            '%punishment%持续多久？',
            '%punishment%什么时候能解除？',
            '%punishment%的处分期是多久？'
        ],
        'cypher': "MATCH (n:Punishment)-[:HAS_DURATION]->(m:Duration) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的期限：%RES%'
    },
    'punishment_conditions': {
        'slots': ['punishment'],
        'question': [
            '什么情况下会受到%punishment%？',
            '哪些行为会导致%punishment%？',
            '为什么会被%punishment%？',
            '%punishment%的触发条件是什么？',
            '什么违纪行为会受到%punishment%？'
        ],
        'cypher': "MATCH (n:Punishment)<-[:LEADS_TO]-(m:Condition) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '以下情况将受到【%punishment%】：%RES%'
    },
    'punishment_process': {
        'slots': ['punishment'],
        'question': [
            '%punishment%需要经过什么流程？',
            '%punishment%怎么执行？',
            '%punishment%的处理步骤是什么？',
            '%punishment%由谁来决定？',
            '如何实施%punishment%？'
        ],
        'cypher': "MATCH (n:Punishment)-[:REQUIRES]->(m:Process) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的处理流程：%RES%'
    },
    'exclusive_awards': {
        'slots': ['award'],
        'question': [
            '%award%与哪些奖项互斥？',
            '获得%award%后还能申请什么奖？',
            '%award%和什么奖不能同时获得？',
            '申请了%award%还能申请其他奖项吗？',
            '%award%有什么相关限制？'
        ],
        'cypher': "MATCH (n:Award)-[:EXCLUSIVE_WITH]->(m:Award) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】与以下奖项互斥：%RES%'
    },
    'award_process': {
        'slots': ['award'],
        'question': [
            '%award%的评审流程是什么？',
            '%award%怎么申请？',
            '申请%award%需要准备什么材料？',
            '%award%的评选步骤是什么？',
            '怎么参加%award%的评选？'
        ],
        'cypher': "MATCH (n:Award)-[:CONSISTS_OF]->(m:Process) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的评审流程：%RES%'
    },
    'award_appeal': {
        'slots': ['award'],
        'question': [
            '%award%评选结果不满意怎么办？',
            '%award%的申诉途径是什么？',
            '对%award%结果有异议怎么处理？',
            '%award%的复议程序是什么？',
            '不服%award%评选结果找谁？'
        ],
        'cypher': "MATCH (n:Award)-[:CAN_APPEAL]->(m:Organization) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的申诉渠道：%RES%'
    },
    'punishment_appeal': {
        'slots': ['punishment'],
        'question': [
            '%punishment%怎么申诉？',
            '对%punishment%不服怎么办？',
            '%punishment%的申诉程序是什么？',
            '收到%punishment%后如何上诉？',
            '%punishment%的复议渠道是什么？'
        ],
        'cypher': "MATCH (n:Punishment)-[:CAN_APPEAL]->(m:Organization) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的申诉渠道：%RES%'
    },
    'condition_leads_to': {
        'slots': ['condition'],
        'question': [
            '%condition%会导致什么处分？',
            '%condition%会受到什么惩罚？',
            '%condition%的后果是什么？',
            '%condition%会有什么处理结果？',
            '如果%condition%会怎么处理？'
        ],
        'cypher': "MATCH (n:Condition)-[:LEADS_TO]->(m:Punishment) WHERE n.id='%condition%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%condition%】将导致：%RES%'
    },
    'department_manages': {
        'slots': ['department'],
        'question': [
            '%department%负责管理什么？',
            '%department%的职责是什么？',
            '%department%主管哪些事务？',
            '%department%有什么权限？',
            '%department%负责什么工作？'
        ],
        'cypher': "MATCH (n:Department)-[:MANAGES]->(m) WHERE n.id='%department%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%department%】负责管理：%RES%'
    },
    'department_evaluates': {
        'slots': ['department'],
        'question': [
            '%department%负责评估什么？',
            '%department%评价什么内容？',
            '%department%考核哪些方面？',
            '%department%评审什么？',
            '%department%如何进行评定？'
        ],
        'cypher': "MATCH (n:Department)-[:EVALUATES]->(m) WHERE n.id='%department%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%department%】负责评估：%RES%'
    },
    'organization_awards': {
        'slots': ['organization'],
        'question': [
            '%organization%有哪些奖项？',
            '%organization%设立了什么奖？',
            '%organization%颁发什么奖项？',
            '%organization%的奖励制度有哪些？',
            '%organization%评选什么奖？'
        ],
        'cypher': "MATCH (n:Organization)-[:AWARDS]->(m:Award) WHERE n.id='%organization%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%organization%】设立的奖项：%RES%'
    }
}