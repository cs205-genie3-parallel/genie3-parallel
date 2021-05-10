---
layout: default
title: Summary
nav_order: 8
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Final Discussion

### Goals Achieved:
Overall, we **achieved parallel implementation of GENIE3 using both distributed memory and shared memory**, which allowed us to significantly reduce runtime. Linearly extrapolating from our serial runtime, the total elapsed time to run GENIE3 on 49,000 genes serially would take 138.8 hours, or 5 days and 19 hours. Under one of the parallel configurations we explored, using 16 AWS instances with 32 cores and 72 GB memory, we will bring the total elapsed time to 23.1 hours, or less than a day. This results in **an overall 6.00 times speed-up** in the first SageMaker part of our project.

We also **created a hybrid parallel program** including both SageMaker orchestration of multiple instances and PySpark large-scale data processing. For the PySpark part of the project where we filter the gene correlation strength, with input files that are gigabytes large, it would not have been possible without using PySpark, cloud and parallel computing. 

Taking a step beyond GENIE3, we **created the feature of graph analysis for the genes network**, where we can explore the graph network relationships of genes. By counting the in-degrees and out-degrees through PySpark, we are able to find the most "significant" genes in the network. We believe our pipeline as a whole could potentially be a useful tool for researchers to computationally analyze gene importance.

This marks the completion of our first big-scale cloud computing project. By exploring with technologies to implement parallel projects on the cloud, we gained a deeper and practical understanding of the technical details, the programming model and the use of infrastructure. We will be much more confident to pursue another cloud or parallel computing project after this.


### Improvements Suggested
* Explore other methods of running custom scripts on SageMaker so we can avoid the restriction of the SKLearn estimator, which did not allow running one job on multiple instances (we bypassed this by running separate jobs) and did not support GPU instances.
* Incorporate the use of GPU: due to the fact that skicit-learn could not use GPU, we are unable to incorporate GPU into our currently model.
* Provide a more generalized and versatile gene expression analysis pipeline involving both SageMaker and PySpark, so other researchers could use reuse this for diverse gene expression analysis tasks.
* Other than GENIE3, explore other algorithms of deriving pairwise gene significance.

### Lessons Learnt
* A new platform for ML: Sagemaker
* Spark Graph (Graphframes)

### Future Work
* Investigate other relationships existed among genes
* Gene clustering
* Gene classficiation
* More explorations in Network and Graph using Spark GraphX and Graphframes
* Graph Visualizations

### Interesting Insights
* Cost-and-benefit analysis for vertical scaling vs hortizontal scaling is important. some instances with a large number of CPUs (as much as 40 or 72 CPUs) are expensive, and yet the increase in performance does not match the increase in price. From our observation of the experiment, the expensive instances sometimes are not really worth it when comparing the speed-up they provide. In our case, horizontal scaling will deliver more certain and less expensive speed-up.
* Memory of an instance sometimes determines the throughput of the program and whether the program can finish successfully at all. 
* Spark job running on cluster may not neccessarily perform better than running on single node due to communication overhead, data I/O and bounds in I/O. Besides, especially when there's GPU instance, we should perferably use GPU instance for our task for faster processing and higher level of parallelism with high computational needs. Sometimes using GPU on shared memory single node could perform better than using CPU instances in distributed memory cluster. This could also due to the limitation of our vCPU number, than disallow us to spin up a cluster of GPUs.

## Citations
1. Huynh-Thu, V., Geurts, P. (2010) Inferring Regulatory Networks from Expression Data Using Tree-Based Methods. PLOS ONE (2010).
[Link to Paper](https://doi.org/10.1371/journal.pone.0012776) 
3. [Github of GENIE3](https://github.com/vahuynh/GENIE3)
4. [Expression Atlas](https://www.ebi.ac.uk/gxa/experiments)
5. [HipSci Project - RNAseq of Healthy Volunteers](https://www.ebi.ac.uk/gxa/experiments/E-ENAD-35/Results)
6. [Amazon Sagemaker Documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html)
7. [Amazon Sagemaker API (Estimators) Documentation](https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html)
8. [Guide: Install Spark in Local Mode](https://harvard-iacs.github.io/2021-CS205/labs/I9/I9.pdf)
9. [Guide: Spark Cluster on AWS](https://harvard-iacs.github.io/2021-CS205/labs/I10/I10.pdf)
10. [Spark GraphFrames Overview](http://graphframes.github.io/graphframes/docs/_site/)
