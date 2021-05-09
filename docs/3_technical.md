---
layout: default
title: Technical Details
nav_order: 3
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Links to Repository with Source Code, Evaluation Data Sets and Test Cases
[View Repo on GitHub](https://github.com/cs205-genie3-parallel/genie3-parallel){: .btn .btn-purple .fs-5 .mb-4 .mb-md-0 }

**Input Datasets (Model Building, Evaluation and Test etc.):**

[Human RNAseq Raw Dataset](https://cs205-final.s3.amazonaws.com/healthy.tsv){: .btn .fs-5 .mb-4 .mb-md-0 }

[PySpark Performance Evaluation Dataset - 17 millions gene records](https://genie3-proj.s3.amazonaws.com/ranking_idx.txt){: .btn .fs-5 .mb-4 .mb-md-0 }


**Output Datasets: (Intermediate Result, Full Output etc.)**

[SageMaker Output Full Dataset](https://cs205-final.s3.amazonaws.com/output/healthy_0_3000_alljobs){: .btn .fs-5 .mb-4 .mb-md-0 }

[PySpark Performance Evaluation Output Dataset - Vertices](https://genie3-proj.s3.amazonaws.com/vertices.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }

[PySpark Performance Evaluation Output Dataset - Edges](https://genie3-proj.s3.amazonaws.com/graph_edges.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }

[PySpark Full Output Dataset - Vertices](https://genie3-proj.s3.amazonaws.com/vertices.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }

[PySpark Full Output Dataset - Edges](https://genie3-proj.s3.amazonaws.com/full_graph_edges.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }


## Technical Description of the Software Design
### SageMaker

For a machine learning job with prepared data for training and testing, SageMaker offers a notebook interface for directly training, testing and deploying estimators on selected AWS EC2 instances. However, since we are using the GENIE3 programming model, we would need to run our custom training script. As novices to SageMaker, we used a SKLearn estimator just for the function of a wrapper. In the custom estimator, we can specify the entry point script, the type of EC2 instance and “hyperparameters” (understandably misused) which will be passed into the entry point script as command line arguments. This is probably a less standard solution of running a custom script on SageMaker and there might be other solutions out there. However, after extensive research and troubleshooting, we find that this is able to fulfil our requirements of orchestrating parallelized computation for now.

```python
customer_estimator = SKLearn(entry_point = 'GENIE3-sagemaker.py',
                            role=get_execution_role(),
                            instance_type='ml.m4.xlarge',
                            framework_version='0.20.0',
                            hyperparameters = {'start_idx': 0, 'stop_idx': 6000, 'n_jobs': -1, 'fname': 'healthy_0_6000_alljobs'})
healthy_uri = f"s3://{bucket_name}/healthy.tsv"
custom_estimator.fit({'train':healthy_uri})
```

In the entry point script, it contains functions from GENIE3 with changes intended to only limit the analysis for genes between the start index and the stop index, instead of running the analysis for all the genes. We also added in a n_jobs argument to parallelize each SKLearn random forest computation.
The main function contains a parser for the arguments passed from the custom estimator, the main GENIE3 function calls, as well as utility functions to read, process data from AWS S3 and to upload output to S3.

```python
if __name__ =='__main__':
 
    parser = argparse.ArgumentParser()
 
    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument('--start_idx', type=int, default=0)
    parser.add_argument('--stop_idx', type=int, default=10)
    parser.add_argument('--nthreads', type=int, default=1)
    parser.add_argument('--n_jobs', type=int, default=1)
    parser.add_argument('--fname', type=str, default='output_ranking.txt')
 
    # Data, model, and output directories
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
 
    args, _ = parser.parse_known_args()
 
    bucket_name = 'cs205-final'
    s3 = boto3.resource('s3')
    output_path = f"s3://{bucket_name}/output/"
 
    data, gene_names = preprocess_data(os.path.join(args.train, "healthy.tsv"))
 
    VIM = GENIE3(data, gene_names=gene_names, start_idx=args.start_idx, stop_idx=args.stop_idx,nthreads=args.nthreads,n_jobs=args.n_jobs)
    output_fname = os.path.join('/opt/ml/output/data', args.fname)
    get_link_list(VIM, gene_names=gene_names, file_name=output_fname)
    
    response = upload_file_to_s3(output_path, output_fname, args.fname)
    print(response)
```

### Spark
Due to the limit on vCPU numbers, we couldn’t start a cluster of GPUs instance **g3.4xlarge**, so we tested performance and speedup of Spark job locally on `Ubuntu 18.04` with **g3.4xlarge** and **m4.xlarge** instances, following guide from [Lab 9](https://harvard-iacs.github.io/2021-CS205/labs/I9/I9.pdf). And then we used m4.xlarge instances to run it in a hadoop cluster with more number of instances and threads per executor, following guide from [Lab 10](https://harvard-iacs.github.io/2021-CS205/labs/I10/I10.pdf). 

When running Spark on a single node, there is a single executor to run the application that can be multi-threaded to use the multi-core parallelism. SparkConf allows you to configure some of the common properties, like for example, the number of threads of the application. Running with `local[2]` means two threads - which represents “minimal” parallelism, which can help detect bugs that only exist when we run in a distributed context or reduces execution time on multi-core systems.

we could set the number of threads used in Spark by changing numbers in setMaster to be passed to Spark.

```python

from pyspark import SparkConf, SparkContext
from pyspark.sql.functions import date_format
from pyspark.sql import SparkSession

conf = SparkConf().setMaster('local[*]').setAppName('genie3')
sc = SparkContext(conf = conf)
spark = SparkSession(sc)


text_file = sc.textFile("ranking_idx.txt")

def toCSVLine(data):
  return ','.join(str(d) for d in data.split('\t'))


# consider gene link > 0.02 as significant and print them out as edge file
text_file.filter(lambda line: float(line.split("\t")[2])> 0.005) \
	.repartition(1).map(toCSVLine).saveAsTextFile("graph_edges.csv")

# print all distinct value in the first two columns as vertices file
text_file.filter(lambda line: float(line.split("\t")[2])> 0.005) \
	.flatMap(lambda x: x.split("\t")[:-1]).distinct().repartition(1) \
	.map(toCSVLine).saveAsTextFile("vertices.csv")
  
```


Next, we could run the following line to create our spark job and reduce pairwise gene correlation we get from previous steps into vertices and edges. 

```bash
$ spark-submit spark_output_to_edge_vertices.py
```

We run spark jobs both locally on a single node and in an EMR Hadoop cluster. Execution time is noted down for both Job 0 and Job 1 individually, and we calculated a total execution time by adding both jobs. 

* Job 0 - Search for all lines in output from Random Forest Model Prediction with significant correlations between pairs (e.g. > 0.02), output as Edges of Graph
* Job 1 - Use flatmap and deduplication to get an unique list of genes from column 1 and 2 in output file, save it as Vertices of Graph
We could view Spark Job status via Spark UI during the time that Spark job is running: 


Spark UI Showing Job Running![image](https://user-images.githubusercontent.com/6150979/117563107-48743f80-b0d6-11eb-83dd-8d70c9d63dc1.png)

Spark UI Showing Job Running![image](https://user-images.githubusercontent.com/6150979/117563125-6477e100-b0d6-11eb-852b-d13fa0e379bb.png)

We changed the number of threads used in Spark single node by editing numbers in setMaster to be passed to Spark, and noted down performance result and speedup for further evaluation in the next section. 

Similarly, we could spin up EMR Spark Cluster with instance m4.xlarge to run code in distributed memory with different number of executors and threads per executors. 

```bash
$ spark-submit --num-executors 2 --executor-cores 2 spark_output_to_edge_vertices.py
```

Everytime time we try to run it on a different number of executors and cores per executors, we remove previous output in the hadoop file system.

```bash
$ hadoop fs -rm -R -f graph_edges.csv/
$ hadoop fs -rm -R -f vertices.csv/
```

After successfully complete a spark job, we could download the result from hadoop file system and take a look:

![image](https://user-images.githubusercontent.com/6150979/117563197-cb959580-b0d6-11eb-9b88-a5a0754a85e5.png)

Eventually, we could copy our output to S3 bucket for future use and graph building in Spark. 

![image](https://user-images.githubusercontent.com/6150979/117563216-eb2cbe00-b0d6-11eb-8ac5-5e45008b6b9d.png)

After submitting to S3, we could take a look in S3 bucket, our results are both included in graph_edges.csv/ and vertices.csv/ folders.  

![image](https://user-images.githubusercontent.com/6150979/117563222-f7188000-b0d6-11eb-977a-6a35fb41263e.png)

### PySpark Graph

In our project, the final output produced by Spark could be further read into PySpark as the input of Graph and build a network. The genes names in `vertices.csv` could be used to build gene vertices, and the gene connection with significant pairwise correlation in `graph_edges.csv` could be used as gene edges and weights to build gene relationships.

More technical details could be found on [Advanced Feature - Part II Graph](https://cs205-genie3-parallel.github.io/genie3-parallel/7_advance_graph.html) page.

Graph Details with Vertices and Edges.
![image](https://user-images.githubusercontent.com/6150979/117568939-ba0fb600-b0f5-11eb-9b2e-80bc2240524f.png)



## Code Baseline 
Code baseline is based on [GENIE3 package](https://github.com/vahuynh/GENIE3/blob/master/GENIE3_python/GENIE3.py).

The code used `multiprocessing` python package to map all gene data into different threads by the following lines.
It independently calls function `wr_GENIE3_single()` to build random forest model individually by setting `nthreads`. 

```python
pool = Pool(nthreads)
alloutput = pool.map(wr_GENIE3_single, input_data)
```

However, the baseline has a high time and space complexity and it requires several days to run the dataset.

The baseline complexity for random forest is calculated as following when we set `n=30k`:
```
O(One tree) = # gene * sqrt(# gene) * log(sqrt(# gene))
O(RF per gene) = # tree * O(One tree)
O(all genes) = # gene * O(RF per gene)
	     = n^2 * sqrt(n) * log(sqrt(n))
	     = 30k * 1000 * 30k * sqrt(30k) * log(30k)
```

Thus, we intended to use SageMaker and parallelize for the scikit learn estimator and Random Forest model building as we described above, to improve computational performance.



## Dependencies
* sklearn==0.24.2
* sagemaker==2.39.0
* boto3
* graphframes 0.6.0


## How to Use the Code

### SageMaker
**System and Environment:**

- SageMaker Notebook Instance: ml.t2.medium (default)
- Kernel: conda_python3 (out of the options provided by SageMaker)

**Steps for Running the Code:**
- Start an AWS SageMaker notebook instance following [this guide](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html), setting Github repo to [our repo](https://github.com/cs205-genie3-parallel/genie3-parallel.git)

- Install requirements with 
```bash
pip install -r requirements.txt
```
- Navigate to sagemaker/GENIE3-sagemaker.ipynb. Select conda_python3 as the kernel.
- Run all the cells, edit the `instance_type`, `hyperparameters` as needed and indicate `start_idx` and `stop_idx` to choose the target genes to compute on.

### PySpark

**System and Environment:**
- OS: Ubuntu 18.04
- Instance for Local Node: tried **m4.xlarge** and **g3.4xlarge**
- Instance for EMR Cluster: **m4.xlarge** with 2 worker nodes, then resize to 4 and 8 worker nodes
- Kernal: x86_64 GNU/Linux
- Java 1.8.0
- Scala 2.11.12
- PySpark 2.4.4
- graphframes 0.6.0

**Steps for Running the Code:**

#### *Spark on Single Node*

Spin up instance by following guide on [Lab 9](https://harvard-iacs.github.io/2021-CS205/labs/I9/I9.pdf)

Open another command line window to upload PySpark script to instance. 

```bash
$ scp -i .ssh/cs205-gpu-keypair.pem ranking_idx.txt ubuntu@3.89.163.176:/home/ubuntu/
$ scp -i .ssh/cs205-gpu-keypair.pem spark_output_to_edge_vertices.py ubuntu@3.89.163.176:/home/ubuntu/
```

Install relevant package and libraries by following Lab 9.
```bash
$ sudo apt-add-repository ppa:webupd8team/java
$ sudo apt-get update
$ sudo apt install openjdk-8-jdk
$ java -version

$ sudo apt-get install scala
$ scala -version

$ sudo apt-get install python
$ python -h

$ sudo curl -O http://d3kbcqa49mib13.cloudfront.net/spark-2.2.0-bin-hadoop2.7.tgz
$ sudo tar xvf ./spark-2.2.0-bin-hadoop2.7.tgz
$ sudo mkdir /usr/local/spark
$ sudo cp -r spark-2.2.0-bin-hadoop2.7/* /usr/local/spark
```

To config environment, add the following line to `~/.profile`. And then execute ```source ~/.profile``` to update PATH in your current session

```bash
export PATH="$PATH:/usr/local/spark/bin"
```
Next, include the internal hostname and IP to `/etc/hosts` with a text editor, with `sudo vim /etc/hosts`

Then we could execute the spark job by running:

```bash
$ spark-submit spark_output_to_edge_vertices.py 
```
We could use `sudo vim spark_output_to_edge_vertices.py` to change the number of thread/core used in that instance by setting different `local[k]` in the line
`conf = SparkConf().setMaster('local[2]').setAppName('genie3')`.

Then, we could rerun the spark job. Before that, remember to remove the previous output files by:

```bash
$ rm -R -f vertices.csv
$ rm -R -f graph_edges.csv
$ spark-submit spark_output_to_edge_vertices.py 
```


#### *Spark on EMR Hadoop Cluster*
Spin up instance by following guide from [Lab 10](https://harvard-iacs.github.io/2021-CS205/labs/I10/I10.pdf)

Everytime when we set different number of executor and thread per executor, and resubmit spark job to evaluate the execution time and speedup performance, 
we need to remove previously produced output file in Hadoop file system by using `hadoop fs -rm -R -f`.
Then we could resubmit the spark job in EMR Hadoop cluster. 

```bash
$ hadoop fs -rm -R -f graph_edges.csv/
$ hadoop fs -rm -R -f vertices.csv/
$ spark-submit --num-executors 2 --executor-cores 1 spark_output_to_edge_vertices.py 
```
Resize the number of workers in hardware option from 2 worker node to 4 nodes, and 8 nodes. Then repeat all the steps above to note down execution times for both job. 

#### *Scale Up to Full Dataset from SageMaker Output* 

Next, as we found out g3.4xlarg instance on a SINGLE node with 16 cores perform the best with 6.16 times speedup. (More details in Performance section)

We will then scale up our project to run on [full dataset](https://cs205-final.s3.amazonaws.com/output/healthy_0_3000_alljobs) (`~3.5G`) with the maximum speedup settings. 

We set the `local[16]` and change the input file name to full dataset filename to use all threads in this GPU instance and rerun the following. 

```bash
$ hadoop fs -rm -R -f graph_edges.csv/
$ hadoop fs -rm -R -f vertices.csv/
$ spark-submit --num-executors 2 --executor-cores 1 spark_output_to_edge_vertices.py 
```

![image](https://user-images.githubusercontent.com/6150979/117566191-cbea5c80-b0e7-11eb-983b-4cc707c708f3.png)


Snippets of Final Output of Significant Human Gene Pairs with more than `0.005` Pairwise Correlations:

(Which could be used as input for graph network edge and weight in Spark Graph)

![image](https://user-images.githubusercontent.com/6150979/117566548-c9890200-b0e9-11eb-8eea-cbee2f75acd3.png)

Snippets of Final Output of Significant Human Distinct Value List:

(Which could be used as input for graph network vertices in Spark Graph)

![image](https://user-images.githubusercontent.com/6150979/117566556-ddccff00-b0e9-11eb-823b-fb6fa673c8ef.png)


### Graph

In the EC2 instance mentioned above in PySpark, start PySpark with Graphframe by

```bash
$ pyspark --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11 --repositories https://repos.spark-packages.org
```

And then we could import output from the Spark Grep tool into PySpark as dataframe, then build graph.

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
```

Afterwards, more interesting details of graph could be explored.
```python
g.vertices.show()
g.edges.show()

vertexInDegrees = g.inDegrees
vertexInDegrees.show()
vertexOutDegrees = g.outDegrees

## explore network by group by or filtering 
g.edges.filter("relationship > 0.008").count()
g.edges.filter("relationship > 0.008").show()
```



## System and Environment needed to Reproduce our Tests

**System and Environment for SageMaker:**
- SageMaker Notebook Instance: ml.t2.medium (default)
- Kernel: conda_python3 (out of the options provided by SageMaker)

**System and Environment for Spark/Graph:**
- OS: Ubuntu 18.04
- Instance for Local Node: tried **m4.xlarge** and **g3.4xlarge**
- Instance for EMR Cluster: **m4.xlarge** with 2 worker nodes, then resize to 4 and 8 worker nodes
- Kernal: x86_64 GNU/Linux
- Java 1.8.0
- Scala 2.11.12
- PySpark 2.4.4
- graphframes 0.6.0
