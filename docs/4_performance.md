---
layout: default
title: Performance
nav_order: 4
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

(speed-up, throughput, weak and strong scaling) and discussion about overheads and optimizations done

## Performance Evaluation for GENIE3 on AWS SageMaker

We ran detailed experiments to investigate the effect of speed-up at different combinations of parallelism set-up and to find out the optimal set-up. As mentioned, the levels of parallelism includes number of instances, instance type (entails number of CPUs, GPUs and amount of memory), number of jobs for SKLearn random forest estimator, and number of processes for Python multiprocessing.

### Experiment 1: Comparison of shared memory parallelism configurations

Does parallelism actually work? Is there a difference between Python multiprocessing and SKLearn multiple jobs? Should we use both or which is better?

| Type of instance| No. of CPUs | Python multiprocessing| No. of SKLearn jobs | No. of genes computed | Total processing time including start-up (s) | Elapsed time (s) | Speed-up (for elapsed time)
|:-------------|:------------------|:------|
| ml.m4.xlarge    | 4           | 1                     | 1                   | 10                    | 161|101.89|1|
| ml.m4.xlarge    | 4           | 4                     | 1                   | 10                    | 108|44.43|2.29|
| ml.m4.xlarge    | 4           | 1                     | 4                   | 10                    | 108|49.44|2.07|
| ml.m4.xlarge    | 4           | 4                     | 4                   | 10                    | 134|43.03|2.37|

