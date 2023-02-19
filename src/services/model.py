import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

IMG_SIZE = 50
LR = 1e-3

'''label'''
def label_img(img):
	word_label = img.split('.')[-3]

	if word_label == 'cat': return [1, 0]
	elif word_label == 'dog': return [0, 1]