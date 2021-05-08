---
layout: default
title: Background
nav_order: 1
description: "Home Pages"
permalink: /
---

# GENIE-3 

[Get started now](#problem-statement){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [View it on GitHub](https://github.com/cs205-genie3-parallel/genie3-parallel){: .btn .fs-5 .mb-4 .mb-md-0 }


## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}



## Description of Problem and Motivation for HPC

### Problem Statement:
Our project aims to explore topics related to human genes. Human genome provides us with insights into the genetic basis of disease and biological information of human beings. We plan to use Random Forest machine learning models to perform large-scale analysis on human genetic expression data to infer the connectivity between genes, and specifically, build a gene expression regulatory network. The network would come with genes as its vertices, and pairwise gene correlation as its weighted edges. We will only selectively take significant gene expression pairs into building our network. With that gene regulatory network, it enables us to compare differences in the human gene expression patterns and gene regulatory networks across normal and tumor tissues. 


### Motivation for HPC and Big Data:
Intuitively, the human gene comes with tons of data. With millions of available genomes, there exists an unprecedented big data challenge. Not to mention that, normally, in order to get meaningful results for analysis, the more the number of samples, the better the results. Hence, all those data will form a huge matrix and require big data processing.
Specifically for our project, we will have 49,196 human genes across 193 human subject samples. The computational challenging part of this project is to build an individual random forest for each gene as a foundation to calculate all pairwise gene expressions. A random forest is a kind of ensemble model that aggregates results from a number of base decision trees, indicating a huge computation time complexity. 
Therefore, we plan to analyze human gene expression data with a parallelized re-implementation of [GENIE3](https://github.com/vahuynh/GENIE3) in AWS SageMaker. By coding in SageMaker, it could parallelize the random forest estimator part into distributed-memory instances. 
In addition, with the pairwise gene correlation output, we will use Spark on Single Node and Hadoop Cluster to reduce the pairwise gene correlations with only significant pairs to be the edge and weights of graph, and distinct list of all gene names to be the vertex of graph. Eventually, all these vertices and edges will be used to build a gene regulatory network in Spark using the graphframe library.
To get a baseline performance, we ran the GENIE3 analysis sequentially on only 4,000 genes (less than 10% of the genes) and the total runtime was 26 hours. This would mean that to compute more than 40,000 genes, the runtime will take more than 10 days, not even taking into account the increased complexity of each random forest computation with more than 10 times the number of genes (growing number of features to be fed into random forest). Therefore, parallelization is crucial to analyze gene expression within a reasonable time.

## Existing Work

As for the existing work, which is the Genie3 code we referred to, it currently includes the option to parallelize using Python multiprocessing. (When trying this option on a local machine, the program was actually stalled. But it later worked on AWS instances.) Understanding the inefficiency of Python multiprocessing, we seek to parallelize GENIE3 on multiple levels in our project, as follows:
* Distributed memory parallelism -- splitting the computation across several AWS EC2 instances through the orchestration of SageMaker
* Increased computing power -- using AWS instances with greater number of CPUs and GPUs (we later realized this was not available for the estimator model we are using)
* Shared memory parallelism -- using either Python multiprocessing or adjusting the `n_jobs` parameter built-in in the SKLearn random forest estimator.
Doing this allows us to implement parallelism on several levels, giving the user a great degree of choice depending on their cloud computing resources or budget. We also conducted in-depth experiments to investigate the optimal set-up for future users.


## Description of Solution

For our solution, we first split our data when generating matrices and calculating related metrics by dividing the dataset using start and output index. In this way, we could manually divide the dataset into chunks, and aid in the later process of distributing jobs to different threads. 
 
In addition, we decided to use AWS Sagemaker and PySpark for our parallel implementation. 
SageMaker is an enterprise service that allows data scientists to build, train and deploy machine learning models in an integrated development environment (IDE). It acts as a high level orchestration tool that allows users to run scripts on specified AWS EC2 instances (indicated through code) simultaneously and monitor the training process and the results. In the SageMaker portion, we tuned the number of threads/jobs parameters in the Sagemaker estimator function to parallelize the process of learning an ensemble of trees for each target gene, and compute scores for candidate regulators. Moreover, SageMaker enables us to spin up and try out instances just by passing in a parameter to the estimator. This allows us to choose and change our instance types for different parts of the pipeline freely as needed.
 
In the PySpark portion, we utilize Spark(as learned in class), to achieve two tasks. One is to reduce our gene-pairs to significant gene-pairs based on a significant threshold we set(in our case, we chose 0.2 as the threshold). Then, we print all the significant gene-pairs into two output files, the edge file, which includes the distances for each pair of our significant gene-pairs, and vertices file, which includes all distinct genes we found in those pairs. The second job is to print all the distinct gene-pairs we found among the significant gene-pairs.


