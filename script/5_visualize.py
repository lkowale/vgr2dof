import numpy as np
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from keras.models import load_model
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
from mpl_toolkits import mplot3d

df = pandas.read_csv("./VGR2d_recorder_data.csv")

# split into input (X) and output (Y) variables

X = df[['blobmec_cx', 'blobmec_cy', 'ulnarbr_angle', 'ulnarbr_cx', 'ulnarbr_cy', 'humerusrbr_angle', 'humerusrbr_cx', 'humerusrbr_cy']]
# set ulna and humerus params constant - values 
for column in X.columns[2:]:
    def_value = X.loc[0, column]
    X[column] = def_value

Y = df[['elbow', 'shoulder']]
Y['elbow_delta'] = Y.apply(lambda row: row.elbow - Y.loc[0, 'elbow'], axis=1)
Y['shoulder_delta'] = Y.apply(lambda row: row.shoulder - Y.loc[0, 'shoulder'], axis=1)
Y = Y[['elbow_delta', 'shoulder_delta']]
# fix random seed for reproducibility
seed=2018

#baseline model MSE 2x6x1=-1392; 2x6x6x1=-863, 2x12x12x1=-1280
np.random.seed(seed)

# define base model
def baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(64, input_dim=8, kernel_initializer='normal', activation='relu'))
    model.add(Dense(64, kernel_initializer='normal', activation='relu'))
    # model.add(Dense(32, kernel_initializer='normal', activation='relu'))
    model.add(Dense(2, kernel_initializer='normal', activation='linear'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


# Load the pipeline first:
pipeline = joblib.load('sklearn_pipeline.pkl')

# Then, load the Keras model:
pipeline.named_steps['regresor'].model = load_model('model_pipeline.h5')

y_pred = pipeline.predict(X)

# ziper=zip(y,Y)
# print(set(ziper))

# axes = np.hsplit(X, 2)
axes = X[['blobmec_cx', 'blobmec_cy']].values

dots = Y.values
pred_dots = np.hsplit(y_pred, 2)

shape=50
x = np.linspace(0, 600, shape)
y = np.linspace(0, 400, shape)
# def predict(x, y):
#     return pipeline.predict((x,y))
xx, yy = np.meshgrid(x, y)
pred_input = np.vstack([xx.ravel(),yy.ravel()]).transpose()#np.vstack([X.ravel(), Y.ravel()])
# set ulna and humerus params constant - values
for column in X.columns[2:]:
    def_value = X.loc[0, column]
    filled_column = np.full(shape=(pred_input.shape[0], 1), fill_value=def_value)
    pred_input = np.append(pred_input, filled_column, axis=1)


Z = pipeline.predict(pred_input)
Z_list = np.hsplit(Z, 2)
ZZ_0 = Z_list[0].reshape(shape, shape)
ZZ_1 = Z_list[1].reshape(shape, shape)



#serwo position of joint0
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter3D(axes[0], axes[1], dots[0], cmap='Reds')
# ax.scatter3D(axes[0], axes[1], pred_dots[0].flatten(), c=dots[0].flatten(), cmap='Reds') #c=pred_dots[0],
ax.plot_surface(xx, yy, ZZ_0, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')

#serwo position of joint1
fig1 = plt.figure()
ax = fig1.add_subplot(111, projection='3d')
ax.scatter3D(axes[0], axes[1],dots[1], c=dots[1].flatten(), cmap='Reds')
# ax.scatter3D(axes[0], axes[1],pred_dots[1], c=pred_dots[1].flatten(), cmap='Reds')
ax.plot_surface(xx, yy, ZZ_1, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')

plt.show()
