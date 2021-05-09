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

### Goals Achieved: 问寒麻烦写一下 ლ(╹◡╹ლ)
xxx

### Improvements Suggested
* optimize data transfer in and out
* modify code to be able to utilize Sagemaker model pipeline and be reused fo other projects
* incorporate the use of GPU
* try out more ML/RL algorithm besides Random Forest

### Lessons Learnt
* A new platform - Sagemaker
* Spark Graph (Graphframes)

### Future Work
* Investigate other relationships existed among genes
* Gene clustering
* Gene classficiation
* More explorations in Network and Graph using Spark GraphX and Graphframes
* Graph Visualizations

### Interesting Insights
* Carefully choose the instance type and number in real life application: some instances take up too much resource and the performance-price ratio is too low. From our observation of the experiment, the expensive instances sometimes do not really worth it when comparing the speed they help improve.
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
