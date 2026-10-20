import matplotlib.pyplot as plt
import numpy as np

from classifier import csp
from utils.load_data import load_data, fs, movement_tyes
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as lda

PLOT_EEG = False
PLOT_ERD = False
PLOT_CSP = False
PLOT_CLASSIFIER = True
PLOT_CLF_RT = False

if PLOT_EEG:
    ## Plot continous EEG from subject:
    eeg, stim, time = load_data(split_in_sessions = False, training = True, low_cut = 5.0, high_cut = 35.0, subject = 1, time_before = 3, time_after = 1.5)
    for ch in range(22):
        plt.plot(time, eeg[ch,:] + ch*40, 'k',linewidth=0.5)

    plt.gca().xaxis.grid(True)
    plt.gca().yaxis.grid(False)

    plt.xlabel('Time [s]')
    plt.xlim([0, time[-1]])
    plt.yticks([])
    plt.show()
if PLOT_ERD:
    ## Plot continous ERD from subject:
    X, Y, trial_time =  load_data(split_in_sessions = True, training = True, low_cut = 8.0, high_cut = 13.0, subject = 1, time_before = 3, time_after = 1.5)
    nmb_runs, nmb_channels, trial_length = X.shape

    Cz = X[:,9, :] - X.mean(axis=1) # Common average reference

    right = Cz[Y == movement_tyes['right hand']]
    left = Cz[Y == movement_tyes['left hand']]
    foot = Cz[Y == movement_tyes['feet']]
    tongue = Cz[Y == movement_tyes['tongue']]
    
    fig, ax = plt.subplots(4, 1)

    def moving_average(a, n):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n
    
    def plot_erd(ax, data, label = None):
        ax[0].plot(trial_time, data[0,:], label= label) #Plot eeg for one trial at Cz
        ax[1].plot(trial_time, data[0,:]**2, label= label) #Plot the power eeg for one trial at Cz
        
        mean_power = np.mean(data**2, axis=0)
        ax[2].plot(trial_time, mean_power, label= label) #Plot the power eeg for one trial at Cz
        
        nmb_trials = data.shape[0]
        erd = np.zeros((nmb_trials, data.shape[-1]))
        for i, trial in enumerate(data): 
            power = trial**2
            reference = power[:2*fs].mean()
            erd[i] = ((power- reference)/reference * 100)

        ax[3].plot(trial_time[int(fs/2)-1:], moving_average(erd.mean(axis=0), int(fs/2)), label= label) #Plot the power eeg for one trial at Cz
    plot_erd(ax, foot, label='feet')
    plot_erd(ax, left, label='left hand')
    plot_erd(ax, right, label='right hand')
    plot_erd(ax, tongue, label='tongue')
    ax[0].legend()
    for a, yaxis in zip(ax, ['μV', 'μV²', 'μV²', 'erd [%]']): 
        a.set_xlim([trial_time[int(fs/2)-1], trial_time[-1]])
        a.set_ylabel(yaxis)

    plt.show()

if PLOT_CSP:
    ## Plot CSP features from subject
    X, Y, trial_time =  load_data(split_in_sessions = True, training = True, low_cut = 8.0, high_cut = 35.0, subject = 1, time_before = 2, time_after = 1)
    nmb_runs, nmb_channels, trial_length = X.shape
    
    # use only trials for left and right hand movements:
    trial_idx = np.zeros(nmb_runs, dtype=bool)
    trial_idx[(Y==movement_tyes['right hand'])+(Y==movement_tyes['left hand'])] = True
    x = X[trial_idx]
    y = Y[trial_idx]
    nmb_runs = X.shape[0] # update number of runs

    clf = csp.CSP(12) 
    clf.fit(x[:, :, 3*fs:5*fs], y, cue = movement_tyes['right hand'])

    # Load test data:
    X, Y, trial_time =  load_data(split_in_sessions = True, training = False, low_cut = 8.0, high_cut = 35.0, subject = 1, time_before = 2, time_after = 1)
    trial_idx = np.zeros(nmb_runs, dtype=bool)
    trial_idx[(Y==movement_tyes['right hand'])+(Y==movement_tyes['left hand'])] = True
    x = X[trial_idx]
    y = Y[trial_idx]
    nmb_runs = X.shape[0] # update number of runs

    # Calculate features:
    features = clf.transform(x[:, :, 3*fs:5*fs], use_logvar=True)
    f_l = features[y == movement_tyes['left hand']].T
    f_r = features[y == movement_tyes['right hand']].T
    
    # Plot features:
    fig, ax = plt.subplots(1,1)
    ax.plot(f_l[0], f_l[1], 'or', label='left hand')
    ax.plot(f_r[0], f_r[1], 'ob', label='right hand')
    ax.set_xlabel('log(var(W[0] @ X))')
    ax.set_ylabel('log(var(W[1] @ X))')
    plt.tight_layout()
    plt.show()

