import scipy
import numpy as np 

class CSP:
    def __init__(self, n_components = []):
        self.n = n_components
        sel = []
        if not n_components == []:   
            if not int(n_components/2) == n_components/2:
                print("n_components should be an equal number, setting it to: {}".format(2*int(n_components/2)))
                n_components = 2*int(n_components/2)
            for n in range(int(n_components/2)):
                sel.append(n)
            for n in range(int(n_components/2)):
                sel.append(-int(n_components/2)+n)
            self.sel_eig = sel

    def fit(self, X, y, cue=0):
        weights = self._calcWeight(X,y, cue=cue)
        
        if self.n == []:
            self.weights = weights.T
        else:
            self.weights = weights[:,self.sel_eig].T
        return 1

    def fit_transform(self, X, y, cue=0):
        flag = self.fit(X, y, cue)
        if flag:
            X_t = self.transform(X)
            return X_t
        else:
            return flag

    def transform(self,X, use_logvar = False):
        if use_logvar:
            return np.array([np.log(np.var(self.weights.dot(x_trial), axis=1) ) for x_trial in X])   
        else:
            return np.array([self.weights.dot(x_trial) for x_trial in X])    

    def _calcWeight(self, X, y, cue=0):
        x1 = X[y==cue,:,:] #[Trial x Channel x Feature]
        x2 = X[y!=cue,:,:]
        S1 = self._calcCov(x1)
        S2 = self._calcCov(x2)

        vals, vecs = scipy.linalg.eig(S1, S1+S2)
        sort_idx = np.argsort(vals)
        return vecs[:, sort_idx]

    def _calcCov(self, x):
        S = np.zeros((x.shape[1],x.shape[1]))
        for n in range(x.shape[2]):
            S += np.cov(x[:,:,n].T)
        S /= x.shape[2]
        return S
