from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
from pathlib import Path
import gym
from gym import spaces

########################################################
# Read GSR values from CSV and convert to henergy
########################################################
def csv2gsr(location,year,SMAX):
    # Get data from CSV
    #####################
    # solar_data/CSV files contain the values of GSR (Global Solar Radiation in MegaJoules per meters squared per hour)
    # weather_data/CSV files contain the weather summary from 06:00 to 18:00 and 18:00 to 06:00+1

    sfile = Path.cwd() / 'solar_data' / location / (str(year) + '.csv')

    # skiprows=4 to remove unnecessary title texts
    # usecols=4 to read only the Global Solar Radiation (GSR) values
    solar_radiation = pd.read_csv(sfile, skiprows=4, encoding='shift_jisx0213', usecols=[4])

    # convert dataframe to numpy array
    solar_radiation = solar_radiation.values

    # convert missing data in CSV files to zero
    solar_radiation[np.isnan(solar_radiation)] = 0

    # reshape solar_radiation into no_of_daysxREADINGS_PER_DAY array
    solar_radiation = solar_radiation.reshape(1,-1).flatten() # 1-D array
    henergy = solar_radiation/SMAX # normalize
    return henergy
########################################################

    
########################################################
# Class for solar energy harvester
########################################################
class csv_solar_harvester(object):
    def __init__(self, 
                 location='tokyo',
                 year=1995,
                 READINGS_PER_DAY = 24,
                 SMAX=4.0, # Max GSR
                 HENERGY_NOISE=0.1, # henergy artifical noise
                 NORMALIZED_HMIN_THRES=1E-5, # henergy cutoff
                 REQ_TIMESLOTS_PER_DAY=240, # no. of timeslots per day
                 PREDICTION_HORIZON=240, # lookahead horizon to predict energy
                 PENERGY_NOISE=0.005): # preidction noise
        
      
        # Initialize variables
        self.day = 0
        self.global_time = 0
        self.henergy_stream = []
        self.penergy_stream = []
        
        henergy = csv2gsr(location,year,SMAX)
        henergy = henergy.reshape(-1, READINGS_PER_DAY)
        # Fix time resolution
        ######################
        self.no_of_days = int(henergy.shape[0]/READINGS_PER_DAY) # the number of days worth of data in the csv file

        # Interpolate the harvested energy data to new time resolution
        ###############################################################
        itp_henergy = interp1d(np.arange(READINGS_PER_DAY),
                               henergy, 
                               kind='quadratic') # quadratic interpolation
        
        new_time_slots =  np.linspace(0, READINGS_PER_DAY-1, REQ_TIMESLOTS_PER_DAY) # new time index
        high_res_henergy = itp_henergy(new_time_slots) # interpolate and fill in the intermediate values
        self.time_slots = new_time_slots # to access from object instance
    
        # Add noise to henergy data
        ###########################
        henergy_noise = np.random.normal(1,HENERGY_NOISE,size=high_res_henergy.shape) # add some noise to it
        high_res_henergy *= henergy_noise # we multiply so that zero energy times slots remain with zero energy
        high_res_henergy[high_res_henergy<NORMALIZED_HMIN_THRES]=0 # clipping threshold
        high_res_henergy[high_res_henergy>1]=1
        self.henergy_stream = high_res_henergy.reshape(1,-1).flatten().tolist() # flattened list of henergy

        # Get energy prediction
        #######################
        self.predictor = rolling_predictor(PREDICTION_HORIZON, PENERGY_NOISE)
        self.penergy_stream = self.predictor.get_prediction(self.henergy_stream)
        self.penergy_stream[self.penergy_stream<NORMALIZED_HMIN_THRES]=0 # clipping threshold
        self.penergy_stream = self.penergy_stream.tolist()
    
    # step through each time step and output time, henergy, penergy
    def step(self):
        if self.global_time < len(self.henergy_stream)-1:
            HARVESTER_END = False
            DAY_END = False
            self.global_time += 1 # new time
            time = self.time_slots[self.global_time%len(self.time_slots)]
            henergy = self.henergy_stream[self.global_time]
            penergy = self.penergy_stream[self.global_time]
            if self.global_time%len(self.time_slots)==len(self.time_slots)-1:
