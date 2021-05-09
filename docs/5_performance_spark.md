---
layout: default
title: Performance Part II - PySpark
nav_order: 5
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}


Speed-up, Throughput, Weak and Strong Scaling and Discussion about Overheads and Optimizations done

## Performance Evaluation for GENIE3 on Spark EC2 Single Node and AWS EMR Hadoop Cluster 

We run spark jobs both locally on a single node and in an EMR Hadoop cluster. Execution time is noted down for both `Job 0` and `Job 1` individually, and we calculated a total execution time by adding both jobs. 

* `Job 0` - Search for all lines in output from Random Forest Model Prediction with significant correlations between pairs (`e.g. > 0.02`), output as Edges of Graph.

* `Job 1` - Use flatmap and deduplication to get an unique list of genes from column `1` and `2` in output file, save it as Vertices of Graph.

As the final output from SageMaker is around 6G, it takes hour to run a single spark job, thus to evaluate performance across single and cluster with different number of executors and thread, we take `17535156` gene expressions to be runned on Spark. After we determined the best settings, we could then run the full dataset on that infrastructure. 

Note	| Instances | 	Number of Executor |	Number of Cores (threads per executor)	| Execution time-Job 0	(Sec) | Execution time - Job 1 (Sec)	| Total execution time	(Sec)| Speedup |
|:-------------|:------------------|:------|:-------------|:------------------|:------|:-------------|:------------------|
SINGLE|m4.xlarge|1|1|40.627743|40.034216|80.661959|1|
SINGLE|m4.xlarge|1|2|24.781344|23.992821|48.774165|1.653784519|
SINGLE|m4.xlarge|1|4|23.923233|22.676687|46.59992|1.730946298|
SINGLE|g3.4xlarge|1|1|39.642083|39.39333|79.035413|1.020579965|
SINGLE|g3.4xlarge|1|2|22.173776|21.679987|43.853763|1.839339511|
SINGLE|g3.4xlarge|1|4|11.677121|11.155805|22.832926|3.532703562|
SINGLE|g3.4xlarge|1|8|8.807559|8.199493|17.007052|4.74285367|
SINGLE|g3.4xlarge|1|16|6.788141|6.307631|13.095772|6.159389382|
CLUSTER|m4.xlarge|2|1|46.135822|39.726582|85.862404|0.939432805|
CLUSTER|m4.xlarge|2|2|32.580215|26.086063|58.666278|1.374928865|
CLUSTER|m4.xlarge|2|4|43.381694|27.571182|70.952876|1.13683847|
CLUSTER|m4.xlarge|4|1|31.877616|24.982805|56.860421|1.418595881|
CLUSTER|m4.xlarge|4|2|33.207751|26.703331|59.911082|1.346361246|
CLUSTER|m4.xlarge|4|4|44.147461|27.483234|71.630695|1.126080921|
CLUSTER|m4.xlarge|8|1|31.007483|26.814587|57.82207|1.395002963|
CLUSTER|m4.xlarge|8|2|32.511647|28.663032|61.174679|1.318551406|
CLUSTER|m4.xlarge|8|4|41.137129|28.146272|69.283401|1.164232094|
 
### Spark Single Node Performance Evaluation
 
From the single node performance comparison, we could see that on **m4.xlarge** itself, with higher number of threads per executor, the execution time decreased, from 80.6 seconds to 48.8, then to 46.6 seconds, achieving around maximum 1.7 speedup. 

If we change the instance from **m4.xlarge** to **g3.4xlarge** with GPUs, we could set more thread per core as **g3.4xlarge** has `16` vCPUs. It has similar total execution times of around 80 seconds, when running on 1 executor and 1 thread per executor. When we increase number of thread per executor, the execution time decreased significantly and could achieve around 6.15 times speedup when we set thread to be 16 per executor.

Regarding speedup performance, it turns out that **g3.4xlarge** GPU instance performs better than **m4.xlarge** on similar settings on a shared memory parallel Spark single code. However, both of them could not achieve their theoritical speedup.

`grep` is a command-line utility for searching plain-text data sets for lines that match a regular expression. Its name comes from the ed command g/re/p (globally search for a regular expression and print matching lines), which has the same effect. 

From the result table, we could see that after we increase the core node in local mode installation of Spark on **m4.xlarge** instance and **g3.4xlarge**, the log time didn't decrease linearly with number of thread. For **m4.xlarge**, the speedup also only increase from `1` to `1.65` and `1.7`, for node increases from `1` to `2` and `4` respectively. For **g3.4xlarge**, the speedup only increase from `1` to `3.5` and `6.15`, for node increase from `1` to `4` and `16` respectively. 

It is mainly because of `grep` has a I/O bound, rather than CPU bound. In CPU we only check for significant pairwise genes with more than 0.2 correlation.

As the `EXECUTION_TIME = CPU_TIME + I/O_TIME + SYSTEM_TIME`, when we increase the node, we could decrease `CPU_TIME` as it is being parallelized. However, as we are doing grep and search for the same pattern, the read and write data part takes a large amount of total execution time, which also keeps unchanged even when the nodes are increased. Thus, as `I/O_TIME` keeps unchanged, while provisioning and shuffle data into more nodes may take more time in Hadoop job, `SYSTEM_TIME` may also be increase, which shows overhead overall is proportional to the number of workers. The total speedup would thus be way less than theortical speed up when number of nodes increases.

