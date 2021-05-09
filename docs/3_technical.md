---
layout: default
title: Technical Details
nav_order: 3
---

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Links to repository with source code, evaluation data sets and test cases 没有！！o(╥﹏╥)o
[View Repo on GitHub](https://github.com/cs205-genie3-parallel/genie3-parallel){: .btn .btn-purple .fs-5 .mb-4 .mb-md-0 }
[SageMaker Output Dataset Sample](https://cs205-final.s3.amazonaws.com/output/healthy_0_3000_alljobs){: .btn .fs-5 .mb-4 .mb-md-0 }
[PySpark Performance Evaluation Dataset - 17 millions gene records](https://genie3-proj.s3.amazonaws.com/ranking_idx.txt){: .btn .fs-5 .mb-4 .mb-md-0 }
[PySpark Output Dataset - Vertices](https://genie3-proj.s3.amazonaws.com/vertices.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }
[PySpark Output Dataset - Edges](https://genie3-proj.s3.amazonaws.com/graph_edges.csv/part-00000){: .btn .fs-5 .mb-4 .mb-md-0 }

## Technical Description of the Software Design 也没有！！o(╥﹏╥)o
### SageMaker

For a machine learning job with prepared data for training and testing, SageMaker offers a notebook interface for directly training, testing and deploying estimators on selected AWS EC2 instances. However, since we are using the GENIE3 programming model, we would need to run our custom training script. As novices to SageMaker, we used a SKLearn estimator just for the function of a wrapper. In the custom estimator, we can specify the entry point script, the type of EC2 instance and “hyperparameters” (understandably misused) which will be passed into the entry point script as command line arguments. This is probably a less standard solution of running a custom script on SageMaker and there might be other solutions out there. However, after extensive research and troubleshooting, we find that this is able to fulfil our requirements of orchestrating parallelized computation for now.

```
customer_estimator = SKLearn(entry_point = 'GENIE3-sagemaker.py',
                            role=get_execution_role(),
                            instance_type='ml.m4.xlarge',
                            framework_version='0.20.0',
                            hyperparameters = {'start_idx': 0, 'stop_idx': 6000, 'n_jobs': -1, 'fname': 'healthy_0_6000_alljobs'})
healthy_uri = f"s3://{bucket_name}/healthy.tsv"
custom_estimator.fit({'train':healthy_uri})
```
In the entry point script, it contains functions from GENIE3 with changes intended to only limit the analysis for genes between the start index and the stop index, instead of running the analysis for all the genes. We also added in a n_jobs argument to parallelize each SKLearn random forest computation.
The main function contains a parser for the arguments passed from the custom estimator, the main GENIE3 function calls, as well as utility functions to read, process data from AWS S3 and to upload output to S3.

```
if __name__ =='__main__':
 
    parser = argparse.ArgumentParser()
 
    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument('--start_idx', type=int, default=0)
    parser.add_argument('--stop_idx', type=int, default=10)
    parser.add_argument('--nthreads', type=int, default=1)
    parser.add_argument('--n_jobs', type=int, default=1)
    parser.add_argument('--fname', type=str, default='output_ranking.txt')
 
    # Data, model, and output directories
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
 
    args, _ = parser.parse_known_args()
 
    bucket_name = 'cs205-final'
    s3 = boto3.resource('s3')
    output_path = f"s3://{bucket_name}/output/"
 
    data, gene_names = preprocess_data(os.path.join(args.train, "healthy.tsv"))
 
    VIM = GENIE3(data, gene_names=gene_names, start_idx=args.start_idx, stop_idx=args.stop_idx,nthreads=args.nthreads,n_jobs=args.n_jobs)
    output_fname = os.path.join('/opt/ml/output/data', args.fname)
    get_link_list(VIM, gene_names=gene_names, file_name=output_fname)
    
    response = upload_file_to_s3(output_path, output_fname, args.fname)
    print(response)
```

### Spark

## Code Baseline 还是没有！！o(╥﹏╥)o

## Dependencies
* sklearn==0.24.2
* sagemaker==2.39.0
* boto3

## How to Use the Code 能不能问寒和佳慧把你们的使用指南/terminal call加在这里！！

### SageMaker
**System and environment:**
- SageMaker notebook instance: ml.t2.medium (default)
- Kernel: conda_python3 (out of the options provided by SageMaker)

**Steps for running the code:**
- Start an AWS SageMaker notebook instance following [this guide] (https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html), setting Github repo to [our repo] (https://github.com/cs205-genie3-parallel/genie3-parallel.git).
- Install requirements with `pip install -r requirements.txt`
- Navigate to sagemaker/GENIE3-sagemaker.ipynb. Select conda_python3 as the kernel.
- Run all the cells, edit the `instance_type`, `hyperparameters` as needed and indicate `start_idx` and `stop_idx` to choose the target genes to compute on.


## System and environment needed to reproduce our tests 麻烦你们double check一下有没有问题
