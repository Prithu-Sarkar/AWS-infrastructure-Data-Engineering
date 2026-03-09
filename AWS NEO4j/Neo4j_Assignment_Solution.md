# Graph Databases and Vector Search with Neo4j
### Assignment 1 — Complete Solution Guide

---

## Setup

### 1. Configure Environment

Edit `./src/env` and set your Neo4j host:

```
NEO4JHOST=<Neo4jDNSConnection>   # From AWS CloudFormation Outputs (no port)
PORT=7687
USERNAME=neo4j
PASSWORD=adminneo4j
```

Or via terminal:
```bash
sed -i 's/<Neo4j-DNS-Connection>/ec2-xx-xx-xx-xx.compute-1.amazonaws.com/' ~/project/src/env
```

### 2. Load Environment & Connect

```python
load_dotenv('./src/env', override=True)

URI = f"neo4j://{os.getenv('NEO4JHOST')}:{os.getenv('PORT')}"
AUTH = (os.getenv('USERNAME'), os.getenv('PASSWORD'))
```

---

## Section 2 — Basic Operations

### Exercise 1 — Node Labels & Count

```python
query = "MATCH (n) RETURN DISTINCT labels(n), count(*)"
```

### Exercise 2 — Query Country Nodes

```python
query = "MATCH (c:Country) RETURN c LIMIT 10"
records = execute_query(query)
```

### Exercise 3 — Count All Relationships

```python
query = "MATCH ()-[r]->() RETURN count(r) AS relationships_count"
```
> Expected: `57645`

### Exercise 4 — Relationship Count by Type

```python
query = "MATCH ()-[r]-() RETURN DISTINCT TYPE(r), count(*)"
```
> Expected: `Route → 101274`, `Contains → 14016`

### Exercise 5 — Node Properties

```python
query = "MATCH (a:Airport) RETURN properties(a) LIMIT 1"
```

### Exercise 6 — Relationship Properties

```python
query = "MATCH ()-[r:Route]-() RETURN properties(r) LIMIT 1"
```
> Expected: `{ "dist": 1732 }`

### Exercise 7 — Filter by Distance

```python
query = "MATCH (a:Airport)-[r:Route]->(b:Airport) WHERE r.dist > 1000 RETURN a LIMIT 5"
```

### Exercise 8 — Create Relationship

```python
query = "MATCH (a:Airport {code: 'CLR'}), (b:Airport {code: 'BWC'}) CREATE (a)-[r:Route {dist: 12}]->(b) RETURN r"
```

### Exercise 9 — Update Node Property

```python
query = "MATCH (a:Airport) WHERE a.code = 'BWC' SET a.elev = -128 RETURN a"
```

### Exercise 10 — Verify Update

```python
query = "MATCH (a:Airport {code: 'BWC'}) RETURN a.elev"
```
> Expected: `-128`

### Exercise 11 — Delete Node & Relationships

```python
query = "MATCH (a:Airport)-[r]-() WHERE a.code = 'CLR' DELETE r, a"
```

### Exercise 12 — Delete Isolated Node

```python
query = "MATCH (a:Airport) WHERE a.code = 'BWC' DELETE a"
```

### Exercise 13 — Verify Deletion

```python
query = "MATCH (a:Airport {code: 'CLR'}), (b:Airport {code: 'BWC'}) RETURN a, b"
```
> Expected: `[]`

---

## Section 3 — Advanced Queries

### Exercise 14 — Count Direct Routes from LGA

```python
query = "MATCH (origin:Airport {code: 'LGA'})-[r:Route]->(dest:Airport) RETURN DISTINCT count(r) AS count_routes"
```
> Expected: `81`

### Exercise 15 — US Airports with Only One Route

```python
query = "MATCH (a:Airport)-[r:Route]->(b:Airport) WITH a, count(r) AS count_routes WHERE count_routes=1 and a.country = 'US' RETURN a LIMIT 10"
```

### Exercise 16 — Routes with One Stopover (COU → MIA)

```python
query = "MATCH paths=(origin:Airport {code: 'COU'})-[:Route*..2]->(dest:Airport{code: 'MIA'}) RETURN paths"
```

---

## Section 4 — Vector Search

### Step 1 — Load Embeddings

```python
query = """LOAD CSV WITH HEADERS FROM 'file:///air-routes-latest-nodes-with-embeddings.csv' AS row
WITH * WHERE row.label = "airport"
MATCH (a:Airport {id: toInteger(row.id)})
SET a.embedding = toFloatList(split(row.embedding,';'))
RETURN count(a);"""
```

### Step 2 — Create Vector Index (Neo4j Browser UI)

Run in Neo4j Browser at `<your-host>:7474`:

```cypher
CREATE VECTOR INDEX `air-route-embeddings` FOR (n:Airport) ON (n.embedding) OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}
```
> Wait for: _Added 1 index, completed after x ms._

### Exercise 17 — Vector Similarity Search

```python
# Find 5 airports similar to ANC (Anchorage)
vector_query = """MATCH (a:Airport {code: 'ANC'}) 
CALL db.index.vector.queryNodes('air-route-embeddings', 5, a.embedding)
YIELD node AS similar_airport, score
MATCH (similar_airport)
RETURN similar_airport.code, similar_airport.country, similar_airport.desc, similar_airport.region, score"""

# Find 10 airports similar to LGA (LaGuardia)
vector_query = """MATCH (a:Airport {code: 'LGA'}) 
CALL db.index.vector.queryNodes('air-route-embeddings', 10, a.embedding)
YIELD node AS similar_airport, score
MATCH (similar_airport)
RETURN similar_airport.code, similar_airport.country, similar_airport.desc, similar_airport.region, score"""
```

### Cleanup (Optional)

In Neo4j Browser:
```cypher
DROP INDEX `air-route-embeddings`
```

In Notebook:
```python
cleanup_query = """MATCH (a:Airport)
WHERE a.embedding IS NOT NULL
REMOVE a.embedding
RETURN count(a)"""
```

---

## Quick Reference — Cypher Syntax

| Pattern | Description |
|:--|:--|
| `(n)` | A node |
| `(n:Airport)` | Node with label |
| `[r:Route]` | Relationship with type |
| `-->` | Directed relationship |
| `[:Route*..2]` | Up to 2 hops |
| `WHERE` | Filter condition |
| `WITH` | Chain query parts |
| `SET` | Update property |
| `DELETE` | Remove node/relationship |

---

*Course: Data Engineering — Week 1 Assignment | Neo4j Air Routes Dataset*
