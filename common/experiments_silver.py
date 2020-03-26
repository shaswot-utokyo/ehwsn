EXP_PARAMS = {
    'silver-utility_v0_T120-enp-g9': { # Derived from #45
        'env_name':         "utility_v0_T120",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    50,
        'replay_size':      5*120*365*2,
        'replay_initial':   120*10,
        'target_net_sync':  120*10,
        'epsilon_frames':   5*120*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       32
    },
    'silver-utility_v0_T24-enp-g9': { # Derived from #37 
        'env_name':         "utility_v0_T24", #<<<<<<
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    5,
        'replay_size':      5*24*365*2,
        'replay_initial':   24*10,
        'target_net_sync':  24*10,
        'epsilon_frames':   5*24*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, #<<
        'batch_size':       32
    },
    'silver-utility_v0_T240-enp': { # Derived from exp #6
        'env_name':         "utility_v0_T240",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    5,
        'replay_size':      240*365*2,
        'replay_initial':   240*10,
        'target_net_sync':  240*10,
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       32
    },
    'silver-utility_v0_T120-enp': { # Derived from #45
        'env_name':         "utility_v0_T120",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    50,
        'replay_size':      5*120*365*2,
        'replay_initial':   120*10,
        'target_net_sync':  120*10,
        'epsilon_frames':   5*120*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.996, 
        'batch_size':       32
    },
    'silver-utility_v0_T24-enp': { # Derived from #37 
        'env_name':         "utility_v0_T24", #<<<<<<
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    5,
        'replay_size':      5*24*365*2,
        'replay_initial':   24*10,
        'target_net_sync':  24*10,
        'epsilon_frames':   5*24*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.98,#<<<<<<<<<<<< 
        'batch_size':       32
    },
}
