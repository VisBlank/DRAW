# coding: utf-8
import tensorflow as tf
import numpy as np
import os
import draw
import cmtf.data.data_mnist as mnist


save_path = 'output/checkpoint.ckpt'


# 检测目录是否存在
save_dir = os.path.dirname(save_path)
if not os.path.exists(save_dir):
	os.makedirs(save_dir)


# 生成图
hp = draw.default_hp()
graph = tf.Graph()
model = draw.DRAW(graph, hp)


# 训练
with graph.as_default():
	# 优化方法
	optimizer = tf.train.AdamOptimizer(hp.learning_rate, beta1=0.5)
	grads = optimizer.compute_gradients(model.loss)
	for i,(g,v) in enumerate(grads):
		if g is not None:
			grads[i]=(tf.clip_by_norm(g,5),v) # clip gradients
	train_op = optimizer.apply_gradients(grads)

	# GPU
	config = tf.ConfigProto()
	config.gpu_options.per_process_gpu_memory_fraction = 0.8
	config.gpu_options.allow_growth = True

	# sess、saver
	sess=tf.InteractiveSession(config=config)
	saver = tf.train.Saver()
	tf.initialize_all_variables().run()

	# restore
	if os.path.exists(save_path):
		saver.restore(sess, save_path)

	data = mnist.read_data_sets()

	# train
	Lx_arr, Lz_arr = [], []
	for i in range(hp.epochs):
		x_, _ = data.train.next_batch(hp.batch_size)
		Lx_, Lz_, _ = sess.run([model.Lx, model.Lz, train_op], {model.x: x_})
		Lx_arr.append(Lx_)
		Lz_arr.append(Lz_)
		if i%100==0:
			print "iter=%d : Lx: %f Lz: %f" % (i, np.mean(np.array(Lx_arr)), np.mean(np.array(Lz_arr)))
			saver.save(sess, save_path)

	sess.close()