#                 print("END OF DAY:", self.day)
                self.day += 1
                DAY_END = True
            if self.global_time == len(self.henergy_stream)-1:
#                 print("END OF YEAR. DAY:",self.day)
                HARVESTER_END = True
            return time, henergy, penergy, DAY_END, HARVESTER_END
        else:
            print("YEAR ALREADY ENDED")
            DAY_END = True
            HARVESTER_END = True
            return -1,-1,-1,DAY_END, HARVESTER_END
# End of csv_solar_harvester
########################################################

########################################################
# random_day_env: harvester outputs energy for random days
########################################################
class csv_solar_harvester_random(csv_solar_harvester):
# random_day_env
# step through each time step and output time, henergy, penergy
    def step(self):
        HARVESTER_END = False
        DAY_END = False
        self.global_time += 1 # new time
        time_index = self.global_time%len(self.time_slots)
        time = self.time_slots[time_index]
        if time_index==0: # if beginning of time slot 
            self.day = np.random.choice(self.no_of_days, replace=False) # pick a random day
#             print("BEGINNING OF DAY:", self.day)
        day_start_index = self.day*len(self.time_slots)
        henergy = self.henergy_stream[day_start_index+time_index]
        penergy = self.penergy_stream[day_start_index+time_index]
        
        if time == self.time_slots[-1]: #if end of time slot,
            DAY_END = True
        
        if self.global_time == len(self.henergy_stream)-1: # All days have been experienced
            HARVESTER_END = True
#             print("END OF YEAR")

        return time, henergy, penergy, DAY_END, HARVESTER_END
# End of csv_solar_harvester_random
########################################################

########################################################
# Class for Energy Prediction
########################################################
class rolling_predictor(object):
        def __init__(self, PREDICTION_HORIZON, PENERGY_NOISE):
            self.PREDICTION_HORIZON = PREDICTION_HORIZON
            self.PENERGY_NOISE = PENERGY_NOISE
            
        def get_prediction(self, henergy_stream):
            PREDICTION_HORIZON = self.PREDICTION_HORIZON
            PENERGY_NOISE = self.PENERGY_NOISE
          # this uses a simple rolling average over a given prediction horizon
            weights = np.ones(PREDICTION_HORIZON) / PREDICTION_HORIZON
            penergy = np.convolve(henergy_stream, weights, mode='same')
            penergy_noise = np.random.normal(0,PENERGY_NOISE,size=penergy.shape) # add noise
            penergy += penergy_noise
            penergy /= penergy.max()
            penergy_stream = penergy.reshape(1,-1).flatten() # flattened list of penergy
            return penergy_stream
# End of rolling_predictor
########################################################

########################################################
# Class for utility generation
########################################################
class utility_generator(object): # generates utility of data, dependent on time
    def __init__(self):
        pass    
    def get_utility(self, time):
        utility = (np.cos(2*np.pi*time/DAY_LENGTH) + 1) * 0.4
#         utility +=  np.random.normal(0,0.1) # add noise
        return np.clip(utility,0,1 )
# End of utility_generator class
########################################################
class night_utility_generator(object): # generates utility of data, dependent on time
    def __init__(self):
        pass    
    def get_utility(self, time):
        assert 0<=time<24, 'Invalid time'
        if 0<=time<6 or 18<time<24:
            utility = 0.8
        else:
            utility = 0.2
        return np.clip(utility,0.1,1 )
# End of utility_generator class
########################################################

