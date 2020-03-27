import sys
import time
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import collections
########################################################
# Replay Buffer
Experience = collections.namedtuple('Experience', field_names=['state', 'action', 'reward', 'done', 'new_state'])
nstepExperience = collections.namedtuple('nstepExperience', field_names=['state', 'action', 'nstep_return', 'done', 'last_state'])

class nstep_ExperienceBuffer:
    def __init__(self, capacity, nsteps, gamma):
        self.nsteps = nsteps
        self.gamma = gamma
        self.buffer = collections.deque(maxlen=nsteps+1) #n-step small buffer contains n+1 elements
        self.nstep_buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.nstep_buffer)

    def append(self, experience):
        self.buffer.append(experience)
        if len(self.buffer)==self.buffer.maxlen:
            self.nstep_populate()
    
    def nstep_populate(self):
        if self.buffer[-1].done or self.buffer[-1].reward<0:
            # calculate all returns then clear buffer
            done = True
            last_state = self.buffer[-1].state # DUMMY. NOT REALLY USED
            nstep_return = 0.0
            for _ in range(self.nsteps):
                for exp in reversed(self.buffer):
                    nstep_return *= self.gamma
                    nstep_return += exp.reward
                self.nstep_buffer.append(nstepExperience(self.buffer[0].state,
                                                         self.buffer[0].action, 
                                                         nstep_return,
                                                         done,
                                                         last_state))
                self.buffer.popleft()
        else:
            done = False
            last_state = self.buffer[-1].state
            nstep_return = 0.0
            elems = list(self.buffer)[:-1]
            for exp in reversed(elems):
                nstep_return *= self.gamma
                nstep_return += exp.reward
            self.nstep_buffer.append(nstepExperience(self.buffer[0].state,
                                                     self.buffer[0].action, 
                                                     nstep_return,
                                                     done,
                                                     last_state))

    def sample(self, batch_size):
        indices = np.random.choice(len(self.nstep_buffer), batch_size, replace=False)
        states, actions, nstep_returns, dones, next_states = zip(*[self.nstep_buffer[idx] for idx in indices])
        return np.array(states),np.array(actions), np.array(nstep_returns, dtype=np.float32), np.array(dones, dtype=np.uint8), np.array(next_states)

########################################################
def calc_loss(batch, net, tgt_net, gamma, device="cpu", double=False):
    states, actions, rewards, dones, next_states = batch    
    
    states_v = torch.tensor(states).to(device)
    next_states_v = torch.tensor(next_states).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.tensor(dones,dtype=torch.bool).to(device)

    state_action_values = net(states_v).gather(dim=1, 
                                               index=actions_v.unsqueeze(-1)).squeeze(-1)
    """
    net(states_v) = [
                     [
                        [q_s1a1, q_s1a2, q_s1a3],
                        [q_s2a1, q_s2a2, q_s2a3],
                        [q_s3a1, q_s3a2, q_s3a3]
                     ]
                    ] # SIZE = 1*batch_size*no_of_actions
                    
                    gives q-values for ALL actions for all states in the batch
    The output is a matrix where each row corresponds to Q-values for each state in the batch
    
    actions_v = [ax, ay, az] contains the actions actually chosen by the agent has size [batch_size].
    
    we need to add an extra dimension to use gather with the output of net(states_v) 
    and then remove it later.
    
    unsqueeze() inserts singleton dim at position given as parameter
    unsqueeze(-1) inserts a dimension at the end.
    if x = M*N tensor, x.unsqueeze(-1) is M*N*1 tensor
    
    
    gather function takes the q-values for the actions specified by actions_v vector
    from the above mentioned matrix.

    
    """
    if double: # double-DQN
        next_state_actions = net(next_states_v).max(dim=1)[1] # get greedy actions from policy net
        next_state_values = tgt_net(next_states_v).gather(1, next_state_actions.unsqueeze(-1)).squeeze(-1)
    else:
        next_state_values = tgt_net(next_states_v).max(dim=1)[0]
    next_state_values[done_mask] = 0.0

    expected_state_action_values = next_state_values.detach() * gamma + rewards_v
    return nn.MSELoss()(state_action_values, expected_state_action_values)
########################################################

########################################################
def calc_values_of_states(states, net, device="cpu"):
    mean_vals = []
    # np.array_split splits the array into sub-arrays 
    # (in this case, each sub-array has a max size of 64)
    # For an array of length l that should be split into n sections, 
    # it returns l % n sub-arrays of size l//n + 1 and the rest of size l//n.
    for batch in np.array_split(states, 64): 
        states_v = torch.tensor(batch).to(device)
        action_values_v = net(states_v) #get q_values of all actions for all the 64 states
        best_action_values_v = action_values_v.max(1)[0] # get maximum q_values for each of the 64 states
        mean_vals.append(best_action_values_v.mean().item()) # take mean of the 64 max q_values
    return np.mean(mean_vals)
########################################################

########################################################
def display_env_log_eno(env, reward_rec, RECOVERY_rec, START_DAY=0, NO_OF_DAY_TO_PLOT = 500):
    # Get Environment Log
    ################################################################
    NO_OF_TIMESLOTS_PER_DAY = len(env.env_timeslot_values)
    END_DAY = START_DAY + NO_OF_DAY_TO_PLOT

    start_index = START_DAY*NO_OF_TIMESLOTS_PER_DAY
    end_index = END_DAY*NO_OF_TIMESLOTS_PER_DAY
    
    reward_rec = np.clip(reward_rec,-0.15,1)
    env_rec = np.array(env.env_log)
    action_rec = np.array(env.action_log)
    eno_perf = np.array(env.eno_log).cumsum()

    time_obs_rec=env_rec[:,0]
    henergy_obs_rec=env_rec[:,1]
    penergy_obs_rec=env_rec[:,2]
    benergy_obs_rec=env_rec[:,3]
