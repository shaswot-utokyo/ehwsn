import math
import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np
import copy

########################################################
# Basic Linear
########################################################
class Linear_DQN(nn.Module):
    def __init__(self, input_shape, n_actions, layer_width):
        super(Linear_DQN, self).__init__()
        
        self.fc = nn.Sequential(
            nn.Linear(input_shape, layer_width),
#             nn.ReLU(),
            nn.Linear(layer_width, n_actions)
        )

    def forward(self, x):
        return self.fc(x.float())
# End of DQN()
########################################################

########################################################
# Basic DQN
########################################################
class DQN(nn.Module):
    def __init__(self, input_shape, n_actions, layer_width):
        super(DQN, self).__init__()
        
        self.fc = nn.Sequential(
            nn.Linear(input_shape, layer_width),
            nn.ReLU(),
            nn.Linear(layer_width, n_actions)
        )

    def forward(self, x):
        return self.fc(x.float())
# End of DQN()
########################################################

########################################################
# DuelingDQN
########################################################
class DuelingDQN(nn.Module):
    def __init__(self, input_shape, n_actions, layer_width):
        super(DuelingDQN, self).__init__()

        self.fc_adv = nn.Sequential(
            nn.Linear(input_shape, int(layer_width)),
            nn.ReLU(),
            nn.Linear(layer_width, n_actions)
        )
        self.fc_val = nn.Sequential(
            nn.Linear(input_shape, int(layer_width)),
            nn.ReLU(),
            nn.Linear(layer_width, 1)
        )

    def forward(self, x):
        val = self.fc_val(x.float())
        adv = self.fc_adv(x.float())
        return val + (adv - adv.mean(dim=1, keepdim=True))
# End of DuelingDQN()
########################################################

########################################################
# DQN Target Net
########################################################
class TargetNet:
    """
    Wrapper around model which provides copy of it instead of trained weights
    """
    def __init__(self, model):
        self.model = model
        self.target_model = copy.deepcopy(model)

    def sync(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def alpha_sync(self, alpha):
        """
        Blend params of target net with params from the model
        :param alpha:
        """
        assert isinstance(alpha, float)
        assert 0.0 < alpha <= 1.0
        state = self.model.state_dict()
        tgt_state = self.target_model.state_dict()
        for k, v in state.items():
            tgt_state[k] = tgt_state[k] * alpha + (1 - alpha) * v
        self.target_model.load_state_dict(tgt_state)

# End of TargetNet()
########################################################