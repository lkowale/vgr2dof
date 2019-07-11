# vgr2dof
## 2 joints vision guided robot 
This robot is a planar mimic of human arm and consists of two mini servos acting as shoulder and elbow joints. It's goal is to put effector called 'blob' over an orange moving ball. Servos angles are the output of NN build with Keras while its inputs are chased ball and arm links positions acquired from camera images with OpenCV. Works only if ball is within effector working space.
