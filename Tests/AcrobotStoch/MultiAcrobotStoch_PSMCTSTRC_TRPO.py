import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"    #just use CPU

# from sandbox.rocky.tf.algos.trpo import TRPO
from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline
from sandbox.rocky.tf.envs.base import TfEnv
from sandbox.rocky.tf.policies.gaussian_mlp_policy import GaussianMLPPolicy
from sandbox.rocky.tf.policies.gaussian_lstm_policy import GaussianLSTMPolicy
from sandbox.rocky.tf.policies.deterministic_mlp_policy import DeterministicMLPPolicy
from sandbox.rocky.tf.optimizers.conjugate_gradient_optimizer import ConjugateGradientOptimizer, FiniteDifferenceHvp
from rllab.misc import logger

from Acrobot.acrobot import AcrobotEnv

from mylab.utils.tree_plot import plot_tree, plot_node_num
from mylab.algos.psmctstrc import PSMCTSTRC
from mylab.algos.trpo import TRPO

import os.path as osp
import argparse
# from example_save_trials import *
import tensorflow as tf
import joblib
import math
import numpy as np

import mcts.BoundedPriorityQueues as BPQ
import csv
# Log Params
from mylab.utils.psmcts_trpo_argparser import get_psmcts_trpo_parser
args = get_psmcts_trpo_parser(log_dir='./Data/AST/PSMCTSTRC_TRPO')

top_k = 10
max_path_length = 100
interactive = True

tf.set_random_seed(0)
sess = tf.Session()
sess.__enter__()

# Instantiate the env
env = TfEnv(AcrobotEnv(success_reward = max_path_length,
						success_threshhold = 1.9999,
						torque_noise_max = 0.1,
						initial_condition_max = 0.1))

# Create policy
policy = DeterministicMLPPolicy(
	name='ast_agent',
	env_spec=env.spec,
    hidden_sizes=(128, 64, 32),
    output_nonlinearity=tf.nn.tanh,
)

policy2 = GaussianMLPPolicy(
	name='ast_agent2',
	env_spec=env.spec,
    hidden_sizes=(128, 64, 32),
    output_nonlinearity=tf.nn.tanh,
    init_std = 0.05,
)

with open(osp.join(args.log_dir, 'total_result.csv'), mode='w') as csv_file:
	fieldnames = ['step_count']
	for i in range(top_k):
		fieldnames.append('reward '+str(i))
	writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
	writer.writeheader()

	for trial in range(args.n_trial):
		# Create the logger
		log_dir = args.log_dir+'/'+str(trial)

		tabular_log_file = osp.join(log_dir, 'process.csv')
		# text_log_file = osp.join(log_dir, 'text.txt')
		params_log_file = osp.join(log_dir, 'args.txt')

		logger.set_snapshot_dir(log_dir)
		logger.set_snapshot_mode(args.snapshot_mode)
		logger.set_snapshot_gap(args.snapshot_gap)
		logger.log_parameters_lite(params_log_file, args)
		if trial > 0:
			old_log_dir = args.log_dir+'/'+str(trial-1)
			logger.pop_prefix()
			# logger.remove_text_output(osp.join(old_log_dir, 'text.txt'))
			logger.remove_tabular_output(osp.join(old_log_dir, 'process2.csv'))
		# logger.add_text_output(text_log_file)
		logger.add_tabular_output(tabular_log_file)
		logger.push_prefix("["+args.exp_name+'_trial '+str(trial)+"_1]")

		np.random.seed(trial)

		params = policy.get_params()
		sess.run(tf.variables_initializer(params))

		# Instantiate the RLLAB objects
		baseline = LinearFeatureBaseline(env_spec=env.spec)
		top_paths = BPQ.BoundedPriorityQueue(top_k)
		algo = PSMCTSTRC(
			env=env,
			policy=policy,
			baseline=baseline,
			batch_size=args.batch_size,
			step_size=args.step_size,
			step_size_anneal=args.step_size_anneal,
			seed=trial,
			ec=args.ec,
			k=args.k,
			alpha=args.alpha,
			n_ca =args.n_ca,
			n_itr=args.n_itr,
			store_paths=False,
			max_path_length=max_path_length,
			top_paths = top_paths,
			fit_f=args.fit_f,
			log_interval=args.log_interval,
			plot=False,
			f_Q=args.f_Q,
			)


		algo.train(sess=sess, init_var=False)
		if args.plot_tree:
			plot_tree(algo.s,d=max_path_length,path=log_dir+"/tree",format="png")
		plot_node_num(algo.s,path=log_dir+"/nodeNum",format="png")

		best_s = algo.best_s
		algo.set_params(best_s)
		best_policy = algo.policy
		best_param_values = best_policy.prob_network.get_param_values(trainable=True)

		params = policy2.get_params()
		sess.run(tf.variables_initializer(params))
		policy2._mean_network.set_param_values(best_param_values,trainable=True)


		algo2 = TRPO(
			env=env,
			policy=policy2,
			baseline=baseline,
			batch_size=args.batch_size2,
			step_size=args.step_size2,
			n_itr=args.n_itr2,
			store_paths=False,
			# optimizer= optimizer,
			max_path_length=max_path_length,
			top_paths=top_paths,
			plot=False,
			)

		logger.pop_prefix()
		logger.remove_tabular_output(tabular_log_file)
		tabular_log_file = osp.join(log_dir, 'process2.csv')
		logger.add_tabular_output(tabular_log_file)
		logger.push_prefix("["+args.exp_name+'_trial '+str(trial)+"_2]")

		algo2.train(sess=sess, init_var=False)

		row_content = dict()
		row_content['step_count'] = algo.stepNum+args.batch_size2*args.n_itr2
		i = 0
		for (r,action_seq) in algo.top_paths:
			row_content['reward '+str(i)] = r
			i += 1
		writer.writerow(row_content)