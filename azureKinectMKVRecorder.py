import os
from configargparse import ArgParser

import open3d as o3d

class Recorder:
	def __init__(self, gui, rec_config):
		self.counter = 0
		self.gui = gui
		# self.vis = None

		# OS Variables
		self.dir = os.getcwd()

		# Azure Kinect Config
		self.rec_config = o3d.io.read_azure_kinect_sensor_config('{}/{}'.format(self.dir, rec_config))

		
		self.recorder = o3d.io.AzureKinectRecorder(self.rec_config, 0)
		if not self.recorder.init_sensor():
			raise RuntimeError('Failed to connect to sensor.')
		
		self.align = True

	def start(self, fn):
		self.counter = 0
		# if self.gui:
			# self.vis = o3d.visualization.Visualizer()
			
			# self.vis.create_window()

			# rgbd = self.recorder.record_frame(False, self.align)
			# self.vis.add_geometry(rgbd)

		if not self.recorder.is_record_created():
			if not os.path.exists('{}/{}'.format(self.dir,fn)):
				os.mkdir('{}/{}'.format(self.dir,fn))
			self.recorder.open_record('{}/{}/capture.mkv'.format(self.dir,fn))

		

	def frame(self, record=True):
		print('Recording frame %03d...'% self.counter, end='')		
		rgbd = self.recorder.record_frame(record, self.align)
		print('Done!')
		
		if record:
			self.counter += 1
		
		# if self.gui:
		# 	self.vis.update_geometry(rgbd)
		# 	self.vis.update_renderer()

		return rgbd

	def end(self):
		if self.recorder.is_record_created():
			self.recorder.close_record()
		
		# if self.gui:
		# 	self.vis.destroy_window()
		# 	self.vis = None
		