########################################################
# Class for channel fading
########################################################
class channel(object): # determines channel fading, dependent on time
    def __init__(self):
        pass    
    def get_channel_state(self, time):
        # very easy implementation of getting channel state
        channel_state = (-np.cos(2*np.pi*time/DAY_LENGTH) + 1) * 0.4
        channel_state +=  np.random.normal(0,0.1) # add noise
        return np.clip(channel_state,0,1 )
# End of channel class
########################################################

########################################################
# Class for battery
########################################################
class battery(object):
    def __init__(self, BINIT, BEFF):
        self.batt = BINIT # battery starts with 70% charge
        self.BEFF = BEFF
        
        assert 0 <= self.batt <= 1, 'Incorrect Battery Initialization'
        assert 0 < self.batt <= 1 , 'Incorrect Battery Efficiency'
    def charge(self, energy):
        assert energy >= 0, "Charging Energy should be >= 0"
        self.batt += energy*self.BEFF
        self.batt = np.clip(self.batt,0,1)
        
    def discharge(self, energy): #energy will be in negative
        assert energy < 0, "Discharging Energy should be < 0"
        self.batt += energy
        self.batt =  np.clip(self.batt,0,1)
        
    def get_batt_state(self):
        return np.clip(self.batt,0,1)
# End of class battery
########################################################





