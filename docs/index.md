## Genie 3



### Description of problem and motivation for HPC

**Problem Statement:**
Our project aims to explore topics related to human genes. Human genome provides us with insights into the genetic basis of disease and biological information of human beings. We plan to use Random Forest machine learning models to perform large-scale analysis on human genetic expression data to infer the connectivity between genes, and specifically, build a gene expression regulatory network. The network would come with genes as its vertices, and pairwise gene correlation as its weighted edges. We will only selectively take significant gene expression pairs into building our network. With that gene regulatory network, it enables us to compare differences in the human gene expression patterns and gene regulatory networks across normal and tumor tissues. 


**Motivation for HPC and Big Data:**
Intuitively, the human gene comes with tons of data. With millions of available genomes, there exists an unprecedented big data challenge. Not to mention that, normally, in order to get meaningful results for analysis, the more the number of samples, the better the results. Hence, all those data will form a huge matrix and require big data processing.
Specifically for our project, we will have 49,196 human genes across 193 human subject samples. The computational challenging part of this project is to build an individual random forest for each gene as a foundation to calculate all pairwise gene expressions. A random forest is a kind of ensemble model that aggregates results from a number of base decision trees, indicating a huge computation time complexity. 
Therefore, we plan to analyze human gene expression data with a parallelized re-implementation of [GENIE3](https://github.com/vahuynh/GENIE3) in AWS SageMaker. By coding in SageMaker, it could parallelize the random forest estimator part into distributed-memory instances. 
In addition, with the pairwise gene correlation output, we will use Spark on Single Node and Hadoop Cluster to reduce the pairwise gene correlations with only significant pairs to be the edge and weights of graph, and distinct list of all gene names to be the vertex of graph. Eventually, all these vertices and edges will be used to build a gene regulatory network in Spark using the graphframe library.
To get a baseline performance, we ran the GENIE3 analysis sequentially on only 4,000 genes (less than 10% of the genes) and the total runtime was 26 hours. This would mean that to compute more than 40,000 genes, the runtime will take more than 10 days, not even taking into account the increased complexity of each random forest computation with more than 10 times the number of genes (growing number of features to be fed into random forest). Therefore, parallelization is crucial to analyze gene expression within a reasonable time.

### Existing work

### Description of solution

### Description of your model and/or data
where did it come from, how did you acquire it, what does it mean, etc.

### Technical description of the parallel application
programming models, platform and infrastructure

### Links to repository with source code, evaluation data sets and test cases

### Technical description of the software design
code baseline, dependencies, how to use the code, and system and environment needed to reproduce your tests

### Performance evaluation 
(speed-up, throughput, weak and strong scaling) and discussion about overheads and optimizations done

### Description of advanced features 
like models/platforms not explained in class, advanced functions of modules, techniques to mitigate overheads, challenging parallelization or implementation aspects...

### Final discussion about goals achieved, 
improvements suggested, lessons learnt, future work, interesting insights…

### Citations
