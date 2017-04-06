# checkspectra
# Author: Josh Norton
# www.github.com/jnorton2

import os, sys, json, datetime, math, shutil
import config
import numpy as np 
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool


AGC_LIST = []

# inits out file directory
def makeDirectoryIfNotExist(directory):
	try:
		os.mkdir(directory)
	except Exception, e:
		pass

# initializes output directorys if they don't exists
def initDirs():
	if not os.path.isdir(config.SRCFILE_DIR):
		raise Exception("No source file driectory found, looking for " + SRCFILE_DIR)		
	
	makeDirectoryIfNotExist(config.OUTPUT_DIR)
	makeDirectoryIfNotExist(config.PLOT_DIR)
	
	if not os.path.exists(config.LOGFILE):
		with open(config.LOGFILE, 'w+') as f:
			pass
	
	if not os.path.exists(config.REJECT_FILE):
		with open(config.REJECT_FILE, 'w+') as rejectfile:
			rejectfile.write(config.REJECT_FILE_HEADER)

	if not os.path.exists(config.ACCEPT_FILE):
		with open(config.ACCEPT_FILE, 'w+') as rejectfile:
			rejectfile.write(config.ACCEPT_FILE_HEADER)


# writes our the information for the source to rms csv file
def accept(src):
	# write csv to accept.csv with same col as rejects
	data = [
		int(src['HD']['AGC']),
		src['RMS'][0],
		src['RMS'][1],
		src['HD']['INPUT'][3]
	]
	csvline = ','.join(map(str,data))
	with open(config.ACCEPT_FILE, 'a') as file:
		file.write(csvline + '\n')
	log('Accepted ' + src['filename'])


# rejects the source from the list and write to the reject file after answering
# prompt for reason for rejection
def promptReject(src):
	os.system('clear')
	print src['filename']
	print config.REJECTION_MESSAGE
	cmd = raw_input("Enter a command: ")

	reason = ''
	done = False
	while not done:
		done = True
		if cmd =='s' : 
			return 0
		elif cmd == 'c':
			reason = config.CONFUSION_MARK		
		elif cmd == 'r':
			reason = config.RFI_WEIGHT_MARK
		elif cmd == 'b':
			reason = config.BASELINE_MARK
		elif cmd == 'm':
			reason = config.MORE_CHECKING_REQUIRED_MARK
		else:
			print 'Sorry, that is not a command'
			done = False

	markRejectWithReason(src, reason)
	
def markRejectWithReason(src, mark):
	data = [
		int(src['HD']['AGC']),
		src['RMS'][0],
		src['RMS'][1],
		src['HD']['INPUT'][3],
		mark
	]
	csvline = ','.join(map(str,data))
	with open(config.REJECT_FILE, 'a') as rejectfile:
		rejectfile.write(csvline + '\n')

	log('Rejected ' + src['filename'] + ' with reason ' + mark)



# provide rms values in each polarization
def i_thing():
	# not sure what this is yet
	print 'provide rms values please'


# flag bad areas of the spectrum. You will be queried for the left and right channels
# once channels are flagged the src file will be modified
def flagSrcUi(src):
	print 'Flag bad areas of the spectrum...'
	correct = 'n'
	while not correct == 'y' or not correct == 'yes': 
		lower = raw_input('Lower channel?')
		upper = raw_input('Upper channel?')
		try:
			print 'Lower : ' + src['VELARR'][lower]
			print 'Upper : ' + src['VELARR'][upper]			
			correct = raw_input('Are these correct? ')
		except Exception as e:
			print 'That is not an acceptable input'
			correct = 'n'
	flagSrc(src, lower, upper)

def flagSrc(src, lower, upper):
	src['WEIGHT']['WSPECA'][lower:upper] = [0.01 for i in src['WEIGHT']['WSPECA'][lower:upper]] 
	src['WEIGHT']['WSPECB'][lower:upper] = [0.01 for i in src['WEIGHT']['WSPECB'][lower:upper]] 
	log("flagged " + src['filename'] + ' with lower channel = ' + str(lower) + " and upper channel " + str(upper)) 
	saveSrc(src)

def saveSrc(src):
	with open(config.SRCFILE_DIR + '/' + src['filename'], 'w') as f:
		json.dump(src, f)


