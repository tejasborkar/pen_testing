from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://a66c47bf.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "68uaOvBiaNe2iJIyUmCBQuVwBuJfDUvNyk9DZdmeec4"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# TO Delete All Nodes & Relationships 
def delete_all_nodes_and_relationships(driver):
    with driver.session() as session:
        cypher_query = """
        MATCH (n)
        DETACH DELETE n
        """
        session.run(cypher_query)
        print("All nodes and relationships have been deleted.")

delete_all_nodes_and_relationships(driver)

driver.close()



# To Delete Specific Relationship

from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def delete_connected_to_relationships(driver):
    with driver.session() as session:
        session.write_transaction(lambda tx: tx.run("MATCH ()-[r:CONNECTED_TO]->() DELETE r"))


delete_connected_to_relationships(driver)

driver.close()