# Environments with UTILITY
########################################################
# utility_v0: environment template
########################################################
class utility_v0(gym.Env):
    """An ambient environment simulator for OpenAI gym."""
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(utility_v0, self).__init__()
        
        # Actions = 10 discrete duty cycles
        self.NO_OF_DUTY_CYCLES = 10
        self.action_space = spaces.Discrete(n=self.NO_OF_DUTY_CYCLES)

        # Observation = [time, h_energy, p_energy, b_energy, utility]
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=(5,))
        
        self.MIN_BATT = 0.1
        self.MIN_DC = 1/self.NO_OF_DUTY_CYCLES # Minimum duty cycle

        self.HFACTOR = 0.02 
        self.DFACTOR = 0.01 
        

    def reset(self, location, year, LOG_DATA=True):

        # Characterize the harvester
        self.READINGS_PER_DAY = 24
        REQ_TIMESLOTS_PER_DAY = 240
        PREDICTION_HORIZON=240
        

        self.env_harvester = csv_solar_harvester(location=location,
                                year=year,
                                READINGS_PER_DAY = self.READINGS_PER_DAY,
                                SMAX=4.0, # Max GSR
                                HENERGY_NOISE=0.1, # henergy artifical noise
                                NORMALIZED_HMIN_THRES=1E-5, # henergy cutoff
                                REQ_TIMESLOTS_PER_DAY=REQ_TIMESLOTS_PER_DAY, # no. of timeslots per day
                                PREDICTION_HORIZON=PREDICTION_HORIZON, # lookahead horizon to predict energy
                                PENERGY_NOISE=0.005)
        self.env_timeslot_values = self.env_harvester.time_slots
        self.ENV_LIFETIME = self.env_harvester.no_of_days
        
        # Characterize the battery
        self.BINIT = 0.7
        self.BEFF  = 1.0
        self.env_battery = battery(self.BINIT,self.BEFF)

        # Characterize utility generator
        self.utility_gen = night_utility_generator()
        # Characterize channel fading
        
        # Data logging variables
        self.LOG_DATA = LOG_DATA # Flag to whether or not log data
        self.env_log = [] # record all values in the environment
        self.action_log = [] # record all actions sent to the environment
        self.eno_log = []
        
        # Observation variables
        self.time_obs = None
        self.henergy_obs = None
        self.penergy_obs = None
        self.benergy_obs = None
        self.utility_obs = None
        
        # Environment Flags
        self.RECOVERY_MODE = False # battery is recovering to BINIT from complete discharge & node is suspended
        

        # Get observation
        self.time_obs, self.henergy_obs, self.penergy_obs, DAY_END, HARVESTER_END = self.env_harvester.step()
        self.benergy_obs = self.env_battery.get_batt_state()
        self.utility_obs = self.utility_gen.get_utility(self.time_obs)
        
        self.obs = (self.time_obs/self.READINGS_PER_DAY, 
                    self.henergy_obs, 
                    self.penergy_obs, 
                    self.benergy_obs,
                    self.utility_obs)
        if self.LOG_DATA:
            self.env_log.append(self.obs)
        return np.array(self.obs)
    
    def step(self, action):
        if self.benergy_obs < self.MIN_BATT: # Is battery less than a threshold?
            self.RECOVERY_MODE = True
        
        if self.RECOVERY_MODE: # Is node in recovery mode?
            self.recovery_action()
            reward = self.reward(action)
        else:
            ACTION_VALID = self.verify_action(action)
            if ACTION_VALID:
                self.execute_action(action)
                reward = self.reward(action)
            else:
                self.recovery_action()
                reward = self.reward(action)
        
        next_obs, done = self.next_obs()
        info = {}
        
        return np.array(next_obs), reward, done, info
    
    
    def verify_action(self, action): # check if actions are valid
        assert self.RECOVERY_MODE == False, "Action does not need to be verified in recovery mode"
        assert 0<=action<=self.NO_OF_DUTY_CYCLES, "Invalid Action"
        sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
        
        surplus_energy = (self.henergy_obs*self.HFACTOR - (sense_dc)*self.DFACTOR)
        if (-surplus_energy) < self.benergy_obs: # if there is sufficient energy in the battery to extract
            return True # valid action
        else:
            self.RECOVERY_MODE = True # switch to recovery mode
            return False # invalid action
        
            
    def recovery_action(self):
        assert self.RECOVERY_MODE == True, "Node is not in recovery mode"
        self.env_battery.charge(self.henergy_obs*self.HFACTOR)
        if self.LOG_DATA:
            self.eno_log.append(self.henergy_obs*self.HFACTOR)
            self.action_log.append((-1))
    
    def execute_action(self, action): 
        assert self.RECOVERY_MODE==False, "Node is in recovery mode. Cannot execute action"
        
        sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
        surplus_energy = (self.henergy_obs*self.HFACTOR - (sense_dc)*self.DFACTOR)
        
        if surplus_energy > 0:
            self.env_battery.charge(surplus_energy)
        else:
            self.env_battery.discharge(surplus_energy)
        
        if self.LOG_DATA:
            self.eno_log.append(surplus_energy)
            self.action_log.append((sense_dc))      
        

    def next_obs(self): # update all observations

        self.time_obs, self.henergy_obs, self.penergy_obs, DAY_END, HARVESTER_END = self.env_harvester.step()
        
        self.benergy_obs = self.env_battery.get_batt_state() # updated battery observation
        self.utility_obs = self.utility_gen.get_utility(self.time_obs) # new utility observation

        if not HARVESTER_END:
            if self.RECOVERY_MODE:
                if self.benergy_obs > self.BINIT: 
                    self.RECOVERY_MODE = False # snap out of recovery mode
                else:
                    self.RECOVERY_MODE = True # remain in recovery mode

        self.obs = (self.time_obs/self.READINGS_PER_DAY, 
                    self.henergy_obs, 
                    self.penergy_obs, 
                    self.benergy_obs,
                    self.utility_obs)
        
        if self.LOG_DATA:
            self.env_log.append(self.obs)
        
        done = HARVESTER_END

        return self.obs, done
    
    def reward(self,action): # reward based on utility
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
            del_qos = self.utility_obs - sense_dc
            if del_qos <= 0:
                return self.utility_obs
            else:
                return 1-del_qos/0.9
    # End of utility_v0
########################################################
########################################################
class utility_v1(utility_v0):
    def reward(self,action): # reward based on utility
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
            return np.clip(2*sense_dc/self.utility_obs, 0,1)
# End of utility_v1
########################################################



