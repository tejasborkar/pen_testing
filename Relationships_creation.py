import csv
from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://a66c47bf.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "68uaOvBiaNe2iJIyUmCBQuVwBuJfDUvNyk9DZdmeec4"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def create_relationships_from_csv(driver, csv_file_path, batch_size=1000):
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]  
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        with driver.session() as session:
            session.write_transaction(create_relationships_in_batch, batch)

def create_relationships_in_batch(tx, batch):
    # HAS_SERVICE relationships
    cypher_query_service = """
    UNWIND $rows AS row
    WITH row WHERE row.Host IS NOT NULL AND row.ServiceName IS NOT NULL AND row.Protocol IS NOT NULL AND row.Port IS NOT NULL
    MATCH (d:Device {name: row.Host})
    MATCH (s:Service {name: row.ServiceName, protocol: row.Protocol, port: toInteger(row.Port)})
    MERGE (d)-[:HAS_SERVICE {protocol: row.Protocol, port: toInteger(row.Port)}]->(s);
    """
    tx.run(cypher_query_service, rows=batch)

    # HAS_VULNERABILITY relationships
    cypher_query_vulnerability = """
    UNWIND $rows AS row
    WITH row WHERE row.Host IS NOT NULL AND row.CVE IS NOT NULL
    MATCH (d:Device {name: row.Host})
    MATCH (v:Vulnerability {id: row.CVE})
    MERGE (d)-[:HAS_VULNERABILITY]->(v);
    """
    tx.run(cypher_query_vulnerability, rows=batch)

    # HAS_CONFIGURATION relationships
    cypher_query_configuration = """
    UNWIND $rows AS row
    WITH row WHERE row.Host IS NOT NULL AND row.`Plugin Output` IS NOT NULL
    MATCH (d:Device {name: row.Host})
    MATCH (c:Configuration {detail: row.`Plugin Output`})
    MERGE (d)-[:HAS_CONFIGURATION]->(c);
    """
    tx.run(cypher_query_configuration, rows=batch)

#     # CONNECTED_TO relationships 
    cypher_query = """
    UNWIND $rows AS row
    WITH row WHERE row.Host IS NOT NULL
    WITH row, split(row.Host, '.') AS octets
    WITH row, octets[0] + '.' + octets[1] + '.' + octets[2] AS subnet, row.Host AS ip
    MATCH (d1:Device {name: ip})  
    MATCH (d2:Device)  
    WHERE d1 <> d2 AND split(d2.name, '.')[0] + '.' + split(d2.name, '.')[1] + '.' + split(d2.name, '.')[2] = subnet
    MERGE (d1)-[:CONNECTED_TO]->(d2)
    MERGE (d2)-[:CONNECTED_TO]->(d1);
    """
    tx.run(cypher_query, rows=batch)

csv_file_path = "C:/Users/TejasBorkar/Desktop/Clean_New_Scan.csv"
create_relationships_from_csv(driver, csv_file_path)
driver.close()