# prints help message
def printHelp():
	print config.HELP_MESSAGE


# cleans up nescessary things
def cleanup():
	print 'cleaning up...'


# loads the source json by file name and add file name to json
def loadSource(filename):
	sourceFilePath = config.SRCFILE_DIR + '/' + filename
	if not os.path.isfile(sourceFilePath):
		raise Exception("Could not find file : " + filename)
	src = ''
	with open(sourceFilePath) as json_data:
		src = json.load(json_data)
	src['filename'] = filename
	saveSrc(src)
	return src

def clearAcceptRejectFiles():
	try:
		os.remove(config.REJECT_FILE)
	except Exception as e:
		pass
	try:
		os.remove(config.ACCEPT_FILE)
	except Exception as e:
		pass
	initDirs()

def log(message):
	print str(message)
	with open(config.LOGFILE, 'a+') as logFile:
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		logFile.write(date + ' : ' + str(message) + '\n')
		

# Loads the agc list if it hasn't already been done
def loadAgcList():
	global AGC_LIST
	if AGC_LIST == []:
		log("Loading agc list for the first time...")
		with open('agclist.txt', 'r') as agclist:
			for line in agclist.readlines():
				data = line.rstrip().split(' ')
				data = filter(lambda a: a != '' , data)
				obj = {
					'agc_number' : int(data[0]),

					# position on the sky
					# ra = long, dec = lat
					'ra' : float(data[1]),
					'dec' : float(data[2]),
					
					'magnitude' : float(data[3]),
					'entry3' : data[4],
					'vel_opt' : float(data[5]),
					'restofdata' : data[6:]
				}
				AGC_LIST.append(obj)
		log("Successfully loaded agc list")

	return AGC_LIST


def getNeighbors(src):
	try:
		print int(src['HD']['AGC'])
		agclist = loadAgcList()
		src_agclist_entry = [x for x in agclist if int(x['agc_number']) == int(src['HD']['AGC'])][0]
		src_ra = src_agclist_entry['ra']
		src_dec = src_agclist_entry['dec']
		neighbors = []
		for entry in agclist:
			ra_seperation = (entry['ra'] - src_ra) * 15
			dec_seperation = (entry['dec'] - src_ra)
			full_seperation = math.sqrt(math.pow(ra_seperation,2) + math.pow(dec_seperation,2)) * 60
			if full_seperation < config.NEIGHBOR_SEPERATION_MAX and full_seperation > config.NEIGHBOR_SEPERATION_MIN:
				neighbors.append(entry)

		if len(neighbors) > 0:
			log('found neighbors for ' + str(int(src['HD']['AGC'])) + ' : ' + str([x['agc_number'] for x in neighbors]))
		else:
			log('found no neighbors for ' + str(int(src['HD']['AGC'])))
		
		return neighbors

	except Exception as e:
		log('Could not get neighbors: ' + str(e))
		return []