if PLOT_CLASSIFIER:
    # Load training data (all trials kept):
    X, Y, trial_time = load_data(split_in_sessions=True, training=True, low_cut=8.0, high_cut=35.0, subject=1, time_before=2, time_after=1)

    x = X
    y = (Y == movement_tyes['right hand']).astype(int)   #1 for right hand. 0 for non-right hand

    clf_csp = csp.CSP(12)                    #12 CSP filters
    _x = x[:, :, 3*fs:5*fs]                  #time window of the raw EEG
    clf_csp.fit(_x, y, cue=1)                #cue=1 -> right hand vs everything else
    train_features = clf_csp.transform(_x, use_logvar=True)   #N trials x 12 features
    clf_lda = lda().fit(train_features, y)

    # Load test data:
    X, Y, trial_time = load_data(split_in_sessions=True, training=False, low_cut=8.0, high_cut=35.0, subject=1, time_before=2, time_after=1)

    x = X
    y = (Y == movement_tyes['right hand']).astype(int)

    # Calculate features and predict:
    features = clf_csp.transform(x[:, :, 3*fs:5*fs], use_logvar=True)
    guess = clf_lda.predict(features)

    cm = np.zeros((2, 2))
    map_to_cm = {1: 0, 0: 1}                 # index 0 = right hand, index 1 = not right hand

    for _guess, _target in zip(guess, y):
        i_guess = map_to_cm[int(_guess)]
        i_targ = map_to_cm[int(_target)]
        cm[i_guess, i_targ] += 1

    print("Confusion Matrix: \n", cm)
    print("Accuracy: ", np.diagonal(cm).sum() / cm.sum() * 100, "%")

if PLOT_CLF_RT:
    ## Plot CSP features from subject
    X, Y, trial_time =  load_data(split_in_sessions = True, training = True, low_cut = 5.0, high_cut = 35.0, subject = 1, time_before = 2, time_after = 1)
    nmb_runs, nmb_channels, trial_length = X.shape

    # use only trials for left and right hand movements:
    trial_idx = np.zeros(nmb_runs, dtype=bool)
    trial_idx[(Y==movement_tyes['right hand'])+(Y==movement_tyes['left hand'])] = True
    x = X[trial_idx]
    y = Y[trial_idx]

    nmb_runs = X.shape[0] # update number of runs

    clf_csp = csp.CSP(6) # Use eight csp features
    _x = x[:, :, 3*fs:5*fs]
    clf_csp.fit(_x, y, cue = movement_tyes['right hand'])
    train_features = clf_csp.transform(_x, use_logvar=True)
    clf_lda = lda().fit(train_features, y)
    
    print(clf_lda.classes_)
    # Load test data: (not split in sessions)
    eeg, stim, time =  load_data(split_in_sessions = False, training = False, low_cut = 5.0, high_cut = 35.0, subject = 1, time_before = 2, time_after = 1)
    window_size = 2*fs
    
    guess = np.zeros((2, eeg.shape[-1]))
    for _sample_id in range(window_size, eeg.shape[-1]): 
        # Calculate features:
        feature = clf_csp.transform([eeg[:, _sample_id-window_size:_sample_id]], use_logvar=True)
        _guess = clf_lda.predict_proba(feature)
        guess[:, _sample_id] = _guess[0]

    #Add shaded area to indicte the duration where participant performed the movement. 
    for _stim in stim: 
        start = _stim['sample']
        cue = _stim['cue']
        if cue == movement_tyes['right hand']:
            color = 'b'
        elif cue == movement_tyes['left hand']: 
            color = 'g'
        else: 
            color = 'r'
        plt.fill_between(time[start:start+fs*4], -np.ones(fs*4)*0.05,-np.ones(fs*4)*0.2, color = color)
    
    for i, label in enumerate(clf_lda.classes_):
        color = 'b' if label == movement_tyes['right hand'] else 'g'
        plt.plot(time, guess[i], color=color)
    plt.ylim([-0.1, 1.1])
    plt.show()
    
