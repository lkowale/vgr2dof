
# https://machinelearningmastery.com/regression-tutorial-keras-deep-learning-library-python/
import numpy
import pandas
import time
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib


def cartesian_product_basic(left, right):
    return left.assign(key=1).merge(right.assign(key=1), on='key').drop('key', 1)


start_time = time.time()

df = pandas.read_csv("./VGR2d_recorder_data.csv")
# get rid of any rows that doesnt have one contour for each mask
# df = df.dropna()
# ,blobmec_radius,,,,

left = df[['blobmec_cx', 'blobmec_cy', 'elbow', 'shoulder']]
left.rename(columns={'elbow': 'elbow_left', 'shoulder': 'shoulder_left'}, inplace=True)

right = df[['ulnarbr_angle', 'ulnarbr_cx', 'ulnarbr_cy', 'humerusrbr_angle', 'humerusrbr_cx', 'humerusrbr_cy', 'elbow', 'shoulder']]
right.rename(columns={'elbow': 'elbow_right', 'shoulder': 'shoulder_right'}, inplace=True)
dataset = cartesian_product_basic(left, right)

# dataset = dataset.values


# split into input (X) and output (Y) variables
# Y = dataset[:,1:]
# X = dataset[:,5:]
X = dataset[['blobmec_cx', 'blobmec_cy', 'ulnarbr_angle', 'ulnarbr_cx', 'ulnarbr_cy', 'humerusrbr_angle', 'humerusrbr_cx', 'humerusrbr_cy']]
Y = dataset[['elbow_left', 'shoulder_left', 'elbow_right', 'shoulder_right']]
# df['c'] = df.apply(lambda row: row.a + row.b, axis=1)
Y['elbow_delta'] = Y.apply(lambda row: row.elbow_left - row.elbow_right, axis=1)
Y['shoulder_delta'] = Y.apply(lambda row: row.shoulder_left - row.shoulder_right, axis=1)
Y = Y[['elbow_delta', 'shoulder_delta']]

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


# fix random seed for reproducibility
seed = 2018

# baseline model MSE 2x6x1=-1392; 2x6x6x1=-863, 2x12x12x1=-1280
numpy.random.seed(seed)

# kfold = KFold(n_splits=10, random_state=seed)
# results = cross_val_score(estimator, X, Y, cv=kfold)
# print("Results: %.2f (%.2f) MSE" % (results.mean(), results.std()))
# estimator.fit(X, Y)
# estimator.model.save("model_base.h5")

# Standardized: -53.11 (34.71) MSE
# Elapsed time 00:04:48
# Standardized: -71.85 (47.51) MSE
# Elapsed time 00:04:51
numpy.random.seed(seed)
estimators = []
estimators.append(('standardize', StandardScaler()))
estimators.append(('regresor', KerasRegressor(build_fn=baseline_model, epochs=1000, batch_size=300, verbose=1)))
pipeline = Pipeline(estimators)
kfold = KFold(n_splits=10, random_state=seed)
results = cross_val_score(pipeline, X, Y, cv=kfold)

pipeline.fit(X, Y)
print("Standardized: %.2f (%.2f) MSE" % (results.mean(), results.std()))
# your script
elapsed_time = time.time() - start_time
print("Elapsed time " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

# Save the Keras model first:
pipeline.named_steps['regresor'].model.save('model_pipeline.h5')
# This hack allows us to save the sklearn pipeline:
pipeline.named_steps['regresor'].model = None
# Finally, save the pipeline:
joblib.dump(pipeline, 'sklearn_pipeline.pkl')


# del pipeline



# pipeline.fit(X, Y)
#
# model_step = pipeline.steps.pop(-1)[1]
# joblib.dump(pipeline, './pipeline.pkl')
# models.save_model(model_step.model, './model.h5')



# estimator.fit(X, Y)
# estimator.model.save("model_stand.h5")
# prediction = estimator.predict(X)
# print(prediction)