We could infer that in **m4.xlarge**, when increase from `1` core to `2` cores, although it is I/O bounded, it is likely that I/O bound is not fully utilised, thus we see considerable improvement of speedup from `1` to `1.6`. When increase from `2` to `4` cores, the speedup is maintained at around `1.7`, and not improved much, which means I/O bandwidth is fully utilised.
 
### Spark EMR Cluster Performance Evaluation

Due to the limit of vCPU, we could not spin up a cluster of `2` GPUs as the number of total vCPU exceeds our account limit. Thus, we stick to **m4.xlarge** for our EMR Hadoop Cluster for Spark. 

From the table, we could see that the cluster could only achieve at maximum `1.4` times of speedup. While holding the number of executor consistent, and compare across the increase of number of threads per executor, it seems speedup increase when there’s only `1` executor, but decrease when there’s more than `1` executors. Besides, increasing number of executor does not seem to have a significant effect on speedup as well. 

Similarly, `grep` is bounded by I/O time but not CPU time in its total execution time. The performance bottleneck is on input and output, reading and writing. Though I/O could also be parallelized, it has its hard limit on I/O bandwidth and could never reach theortical speedup.

From the performance and speedup, we could observe that 8 workers are overall better than `2` or `4` worker instance, while both increasing cores per nodes and number of instances didn't make the speedup reach theortical speedup.

As data are stored in S3, the I/O happens between instances and S3, instead of between instances themselves. So theortically, when we increase number of worker instances to `2` times, the total I/O bandwidth increases proportionally at `2` times. 

From observation, we could infer that in one worker instance, the I/O bandwidth can be fully utilised by `2` cores but it is not enough. It means I/O bandwidth/ability is roughly between `1` to `2` cores. 

Thus, from the table above we could infer the following as examples:
 
* (1). `2` instance and `1` core per node, I/O not fully utilised.
* (2). `2` instance and `2` cores per node, I/O fully utilised, it is bounded by I/O bandwidth. Simiarly, for `2` instance and `4` cores per node, I/O bounded.
* (3). `4` instances and `1` core per node, I/O not fully utilised; Thus it is still not yet bounded by I/O bandwidth, so its speedup is more than what we see in (2)
* (4). `4` instances and `2` core per node,  but with I/O fully utilised, so it reaches the around the similar or even lower speedup comparing with (3). The lower speedup maybe due to communication overhead. However, it is still way less than theortical speedup as there's other overhead proportional to number of worker instances, and I/O time is bounded by its bandwidth.
* (5). Similarly for `8` instances, I/O is bounded between `1` to `2` threads, thus it achieves maximum speedup of `1.39` when there’s only 1 thread per executor. 

To conclude, we could see that Spark job running on cluster may not neccessarily perform better than running on single node due to communication overhead, data I/O and bounds in I/O. Besides, especially when there's GPU instance, we should perferably use GPU instance for our task for faster processing and higher level of parallelism with high computational needs. Sometimes using GPU on shared memory single node could perform better than using CPU instances in distributed memory cluster. This could also due to the limitation of our vCPU number, than disallow us to spin up a cluster of GPUs.

### Best Performance, Scaling to Upsize Full Dataset (3.5G) from SageMaker Output

Next, as we found out g3.4xlarg instance on a SINGLE node with 16 cores perform the best with 6.16 times speedup.

We will then scale up our project to run on [full dataset](https://cs205-final.s3.amazonaws.com/output/healthy_0_3000_alljobs) (`~3.5G`) with the maximum speedup settings. 

We set the `local[16]` to use all threads in this GPU instance. 

**Performance on 3.5G full dataset:**
Note	| Instances | 	Number of Executor |	Number of Cores (threads per executor)	| Execution time-Job 0	(Sec) | Execution time - Job 1 (Sec)	| Total execution time	(Sec)| Speedup |
|:-------------|:------------------|:------|:-------------|:------------------|:------|:-------------|:------------------|
SINGLE|g3.4xlarge|1|16|50.482629|50.066045|100.548674 | N/A|


![image](https://user-images.githubusercontent.com/6150979/117566474-567f8b80-b0e9-11eb-9af4-606bc5fb0c95.png)

![image](https://user-images.githubusercontent.com/6150979/117566454-49629c80-b0e9-11eb-90e6-d043bd821cf8.png)

Snippets of Final Output of Significant Human Gene Pairs with more than `0.005` Pairwise Correlations:
(Which could be used as input for graph network edge and weight in Spark Graph)

![image](https://user-images.githubusercontent.com/6150979/117566548-c9890200-b0e9-11eb-8eea-cbee2f75acd3.png)

Snippets of Final Output of Significant Human Distinct Value List:
(Which could be used as input for graph network vertices in Spark Graph)

![image](https://user-images.githubusercontent.com/6150979/117566556-ddccff00-b0e9-11eb-823b-fb6fa673c8ef.png)



