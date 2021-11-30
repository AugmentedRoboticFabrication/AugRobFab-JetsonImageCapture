import os
from configargparse import ArgParser

import open3d as o3d

class Recorder:
	def __init__(self, gui, rec_config):
		self.counter = 0
		self.gui = gui
		self.vis = None
		self.vis_geometry_added = False

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
		if self.gui:
			self.vis = o3d.visualization.VisualizerWithKeyCallback()
			self.vis.create_window("Azure Kinect")

		if not self.recorder.is_record_created():
			if not os.path.exists('{}/{}'.format(self.dir,fn)):
				os.mkdir('{}/{}'.format(self.dir,fn))
			self.recorder.open_record('{}/{}/capture.mkv'.format(self.dir,fn))

		

	def recordFrame(self):
		print('Recording frame %03d...'% self.counter, end='')		
		rgbd = self.recorder.record_frame(True,self.align)
		print('Done!')
		
		if self.gui:
			if not self.vis_geometry_added:
				self.vis.add_geometry(rgbd)
			else:
				self.vis.update_geometry(rgbd)
			self.vis.update_renderer()

		self.counter += 1

		return True

	def end(self):
		if self.recorder.is_record_created():
			self.recorder.close_record()
		
		if self.gui:
			self.vis.destroy_window()
			self.vis = None
		
		self.counter = 0
		
