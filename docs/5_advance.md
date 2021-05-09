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

* Studio
 * SageMaker Studio is an integrated development environment (IDE) that we used to build, train, debug, deploy, and monitor our machine learning models. It helps us to take our models from experimentation to production while boosting productivity easily. The best thing we like about the Studio is that we could operate in a single unified visual interface. We are able to conveniently link our Github repository and write and execute code in Jupyter notebooks. In addition, for the test/experiment stage, we could deploy the models and monitor the performance of each model. At last, Studio also makes it easier to track and debug the machine learning experiments.
* model building pipelines
 *This is also a feature we have tried out in our process. We tried SageMaker Model Building Pipelines to help build machine learning pipelines that take advantage of direct SageMaker integration. Because of this integration, we can create a pipeline and set up SageMaker Projects without worrying about the step creation and management. The easy steps include:(code of our pipeline attached)
setup the environment
