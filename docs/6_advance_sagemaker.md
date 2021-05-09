---
layout: default
title: Advanced Features
nav_order: 6
---
## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Description of advanced features 
*Models/platforms not Explained in Class, Advanced Functions of Modules*


### SageMaker
In our project, we incorporate SageMaker to parallelize our model. Amazon SageMaker is an easy-to-use machine learning service. It enables us to use Jupyter authoring notebook instances to access our datasets. There are many machine learning algorithms that could be utilized to optimize to run efficiently against extremely large data in a distributed environment. There are many specific features(“perks”) for choosing SageMaker as our main service. We will illustrate the details below.

### Support for Our Own Algorithms and Frameworks
  * SageMaker offers flexible distributed training options that adjust to users' specific workflows. This means that we could deploy a model into a secure and scalable environment by launching it with only a few clicks from SageMaker Studio or the SageMaker console. Moreover, training and hosting are billed by minutes of usage, with no minimum fees and no upfront commitments. For our case, SageMaker is easy to adapt to our customized Random Forest algorithm specifically designed to process gene expression data. This is a great advantage since we need to parallelize other researchers’ existing code. This is a platform perfect for our project’s use.
  
### Studio
  * SageMaker Studio is an integrated development environment (IDE) that we used to build, train, debug, deploy, and monitor our machine learning models. It helps us to take our models from experimentation to production while boosting productivity easily. The best thing we like about the Studio is that we could operate in a single unified visual interface. We are able to conveniently link our Github repository and write and execute code in Jupyter notebooks. In addition, for the test/experiment stage, we could deploy the models and monitor the performance of each model. At last, Studio also makes it easier to track and debug the machine learning experiments.

### Model Building Pipelines
  * This is also a feature we have tried out in our process. We tried SageMaker Model Building Pipelines to help build machine learning pipelines that take advantage of direct SageMaker integration. Because of this integration, we can create a pipeline and set up SageMaker Projects without worrying about the step creation and management. The easy steps include:(code of our pipeline attached)
  * setup the environment<img width="776" alt="Screen Shot 2021-05-08 at 11 42 41" src="https://user-images.githubusercontent.com/35304349/117558249-a870d480-b049-11eb-8db8-ad0739058f41.png">
  * download the dataset<img width="778" alt="Screen Shot 2021-05-08 at 11 42 47" src="https://user-images.githubusercontent.com/35304349/117558252-adce1f00-b049-11eb-8272-7da68d08b911.png">
  * define pipeline parameters<img width="776" alt="Screen Shot 2021-05-08 at 11 42 52" src="https://user-images.githubusercontent.com/35304349/117558263-b7578700-b049-11eb-90e1-bb80503d9535.png">
  * define training step<img width="776" alt="Screen Shot 2021-05-08 at 11 43 00" src="https://user-images.githubusercontent.com/35304349/117558264-ba527780-b049-11eb-9bcc-1fd2deec2da6.png">

### Function Estimator
  * We have our code attached in the previous section. Some more technical details. Estimators is a high level interface for SageMaker training. It could handle end-to-end Amazon SageMaker training and deployment tasks. We could define a way to determine what image to use for training, what hyperparameters to use, and how to create an appropriate predictor instance.

### Data Wrangler
  * This feature includes lots of functions , including import, prepare, transform, featurize, and analyze data. However, we mainly utilize the Import and Data Flow parts. For our project, we use this to connect to and import data from Amazon Simple Storage Service (Amazon S3) directly. This enables a smooth pipeline of combining our data source, SageMaker scripts, Jupyter Notebook, and Spark scripts.

### Studio Notebook
  * Our motivation to use Studio Notebook is that we have been using Jupyter Notebook in other platforms and classes, and we are familiar with the features of Jupyter Notebook. It has following benefits:
  * Amazon SageMaker Studio notebooks are collaborative notebooks that we can launch quickly because we don't need to set up compute instances and file storage beforehand. A set of instance types, known as Fast launch types are designed to launch in under two minutes. This increases the productivity of the experiments we described in other sections of our report. 
  * In addition, Studio notebooks provide persistent storage, which enables us to view and share notebooks even if the instances that the notebooks run on are shut down.
  
### Preprocessing
  * This is a feature we suggest future researchers could use to combine with our notebooks and scripts. We originally plan to use this feature to manage our data processing workloads, such as feature engineering, data validation, model evaluation, and model interpretation. However, due to limited time and Amazon resources, we could not utilize this. But our pipeline could be modified to fit this feature easily.

### Techniques to Mitigate Overheads
* The configuration of the number of CPU used. Through the experiment, we parallelize the process using 4 to 72 cores. However, the optimal number of cores is 8 cores. The reason might be it minimizes the data transfer and communication cost comparing to larger number of cores.

### Challenging Oarallelization or Implementation Aspects
* Data size too big: with limited instance and memory resources we have, we need to choose carefully the most economical-friendly instance with as large memory as possible.
* Though AWS estimator allows multiple instances for each job, it requires us to convert our data to a different data type which is harder to process and modify in our original cod. Hence, considering the trade off, we didn’t use it. 