def showPlot(src):
	title = src['filename']

	velarray = src['VELARR']
	yarra = src['SPECPOL']['YARRA']
	yarrb = src['SPECPOL']['YARRB']
	
	bothyarr = np.array(yarrb) + np.array(yarra)
	bothyarr = bothyarr / 2
	wspecaTruthArray = []
	for x in src['WEIGHT']['WSPECA']:
		if x > .05:
			wspecaTruthArray.append(1)
		else:
			wspecaTruthArray.append(0)
	wspecaTruthArray = np.array(wspecaTruthArray)

	bothyarr = bothyarr * wspecaTruthArray

	TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

	plotWidth = 700
	# pol A graph
	polAGraph = figure(tools=TOOLS, width=plotWidth, height=150)
	polAGraph.line(velarray, yarra, line_color='red')
	polAGraph.line(x=src["VELARR"][src["CCH"]], y=[min(yarra), max(yarra)],line_dash='dotted', color='black')
	polAGraph.yaxis.axis_label = 'Flux Density (mJy)'
	polAGraph.title.text = 'Polarization A'


	# pol B graph
	polBGraph = figure(tools=TOOLS, width=plotWidth, height=150)
	polBGraph.line(velarray, yarrb)
	polBGraph.line(x=src["VELARR"][src["CCH"]], y=[min(yarrb), max(yarrb)],line_dash='dotted', color='black')
	polBGraph.yaxis.axis_label = 'Flux Density (mJy)'
	polBGraph.title.text = 'Polarization B'

	
	# weight graph
	weightGraph = figure(tools=TOOLS, width=plotWidth, height=150)
	weightGraph.line(velarray, src['WEIGHT']['WSPECA'], line_color="red")
	weightGraph.line(velarray, src['WEIGHT']['WSPECB'])
	weightGraph.xaxis.axis_label = 'Velocity'
	weightGraph.yaxis.axis_label = 'Weight'

	# combined graph
	combinedGraph = figure(tools=TOOLS, width=plotWidth, height=250)
	combinedGraph.line(velarray, bothyarr, line_color='black')
	combinedGraph.line(x=src["VELARR"][src["CCH"]], y=[min(bothyarr), max(bothyarr)],line_dash='dotted', color='black')
	wopt = src['HD']['INPUT'][3]
	combinedGraph.line(x=src["VELARR"][src["CCH"]]+ wopt / 2 , y=[min(bothyarr), max(bothyarr)],line_dash='dotted', color='red')
	combinedGraph.line(x=src["VELARR"][src["CCH"]]- wopt / 2 , y=[min(bothyarr), max(bothyarr)],line_dash='dotted', color='red')
	
	neighbors = getNeighbors(src)

	if len(neighbors) > 0 :
		source = ColumnDataSource(
        	data=dict(
            	x=[[x['vel_opt'], x['vel_opt']] for x in neighbors],
            	y=[[min(bothyarr), max(bothyarr)] for x in neighbors],
           		agc_number=[x['agc_number'] for x in neighbors],
           		magnitude=[x['magnitude'] for x in neighbors]
        		)
    		)
		hover = HoverTool(
    	    tooltips=[
	            ("AGC", "@agc_number"),
	            ("Velocity", "$x"),
	            ("Magnitude", "@magnitude")
	        ]
	    )
		combinedGraph.add_tools(hover)
		combinedGraph.multi_line('x','y',line_dash='dashed',color='green', source=source)
	
		combinedGraph.title.text = 'Combined Polarizations'
	else:
		combinedGraph.title.text = 'Combined Polarizations (No neighboring galaxies within '+ str(config.NEIGHBOR_SEPERATION_MAX) + ' arc min)'
		
	combinedGraph.yaxis.axis_label = 'Flux Density Combined (mJy)'


	output_file(config.PLOT_DIR + '/' +  title[:-5] + '.html')

	plot = gridplot(combinedGraph, weightGraph, polAGraph, polBGraph, ncols = 1)
	show(plot)



def hasBeenChecked(file):
	with open(config.REJECT_FILE, "r") as rfile:
		for line in rfile.readlines():
			if line.startswith(file.split('.')[0][3:]):
				return True

	with open(config.ACCEPT_FILE, "r") as afile:
		for line in afile.readlines():
			if line.startswith(file.split('.')[0][3:]):
				return True
	
	return False



# runs the main menu
def run():
	initDirs()

	srcFiles =[s for s in os.listdir(config.SRCFILE_DIR)]
	for srcFile in srcFiles:
		if not srcFile.endswith('.json'):
			srcFiles.remove(srcFile)

	i = 0
	while i < range(len(srcFiles)) and i >= 0:
		file = srcFiles[i]
		os.system('clear')
		print 'loaded ' + file		
		src = loadSource(file)
		showPlot(src)
		printHelp()
		cmd = raw_input('Enter command: ')

		# exit
		if cmd == 'x' or cmd == 'exit' or cmd == 'quit':
			cleanup()
			sys.exit(1)
		
		# next 
		elif cmd == 'n':
			if i + 1 >= len(srcFiles):
				print 'this is the last file'
			else:
				i += 1
		
		# previous
		elif cmd == 'p':
			if i == 0:
				print 'this is the first file'
				i == 0
			else: 
				i -= 1
		
		elif cmd == 'a':
			accept(src)

		
		elif cmd == 'r':
			promptReject(src)
			i += 1

		elif cmd == 'i':
			i_thing(src)

		elif cmd == 'f':
			flagSrcUi(src)

		else:
			print 'command unknown'



if __name__ == "__main__":
	loadAgcList()
	run()




	