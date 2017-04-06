OUTPUT_DIR = 'out'
PLOT_DIR = 'out/plots'
SRCFILE_DIR = 'srcfiles_json'
REJECT_FILE = OUTPUT_DIR + '/' + 'reject.csv'
ACCEPT_FILE = OUTPUT_DIR + '/' + 'accept.csv'
LOGFILE = OUTPUT_DIR + '/' + 'checkspectra.log'

CONFUSION_MARK = 'confusion'
RFI_WEIGHT_MARK = 'rfi/weight'
BASELINE_MARK = 'baseline problem'
MORE_CHECKING_REQUIRED_MARK = 'more checking required'

REJECT_MARKS = [CONFUSION_MARK, RFI_WEIGHT_MARK, BASELINE_MARK, MORE_CHECKING_REQUIRED_MARK]

REJECTION_MESSAGE = '''What is the reason for rejecting the source....
	c    : confusion
	r    : rfi/weight
	b    : baseline problem
	m    : more checking required
	s    : skip and go back'''

HELP_MESSAGE = '''Instructions:
	n : move on to NEXT source; do not write info out
	a: ACCEPT source from list and write to accept csv file
	r: REJECT source from list and write to rej csv file after
		answering prompt for reason for rejection; see OUTPUT
	i: provides rms values in each polarization
	p: go back to PREVIOUS
	x, exit: close all files and exit the program 
	(c: included to allow changes in the central velocity, but not working)
	f: FLAG bad areas of the spectrum. You will be queried for the left 
		and right channels. The source file will be modified.'''

REJECT_FILE_HEADER = "AGC,rmsa,rmsb,avg_rms,w_opt,note\n"
ACCEPT_FILE_HEADER = "AGC,rmsa,rmsb,avg_rms,w_opt\n"

NEIGHBOR_SEPERATION_MAX = 6.0
# NEIGHBOR_SEPERATION_MAX = 40
NEIGHBOR_SEPERATION_MIN = 0.0
