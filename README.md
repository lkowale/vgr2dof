# vgr2dof
## 2 joints vision guided robot 
This robot is a planar mimic of human arm and consists of two mini servos acting as shoulder and elbow joints. It's goal is to put effector called 'blob' over an orange moving ball. Servos angles are the output of NN build with Keras while its inputs are chased ball and arm links positions acquired from camera images with OpenCV. Works only if ball is within effector's working space. Application that provides a tkinter video interface starts with aspectstuner.py script.

<!-- [vgr2d](/img/vgr2d_short.gif) -->

Youtube link:

[![vgr2d youtube](http://img.youtube.com/vi/9y-y2UV7cYU/0.jpg)](http://www.youtube.com/watch?v=9y-y2UV7cYU)
