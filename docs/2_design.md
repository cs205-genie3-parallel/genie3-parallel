---
layout: default
title: Data and Parallelism Design
nav_order: 2
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}


## Description of Model and Data
As aforementioned, GENIE3 is a Python package designed to compute the relative pairwise significance between genes using random forests. Both the paper and the package can be accessed openly online. 
We obtained healthy human gene expression data from the Expression Atlas, specifically from the HipSci Project. The expression data contains `193` human subject samples of RNA sequencing of `49,196` genes. 
In terms of computational complexity, given `N = 49,196`, this would mean there would be `N` random forest computations, `1000*N` decision trees, and the resulting pairwise significance matrix will contain `N^2` entries, which is more than `2.4` billion. This definitely calls for the parallel program that we have designed.


## Technical Description of the Parallel Application

The parallel application is a hybrid model consists of two parts, as indicated below:
* **Part 1:** Using AWS SageMaker to parallelize and orchestrate the random forest computation pairwise gene correlation across multiple EC2 instances, which comprise a distributed memory parallelism system.
* **Part 2:** Using PySpark on AWS EMR Spark Hadoop Cluster to build grep tool, using flatmap and de-duplicate to reduce pairwise gene expressions and get significant pairwise correlations as graph edges and weights, distinct gene names as graph vertices. It is also a distributed memory parallelism. However, to compare performance across different instances, we also run it on a single node Spark instance to get a sense of baseline performance.

* **Platform**: AWS SageMaker and AWS EMR Spark Hadoop Cluster

| AWS Service      | AWS SageMaker | AWS Spark on Single Node| AWS EMR Spark Hadoop Cluster|
| ----------- | ----------- |  ----------- |  ----------- |
| Infrastructure   | Experimented across: ml.m4.xlarge; ml.m5.2xlarge; ml.m5.4xlarge;ml.m5.10xlarge;ml.c5.2xlarge |m4.xlarge: - ECUs, 4 vCPUs, 2.4 GHz, -, 16 GiB memory, EBS only; G3.4xlarge: - ECUs, 16 vCPUs, 2.7 GHz, -, 122 GiB memory, EBS only)|m4.xlarge: - ECUs, 4 vCPUs, 2.4 GHz, -, 16 GiB memory, EBS only; G3.4xlarge: (not used due to vCPU limit)|
|  Parallelism   | Distributed memory computation across several instances; Shared memory computation using multiple processes|Shared-Memory Parallel Programming on a Single node| Distributed Memory in a cluster; Shared Memory; Parallel Data Processing|
| Programming model| GENIE3 gene expression analysis programming model; Within a SageMaker Notebook instance, use different notebooks to orchestrate multiple jobs on separate instances.|Text        |Text        |
