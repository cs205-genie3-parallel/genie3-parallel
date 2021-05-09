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

### Experiment 1: Comparison of shared memory parallelism solutions

Does parallelism actually work? Is there a difference between Python multiprocessing and SKLearn multiple jobs? Should we use both or which is better?

| Type of instance| No. of CPUs | Python multiprocessing| No. of SKLearn jobs | No. of genes computed | Total processing time including start-up (s) | Elapsed time (s) | Speed-up (for elapsed time)
|:-------------|:------------------|:------|
| ml.m4.xlarge    | 4           | 1                     | 1                   | 10                    | 161|101.89|1|
| ml.m4.xlarge    | 4           | 4                     | 1                   | 10                    | 108|44.43|2.29|
| ml.m4.xlarge    | 4           | 1                     | 4                   | 10                    | 108|49.44|2.07|
| ml.m4.xlarge    | 4           | 4                     | 4                   | 10                    | 134|43.03|2.37|

**Takeaways:**
- Using more processes certainly reduced runtime significantly, though it did not necessarily achieve speed-up linear to the number of processes used. 
- Running on only 10 genes, the speed-up effect of using 4 Python processes is slightly better than using 4 SKLearn jobs. 
- When trying to use both Python multiprocessing and SKLearn multiple-jobs together, the elapsed run time minimally decreased but the total processing time actually increased significantly compared to using either one. This suggests that Python multiprocessing and SKLearn multiple-jobs might be using similar parallel processing solutions and using both might cause interference and not improvement.

### Experiment 2: Optimal configuration of shared memory parallelism 

At a higher number of genes, is Python multiprocessing better or SKLearn multiple-jobs better? How many jobs is “all jobs” in SKLearn n_jobs parameter?

| Type of instance| No. of CPUs | Python multiprocessing| No. of SKLearn jobs | No. of genes computed | Elapsed time (s) | Speed-up (for elapsed time)
|:-------------|:------------------|:------|
| ml.m4.xlarge    | 4           | 1                     | 1                   | 100                   | 1018.9 (Extrapolated)|1|
| ml.m4.xlarge    | 4           | 1                     | All                 | 100                   | 488.20|2.09|
| ml.m4.xlarge    | 4           | 1                     | 32                  | 100                   | 502.27|2.03|
| ml.m4.xlarge    | 4           | 32                    | 1                   | 100                   | 977.04|1.04|

**Takeaways:**
- Running with 32 jobs using SKLearn is much more efficient than running with 32 Python processes
- With 32 processes, Python multiprocessing has so much overhead that it cancelled out the gains of parallelism and has similar runtime to the extrapolated linear runtime.
- SKLearn running with all jobs is slightly faster than with 32 jobs, though not significantly.

