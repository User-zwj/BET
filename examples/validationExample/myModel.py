# Copyright (C) 2016 The BET Development Team

# -*- coding: utf-8 -*-
import numpy as np

# Define a model that is a linear QoI map
def my_model(parameter_samples):
    Q_map = np.array([[0.506, 0.463], [0.253, 0.918]])
    QoI_samples = np.dot(parameter_samples,Q_map)
    return QoI_samples

