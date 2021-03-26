import sys
# import pandas as pd
import numpy as np
# from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from purity_analysis import Tracer

# df = pd.read_csv('purity_analysis/tests/data.csv')

# features = df.drop('TARGET CLASS',axis=1)
# targets = df['TARGET CLASS']
# X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.30)

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

# k = 40
# error_rate = [0]*k
# for i in range(1, k):
knn = KNeighborsClassifier(n_neighbors=1)
    # knn.fit(X_train, y_train)
    # pred_i = knn.predict(X_test)
    # error = np.mean(pred_i != y_test)
    # error_rate[i-1] = error
# print(error_rate)

sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
