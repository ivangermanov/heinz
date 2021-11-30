from sklearn.base import BaseEstimator
from tensorflow.keras.optimizers import Adam, RMSprop, Nadam, Adadelta, SGD, Adamax, Ftrl
from keras.layers import Input, Convolution2D, Dense, concatenate, multiply, Flatten, LSTM, TimeDistributed, Reshape, \
    RepeatVector, Permute, Dropout, Embedding, Reshape, Add, BatchNormalization, LeakyReLU, Dot

from keras.models import Model
from keras.callbacks import EarlyStopping
import xgboost as xgb
import numpy as np

OPTIMIZERS = {
    "nadam": Nadam,
    "adam": Adam,
    "adamax": Adamax,
    "rmsprop": RMSprop,
    "adadelta": Adadelta,
    "ftrl": Ftrl,
    "sgd": SGD
}

class LSTMForecaster(BaseEstimator):
    def __init__(self, estimator_params, preprocessing_params):
        self.estimator_params = estimator_params
        self.preprocessing_params = preprocessing_params
        self.loss = estimator_params["loss"]

    def design_model(self,
                     h_dim,
                     drop_out_rate,
                     reg_penalty):

        if "year" in self.preprocessing_params["input_temporal_granularities"]:

            year_input = Input(shape=(1))
            year_layer =  Embedding(3, h_dim)(year_input)
            year_layer = Dense(h_dim, activation='relu')(year_layer)
            year_layer = Flatten()(year_layer)
            year_layer = Reshape((1, h_dim))(year_layer)

        if "Shift" in self.preprocessing_params["relevant_vars_HW"]:
            shift_input = Input(shape=(1))
            shift_layer =  Embedding(3, h_dim)(shift_input)
            shift_layer = Dense(h_dim, activation='relu')(shift_layer)
            shift_layer = Flatten()(shift_layer)
            shift_layer = Reshape((1, h_dim))(shift_layer)

        if "day of week" in self.preprocessing_params["input_temporal_granularities"]:
            dow_input = Input(shape=(1))
            dow_layer =  Embedding(7, h_dim)(dow_input)
            dow_layer = Dense(h_dim, activation='relu')(dow_layer)
            dow_layer = Flatten()(dow_layer)
            dow_layer = Reshape((1, h_dim))(dow_layer)

        if "hour" in self.preprocessing_params["input_temporal_granularities"]:
            hour_input = Input(shape=(1))
            hour_layer =  Embedding(24, h_dim)(hour_input)
            hour_layer = Dense(h_dim, activation='relu')(hour_layer)
            hour_layer = Flatten()(hour_layer)
            hour_layer = Reshape((1, h_dim))(hour_layer)

        ai_input = Input(
            shape=(len(self.preprocessing_params["relevant_vars_HW"])-1, 1)
        )
        cw_input = Input(
            shape=(len(self.preprocessing_params["input_lag_columns"]), self.preprocessing_params["input_lag_cw"])
        )

        ai_layer = Dense(self.preprocessing_params["input_lag_cw"], activation="relu")(ai_input)

        total_layer = concatenate([ai_layer, cw_input, year_layer, shift_layer, dow_layer, hour_layer], axis=1)
        total_layer = Permute((2, 1))(total_layer)

        lstm1 = LSTM(units=2*h_dim,
                       activation="relu",
                       return_sequences=True)(total_layer)
        
        lstm2 = LSTM(units=2*h_dim,
                       activation="relu",
                       return_sequences=False)(lstm1)

        gate2 = Dense(1)(lstm2)

        model = Model([ai_input, cw_input, year_input, shift_input, dow_input, hour_input],
                gate2)

        return model


    def __initialize_model(self, X, y):
               # Here we define the model:
        drop_out_rate = self.estimator_params["drop_out_rate"]
        reg_penalty = self.estimator_params["reg_penalty"]
        h_dim = self.estimator_params["h_dim"]

        self.model = \
            self.design_model(h_dim, drop_out_rate, reg_penalty)

        print(f"{self.model.summary()}")

    def __fit(self, input, labels):
        callback = EarlyStopping(
            monitor='val_loss',
            verbose=self.estimator_params["verbose"],
            min_delta=0,
            patience=10,
            mode='auto')

        optimizer = OPTIMIZERS[self.estimator_params["optimizer"]]

        self.model.compile(
            optimizer(lr=self.estimator_params["learning_rate"]),
            loss=self.loss)

        self.model.fit(
            input,
            labels,
            epochs=self.estimator_params["epochs"],
            verbose=self.estimator_params["verbose"],
            shuffle=True,
            batch_size=self.estimator_params["batch_size"],
            validation_split=0.1,
            callbacks=[callback])

    def fit(self, X, y):
        self.__initialize_model(X, y)
        input, y = self.extract_input_and_labels(X, y)
        self.__fit(input, y)
        
        return self

    def predict(self, X):
        input = self.extract_input(X)
        results = self.model.predict(input)
        return results

    def extract_input_and_labels(self, X, y):
        relevant_vars_HW = self.preprocessing_params["relevant_vars_HW"]
        if "Date" in relevant_vars_HW:
            relevant_vars_HW.remove("Date")
        
        ai_input = X[relevant_vars_HW]
        
        cw_input_cols = []
        CW_cols = self.preprocessing_params["input_lag_columns"]
        cw_input_cols.extend(CW_cols)
        lag_cw = self.preprocessing_params["input_lag_cw"]
        for lag in range(1, lag_cw):
            for CW_col in CW_cols:
                cw_input_cols.append(f"{CW_col}_{lag}")

        cw_input = X[cw_input_cols].values
        cw_input = np.reshape(cw_input, (cw_input.shape[0], len(CW_cols), lag_cw))

        year_input = X["year"]
        shift_input = X["Shift"]
        dow_input = X["day of week"]
        hour_input = X["hour"]

        return [ai_input.values, cw_input, year_input, shift_input, dow_input, hour_input], y

    def extract_input(self, X):
        relevant_vars_HW = self.preprocessing_params["relevant_vars_HW"]
        if "Date" in relevant_vars_HW:
            relevant_vars_HW.remove("Date")
        
        ai_input = X[relevant_vars_HW]
        
        cw_input_cols = []
        CW_cols = self.preprocessing_params["input_lag_columns"]
        cw_input_cols.extend(CW_cols)
        lag_cw = self.preprocessing_params["input_lag_cw"]
        for lag in range(1, lag_cw):
            for CW_col in CW_cols:
                cw_input_cols.append(f"{CW_col}_{lag}")

        cw_input = X[cw_input_cols].values
        cw_input = np.reshape(cw_input, (cw_input.shape[0], len(CW_cols), lag_cw))

        year_input = X["year"]
        shift_input = X["Shift"]
        dow_input = X["day of week"]
        hour_input = X["hour"]

        return [ai_input.values, cw_input, year_input, shift_input, dow_input, hour_input]
    

class XgbForecaster(BaseEstimator):
    def __init__(self, estimator_params, preprocessing_params):
        self.estimator_params = estimator_params
        self.preprocessing_params = preprocessing_params
    def __initialize_model(self, X, y):
        n_estimators = self.estimator_params["n_estimators"]
        max_depth = self.estimator_params["max_depth"]
        eta= self.estimator_params["eta"]
        subsample= self.estimator_params["subsample"]
        colsample_bytree= self.estimator_params["colsample_bytree"]

        model_xgb = xgb.XGBRegressor(n_estimators=n_estimators,
                                     max_depth=max_depth,
                                     eta=eta,
                                     subsample=subsample,
                                     colsample_bytree=colsample_bytree)

        self.model = model_xgb

    def __fit(self, input, labels):
        self.model.fit(input, labels) 

    def fit(self, X, y):
        self.__initialize_model(X, y)
        self.__fit(X, y)

    def predict(self, X):
        results = self.model.predict(X)
        return results