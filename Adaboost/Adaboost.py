import numpy as np
from collections import defaultdict


class WeakClf:
    def __init__(self, factor, k, weights, Q=5):
        self.Q = Q
        self.w_plus = None
        self.w_minus = None
        self.epsilon = 1/18
        self.weights = weights
        self.factor = factor
        self.k = k

    def fit(self, y):
        self.w_plus = []
        self.w_minus = []

        quantile_factor = self._div_quantile(self.factor)
        Z = 0

        for q in range(1, self.Q+1):
            W_plus = self.weights[(quantile_factor == q) & (y == 1)].sum()
            W_minus = self.weights[(quantile_factor == q) & (y == -1)].sum()
            self.w_plus.append(W_plus)
            self.w_minus.append(W_minus)
            Z += np.sqrt(W_plus * W_minus)
        return Z

    def _div_quantile(self, factor):
        res = factor.copy()
        for q in range(1, self.Q+1):
            cond = (factor <= q/self.Q) & (factor > (q-1)/self.Q)
            res[cond] = q
        return res

    def _predict(self, q):
        return 0.5 * np.log((self.w_plus[q-1] + self.epsilon) / (self.w_minus[q-1] + self.epsilon))

    def predict(self, X):
        quantile_factor = self._div_quantile(X[:, self.k])
        prediction = np.empty(len(X))
        for i, q in enumerate(quantile_factor):
            prediction[i] = self._predict(int(q))
        return prediction


class Adaboost:
    def __init__(self):
        self.Q = None
        self.weak_clfs = None
        self.best_weak_clfs = []

    def fit(self, X, y, num_of_iteration=100, Q=5):
        self.Q = Q
        self.weak_clfs = defaultdict(list)
        samples, num_of_factors = X.shape
        weights = np.ones(samples) / samples
        for l in range(num_of_iteration):
            Z = np.empty(num_of_factors)
            for k in range(num_of_factors):
                factor = X[:, k]
                weak_clf = WeakClf(factor, k=k, weights=weights)
                weak_clf_Z = weak_clf.fit(y)
                Z[k] = weak_clf_Z
                self.weak_clfs[l].append(weak_clf)
            best_k = Z.argmin()
            best_weak_clf = self.weak_clfs[l][best_k]
            self.best_weak_clfs.append(best_weak_clf)
            # update the weights
            best_weak_clf_prediction = best_weak_clf.predict(X)
            weights = weights * np.exp(-y * best_weak_clf_prediction)
            weights = weights / np.sum(weights)

    def predict(self, X):
        prediction = 0
        for weak_clf in self.best_weak_clfs:
            a = weak_clf.predict(X)
            prediction += a
        return prediction


def normalize_factor(X):
    import pandas as pd
    return pd.DataFrame(X).apply(lambda x: (x.argsort().argsort() + 1) / len(x)).values


if __name__ == "__main__":
    size = 1000
    X1 = np.random.normal(loc=-1, size=(size, 2))
    y1 = np.ones(size)
    X2 = np.random.normal(loc=1, size=(size, 2))
    y2 = np.ones(size) * -1
    X = np.vstack((X1, X2))
    y = np.hstack((y1, y2))

    X = normalize_factor(X)
    from sklearn.cross_validation import train_test_split
    from sklearn.ensemble import AdaBoostClassifier
    import matplotlib.pyplot as plt

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state = 42)
    ada = Adaboost()
    ada.fit(X_train, y_train)
    ada2 = AdaBoostClassifier()
    ada2.fit(X_train, y_train)
    plt.xlim((0,2))
    plt.ylim((0,2))
    for x, y in zip(X_train, y_train):
        if y > 0:
            plt.plot(x[0], x[1], 'ro')
        else:
            plt.plot(x[0], x[1], 'bo')

    for x, y in zip(X_test, y_test):
        if y > 0:
            plt.plot(x[0], x[1], 'ro', markersize=10)
        else:
            plt.plot(x[0], x[1], 'bo', markersize=10)

    plt.show()

    # print(X_test)
    # print(ada.predict(X_test))
    # print(y_test)
    print(sum(ada.predict(X_test) * y_test > 0) / len(y_test))
    print(sum(ada2.predict(X_test) * y_test > 0) / len(y_test))
