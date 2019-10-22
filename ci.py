import numpy as np
import pandas as pd
from scipy import stats
import sys
import glob

CI = 0.95

#fn = results/Base_0051_Batch_3805321_batch_results.csv
fns = glob.glob("results/*-1-2.csv")

all_valid_scores = []

def get_mos(name, scores):
    mu = scores.mean()
    sigma = np.sqrt(scores.var())
    N = scores.shape[0]
    interval = stats.norm.interval(CI, loc=mu, scale=sigma/np.sqrt(N))
    half_interval = (interval[1] - interval[0]) / 2
    return mu, half_interval, N
    print("{} {} {} {}".format(name, mu, half_interval, N))


for fn in fns:
    data = pd.read_csv(fn)
    correct = data[data['AssignmentStatus'] != 'Rejected']

    col_names = correct.columns

    gt_cols = [c for c in col_names if c[:9] == "Answer.GT"]
    bad_cols = [c for c in col_names if c[:10] == "Answer.bad"]
    test_col = [c for c in col_names if c not in gt_cols and c not in bad_cols and c[:6] == "Answer"][0]

    correct = []
    gt_scores = [data[c] for c in gt_cols]
    bad_scores = [data[c] for c in bad_cols]
    correct = data.loc[(gt_scores[0] > bad_scores[0]) &
                       (gt_scores[1] > bad_scores[0]) &
                       (gt_scores[0] > bad_scores[1]) &
                       (gt_scores[1] > bad_scores[1])]
    valid_scores = correct[test_col]

    #print_mos(test_col, valid_scores)

    all_valid_scores += list(valid_scores)

def get_ci(answers):
    col_names = list(answers[0].keys())
    gt_cols = [c for c in col_names if c[:2] == "GT"]
    bad_cols = [c for c in col_names if c[:3] == "bad"]
    test_col = [c for c in col_names if c not in gt_cols and c not in bad_cols][0]

    correct = []
    gt_scores = np.array([[a[c] for c in gt_cols] for a in answers])
    bad_scores = np.array([[a[c] for c in bad_cols] for a in answers])
    correct = np.where((gt_scores[:,0] > bad_scores[:,0]) &
                       (gt_scores[:,1] > bad_scores[:,0]) &
                       (gt_scores[:,0] > bad_scores[:,1]) &
                       (gt_scores[:,1] > bad_scores[:,1]))[0]
    valid_scores = np.array([int(answers[c][test_col]) for c in correct])
    return get_mos(test_col, valid_scores)

#print_mos("overall", np.array(all_valid_scores))
