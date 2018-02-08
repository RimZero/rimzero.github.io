from py2neo import Graph, Node, Relationship, authenticate
import pandas as pd
# import chardet

# with open('coachsnetwork.csv', 'rb') as f:
#     result = chardet.detect(f.read())
# print(result)

RELATIONS = {'player': 'Player of', 'assistant': 'Assistant of'}

authenticate("localhost:7474", "neo4j", "baichi")

# graph = Graph('http://localhost:7474/db/data')
graph = Graph("http://localhost:7474/db/data/")

df = pd.read_csv('coachsnetwork.csv', encoding='ISO-8859-1')
# graph.schema.create_uniqueness_constraint("Coach", "name")
coaches = []
for index, row in df.iterrows():

    a = graph.find_one(label='Coach', property_key='name',
                       property_value=row['CoachA'])
    if a == None:
        a = Node("Coach", name=row['CoachA'])
    b = graph.find_one(label='Coach', property_key='name',
                       property_value=row['CoachB'])
    if b == None:
        b = Node("Coach", name=row['CoachB'])
    ab = Relationship(a, RELATIONS[row['relationship']], b)
    graph.create(ab)
