import argparse
import os
# from sklearn.tree.tree import BaseDecisionTree
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from numpy import *
import time
from operator import itemgetter
from multiprocessing import Pool
import pandas as pd
import boto3


def compute_feature_importances(estimator):
#     if isinstance(estimator, BaseDecisionTree):
#         return estimator.tree_.compute_feature_importances(normalize=False)
#     else:
    importances = [e.tree_.compute_feature_importances(normalize=False)
                       for e in estimator.estimators_]
    importances = asarray(importances)
    # number of samples meeting these conditions / total number of samples
    return sum(importances,axis=0) / len(estimator)



def get_link_list(VIM,gene_names=None,regulators='all',maxcount='all',file_name=None):

    """Gets the ranked list of (directed) regulatory links.

    Parameters
    ----------

    VIM: numpy array
        Array as returned by the function GENIE3(), in which the element (i,j) is the score of the edge directed from the i-th gene to the j-th gene.

    gene_names: list of strings, optional
        List of length p, where p is the number of rows/columns in VIM, containing the names of the genes. The i-th item of gene_names must correspond to the i-th row/column of VIM. When the gene names are not provided, the i-th gene is named Gi.
        default: None

    regulators: list of strings, optional
        List containing the names of the candidate regulators. When a list of regulators is provided, the names of all the genes must be provided (in gene_names), and the returned list contains only edges directed from the candidate regulators. When regulators is set to 'all', any gene can be a candidate regulator.
        default: 'all'

    maxcount: 'all' or positive integer, optional
        Writes only the first maxcount regulatory links of the ranked list. When maxcount is set to 'all', all the regulatory links are written.
        default: 'all'

    file_name: string, optional
        Writes the ranked list of regulatory links to the file file_name.
        default: None



    Returns
    -------

    The list of regulatory links, ordered according to the edge score. Auto-regulations do not appear in the list. Regulatory links with a score equal to zero are randomly permuted. In the ranked list of edges, each line has format:

        regulator   target gene     score of edge
    """

    # Check input arguments
#     if not isinstance(VIM,ndarray):
#         raise ValueError('VIM must be a square array')
#     elif VIM.shape[0] != VIM.shape[1]:
#         raise ValueError('VIM must be a square array')

    ngenes = VIM.shape[0]

#     if gene_names is None:
#         gene_names = []
#     else:
#         if not isinstance(gene_names,(list,tuple,ndarray)):
#             raise ValueError('input argument gene_names must be a list of gene names')
#         elif len(gene_names) != ngenes:
#             raise ValueError('input argument gene_names must be a list of length p, where p is the number of columns/genes in the expression data')

    if regulators != 'all':
        if not isinstance(regulators,(list,tuple)):
            raise ValueError('input argument regulators must be a list of gene names')

        if gene_names is None:
            raise ValueError('the gene names must be specified (in input argument gene_names)')
        else:
            sIntersection = set(gene_names).intersection(set(regulators))
            if not sIntersection:
                raise ValueError('The genes must contain at least one candidate regulator')

    if maxcount != 'all' and not isinstance(maxcount,int):
        raise ValueError('input argument maxcount must be "all" or a positive integer')

    if file_name and not isinstance(file_name,str):
        raise ValueError('input argument file_name must be a string')



    # Get the indices of the candidate regulators
    if regulators == 'all':
        input_idx = range(ngenes)
    else:
        input_idx = [i for i, gene in enumerate(gene_names) if gene in regulators]

    # Get the non-ranked list of regulatory links
    vInter = [(i,j,score) for (i,j),score in ndenumerate(VIM) if i in input_idx and i!=j]

    # Rank the list according to the weights of the edges
    vInter_sort = sorted(vInter,key=itemgetter(2),reverse=True)
    nInter = len(vInter_sort)

    # Random permutation of edges with score equal to 0
    flag = 1
    i = 0
    while flag and i < nInter:
#         print(f'nInter = {i}')
        (TF_idx,target_idx,score) = vInter_sort[i]
        if score == 0:
            flag = 0
        else:
            i += 1

    if not flag:
        items_perm = vInter_sort[i:]
        items_perm = random.permutation(items_perm)
        vInter_sort[i:] = items_perm

    # Write the ranked list of edges
    nToWrite = nInter
    if isinstance(maxcount,int) and maxcount >= 0 and maxcount < nInter:
        nToWrite = maxcount

    if file_name:

        outfile = open(file_name,'w')

        for i in range(nToWrite):
            (TF_idx,target_idx,score) = vInter_sort[i]
            TF_idx = int(TF_idx)
            target_idx = int(target_idx)
            outfile.write('%s\t%s\t%.6f\n' % (gene_names[TF_idx],gene_names[target_idx],score))
        
        if gene_names is None:
            for i in range(nToWrite):
                (TF_idx,target_idx,score) = vInter_sort[i]
                TF_idx = int(TF_idx)
                target_idx = int(target_idx)
                outfile.write('G%d\tG%d\t%.6f\n' % (TF_idx+1,target_idx+1,score))


        outfile.close()

    else:

        if gene_names is None:
            for i in range(nToWrite):
                (TF_idx,target_idx,score) = vInter_sort[i]
                TF_idx = int(TF_idx)
                target_idx = int(target_idx)
                print('G%d\tG%d\t%.6f' % (TF_idx+1,target_idx+1,score))
        else:
            for i in range(nToWrite):
                (TF_idx,target_idx,score) = vInter_sort[i]
                TF_idx = int(TF_idx)
                target_idx = int(target_idx)
                print('%s\t%s\t%.6f' % (gene_names[TF_idx],gene_names[target_idx],score))


