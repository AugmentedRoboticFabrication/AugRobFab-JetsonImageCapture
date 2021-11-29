import os
from configargparse import ArgParser

import open3d as o3d

class Recorder:
	def __init__(self, gui, rec_config):
		self.counter = 0

		# OS Variables
		self.dir = os.getcwd()

		# O3D Config 
		self.gui = gui
		if self.gui:
			self.vis = o3d.visualization.VisualizerWithKeyCallback()

		# Azure Kinect Config
		self.rec_config = o3d.io.read_azure_kinect_sensor_config('{}/{}'.format(self.dir, rec_config))

		
		self.recorder = o3d.io.AzureKinectRecorder(self.rec_config, 0)
		if not self.recorder.init_sensor():
			raise RuntimeError('Failed to connect to sensor.')
		
		self.align = True

	def start(self, fn):
		print('Initiating Recorder...', end='')
		if not self.recorder.is_record_created():
			if not os.path.exists('{}/{}'.format(self.dir,fn)):
				os.mkdir('{}/{}'.format(self.dir,fn))
			if self.recorder.open_record('{}/{}/capture.mkv'.format(self.dir,fn)):
				print('Success!')
			else:
				print('Fail!')
				# raise RuntimeError('Failed to open MKV file.')
		else:
			print('Fail!')
			# raise RuntimeError('Another recording is already open.')

	def recordFrame(self):
		print('Recording frame %03d...'% self.counter, end='')
		if not self.recorder.is_record_created():
			print('Fail!')
			# raise RuntimeError('No created recording.')
		
		rgbd = self.recorder.record_frame(True,self.align)
		print('Success!')
		
		if self.gui:
			if self.counter == 0:
				self.vis.add_geometry(rgbd)

			self.vis.update_geometry(rgbd)
			self.vis.update_renderer()

		self.counter += 1

		return True

	def end(self):
		print('Saving recording...', end='')
		if self.recorder.is_record_created():
			self.recorder.close_record()
			print('Success!')
		else:
			print('Fail!')
			# raise RuntimeError('No created recording.')