#     utility_obs_rec=env_rec[:,4]

    sense_dc_rec = action_rec[:]
    # Draw figure
    ##############
    SUBPLOTS=4
    subplot_height  = np.ceil(12/SUBPLOTS)*SUBPLOTS
    fig = plt.figure(figsize=[20,subplot_height])

    henergy_ax   = fig.add_subplot(SUBPLOTS,1,1)
    sense_dc_ax  = fig.add_subplot(SUBPLOTS,1,2)
    benergy_ax   = fig.add_subplot(SUBPLOTS,1,3)
    eno_perf_ax  = fig.add_subplot(SUBPLOTS,1,4)
    
    henergy_ax.grid(which='major', axis='x', linestyle='--')
    sense_dc_ax.grid(which='major', axis='x', linestyle='--')
    benergy_ax.grid(which='major', axis='x', linestyle='--')
    eno_perf_ax.grid(which='major', axis='x', linestyle='--')

#     time_ax.set_ylim(0, env.READINGS_PER_DAY)
#     henergy_ax.set_ylim(0,1)
#     penergy_ax.set_ylim(0,1)
    benergy_ax.set_ylim(0,1)
    sense_dc_ax.set_ylim(-0.1,1)
#     reward_ax.set_ylim(-1,1)
#     recovery_ax.set_ylim(0,1)
#     utility_ax.set_ylim(0,1)


#     time_ax.plot(time_obs_rec[start_index:end_index])
    henergy_ax.plot(henergy_obs_rec[start_index:end_index],color='k',linewidth=1.0,alpha=0.5)
    henergy_ax.plot(penergy_obs_rec[start_index:end_index],linewidth=0.25)
    
    sense_dc_ax.plot(sense_dc_rec[start_index:end_index], alpha=0.7)
#     sense_dc_ax.plot(utility_obs_rec[start_index:end_index], color='y',linestyle='--')
    
    benergy_ax.plot(benergy_obs_rec[start_index:end_index], color='r')
    benergy_ax.plot(reward_rec[start_index:end_index],color='m', alpha=0.5)

    eno_perf_ax.plot(eno_perf[start_index:end_index], color ='g')
    eno_perf_ax.plot(RECOVERY_rec[start_index:end_index],linestyle=':')
    plt.show()
########################################################
########################################################

########################################################
def display_env_log_utility(env, reward_rec, RECOVERY_rec, START_DAY=0, NO_OF_DAY_TO_PLOT = 500):
   # Get Environment Log
    ################################################################
    NO_OF_TIMESLOTS_PER_DAY = len(env.env_timeslot_values)
    END_DAY = START_DAY + NO_OF_DAY_TO_PLOT

    start_index = START_DAY*NO_OF_TIMESLOTS_PER_DAY
    end_index = END_DAY*NO_OF_TIMESLOTS_PER_DAY
    
    reward_rec = np.clip(reward_rec,-0.15,1)
    env_rec = np.array(env.env_log)
    action_rec = np.array(env.action_log)
    eno_perf = np.array(env.eno_log).cumsum()

    time_obs_rec=env_rec[:,0]
    henergy_obs_rec=env_rec[:,1]
    penergy_obs_rec=env_rec[:,2]
    benergy_obs_rec=env_rec[:,3]
    utility_obs_rec=env_rec[:,4]

    sense_dc_rec = action_rec[:]
    # Draw figure
    ##############
    SUBPLOTS=4
    subplot_height  = np.ceil(12/SUBPLOTS)*SUBPLOTS
    fig = plt.figure(figsize=[20,subplot_height])

    henergy_ax   = fig.add_subplot(SUBPLOTS,1,1)
    sense_dc_ax  = fig.add_subplot(SUBPLOTS,1,2)
    benergy_ax   = fig.add_subplot(SUBPLOTS,1,3)
    eno_perf_ax  = fig.add_subplot(SUBPLOTS,1,4)
    
    henergy_ax.grid(which='major', axis='x', linestyle='--')
    sense_dc_ax.grid(which='major', axis='x', linestyle='--')
    benergy_ax.grid(which='major', axis='x', linestyle='--')
    eno_perf_ax.grid(which='major', axis='x', linestyle='--')
    
#     time_ax.set_ylim(0, env.READINGS_PER_DAY)
#     henergy_ax.set_ylim(0,1)
#     penergy_ax.set_ylim(0,1)
    benergy_ax.set_ylim(0,1)
    sense_dc_ax.set_ylim(-0.1,1)
#     reward_ax.set_ylim(-1,1)
#     recovery_ax.set_ylim(0,1)
#     utility_ax.set_ylim(0,1)


#     time_ax.plot(time_obs_rec[start_index:end_index])
    henergy_ax.plot(henergy_obs_rec[start_index:end_index],color='k',linewidth=1.0,alpha=0.5)
    henergy_ax.plot(penergy_obs_rec[start_index:end_index],linewidth=0.25)
    
    sense_dc_ax.plot(sense_dc_rec[start_index:end_index], alpha=0.7)
    sense_dc_ax.plot(utility_obs_rec[start_index:end_index], color='y',linestyle='--')
    
    benergy_ax.plot(benergy_obs_rec[start_index:end_index], color='r')
    benergy_ax.plot(reward_rec[start_index:end_index],color='m', alpha=0.5)

    eno_perf_ax.plot(eno_perf[start_index:end_index], color ='g')
    eno_perf_ax.plot(RECOVERY_rec[start_index:end_index],linestyle=':')
    plt.show()
########################################################