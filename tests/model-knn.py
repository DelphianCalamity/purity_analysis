TRACE = True
CTRACE = False


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

df = pd.read_csv('purity_analysis/tests/data.csv')

features = df.drop('TARGET CLASS',axis=1)
targets = df['TARGET CLASS']
X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.30)


k = 40
error_rate = [0]*k
for i in range(1, k):
    if TRACE:
        import sys
        from tracer import Tracer
        tracer = Tracer([])
        sys.settrace(tracer.trace_calls)
        sys.setprofile(tracer.trace_c_calls)

    if CTRACE:
        import ctracer
        ctracer.start()

    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    error = np.mean(pred_i != y_test)
    error_rate[i-1] = error
    if TRACE:
        sys.settrace(None)
        sys.setprofile(None)
        print("OUT!")
        tracer.log_annotations(__file__)

    if CTRACE:
        ctracer.stop()

    break
print(error_rate)


