import csv
from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://a66c47bf.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "68uaOvBiaNe2iJIyUmCBQuVwBuJfDUvNyk9DZdmeec4"


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def create_nodes_and_relationships_from_csv(driver, csv_file_path, batch_size=1000):

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader] 
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]

        with driver.session() as session:
            session.write_transaction(create_nodes_in_batch, batch)


def create_nodes_in_batch(tx, batch):
    cypher_query = """
    UNWIND $rows AS row
    // Device node creation
    WITH row
    WHERE row.Host IS NOT NULL
    MERGE (d:Device {name: row.Host})

    // Vulnerability node creation
    WITH row, d
    WHERE row.ServiceName IS NOT NULL AND row.ServiceName <> "" AND row.CVE IS NOT NULL AND row.Synopsis IS NOT NULL AND row.Risk IS NOT NULL
    MERGE (v:Vulnerability {id: row.CVE})
    ON CREATE SET 
        v.type = row.ServiceName,
        v.effect = row.Synopsis,
        v.cvss_score = CASE WHEN row.`CVSS v2.0 Base Score` <> '' THEN toFloat(row.`CVSS v2.0 Base Score`) ELSE NULL END,
        v.risk = row.Risk

    // Service node creation
    WITH row, d, v
    WHERE row.ServiceName IS NOT NULL AND row.ServiceName <> "" AND row.Protocol IS NOT NULL AND row.Port IS NOT NULL
    MERGE (s:Service {
        name: row.ServiceName,
        protocol: row.Protocol,
        port: toInteger(row.Port)
    })

    // Configuration node creation
    WITH row, d, v, s
    WHERE row.`Plugin Output` IS NOT NULL
    MERGE (c:Configuration {detail: row.`Plugin Output`})
    """
    tx.run(cypher_query, rows=batch)

csv_file_path = "C:/Users/TejasBorkar/Desktop/Clean_New_Scan.csv"
create_nodes_and_relationships_from_csv(driver, csv_file_path)
driver.close()