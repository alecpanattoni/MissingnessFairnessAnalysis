#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from scipy.stats import bernoulli

import matplotlib.pylab as plt


# In[3]:


def mcar(dataset : pd.DataFrame, column : str, p = 0.2):
    """
    Missing Completely at Random -- there is no dependency of the rate of
    missingness on other values or the value itself.
    
    dataset: the dataframe
    column: the column in which missingness will be produced
    p: The probability in which each value has of being missing

    Generated with each value having probability p of being a missing value
    """
    # check for p
    if (p < 0) or (p > 1):
        raise Exception('probability of missing values must be between 0 and 1')

    # go over values in the target column, 
    # randomly make it missing based on probability p
    for i, val in enumerate(dataset[column]):
        if np.random.choice([1, 0], p = [p, 1 - p]) == 1:
                dataset[column].iloc[i] = np.nan
    
    # return edited dataset
    return dataset


# In[4]:


def mar(dataset : pd.DataFrame, miss_column : str, dep_column : str, b = 0.5):
    """
    Missing at Random -- data is missing due to dependency on another
    variable.
    
    dataset: the dataframe
    miss_column: the column in which missingness will be produced
    dep_column: the column in which missingness is dependent on
    b: tuning parameter between 0 and 1; the higher the beta, the more missingness

    Missingness is generated differently depeending on the type of the dependent column.
    If the dep_column is categorical, for each unique categorical value, a random z-score is
    generated from a normal distribution and put into a sigmoid function. This will produce
    a probability for each unique value of dep_column. For a dep_column with a numerical type,
    the z-score of each value is determined and passed into a sigmoid function to determine
    the probability of missingness for each value. Then, for each tuple in the dataframe, the
    probability that each value in miss_column will be missing is determined by the probability
    generated by the sigmoid function of that tuples' dep_column value. The beta value is
    multiplied by the generated probability as a way to tune how much missingness is generated.
    The higher the beta value (between 0 and 1), the more missingness is generated. 
    """
    # check for beta
    if (b < 0) or (b > 1):
        raise Exception('beta value must be between 0 and 1')

    # helper sigmoid function
    def sig(x):
        return 1 / (1 + np.exp(-x))
    

    # check for categorical
    if (dataset.dtypes.loc[dep_column] == object) or (dataset.dtypes.loc[dep_column] == bool):
        # generate probabilities -> sigmoid for each unique categorical value
        cat_dict = {cat: sig(np.random.normal()) for cat in dataset[dep_column].unique()}
        
        # generate missingness based on generated probabilities
        for i in range(dataset.shape[0]):
            dep_val = dataset.iloc[i, dataset.columns.get_loc(dep_column)]
            if np.random.choice([1, 0], p = [cat_dict[dep_val] * b, 1 - (cat_dict[dep_val] * b)]) == 1:
                dataset[miss_column].iloc[i] = np.nan
    else:
        # normalize the value (create Z value)
        def norm(val, mean, std):
            return (val - mean) / std
        
        # take mean and standard deviation for Z-value
        mean = np.mean(dataset[dep_column])
        std = np.std(dataset[dep_column])

        # generate missingness using normal distribution
        for i in range(dataset.shape[0]):
            dep_val = dataset.iloc[i, dataset.columns.get_loc(dep_column)]
            prob = sig(norm(dep_val, mean, std))
            if np.random.choice([1, 0], p = [prob * b, 1 - (prob * b)]) == 1:
                dataset[miss_column].iloc[i] = np.nan
        

    return dataset


# In[6]:


def nmar(dataset : pd.DataFrame, column : str, b = 0.5):
    """
    Not Missing at Random -- data is missing due to the value of the variable
    itself. For example, sales not recorded for the stores that produced less
    than a specific amount of revenue.
    
    dataset: the dataframe
    column: the column in which missingness will be produced
    b: tuning parameter between 0 and 1; the higher the beta, the more missingness

    Missingness is generated differently depending on the type of the column.
    If the column is categorical, for each unique categorical value, a random z-score is
    generated from a normal distribution and put into a sigmoid function. This will produce
    a probability for each unique value of the column. If the column is numerical, the 
    z-score of each value is determined and passed into a sigmoid function to determine
    the probability of missingness for each value. Whether each value in the column will
    be missing is determined by the probability generated by the sigmoid function. The 
    beta value is multiplied by the generated probability as a way to tune how much 
    missingness is generated. The higher the beta value (between 0 and 1), the more
    missingness is generated. 
    """
    # check for beta
    if (b < 0) or (b > 1):
        raise Exception('beta value must be between 0 and 1')

    # helper sigmoid function
    def sig(x):
        return 1 / (1 + np.exp(-x))
    
    # check for categorical
    if (dataset.dtypes.loc[column] == object) or (dataset.dtypes.loc[column] == bool):
        # create probabilities based on normal distribution, passed through sigmoid
        cat_dict = {cat: sig(np.random.normal()) for cat in dataset[column].unique()}

        # generate missing values based on probabilities calculated
        for i, val in enumerate(dataset[column]):
            if np.random.choice([1, 0], p = [cat_dict[val] * b, 1 - (cat_dict[val] * b)]) == 1:
                dataset[column].iloc[i] = np.nan
    else:
        # Z-value
        def norm(val, mean, std):
            return (val - mean) / std

        # find mean and std for normalization
        mean = np.mean(dataset[column])
        std = np.std(dataset[column])

        # generate missingness using probabilities
        for i, val in enumerate(dataset[column]):
            prob = sig(norm(val, mean, std))
            if np.random.choice([1, 0], p = [prob * b, 1 - (prob * b)]) == 1:
                dataset[column].iloc[i] = np.nan
    
    return dataset


# ## Plotting

# In[ ]:


matrix = np.array([
    [1, 2, 3, 4],
    [2, 3, 4, 5],
    [2, 2, 4, 4],
    [1, 2, 3, 4]
])

fig, ax = plt.subplots()
im = ax.matshow(matrix)

for i in range((matrix.shape[0])):
    for j in range((matrix.shape[1])):
        text = ax.text(j, i, matrix[i, j],
                       ha="center", va="center", color="black", fontsize=15)

ax.set_xticklabels(['']+['a', 'b', 'c', 'd'])
ax.set_yticklabels(['']+['e', 'f', 'g', 'h'])

plt.show()


# In[ ]:


def plot_results(results_matrix : np.array):
    fig, ax = plt.subplots()
    im = ax.matshow(results_matrix)

    for i in range((results_matrix.shape[0])):
        for j in range((results_matrix.shape[1])):
            text = ax.text(j, i, results_matrix[i, j],
                        ha="center", va="center", color="black", fontsize=15)

    ax.set_xticklabels(['']+['insert', 'fairness', 'notions', 'here'])
    ax.set_yticklabels(['']+['No Missing', 'MCAR', 'MAR', 'NMAR'])

    plt.show()


# In[ ]:


plot_results(results_matrix=matrix)


# In[ ]:




