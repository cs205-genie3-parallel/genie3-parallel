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
- Running with 32 jobs using SKLearn is much more efficient than running with 32 Python processes. Going forward, we have decided to use SKLearn multiple-jobs instead of Python multiprocessing.
- With 32 processes, Python multiprocessing has so much overhead that it cancelled out the gains of parallelism and has similar runtime to the extrapolated linear runtime.
- SKLearn running with all jobs is slightly faster than with 32 jobs, though not significantly.

### Experiment 3: Cost-effectiveness of vertical scaling
How much speed-up can we get from using instances with more CPUs? What about GPU instances? Are the more expensive EC2 instances worth it?

| Type of instance| No. of CPUs | No. of SKLearn jobs | No. of genes computed | Total processing time including start-up (s) | Speed-up | Price per hour and mark-up |
|:-------------|:------------------|:------|
| ml.m4.xlarge    | 4           | 32                  | 100                   | 591|1|$0.24 (1)|
| ml.m5.2xlarge   | 8           | 32                  | 100                   | 374|1.58|$0.461 (1.92)|
| ml.m5.4xlarge   | 16          | 32                  | 100                   | 347|1.70|$0.922 (3.84)|
| ml.m5.10xlarge  | 40          | 32                  | 100                   | 342|1.73|$2.40 (10)|

_Note: Speed-up for this experiment is calculated based on total processing time which is the total billable time._

**Takeaways:**
- GPU instances were actually not available to us because we were using a SKLearn estimator wrapper to run our custom script.
- The speed-up (with the instance with 4 CPUs as the baseline) is significant when the number of CPUs increases to 8, however from 8 to 16 and 16 to 40 CPUs, the speed-up is minimal.
- Economically, it is not worth it to use the larger instances as the speed-up does not match the mark-up in the cost.

### Experiment 4: Effect of memory on throughput and successful completion of job

| Type of instance| No. of CPUs | Memory              | No. of SKLearn jobs | No. of genes computed | Elapsed time (s) | Speed-up (compared across same throughput)|
|:-------------|:------------------|:------|
| ml.m5.2xlarge   | 8           | 32 GB `memory error`| All                 | 6000                  |15947.86  |1|
| ml.m5.2xlarge   | 8           | 32 GB `memory error`| All                 | 3000                  |8178.34   |1|
| ml.m5.4xlarge   | 16          | 64 GB `memory error`| All                 | 6000                  |13236.91  |1.20|
| ml.m5.4xlarge   | 16          | 64 GB               | All                 | 3000                  |6470.35   |1.26|
| ml.c5.2xlarge   | 8           | 16 GB `memory error`| All                 | 6000                  |14034.08  |1.14|
| ml.c5.2xlarge   | 8           | 16 GB `memory error`| All                 | 3000                  |6891.09   |1.29|
| ml.c5.4xlarge   | 16          | 32 GB `memory error`| All                 | 6000                  |10550.77  |1.51|
| ml.c5.4xlarge   | 16          | 32 GB `memory error`| All                 | 3000                  |5401.38   |1.51|
| ml.c5.9xlarge   | 32          | 72 GB `memory error`| All                 | 6000                  |9715.57   |1.64|
| ml.c5.9xlarge   | 32          | 72 GB               | All                 | 3000                  |5081.83   |1.61|
| ml.c5.18xlarge  | 72          | 144 GB              | All                 | 6000                  |10317.16  |1.55|

_Note: Speed-up is compared across same throughout, i.e. 6000 genes or 3000 genes._

**Takeaways:**
- When running separate instances to get the final output, we unexpectedly ran into memory error. This meant that even though the jobs finished computing all of the genes, the memory was not large enough to write the pairwise correlations one by one to the output file.
- If running on 6000 genes, only the instance with 144 GB of memory could output without error; If running on 3000 genes, only the instances with 64 GB or 72 GB of memory could output without error. This brings in a new dimension to consider when choosing instances.
- The highest speed-up was 1.64 even though we tried using as 9 times as many CPUs at one point. This points to limited gains in speed-up with increasing CPU number, probably as a result of communications overhead.

