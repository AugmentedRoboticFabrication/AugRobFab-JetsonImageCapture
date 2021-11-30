import os, time
from configargparse import ArgParser
import RPi.GPIO as GPIO
import open3d as o3d

class azureKinectMKVRecorder:
	def __init__(self, fn, gui, rec_config, out_dir):
		# GPIO config
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(15, GPIO.IN)
		GPIO.setup(16, GPIO.IN)

		#Global variables
		self.isRunning = True
		self.isRecording = False
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

	def start(self):
			fn = self.fn + '_%d' % round(time.time())
			if not self.recorder.is_record_created():
				if not os.path.exists('{}/{}'.format(self.dir,fn)):
					os.mkdir('{}/{}'.format(self.dir,fn))
				self.recorder.open_record("{}/{}/capture.mkv".format(self.dir,fn))
			print('%s recording started' % fn)
	def end(self):
		if self.recorder.is_record_created():
			self.recorder.close_record()
		if self.gui:
			self.vis.clear_geometries()
			self.vis.close()
		self.counter = 0
		return False

	def frame(self):
		print("Recording frame %03d..."%self.counter, end="")
		rgbd = self.recorder.record_frame(True,self.align)
		print("Done!")
		
		if self.gui:
			if self.counter == 0:
				self.vis.add_geometry(rgbd)

			self.vis.update_geometry(rgbd)
			self.vis.update_renderer()

	def exit(self, vis):
		self.isRunning = False

		self.counter+=1
		return False

##############################################################################

	def run(self):
		if self.gui:
			self.vis.register_key_callback(256, self.exit)

			self.vis.create_window()
		
		try:
			pin15 = GPIO.input(15)
			pin16 = GPIO.input(16)
			
			print('*Waiting for DO Signal*')
			while self.isRunning:
				curPin15 = GPIO.input(15)
				curPin16 = GPIO.input(16)

				if self.gui:
					self.vis.poll_events()
				if self.isRecording:
					# if pin15 0->1 | DO 1->0 (end recording)
					if not pin15 and curPin15:
						self.end(None)
						self.isRecording = False

					# if pin15=0 | DO 1 && pin16 1->0 (capture frame)
					if not curPin15 and (pin16 and not curPin16):
						self.frame(None)
				else:
					# if pin15 1->0 | DO 0->1 (start recording)
					if pin15 and not curPin15:
						print('---------------')
						self.start()
						self.isRecording = True

				pin15 = curPin15
				pin16 = curPin16

				time.sleep(.1)

		except KeyboardInterrupt:
			GPIO.cleanup()
			print('\nBye!')
		except Exception as e:
			GPIO.cleanup()
			print(e)

if __name__ == '__main__':
	parser = ArgParser()
	parser.add('--fn', default='capture')
	parser.add('--gui', action='store_true')
	parser.add('--rec_config', help='relative path to rec_config.json file.', default='rec_config.json')
	parser.add('--out_dir', default=None)

	config = parser.parse_args()

	recorder = azureKinectMKVRecorder(config.fn, config.gui, config.rec_config, config.out_dir)
	recorder.run()

