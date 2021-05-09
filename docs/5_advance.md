---
layout: default
title: Advanced Features
nav_order: 5
---
## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Description of advanced features 
like models/platforms not explained in class, advanced functions of modules, techniques to mitigate overheads, challenging parallelization or implementation aspects...

In our project, we incorporate SageMaker to parallelize our model. Amazon SageMaker is an easy-to-use machine learning service. It enables us to use Jupyter authoring notebook instances to access our datasets. There are many machine learning algorithms that could be utilized to optimize to run efficiently against extremely large data in a distributed environment. There are many specific features(“perks”) for choosing SageMaker as our main service. We will illustrate the details below.
* it includes native support for our own algorithms and frameworks
 * SageMaker offers flexible distributed training options that adjust to users' specific workflows. This means that we could deploy a model into a secure and scalable environment by launching it with only a few clicks from SageMaker Studio or the SageMaker console. Moreover, training and hosting are billed by minutes of usage, with no minimum fees and no upfront commitments. For our case, SageMaker is easy to adapt to our customized Random Forest algorithm specifically designed to process gene expression data. This is a great advantage since we need to parallelize other researchers’ existing code. This is a platform perfect for our project’s use.

