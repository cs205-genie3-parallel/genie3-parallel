---
layout: default
title: Advanced Features - Graph
nav_order: 7
---
## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Description of advanced features 
*Models/platforms not Explained in Class, Advanced Functions of Modules*

### Graph Analysis

In our project, the final output produced by Spark could be further read into PySpark as the input of Graph and build a network.
The genes names in `vertices.csv` could be used to build gene vertices, and the gene connection with significant pairwise correlation could be used as gene edges
and weights to build gene relationships.


First, we could launch Pyspark with:

Remember, we need to specify `--repositories https://repos.spark-packages.org# ` to fix a bug of repo used by `dl.bintray.com` could not be found in PySpark mvn.

```bash
$ pyspark --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11 --repositories https://repos.spark-packages.org# 
```

Next, we could build graph and explore gene pairwise relationship by using the following code:

```python

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
```

Build graph by using pyspark graphframe![image](https://user-images.githubusercontent.com/6150979/117568555-8338a080-b0f3-11eb-965c-6882a73b4b3d.png)


Read in output from Spark Single Node/ EMR Cluster into PySpark as DataFrame![image](https://user-images.githubusercontent.com/6150979/117568572-98adca80-b0f3-11eb-8d08-139d8f0a0be3.png)

We could explore graph's In Degree and Out Degree Centrality, to get an insight of the signficant relationship correlated to one particular gene.
![image](https://user-images.githubusercontent.com/6150979/117568605-cbf05980-b0f3-11eb-981e-b410a40ca077.png)

We could also explore graph's relationship between vertices by filtering and other more advanced graphframe functions, as a further application to our project.
By using Spark Graphframe, it provides possibility to easily look into particular genes with relatively low computation complexity, and enable users to compare with tumor genes, cancerous genes with other human gene network as well. 
![image](https://user-images.githubusercontent.com/6150979/117568622-e0cced00-b0f3-11eb-9974-54a31471c98a.png)


