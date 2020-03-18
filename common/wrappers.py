import gym
from gym import spaces
import numpy as np
########################################################
# OBSERVATION WRAPPERS
########################################################
class add_enp_obs(gym.ObservationWrapper):
    def __init__(self, env=None):
        super(add_enp_obs, self).__init__(env)
        self.observation_space = spaces.Box(low=-1.0, 
                                            high=1.0, 
                                            shape=(self.env.observation_space.shape[0]+1,),
                                            dtype=np.float32)

    def observation(self, obs):
        enp = 0.5 - obs[3] #BMAX/2 - benergy_obs
        return np.append(obs,enp)
########################################################
class remove_time_obs(gym.ObservationWrapper):
    def __init__(self, env=None):
        super(remove_time_obs, self).__init__(env)
        self.observation_space = spaces.Box(low=-1.0, 
                                            high=1.0, 
                                            shape=(self.env.observation_space.shape[0]-1,),
                                            dtype=np.float32)

    def observation(self, obs):
        return obs[1:]
########################################################
class symmetric_normalize_obs(gym.ObservationWrapper):
    def __init__(self,env=None):
        super(symmetric_normalize_obs, self).__init__(env)
        self.observation_space = spaces.Box(low=-1.0, 
                                            high=1.0, 
                                            shape=self.env.observation_space.shape,
                                            dtype=np.float32)

    def observation(self, obs):
        return (obs-0.5)*2
# [0, 1]       >>  -0.5 >>  [-0.5, 0.5]
# [-0.5, 0.5]  >>  *2   >>  [-1,1]
########################################################
    
########################################################
# REWARD WRAPPERS
########################################################
# class high_negative_reward(gym.RewardWrapper):
#     def __init__(self, env=None):
#         super(high_negative_reward, self).__init__(env)
    
#     def reward(self,action): # reward based on utility
#         if self.RECOVERY_MODE:
#             return -240 # penalize recovery mode
#         else:
#             sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
#             del_qos = self.utility_obs - sense_dc
#             if del_qos <= 0:
#                 return 1
#             else:
#                 return 1-del_qos/0.9
########################################################
########################################################
class non_symmetric_reward(gym.RewardWrapper):
    def __init__(self, env=None):
        super(non_symmetric_reward, self).__init__(env)
    
    def reward(self,action):
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        if self.benergy_obs < 0.5:
            return 5*self.benergy_obs-1.5
        else:
            return -2*(self.benergy_obs-1)
########################################################
class sparse_reward(gym.RewardWrapper):
    def __init__(self, env=None):
        super(sparse_reward, self).__init__(env)
    def reward(self,action):
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        if self.time_obs == self.env_timeslot_values[-1]: # if end of day
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[1-len(self.env_timeslot_values)])
            lowthreshold = 3*self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1#1.5-5*np.abs(mean_day_batt-0.5)
        else:
            return 0
########################################################
########################################################
class sparse_reward_v2(gym.RewardWrapper):
    def __init__(self, env=None):
        super(sparse_reward_v2, self).__init__(env)
    def reward(self,action):
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        if self.time_obs == self.env_timeslot_values[-1]: # if end of day
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[1-len(self.env_timeslot_values)])
            lowthreshold = self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1#1.5-5*np.abs(mean_day_batt-0.5)
        else:
            return 0
########################################################
########################################################
class sparse_reward_v2a(gym.RewardWrapper):
    def __init__(self, env=None):
        super(sparse_reward_v2a, self).__init__(env)
    def reward(self,action):
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        if self.time_obs == self.env_timeslot_values[-1]: # if end of day
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[1-len(self.env_timeslot_values)])
            lowthreshold = self.MIN_BATT*2
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1#1.5-5*np.abs(mean_day_batt-0.5)
        else:
            return 0
########################################################
########################################################
class sparse_reward_v3(gym.RewardWrapper):
    def __init__(self, env=None):
        super(sparse_reward_v3, self).__init__(env)
    def reward(self,action):
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        if self.time_obs == self.env_timeslot_values[-1]: # if end of day
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[1-len(self.env_timeslot_values)])
            lowthreshold = self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return 1.5-5*np.abs(mean_day_batt-0.5)
        else:
            return 0
########################################################

########################################################
# ACTION WRAPPERS
########################################################
# For continuous actions that need to be converted from [-1,+1] >> [min_dc, 1]
class symmetric_normalize_action(gym.ActionWrapper):
    def __init__(self, env=None, min_dc=None):
        super(symmetric_normalize_action, self).__init__(env)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(self.env.action_space.shape[0],))
        self.min_dc = min_dc

    def action(self, action):
        return (action+1)*(1-self.min_dc)/2 + self.min_dc

# [-1 , +1]     >> +1              >> [0, + 2]
# [0, + 2]      >> *(1-min_dc)/2   >> [0, 1-min_dc]
# [0, 1-min_dc] >> + min_dc        >> [min_dc, 1]
########################################################