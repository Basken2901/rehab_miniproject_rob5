import matplotlib.pyplot as plt
import numpy as np

from braindecode.datasets import MOABBDataset
from braindecode.preprocessing import Preprocessor, preprocess, create_windows_from_events

from classifier import csp

"""
ABOUT THE DATA: 

This data set consists of EEG data from 9 subjects. The cue-based BCI paradigm consisted of four different motor imagery tasks, namely the imag- ination of movement of the left hand (class 1), right hand (class 2), both feet (class 3), and tongue (class 4). Two sessions on different days were recorded for each subject. Each session is comprised of 6 runs separated by short breaks. One run consists of 48 trials (12 for each of the four possible classes), yielding a total of 288 trials per session.

The subjects were sitting in a comfortable armchair in front of a computer screen. 
At the beginning of a trial ( t = 0 s), a fixation cross appeared on the black screen. 
In addition, a short acoustic warning tone was presented. 
After two seconds ( t = 2 s), a cue in the form of an arrow pointing either to the left, right, down or up (corresponding to one of the four classes left hand, right hand, foot or tongue) appeared and stayed on the screen for 1.25 s. This prompted the subjects to perform the desired motor imagery task. No feedback was provided. 
The subjects were ask to carry out the motor imagery task until the fixation cross disappeared from the screen at t = 6 s.

Twenty-two Ag/AgCl electrodes (with inter-electrode distances of 3.5 cm) were used to record the EEG; the montage is shown in Figure 3 left. All signals were recorded monopolarly with the left mastoid serving as reference and the right mastoid as ground. 
The signals were sampled with. 250 Hz and bandpass-filtered between 0.5 Hz and 100 Hz. The sensitivity of the amplifier was set to 100 μV . An additional 50 Hz notch filter was enabled to suppress line noise

"""
# Load data and preprocess:
time_mi = 4
fs = 250
nmb_chan = 22
movement_tyes = {'feet' : 0, 'left hand' : 1, 'right hand' : 2, 'tongue' : 3}

def load_data(split_in_sessions = True, training = True, low_cut = 8.0, high_cut = 35.0, subject = 1, time_before = 2, time_after = 1):
    """Load data from the BCI competition.

    Args:
        split_in_sessions (bool) : should the data be continuous or split into trials? Default=True
        training (bool) : should the data be extracted from training sessions (True) or test session (false). Default=True
        low_cut (float) : the low bandpass filter frequency. Default = 5.0
        high_cut (float) : the high bandpass filter frequency. Default = 35.0
        subject (int) : Subject number. Default = 1
        time_before (float) : Only used when split_in_session=True. Number of seconds to include before cue-onset. Default = 2.0. 
        time_after (float) :  Only used when split_in_session=True. Number of seconds to include after cue-offset. Default = 1.0. 

    Returns:
        X (np.array): EEG data of size (channel x time) if split_in_session = False. Else of size (trial x channel x trial_time)
        y (np.array or structure-array): If split_in_session = True it returns an np.array with of size (trial), where each element indicate the trial cue. 
                                         If split_in_session = False it returns a vector array where each element is a dictionary such that y[trial]['cue'] is the cue with onset at data sample y[trial]['sample']
        time (np.array): Is a array that indicate the time. 
    """

    nmb_samples = int(fs*(time_before+time_mi+time_after)) # 1 second before + 4 second trial + 1 second after
    
    dataset = MOABBDataset(dataset_name="BNCI2014_001", subject_ids=[subject])
    eeg_preprocessors = [
        Preprocessor("pick_types", eeg=True, meg=False, stim= not split_in_sessions),
        Preprocessor("filter", l_freq=low_cut, h_freq=high_cut),  # Bandpass filter
    ]

    splitted = dataset.split("session")
    if training: 
        session_dataset = splitted["0train"]  # Session train
    else: 
        session_dataset = splitted["1test"]  # Session train

    preprocess(session_dataset, eeg_preprocessors)

    if split_in_sessions: 
        windows_dataset = create_windows_from_events(
            session_dataset,
            trial_start_offset_samples=-int(time_before*250),
            trial_stop_offset_samples=int(time_after*fs),
            preload=True,
        )

        nmb_runs = len(windows_dataset.datasets)*len(windows_dataset.datasets[0]) 
        X = np.empty((nmb_runs, nmb_chan, nmb_samples))
        Y = np.empty((nmb_runs, ))
        run_i = 0

        for run in windows_dataset.datasets:
            for x, y, _ in run:
                X[run_i] = x*1e6
                Y[run_i] = y
                run_i += 1
        time = np.arange(nmb_samples)/fs-time_before
        return X, Y, time
    else: 
        sample = 0 
        eeg = np.empty((22, len(session_dataset)))
        stim = []
        cue_remap = [1, 2, 0, 3]
        for x, y in session_dataset:
            eeg[:,sample] = x[:22,0]*1e6
            if x[22, 0] > 0:
                stim.append({"cue": cue_remap[int(x[22, 0]-1)], 'sample': sample+2*fs})#Shift stim time by 2s to occur when stim was presented
            sample += 1
        time = np.arange(len(session_dataset))/fs
        return eeg, stim, time

