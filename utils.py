import os
import logging
import json
import numpy as np
import torch

from sklearn.metrics.cluster import supervised
from scipy.optimize import linear_sum_assignment


def sort_dataset(data, labels, num_classes=10, stack=False):
    sorted_data = [[] for _ in range(num_classes)]
    for i, lbl in enumerate(labels):
        sorted_data[lbl].append(data[i])
    sorted_data = [np.stack(class_data) for class_data in sorted_data]
    sorted_labels = [np.repeat(i, (len(sorted_data[i]))) for i in range(num_classes)]
    if stack:
        sorted_data = np.vstack(sorted_data)
        sorted_labels = np.hstack(sorted_labels)
    return sorted_data, sorted_labels


def init_pipeline(model_dir):
    """Initialize folder and csv logger. """
    # project folder
    os.makedirs(model_dir)
    os.makedirs(os.path.join(model_dir, 'checkpoints'))
    os.makedirs(os.path.join(model_dir, 'figures'))
    print("project dir: {}".format(model_dir))

    # csv
    csv_path = os.path.join(model_dir, 'losses.csv')
    headers = ["epoch", "step", "loss", "discrimn_loss_e", "compress_loss_e", 
        "discrimn_loss_t",  "compress_loss_t"]
    with open(csv_path, 'a') as f:
        f.write(','.join(map(str, headers)))


def dataset_per_class(images, labels, num_classes):
    new_images = [[] for _ in range(num_classes)]
    for i, lbl in enumerate(labels):
        new_images[lbl].append(images[i])
    return np.array(new_images)


def save_params(model_dir, params):
    path = os.path.join(model_dir, 'params.json')
    with open(path, 'w') as f:
        json.dump(params, f, indent=2, sort_keys=True)


def load_params(model_dir):
    _path = os.path.join(model_dir, "params.json")
    with open(_path, 'r') as f:
        _dict = json.load(f)
    return _dict


def save_state(model_dir, *entries):
    csv_path = os.path.join(model_dir, 'losses.csv')
    assert os.path.exists(csv_path), 'CSV file is missing in project directory.'
    with open(csv_path, 'a') as f:
        f.write('\n'+','.join(map(str, entries)))


def save_ckpt(model_dir, net, epoch):
    torch.save(net.state_dict(), os.path.join(model_dir, 'checkpoints', 
        'model-epoch{}.pt'.format(epoch)))


def compute_accuracy(y_pred, y_true):
    assert y_pred.shape == y_true.shape
    return 1 - np.count_nonzero(y_pred - y_true) / y_true.size()[0]


def clustering_accuracy(labels_true, labels_pred):
    labels_true, labels_pred = supervised.check_clusterings(labels_true, labels_pred)
    # value = supervised.contingency_matrix(labels_true, labels_pred, sparse=False)
    value = supervised.contingency_matrix(labels_true, labels_pred)
    [r, c] = linear_sum_assignment(-value)
    return value[r, c].sum() / len(labels_true)