# launch pyspark with:
# pyspark --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11

import graphframes as GF
from pyspark.sql import SQLContext
from pyspark import SparkConf, SparkContext
import pyspark.sql.functions as sf
from pyspark.sql import SparkSession

conf = SparkConf().setMaster('local[2]').setAppName('graph')
sc = SparkContext(conf = conf)
spark = SparkSession(sc)
sql_context = SQLContext(sc)


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


# Exploring the Graph
g.vertices.show()

g.edges.show()

vertexInDegrees = g.inDegrees
vertexInDegrees.show()
vertexOutDegrees = g.outDegrees
vertexOutDegrees.show()