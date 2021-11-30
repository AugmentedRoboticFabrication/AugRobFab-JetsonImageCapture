import os, datetime, keyboard
from configargparse import ArgParser

import open3d as o3d

class azureKinectMKVRecorder:
	def __init__(self, fn, gui, rec_config, out_dir):
		#Global variables
		self.exit = False
		self.record = False
		self.counter = 0
		
		#GUI
		self.gui = gui
		if self.gui:
			self.vis = o3d.visualization.VisualizerWithKeyCallback()

		#OS variables
		self.fn = fn
		self.dir = os.getcwd()
		self.abspath = "{}/{}".format(self.dir,self.fn)

		if not os.path.exists(self.abspath):
			os.mkdir(self.abspath)
		
		#Azure Config
		self.rec_config = o3d.io.read_azure_kinect_sensor_config('{}/{}'.format(self.dir, rec_config))

		
		self.recorder = o3d.io.AzureKinectRecorder(self.rec_config, 0)
		if not self.recorder.init_sensor():
			raise RuntimeError('Failed to connect to sensor')
		
		self.align = True


	def exit_callback(self, vis):
		if self.recorder.is_record_created():
			self.recorder.close_record()
			self.record = False
		self.exit = True
		return False

	def record_callback(self, vis):
		if not self.recorder.is_record_created():
			if self.recorder.open_record("{}/{}/capture.mkv".format(self.dir,self.fn)):
				self.record = True

		print("Recording frame %03d..."%self.counter, end="")
		rgbd = self.recorder.record_frame(True,self.align)
		print("Done!")
		
		if self.gui:
			if self.counter == 0:
				self.vis.add_geometry(rgbd)

			self.vis.update_geometry(rgbd)
			self.vis.update_renderer()

		

		self.counter+=1
		return False

##############################################################################

	def run(self):
		if self.gui:
			self.vis.register_key_callback(32, self.record_callback)
			self.vis.register_key_callback(256, self.exit_callback)

			self.vis.create_window()#'recorder', 1920, 540)

		while not self.exit:
			if self.gui:
				self.vis.poll_events()
		self.recorder.close_record()

if __name__ == '__main__':
	parser = ArgParser()
	parser.add('--fn', default='capture_{date:%Y-%m-%d-%H-%M-%S}'.format(date=datetime.datetime.now()))
	parser.add('--gui', action='store_true')
	parser.add('--rec_config', help='relative path to rec_config.json file.', default='rec_config.json')
	parser.add('--out_dir', default=None)

	config = parser.parse_args()

	recorder = azureKinectMKVRecorder(config.fn, config.gui, config.rec_config, config.out_dir)
	recorder.run()

