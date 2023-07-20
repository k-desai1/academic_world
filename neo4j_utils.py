from neo4j import GraphDatabase
    
def connect_neo4j():
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('', ''))
    session = driver.session(database='academicworld')
    return session