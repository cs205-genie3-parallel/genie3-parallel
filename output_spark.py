from pyspark import SparkConf, SparkContext
from pyspark.sql.functions import date_format
from pyspark.sql import SparkSession

conf = SparkConf().setMaster('local[1]').setAppName('meterite')
sc = SparkContext(conf = conf)
spark = SparkSession(sc)


text_file = sc.textFile("ranking_idx.txt")


# consider gene link > 0.02 as significant and print them out as edge file
text_file.filter(lambda line: float(line.split("\t")[2])> 0.02) \
	.repartition(1).saveAsTextFile("graph_edges.txt")

# print all distinct value in the first two columns as vertices file
text_file.flatMap(lambda x: x.split("\t")[:-1]).distinct().repartition(1).saveAsTextFile("vertices.txt")