def GENIE3(expr_data,gene_names=None,start_idx=None,stop_idx=None,regulators='all',tree_method='RF',K='sqrt',ntrees=1000): #,nthreads=1

    '''Computation of tree-based scores for all putative regulatory links.

    Parameters
    ----------

    expr_data: numpy array
        Array containing gene expression values. Each row corresponds to a condition and each column corresponds to a gene.

    gene_names: list of strings, optional
        List of length p, where p is the number of columns in expr_data, containing the names of the genes. The i-th item of gene_names must correspond to the i-th column of expr_data.
        default: None

    regulators: list of strings, optional
        List containing the names of the candidate regulators. When a list of regulators is provided, the names of all the genes must be provided (in gene_names). When regulators is set to 'all', any gene can be a candidate regulator.
        default: 'all'

    tree-method: 'RF' or 'ET', optional
        Specifies which tree-based procedure is used: either Random Forest ('RF') or Extra-Trees ('ET')
        default: 'RF'

    K: 'sqrt', 'all' or a positive integer, optional
        Specifies the number of selected attributes at each node of one tree: either the square root of the number of candidate regulators ('sqrt'), the total number of candidate regulators ('all'), or any positive integer.
        default: 'sqrt'

    ntrees: positive integer, optional
        Specifies the number of trees grown in an ensemble.
        default: 1000

    nthreads: positive integer, optional
        Number of threads used for parallel computing
        default: 1


    Returns
    -------
    An array in which the element (i,j) is the score of the edge directed from the i-th gene to the j-th gene. All diagonal elements are set to zero (auto-regulations are not considered). When a list of candidate regulators is provided, the scores of all the edges directed from a gene that is not a candidate regulator are set to zero.

    G1, G2, G3, G4, G5, ... GN
    num cols (genes) = N
    num rows (samples) = M
    k = sqrt(N)
    ntrees = 1000

    not even one gene, time complexity one tree = Nk logk
    one gene, time complexity of one RF = ntrees * Nk logk
    all genes, number of trees in all RF = ntrees * (N^2)k logk

    G1  G5  0.0342   1
    G1  G2  0.0324   1
    G2  G13 0.0274   0

    N^2 = 30,000^2 = 900,000,000

    Threshold: e.g. 0.3
    '''

    time_start = time.time()

    # Check input arguments
    if not isinstance(expr_data,ndarray):
        raise ValueError('expr_data must be an array in which each row corresponds to a condition/sample and each column corresponds to a gene')

    ngenes = expr_data.shape[1]
    
    if gene_names is None:
        gene_names = []
    else:
        if not isinstance(gene_names,(list,tuple,ndarray)):
            raise ValueError('input argument gene_names must be a list of gene names')
        elif len(gene_names) != ngenes:
            raise ValueError('input argument gene_names must be a list of length p, where p is the number of columns/genes in the expr_data')

    if regulators != 'all':
        if not isinstance(regulators,(list,tuple)):
            raise ValueError('input argument regulators must be a list of gene names')

        if gene_names is None:
            raise ValueError('the gene names must be specified (in input argument gene_names)')
        else:
            sIntersection = set(gene_names).intersection(set(regulators))
            if not sIntersection:
                raise ValueError('the genes must contain at least one candidate regulator')

    if tree_method != 'RF' and tree_method != 'ET':
        raise ValueError('input argument tree_method must be "RF" (Random Forests) or "ET" (Extra-Trees)')

    if K != 'sqrt' and K != 'all' and not isinstance(K,int):
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if isinstance(K,int) and K <= 0:
        raise ValueError('input argument K must be "sqrt", "all" or a stricly positive integer')

    if not isinstance(ntrees,int):
        raise ValueError('input argument ntrees must be a stricly positive integer')
    elif ntrees <= 0:
        raise ValueError('input argument ntrees must be a stricly positive integer')


    print('Tree method: ' + str(tree_method))
    print('K: ' + str(K))
    print('Number of trees: ' + str(ntrees))
    print('\n')


    # Get the indices of the candidate regulators
    if regulators == 'all':
        input_idx = list(range(ngenes))
    else:
        input_idx = [i for i, gene in enumerate(gene_names) if gene in regulators]


    # Learn an ensemble of trees for each target gene, and compute scores for candidate regulators
