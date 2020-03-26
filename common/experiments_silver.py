EXP_PARAMS = {
    'silver-sparse_v0': { 
        'env_name':         "sparse_v0",
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
