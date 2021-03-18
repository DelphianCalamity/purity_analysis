import pandas as pd
import sys

from bytecodes_analysis.tracer import Tracer
import sys

import pandas as pd

from bytecodes_analysis.tracer import Tracer

tracer = Tracer([])
sys.settrace(tracer.trace_calls)
sys.setprofile(tracer.trace_c_calls)

df = pd.read_csv('../knn-data.csv')

# features = df.drop('TARGET CLASS',axis=1)
# targets = df['TARGET CLASS']
# X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.30)

# error_rate = []

# for i in range(1, 2):
#     knn = KNeighborsClassifier(n_neighbors=i)
# knn.fit(X_train,y_train)
# pred_i = knn.predict(X_test)
# error = np.mean(pred_i != y_test)
# error_rate.append(error)  #


sys.settrace(None)
sys.setprofile(None)
tracer.log_annotations(__file__)
