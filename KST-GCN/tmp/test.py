import tensorflow as tf
import numpy as np

inputs = tf.placeholder(tf.float32, shape=[None, 2, 3])
my_tensor = tf.reduce_sum(inputs, axis=-1)  # 假设 `my_tensor` 是由 `inputs` 计算得到的
print(inputs, my_tensor)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    # 提供输入数据
    input_data = np.random.randn(5, 2, 3)  # 示例输入数据
    tensor_value = sess.run(my_tensor, feed_dict={inputs: input_data})
    print(tensor_value)
