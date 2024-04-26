# Özkan Gezmis 12327230

import numpy as np
from ai_assignments.datastructures.queue import Queue
from ai_assignments.decision_tree.dt_node import DecisionTreeNodeBase
from scipy.stats import entropy as sci_entropy


def entropy(y):
    '''Takes in list y and computes its entropy.'''
    positive = sum(y) / len(y)
    negative = 1 - positive
    return sci_entropy([positive, negative], base=2)


def unique_unsorted(L):
    '''Takes in list L and returns its unique values, keeping their order.'''
    _, indeces = np.unique(L, return_index=True)
    return [L[index] for index in sorted(indeces)]


class DecisionTreeNode(DecisionTreeNodeBase):
    def __init__(self, features, labels):
        super().__init__()
        self.features = features
        self.labels = labels

        if self.features is not None and self.labels is not None:
            self.split()

    def get_all_possible_split_points(self):
        nr_samples, nr_features = self.features.shape
        split_points = []
        for f_idx in range(nr_features):
            idx_sort = self.features[:, f_idx].argsort()
            self.features = self.features[idx_sort,
                            :]  # it makes a difference if features is overwritten or not (sorted differently)
            self.labels = self.labels[idx_sort]

            # TODO: check for consecutive samples whether the labels and features are different
            # be careful to not compare the 0th sample with the last sample when indexing
            # compute splitting values and add to list: split_points.append((f_idx, split_at))

            x_arr = self.features[:, f_idx]  # samples of the feature at index f_idx
            for i in range(nr_samples - 1):  # until the end of the sample
                if self.labels[i] != self.labels[i + 1]:  # if labels are same we shouldn't split
                    first_point = x_arr[i]  # for splitting  point we need two points
                    second_point = x_arr[i + 1]  # second point should be first different label point
                    split_at = (first_point + second_point) / 2  # split point is average of the points
                    split_points.append((f_idx, split_at))  # append the split with feature index and split point

        return split_points

    def get_optimal_split_point(self):
        split_feature, split_point = None, None

        # TODO: 
        # 1. get all possible split points (self.get_all_possible_split_points())
        # 2. loop over all possible split points that you computed and return the best one

        all_split_points = self.get_all_possible_split_points()
        info_gain_arr = []  # information gain list of all the split points
        for split in all_split_points:
            info_gain = self.compute_information_gain(self.features[:, split[0]],
                                                      split[1])  # split[0] is the feature column
            # index and split[1] is the split point for info gain function we should send feature not the index as input
            info_gain_arr.append((info_gain, split[0], split[1]))  # calculated info gain is added to the list,
            # split[0] is the feature index, split[1] is the splitting point value

        max_info_split = max(info_gain_arr, key=lambda item: item[0])  # returns the max info gain and its index
        opt_split_feature_index = max_info_split[1]  # it is the f_idx of the optimal split point

        split_feature = opt_split_feature_index  # feature index of optimum splitting point
        split_point = max_info_split[2]  # optimum splitting point value
        return split_feature, split_point

    def compute_information_gain(self, x, split_point):
        '''computes the information gain for a given feature x and the given split_point'''

        labels_left_branch = self.labels[x <= split_point]
        labels_right_branch = self.labels[x > split_point]

        weight_left = len(labels_left_branch) / len(x)
        weight_right = len(labels_right_branch) / len(x)

        e_data = entropy(self.labels)
        e_right = entropy(labels_right_branch)
        e_left = entropy(labels_left_branch)
        return e_data - (weight_left * e_left + weight_right * e_right)

    def split(self):
        # TODO: implement the ID3 algorithm based on the lecture slides "The ID3 Algorithm"
        # 1. If all examples X in the current node belong to the same class,
        #    make current node a leaf, label with class (use unique_unsorted)

        flag_val = self.labels[0]  # first label of the data set
        flag = False  # if flag remains false we don't need to split
        for value in self.labels:  # I didn't use the unique_unsorted since it didn't make a difference
            if value != flag_val:  # that means there are two different labels in the data set and we should split
                flag = True
                break
        # if flag is still false that means all nodes have same label
        if flag is False:
            self.label = flag_val  # this makes node to leaf node since all datas are labeled same
            return  # don't need to split

        # 2. use get_optimal_split_point() to determine best feature for splitting

        opt_split_point_tuple = self.get_optimal_split_point()  # returns the optimal split feature index and the point
        opt_split_point_feature_index = opt_split_point_tuple[0]  # first element is the feature index
        opt_split_point = opt_split_point_tuple[1]  # second element is the split point value
        opt_split_feature = self.features[:, opt_split_point_feature_index]  # this is feature column vector

        # 3. + 4. Create a branch + successor node N_i for each value of the selected feature
        #         containing a subset of X
        #         - X <= split_point goes into left_child
        #         - X > split_point goes into right_child

        labels_left_branch = self.labels[opt_split_feature <= opt_split_point]  # gets label's of the left branch
        labels_right_branch = self.labels[opt_split_feature > opt_split_point]  # gets label's of the left branch

        features_left_branch = self.features[opt_split_feature <= opt_split_point]  # split data to half. On the left
        # part elements of the feature vector are smaller than the split point value
        features_right_branch = self.features[opt_split_feature > opt_split_point]  # and on the right part elements are
        # bigger than the split point value, the other features aren't used but after split each sample still has all
        # the features

        # 5. For each subnode split is called recursively

        self.left_child = DecisionTreeNode(features_left_branch, labels_left_branch)  # recursive definition since after
        # creating new decision tree node it calls split function
        self.right_child = DecisionTreeNode(features_right_branch, labels_right_branch)  # until pure node which has
        # homogeneous labels, recursions continue. After this line statement we need to go back and the function doesn't
        # need to return something

        self.split_feature = opt_split_point_feature_index  # node's split feature is the x-feature_index for example x4
        self.split_point = opt_split_point  # and node's split point is the optimum splitting point

        return


class ID3():
    def __init__(self):
        self.root = None

    def fit(self, X, y):
        self.root = DecisionTreeNode(X, y)
        return self

    def __str__(self):
        return str(self.root)

    def get_height(self, node):
        if node is None:
            return 0
        return max(self.get_height(node.left_child), self.get_height(node.right_child)) + 1

    def print_decision_tree(self):
        height = self.get_height(self.root)
        visited = set()
        frontier = Queue()

        lines = ['']

        previous_level = 1
        frontier.put((self.root, 1))

        while frontier.has_elements():
            current, level = frontier.get()
            if level > previous_level:
                lines.append('')
                previous_level = level
            lines[-1] += current.print_node(height, level)
            if current not in visited:
                visited.add(current)
                if current.left_child is not None:
                    frontier.put((current.left_child, level + 1))
                else:
                    if level < height: frontier.put((DecisionTreeNode(None, None), level + 1))
                if current.right_child is not None:
                    frontier.put((current.right_child, level + 1))
                else:
                    if level < height: frontier.put((DecisionTreeNode(None, None), level + 1))

        for line in lines:
            print(line)
        return None
