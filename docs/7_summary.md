---
layout: default
title: Summary
nav_order: 7
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Final discussion 这部分麻烦你们再看一下啦 (*^▽^*)
#### goals achieved: 问寒麻烦写一下 ლ(╹◡╹ლ)
#### improvements suggested
* optimize data transfer in and out
* modify code to be able to utilize Sagemaker model pipeline and be reused fo other projects
* incorporate the use of GPU
* try out more ML/RL algorithm besides Random Forest
#### lessons learnt
* a new platform - Sagemaker
#### future work
* investigate other relationships existed among genes
* gene clustering
* gene classficiation
#### interesting insights
* carefully choose the instance type and number in real life application: some instances take up too much resource and the performance-price ratio is too low. From our observation of the experiment, the expensive instances sometimes do not really worth it when comparing the speed they help improve.

## Citations
1. Huynh-Thu, V., Geurts, P. (2010) Inferring Regulatory Networks from Expression Data Using Tree-Based Methods. PLOS ONE (2010). https://doi.org/10.1371/journal.pone.0012776 
1. Github of GENIE3, https://github.com/vahuynh/GENIE3 
1. Expression Atlas https://www.ebi.ac.uk/gxa/experiments 
1. HipSci Project - RNAseq of healthy volunteers https://www.ebi.ac.uk/gxa/experiments/E-ENAD-35/Results 
1. Amazon Sagemaker documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html
1. Amazon Sagemaker API (Estimators) documentation: https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html