# Base Environments
########################################################
# eno_v0: environment template
########################################################
class eno_v0(gym.Env):
    """An ambient environment simulator for OpenAI gym."""
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(eno_v0, self).__init__()
        
        # Actions = 10 discrete duty cycles
        self.NO_OF_DUTY_CYCLES = 10
        self.action_space = spaces.Discrete(n=self.NO_OF_DUTY_CYCLES)

        # Observation = [time, h_energy, p_energy, b_energy]
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=(4,))
        
        self.MIN_BATT = 0.1
        self.MIN_DC = 1/self.NO_OF_DUTY_CYCLES # Minimum duty cycle

        
#         self.HFACTOR = 0.01 # Default
#         self.DFACTOR = 0.005 # Default
        self.HFACTOR = 0.02 
        self.DFACTOR = 0.01 
        

    def reset(self, location, year, LOG_DATA=True):

        # Characterize the harvester
        self.READINGS_PER_DAY = 24
        REQ_TIMESLOTS_PER_DAY = 240
        PREDICTION_HORIZON=240
        

        self.env_harvester = csv_solar_harvester(location=location,
                                year=year,
                                READINGS_PER_DAY = self.READINGS_PER_DAY,
                                SMAX=4.0, # Max GSR
                                HENERGY_NOISE=0.1, # henergy artifical noise
                                NORMALIZED_HMIN_THRES=1E-5, # henergy cutoff
                                REQ_TIMESLOTS_PER_DAY=REQ_TIMESLOTS_PER_DAY, # no. of timeslots per day
                                PREDICTION_HORIZON=PREDICTION_HORIZON, # lookahead horizon to predict energy
                                PENERGY_NOISE=0.005)
        self.env_timeslot_values = self.env_harvester.time_slots
        self.ENV_LIFETIME = self.env_harvester.no_of_days
        
        # Characterize the battery
        self.BINIT = 0.7
        self.BEFF  = 1.0
        self.env_battery = battery(self.BINIT,self.BEFF)

        # Characterize utility generator
        
        # Characterize channel fading
        
        # Data logging variables
        self.LOG_DATA = LOG_DATA # Flag to whether or not log data
        self.env_log = [] # record all values in the environment
        self.action_log = [] # record all actions sent to the environment
        self.eno_log = []
        
        # Observation variables
        self.time_obs = None
        self.henergy_obs = None
        self.penergy_obs = None
        self.benergy_obs = None
        
        # Environment Flags
        self.RECOVERY_MODE = False # battery is recovering to BINIT from complete discharge & node is suspended
        

        # Get observation
        self.time_obs, self.henergy_obs, self.penergy_obs, DAY_END, HARVESTER_END = self.env_harvester.step()
        self.benergy_obs = self.env_battery.get_batt_state()
        
        self.obs = (self.time_obs/self.READINGS_PER_DAY, 
                    self.henergy_obs, 
                    self.penergy_obs, 
                    self.benergy_obs)
        if self.LOG_DATA:
            self.env_log.append(self.obs)
        return np.array(self.obs)
    
    def step(self, action):
        if self.benergy_obs < self.MIN_BATT: # Is battery less than a threshold?
            self.RECOVERY_MODE = True
        
        if self.RECOVERY_MODE: # Is node in recovery mode?
            self.recovery_action()
            reward = self.reward(action)
        else:
            ACTION_VALID = self.verify_action(action)
            if ACTION_VALID:
                self.execute_action(action)
                reward = self.reward(action)
            else:
                self.recovery_action()
                reward = self.reward(action)
        
        next_obs, done = self.next_obs()
        info = {}
        
        return np.array(next_obs), reward, done, info
    
    
    def verify_action(self, action): # check if actions are valid
        assert self.RECOVERY_MODE == False, "Action does not need to be verified in recovery mode"
        assert 0<=action<self.NO_OF_DUTY_CYCLES, "Invalid Action"
        sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
        
        surplus_energy = (self.henergy_obs*self.HFACTOR - (sense_dc)*self.DFACTOR)
        if (-surplus_energy) < self.benergy_obs: # if there is sufficient energy in the battery to extract
            return True # valid action
        else:
            self.RECOVERY_MODE = True # switch to recovery mode
            return False # invalid action
        
            
    def recovery_action(self):
        assert self.RECOVERY_MODE == True, "Node is not in recovery mode"
        self.env_battery.charge(self.henergy_obs*self.HFACTOR)
        if self.LOG_DATA:
            self.eno_log.append(self.henergy_obs*self.HFACTOR)
            self.action_log.append((-1))
    
    def execute_action(self, action): 
        assert self.RECOVERY_MODE==False, "Node is in recovery mode. Cannot execute action"
        
        sense_dc = action/self.NO_OF_DUTY_CYCLES + self.MIN_DC
        surplus_energy = (self.henergy_obs*self.HFACTOR - (sense_dc)*self.DFACTOR)
        
        if surplus_energy > 0:
            self.env_battery.charge(surplus_energy)
        else:
            self.env_battery.discharge(surplus_energy)
        
        if self.LOG_DATA:
            self.eno_log.append(surplus_energy)
            self.action_log.append((sense_dc))      
        

    def next_obs(self): # update all observations

        self.time_obs, self.henergy_obs, self.penergy_obs, DAY_END, HARVESTER_END = self.env_harvester.step()

        if not HARVESTER_END:
            self.benergy_obs = self.env_battery.get_batt_state() # updated battery observation
            if self.RECOVERY_MODE:
                if self.benergy_obs > self.BINIT: 
                    self.RECOVERY_MODE = False # snap out of recovery mode
                else:
                    self.RECOVERY_MODE = True # remain in recovery mode

        self.obs = (self.time_obs/self.READINGS_PER_DAY, 
                    self.henergy_obs, 
                    self.penergy_obs, 
                    self.benergy_obs)
        
        if self.LOG_DATA:
            self.env_log.append(self.obs)
        
        done = HARVESTER_END

        return self.obs, done
    
    def reward(self,action): # symmetric linear reward
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            return (0.5 - np.abs(self.benergy_obs - 0.5))*4 - 1
    # End of eno_v0
