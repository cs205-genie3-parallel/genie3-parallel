# launch pyspark with:
# pyspark --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11 --repositories https://repos.spark-packages.org# 

import graphframes as GF
from pyspark.sql import SQLContext
sql_context = SQLContext(sc)

vertice_df = sql_context.read.csv(
    "vertices.csv/part-00000", 
    header=False
).toDF("id")


edge_df = sql_context.read.csv(
    "graph_edges.csv/part-00000", 
    header=False,
    sep = ','
).toDF("src", "dst", "relationship")

g = GF.GraphFrame(vertice_df, edge_df) 

g.vertices.write.parquet("vertices")
g.edges.write.parquet("edges")

# Load the vertices and edges.
# v = sqlContext.read.parquet("hdfs://./vertices")
# e = sqlContext.read.parquet("hdfs://./edges")
# Create a graph
# g = GF.GraphFrame(v, e)

# Exploring the Graph
g.vertices.show()
g.edges.show()

vertexInDegrees = g.inDegrees
vertexInDegrees.show()
vertexOutDegrees = g.outDegrees


## explore network by group by or filtering 
g.edges.filter("relationship > 0.008").count()
g.edges.filter("relationship > 0.008").show()