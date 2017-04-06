from Tkinter import * 
from checkspectra import *
import tkMessageBox
import config, os
WINDOW_HEIGHT = 450
WINDOW_WIDTH = 800

class MyApp:
	def __init__(self, parent):
		self.SELECTED = None
		self.SELECTED_INDEX = 0

		initDirs()
		loadAgcList()
		self.setupLists(parent)
		self.setupScanner(parent)
		self.setupMarkers(parent)
		Button(self.rightsideholder, text='Reset rej/acpt files', command=self.click_refresh).pack()
		Label(self.rightsideholder, text='Bugs? Email jnorton2@skidmore.edu').pack(side='bottom')


	def setupLists(self, parent):
		self.listholder = Frame(parent)
		self.listholder.pack(fill='both', side='left', expand=True)
		self.checkedFiles =[s for s in os.listdir(config.SRCFILE_DIR) if hasBeenChecked(s)]
		self.uncheckedFiles =[s for s in os.listdir(config.SRCFILE_DIR) if not hasBeenChecked(s)]

		if len(self.uncheckedFiles) > 0:
			self.SELECTED = self.uncheckedFiles[0]
			self.SELECTED_INDEX = 0

		self.labelchecked = Label(self.listholder, text='Checked')
		self.labelchecked.pack()
		self.checkedlb = Listbox(self.listholder, selectmode='SINGLE')
		self.checkedlb.pack()

		self.labelunchecked = Label(self.listholder, text='Unchecked')
		self.labelunchecked.pack()
		self.uncheckedlb = Listbox(self.listholder, selectmode='SINGLE')
		self.uncheckedlb.pack(padx=5, pady=5)

		for f in self.checkedFiles:		
			self.checkedlb.insert(END, f)

		for f in self.uncheckedFiles:		
			self.uncheckedlb.insert(END, f)

	def setupScanner(self, parent):
		self.infoholder = Frame(parent)
		self.infoholder.pack(fill='both', side='left', expand=True)

		self.frame_middleInner = Frame(self.infoholder)
		self.frame_middleInner.pack(anchor='c', pady=5)

		self.titlelabel = Label(self.frame_middleInner, text='Source file:')
		self.titlelabel.pack()

		self.namelabel = Label(self.frame_middleInner, text='name')
		self.namelabel.pack()

		self.selectingButtonFrame = Frame(self.frame_middleInner)
		self.selectingButtonFrame.pack()
		self.b_next = Button(self.selectingButtonFrame, text='next', command=self.click_next, width=10).pack(side='right')
		self.b_prev = Button(self.selectingButtonFrame, text='previous', command=self.click_previous, width=10).pack(side='left')

		
	def setupMarkers(self, parent):
		self.rightsideholder=Frame(parent)
		self.rightsideholder.pack(fill='both', side='left', expand=True)

		self.b_show = Button(self.rightsideholder, text='show plot', command=self.click_show).pack(pady=10)
		self.b_accept = Button(self.rightsideholder, text='accept', command=self.click_accept).pack()

		self.markRadioButtonFrame = Frame(self.rightsideholder)
		self.selectedMark = StringVar()
		for mark in config.REJECT_MARKS:
			Radiobutton(self.markRadioButtonFrame, text=mark, variable=self.selectedMark, value=mark).pack(anchor = W)
		
		self.markRadioButtonFrame.pack()
		self.b_reject = Button(self.rightsideholder, bg='red', text='reject with reason ^', command=self.click_reject).pack()
		self.select(0)

		self.markingBadRegionFrame = Frame(self.rightsideholder)
		self.badRegionTopFrame = Frame(self.markingBadRegionFrame)
		self.badRegionBottomFrame = Frame(self.markingBadRegionFrame)

		Label(self.badRegionTopFrame, text='lower channel: ').pack(side='left', anchor = W)
		self.lowerChannel = StringVar()
		self.upperChannel = StringVar()
		self.e_lowerChannel = Entry(self.badRegionTopFrame, textvariable=self.lowerChannel).pack(side='right')

		Label(self.badRegionBottomFrame, text='upper channel: ').pack(side='left', anchor = W)
		self.e_upperChannel = Entry(self.badRegionBottomFrame,textvariable=self.upperChannel).pack(side='right')
		
		self.badRegionTopFrame.pack(side='top')
		self.badRegionBottomFrame.pack(side='top')
		self.markingBadRegionFrame.pack(pady=10)
		self.b_markBadRegion = Button(self.markingBadRegionFrame, text='Check bad regions', command=self.click_badRegions).pack()

	def showMessage(self, text):
		log(str(text))
		tkMessageBox.showinfo("Error", str(text))

	def click_badRegions(self):
		try:
			bri = self.getBadRegionInput()
			if bri:
				flagSrc(loadSource(self.SELECTED), bri[0], bri[1])
				self.select(self.SELECTED_INDEX)
			else:
				self.showMessage('Bad input, did not mark bad regions')

		except Exception as e:
			self.showMessage('Bad input, did not mark bad regions')
		

	def getBadRegionInput(self):
		lower = self.lowerChannel.get()
		upper = self.upperChannel.get()
		print lower
		print upper
		if self.isInt(lower) and self.isInt(upper) :
			return [int(lower),int(upper)]
		else:
			return []


	def isInt(self, s):
		try: 
			int(s)
			return True
		except ValueError:
			return False


	def click_refresh(self):
		try:
			clearAcceptRejectFiles()
			self.refresh()
		except Exception as e:
			log('Couldnt refresh ')
			self.showMessage('Refresh failed ')


	def click_show(self):
		try:
			showPlot(loadSource(self.SELECTED))
		except Exception as e:
			log('could not show plot for ' + self.SELECTED)
			self.showMessage('Could not show plot for ' + self.SELECTED)
			

	def click_accept(self):
		try:
			accept(loadSource(self.SELECTED))
			self.select(self.SELECTED_INDEX + 1)
		except Exception as e:
			log('could not accept source ' + self.SELECTED)
		
	def click_reject(self):
		try:
			mark = 'no reason'
			if self.selectedMark.get():
				mark = self.selectedMark.get()
				src = loadSource(self.SELECTED)
				markRejectWithReason(src, mark)
				self.select(self.SELECTED_INDEX + 1)

		except Exception as e:
			log(str(e))
			self.showMessage("Failed to mark with reject" + str(e))
	
	def click_next(self):
		try:
			if self.SELECTED_INDEX + 1 >= len(self.uncheckedFiles):
					print 'this is the last file'
			else:
				self.select(self.SELECTED_INDEX + 1)
		except Exception as e:
			log(str(e))
			self.showMessage("Couldnt go to next" + str(e))

	
	def click_previous(self):
		try:
			if self.SELECTED_INDEX == 0:
				print 'this is the first file'
			else: 
				self.select(self.SELECTED_INDEX - 1)
		except Exception as e:
			log(str(e))
			self.showMessage("Couldnt go to previous" + str(e))
		
		
		

	def refresh(self):
		try:
			#refresh lists
			self.checkedFiles =[s for s in os.listdir(config.SRCFILE_DIR) if hasBeenChecked(s) and s.endswith('.json')]
			self.uncheckedFiles =[s for s in os.listdir(config.SRCFILE_DIR) if not hasBeenChecked(s) and s.endswith('.json')]

			self.checkedlb.delete(0, END)
			self.uncheckedlb.delete(0, END)

			for f in self.checkedFiles:		
				self.checkedlb.insert(END, f)

			for f in self.uncheckedFiles:		
				self.uncheckedlb.insert(END, f)


			self.checkedlb.pack(padx=15, pady=15)
			self.uncheckedlb.pack(padx=15, pady=15)

			self.namelabel['text'] = self.SELECTED

			self.namelabel.pack()
		except Exception as e:
			self.showMessage("Couldnt refresh list")
		



	def select(self, index):
		self.refresh()
		try:
			self.SELECTED = self.uncheckedFiles[index]
			self.SELECTED_INDEX = index
			self.refresh()
		except Exception as e:
			if len(self.uncheckedFiles) > 0:
				self.select(0)
			else:
				self.SELECTED_INDEX = -1
				self.SELECTED = 'No source files left'
			self.refresh()
		



root = Tk()
root.title('Checkspectra')
root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT))
myapp = MyApp(root)
root.mainloop()

	