########################################################
class eno_v0_g99(eno_v0): # for gamma=0.99
    def reward(self,action): # symmetric linear reward
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            return ((0.5 - np.abs(self.benergy_obs - 0.5))*4 - 1)*0.1
# End of eno_v0_g99
########################################################
########################################################
class eno_v0_g999(eno_v0): # for gamma=0.99
    def reward(self,action): # symmetric linear reward
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            return ((0.5 - np.abs(self.benergy_obs - 0.5))*4 - 1)*0.01
# End of eno_v0_g999
########################################################
########################################################
class eno_v0_g999a(eno_v0): # for gamma=0.99
    def reward(self,action): # symmetric linear reward
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        else:
            return ((0.5 - np.abs(self.benergy_obs - 0.5))*4 - 1)*0.1
# End of eno_v0_g999a
########################################################
########################################################
class sparse_v0a(eno_v0):
    def reward(self,action): # sparse rewards at particular time intervals
        end_time = self.env_timeslot_values[-1]
        half_time = self.env_timeslot_values[int(2*len(self.env_timeslot_values)/4)]
        q1_time = self.env_timeslot_values[int(len(self.env_timeslot_values)/4)]
        q3_time = self.env_timeslot_values[int(3*len(self.env_timeslot_values)/4)]
        interval_set = set((end_time))
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        
        if self.time_obs in interval_set:
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[-len(self.env_timeslot_values):-1])
            lowthreshold = 2*self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1
        else:
            return 0
