EXP_PARAMS = {
    'koi-eno_v0_T48-base': { 
        'env_name':         "eno_v0_T48",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      48*365*2,#240*365*2/5, #<<<
        'replay_initial':   48*10,#240*10/5,#<<<
        'target_net_sync':  48*10,#240*10/5, #<<<
        'epsilon_frames':   48*30*6,#240*30*6/5,#<<<
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       32
    },
    'koi-eno_v0_T120-base': { 
        'env_name':         "eno_v0_T120",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      120*365*2,#240*365*2/2, #<<<
        'replay_initial':   120*10,#240*10/2,#<<<
        'target_net_sync':  120*10,#240*10/2, #<<<
        'epsilon_frames':   120*30*6,#240*30*6/2,#<<<
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       32
    },
    'koi-eno_v0_T24-base': { 
        'env_name':         "eno_v0_T24",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      24*365*2,#240*365*2/10, #<<<
        'replay_initial':   24*10,#240*10/10,#<<<
        'target_net_sync':  24*10,#240*10/10, #<<<
        'epsilon_frames':   24*30*6,#240*30*6/10,#<<<
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       32
    },
    'koi-eno-5step-g95': { 
        'env_name':         "eno_v0",
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
        'gamma':            0.95, #<<<<
        'batch_size':       32
    },
    'koi-eno-5step-g99': { 
        'env_name':         "eno_v0",
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
        'gamma':            0.99, #<<<<
        'batch_size':       32
    },
    'koi-eno-g999a': { 
        'env_name':         "eno_v0_g999a",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      240*365*2, 
        'replay_initial':   240*10,
        'target_net_sync':  240*10, 
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.999, 
        'batch_size':       32
    },
    'koi-eno-g999': { 
        'env_name':         "eno_v0_g999",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      240*365*2, 
        'replay_initial':   240*10,
        'target_net_sync':  240*10, 
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.99, 
        'batch_size':       32
    },
    'koi-eno-g99': { 
        'env_name':         "eno_v0_g99",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      240*365*2, 
        'replay_initial':   240*10,
        'target_net_sync':  240*10, 
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.99, 
        'batch_size':       32
    },
    'koi-eno-enp': { # add enp observation
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
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
    'koi-eno-notime': { # remove time observation
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
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
    'koi-eno-50step': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    50,#<<<<<
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
    'koi-eno-10step': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    10,#<<<<<
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
    'koi-eno-5step': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    5,#<<<<<
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
    'koi-eno-3step': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    3,#<<<<<
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
    'koi-eno-nn128-b128': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   128,#<<<<
        'rollout_steps':    1,
        'replay_size':      240*365*2, 
        'replay_initial':   240*10,
        'target_net_sync':  240*10, 
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       128
    },
    'koi-eno-b128': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
        'replay_size':      240*365*2, 
        'replay_initial':   240*10,
        'target_net_sync':  240*10, 
        'epsilon_frames':   240*30*6,
        'epsilon_start':    1.0,
        'epsilon_final':    0.01,
        'learning_rate':    1E-3,
        'gamma':            0.9, 
        'batch_size':       128#<<<<<
    },
    'koi-eno-nn128': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   128,#<<<<
        'rollout_steps':    1,
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
    'koi-eno-base': { 
        'env_name':         "eno_v0",
        'double_q':         True,
        'dueling':          True,
        'nn_layer_width':   32,
        'rollout_steps':    1,
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
}
