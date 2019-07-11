# vgr2dof
## 2 joints vision guided robot 
This robot is a planar mimic of human arm and consists of two mini servos acting as shoulder and elbow joints. It's goal is to put effector called 'blob' over an orange moving ball. Ball and arm links positions are acquired from camera picture with OpenCV, and upone those new servos angles are set. Those angles are the output of NN build with Keras.