# End of sparse_v0a
########################################################
########################################################
class sparse_v0b(eno_v0):
    def reward(self,action): # sparse rewards at particular time intervals
        end_time = self.env_timeslot_values[-1]
        half_time = self.env_timeslot_values[int(2*len(self.env_timeslot_values)/4)]
        q1_time = self.env_timeslot_values[int(len(self.env_timeslot_values)/4)]
        q3_time = self.env_timeslot_values[int(3*len(self.env_timeslot_values)/4)]
        interval_set = set((half_time, end_time))
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        
        if self.time_obs in interval_set:
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[-len(self.env_timeslot_values):-1])
            lowthreshold = 2*self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1
        else:
            return 0
# End of sparse_v0b
########################################################
########################################################
class sparse_v0c(eno_v0):
    def reward(self,action): # sparse rewards at particular time intervals
        end_time = self.env_timeslot_values[-1]
        half_time = self.env_timeslot_values[int(2*len(self.env_timeslot_values)/4)]
        q1_time = self.env_timeslot_values[int(len(self.env_timeslot_values)/4)]
        q3_time = self.env_timeslot_values[int(3*len(self.env_timeslot_values)/4)]
        interval_set = set((q1_time, half_time, q3_time, end_time))
        if self.RECOVERY_MODE:
            return -1 # penalize recovery mode
        
        if self.time_obs in interval_set:
            batt_log = [obs[3] for obs in self.env_log]
            mean_day_batt = np.mean(batt_log[-len(self.env_timeslot_values):-1])
            lowthreshold = 2*self.MIN_BATT
            if lowthreshold<mean_day_batt<(1-lowthreshold):
                return 1
            else:
                return -1
        else:
            return 0
# End of sparse_v0c
########################################################
class eno_v0a(eno_v0):
    """An ambient environment simulator for OpenAI gym."""
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(eno_v0a, self).__init__()
        
        # Actions = 10 discrete duty cycles
        self.NO_OF_DUTY_CYCLES = 10
        self.action_space = spaces.Discrete(n=self.NO_OF_DUTY_CYCLES)

        # Observation = [time, h_energy, p_energy, b_energy]
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=(4,))
        
        self.MIN_BATT = 0.1
        self.MIN_DC = 1/self.NO_OF_DUTY_CYCLES # Minimum duty cycle

        
#         self.HFACTOR = 0.01 # Default
#         self.DFACTOR = 0.005 # Default
        self.HFACTOR = 0.02 
        self.DFACTOR = 0.005
# End of eno_v0a
########################################################
########################################################
class eno_v0b(eno_v0):
    """An ambient environment simulator for OpenAI gym."""
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(eno_v0b, self).__init__()
        
        # Actions = 10 discrete duty cycles
        self.NO_OF_DUTY_CYCLES = 10
        self.action_space = spaces.Discrete(n=self.NO_OF_DUTY_CYCLES)

        # Observation = [time, h_energy, p_energy, b_energy]
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=(4,))
        
        self.MIN_BATT = 0.1
        self.MIN_DC = 1/self.NO_OF_DUTY_CYCLES # Minimum duty cycle

        
#         self.HFACTOR = 0.01 # Default
#         self.DFACTOR = 0.005 # Default
        self.HFACTOR = 0.01 
        self.DFACTOR = 0.005
# End of eno_v0b
########################################################
########################################################
class eno_v0c(eno_v0):
    """An ambient environment simulator for OpenAI gym."""
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(eno_v0c, self).__init__()
        
        # Actions = 10 discrete duty cycles
        self.NO_OF_DUTY_CYCLES = 5 #<<<<<
        self.action_space = spaces.Discrete(n=self.NO_OF_DUTY_CYCLES)

        # Observation = [time, h_energy, p_energy, b_energy]
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=(4,))
        
        self.MIN_BATT = 0.1
        self.MIN_DC = 1/self.NO_OF_DUTY_CYCLES # Minimum duty cycle

        
#         self.HFACTOR = 0.01 # Default
#         self.DFACTOR = 0.005 # Default
        self.HFACTOR = 0.01 
        self.DFACTOR = 0.005
# End of eno_v0b
########################################################