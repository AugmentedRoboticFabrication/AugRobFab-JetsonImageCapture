import time, os
from configargparse import ArgParser
import RPi.GPIO as GPIO
import open3d as o3d
# from azureKinectMKVRecorder import Recorder

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
				self.vis_geometry_added = True
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

if __name__ == '__main__':
	parser = ArgParser()
	parser.add('--fn', default='capture')
	parser.add('--gui', action='store_true')
	parser.add('--rec_config', help='relative path to rec_config.json file.', default='rec_config.json')
	parser.add('--out_dir', default=None)
	
	config = parser.parse_args()

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(15, GPIO.IN)
	GPIO.setup(16, GPIO.IN)
	
	try:
		isRecording = False
		recorder = Recorder(config.gui, config.rec_config)

		pin15 = GPIO.input(15)
		pin16 = GPIO.input(16)

		print('Waiting for DO signal to start recording...')
		while True:
			curPin15 = GPIO.input(15)
			curPin16 = GPIO.input(16)

			if isRecording:
				# if pin15 0->1 | DO 1->0 (end recording)
				if not pin15 and curPin15:
					recorder.end()
					isRecording = False
					print('---------------')

				# if pin15=0 | DO 1 && pin16 1->0 (capture frame)
				if not curPin15 and (pin16 and not curPin16):
					recorder.recordFrame()
			else:
				# if pin15 1->0 | DO 0->1 (start recording)
				if pin15 and not curPin15:
					fn = config.fn + '_%d' % round(time.time())
					recorder.start(fn)
					isRecording = True

			pin15 = curPin15
			pin16 = curPin16

			time.sleep(.1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		print('\nKeyboard Interrupt.')
	except Exception as e:
		GPIO.cleanup()
		print(e)