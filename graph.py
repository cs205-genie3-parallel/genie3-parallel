# launch pyspark with:
# pyspark --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11

import graphframes as GF

vertice_df = spark.read.csv(
    "vertices.csv", 
    header=False
).toDF("id")


edge_df = spark.read.csv(
    "graph_edges.csv", 
    header=False
).toDF("src","dst","relationship")

g = GF.GraphFrame(vertice_df, edge_df) 

g.vertices.write.parquet("vertices")
g.edges.write.parquet("edges")

# Load the vertices and edges.
# v = sqlContext.read.parquet("hdfs://myLocation/vertices")
# e = sqlContext.read.parquet("hdfs://myLocation/edges")
# Create a graph
# g = GF.GraphFrame(v, e)


# Exploring the Graph
g.vertices.show()

g.edges.show()

vertexInDegrees = g.inDegrees
vertexInDegrees.show()
vertexOutDegrees = g.outDegrees
vertexOutDegrees.show()