#     VIM = zeros((ngenes,ngenes))
    VIM = zeros((stop_idx-start_idx,ngenes))

    # if nthreads > 1:
    #     print('running jobs on %d threads' % nthreads)

    #     # list of list of paramaters, len is ngenes
    #     input_data = list()
    #     for i in range(ngenes):
    #         # Parameters of GENIE3 function, i refers to output_idx
    #         input_data.append( [expr_data,i,input_idx,tree_method,K,ntrees] )

    #     # PARALLEL process targeting each gene
    #     pool = Pool(nthreads)
    #     alloutput = pool.map(wr_GENIE3_single, input_data)

    #     # len(alloutput) is ngenes
    #     for (i,vi) in alloutput:
    #         VIM[i,:] = vi

    # else:


    print('running single threaded jobs')
    for i in range(stop_idx-start_idx):
        print('Gene %d/%d...' % (i+start_idx,stop_idx))

        vi = GENIE3_single(expr_data,i,input_idx,tree_method,K,ntrees)
        VIM[i,:] = vi


    VIM = transpose(VIM)

    time_end = time.time()
    print("Elapsed time: %.2f seconds" % (time_end - time_start))

    return VIM


# function for single thread
def wr_GENIE3_single(args):
    return([args[1], GENIE3_single(args[0], args[1], args[2], args[3], args[4], args[5])])


# In parallel, split up the output_idx
def GENIE3_single(expr_data,output_idx,input_idx,tree_method,K,ntrees):

    ngenes = expr_data.shape[1]

    # Expression of target gene, select column
    output = expr_data[:,output_idx]

    # Normalize output data
    output = output / std(output)

    # Remove target gene from candidate regulators
    input_idx = input_idx[:]
    if output_idx in input_idx:
        input_idx.remove(output_idx)
    expr_data_input = expr_data[:,input_idx]

    # Parameter K of the tree-based method
    if (K == 'all') or (isinstance(K,int) and K >= len(input_idx)):
        max_features = "auto"
    else:
        max_features = K

    if tree_method == 'RF':
        treeEstimator = RandomForestRegressor(n_estimators=ntrees,max_features=max_features)
    elif tree_method == 'ET':
        treeEstimator = ExtraTreesRegressor(n_estimators=ntrees,max_features=max_features)

    # Learn ensemble of trees
    treeEstimator.fit(expr_data_input,output)

    # Compute importance scores
    feature_importances = compute_feature_importances(treeEstimator)
    vi = zeros(ngenes)

    # for each target, all the other genes
    vi[input_idx] = feature_importances

    return vi

def preprocess_data(uri):
#     print("URI: " + uri)
#     print(os.listdir(uri))
    df = pd.read_csv(uri, sep='\t')
    gene_names = df['Gene Name'].values 
    df = df.drop(['Gene ID'], axis=1)
    df = df.set_index('Gene Name', drop=True)
    df_T = df.T
    df_T = df_T.fillna(0)
    data = df_T.values
    return data, gene_names
    

if __name__ =='__main__':

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script.
    # parser.add_argument('--epochs', type=int, default=50)
    # parser.add_argument('--batch-size', type=int, default=64)
    # parser.add_argument('--learning-rate', type=float, default=0.05)
    parser.add_argument('--start_idx', type=int, default=0)
    parser.add_argument('--stop_idx', type=int, default=10)
#     parser.add_argument('--gene_names', type=list, default=[])

    # Data, model, and output directories
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    # parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    # parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))

    args, _ = parser.parse_known_args()
    
#     m_boto3 = boto3.client('sagemaker') 


    
#     bucket_name = 'cs205-final'
    s3 = boto3.resource('s3')
#     healthy_uri = f"s3://{bucket_name}/healthy.tsv"
#     cancer_uri = f"s3://{bucket_name}/675_cancer.tsv"
#     output_path = f"s3://{bucket_name}/output/"

#     input_files = [ os.path.join(args.train, file) for file in os.listdir(args.train) ]
#     raw_data = [ pd.read_csv(file, header=None, engine="python") for file in input_files ]

    data, gene_names = preprocess_data(os.path.join(args.train, "healthy.tsv"))
    print(args.start_idx)
    print(args.stop_idx)
#     print(gene_names)

    #VIM = GENIE3(healthy_arr[:,:5])

    VIM = GENIE3(data, gene_names=gene_names, start_idx=args.start_idx, stop_idx=args.stop_idx)
    get_link_list(VIM, gene_names=gene_names, file_name='healthy_output_ranking.txt')
    
    
#     from boto.s3.key import Key
#     key = Key('hello.txt')
#     key.set_contents_from_file('/tmp/hello.txt')

#     # Boto 3
#     s3.Object('mybucket', 'hello.txt').put(Body=open('/tmp/hello.txt', 'rb'))


    # ... load from args.train and args.test, train a model, write model to args.model_dir.
