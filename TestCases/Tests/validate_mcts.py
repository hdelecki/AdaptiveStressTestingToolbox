from TestCases.AV.example_runner_mcts_av import runner as mcts_runner


def validate_mcts():
    # Overall settings
    max_path_length = 50
    s_0 = [0.0, -4.0, 1.0, 11.17, -35.0]
    base_log_dir = './data'
    # experiment settings
    run_experiment_args = {'snapshot_mode':'last',
                           'snapshot_gap':1,
                           'log_dir':None,
                           'exp_name':None,
                           'seed':0,
                           'n_parallel':1,
                           'tabular_log_file':'progress.csv'
                           }

    # runner settings
    runner_args = {'n_epochs':5,
                   'batch_size':500,
                   'plot':False
                   }

    # env settings
    env_args = {'id':'mylab:GoExploreAST-v1',
                'blackbox_sim_state':True,
                'open_loop':False,
                'fixed_init_state':True,
                's_0':s_0,
                }

    # simulation settings
    sim_args = {'blackbox_sim_state':True,
                'open_loop':False,
                'fixed_initial_state':True,
                'max_path_length':max_path_length
                }

    # reward settings
    reward_args = {'use_heuristic':True}

    # spaces settings
    spaces_args = {}

    # MCTS Settings

    mcts_policy_args = {}

    mcts_baseline_args = {}

    mcts_algo_args = {'max_path_length':max_path_length,
                      'stress_test_mode':2,
                      'ec':100.0,
                      'n_itr':1,
                      'k':0.5,
                      'alpha':0.5,
                      'clear_nodes':True,
                      'log_interval':500,
                      'plot_tree':False,
                      'plot_path':None,
                      'log_dir':None,
                      }

    mcts_bpq_args = {'N':10}

    exp_log_dir = base_log_dir
    max_path_length = 50
    s_0 = [0.0, -4.0, 1.0, 11.17, -35.0]
    env_args['s_0'] =s_0
    reward_args['use_heuristic'] = True
    sim_args['max_path_length'] = max_path_length

    # MCTS settings
    run_experiment_args['log_dir'] = exp_log_dir + '/mcts'
    run_experiment_args['exp_name'] = 'mcts'

    mcts_algo_args['max_path_length'] = max_path_length
    mcts_algo_args['log_dir'] = run_experiment_args['log_dir']
    mcts_algo_args['plot_path'] = run_experiment_args['log_dir']

    mcts_runner(
        env_args=env_args,
        run_experiment_args=run_experiment_args,
        sim_args=sim_args,
        reward_args=reward_args,
        spaces_args=spaces_args,
        policy_args=mcts_policy_args,
        baseline_args=mcts_baseline_args,
        algo_args=mcts_algo_args,
        bpq_args=mcts_bpq_args,
        runner_args=runner_args,
    )

    return True


if __name__ == '__main__':
    validate_mcts()
