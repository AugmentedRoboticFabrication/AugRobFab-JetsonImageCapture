import os, time, shutil
from configargparse import ArgParser
import RPi.GPIO as GPIO
import open3d as o3d

class azureKinectMKVRecorder:
	def __init__(self, fn, gui, rec_config):
		print('---------------')
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
		self.root = os.getcwd()
		self.out_dir = None

		if not os.path.exists('%s/out' % self.root):
			os.mkdir('%s/out' % self.root)
		
		# External Backup Config
		self.copy_root = None
		mediaList = os.listdir('/media/nano')
		if 'L4T-README' in mediaList:
			mediaList.remove('L4T-README')
		if len(mediaList) == 0:
			print('No External USB storage device found. Falling back to CWD.')
		elif len(mediaList) == 1:
			self.copy_root = '/media/nano/%s' % mediaList[0]
			print('Found External USB storage device for backup: %s.' % mediaList[0])
		else:
			print('Multiple External USB storage devices found. Falling back to CWD.')
		print('---------------')
		
		#Azure Config
		self.rec_config = o3d.io.read_azure_kinect_sensor_config('%s/%s' % (self.root, rec_config))
		
		self.recorder = o3d.io.AzureKinectRecorder(self.rec_config, 0)
		if not self.recorder.init_sensor():
			raise RuntimeError('Failed to connect to sensor.')
		
		self.align = True

	def start(self):
			self.out_dir = self.fn + '_%d' % round(time.time())
			if not self.recorder.is_record_created():
				if not os.path.exists('%s/out/%s' % (self.root,self.out_dir)):
					os.mkdir('%s/out/%s' % (self.root,self.out_dir))
				self.recorder.open_record('%s/out/%s/capture.mkv' % (self.root,self.out_dir))
			print('Starting Recording: %s' % self.out_dir)

	def end(self):
		if self.recorder.is_record_created():
			self.recorder.close_record()
			# Copy capture to external USB storage device
			if self.copy_root is not None:
				print("Backing up capture to %s..."% self.copy_root, end="")
				if os.path.exists(self.copy_root):
					shutil.copytree('%s/out/%s' % (self.root, self.out_dir),
								'%s/%s' % (self.copy_root, self.out_dir))
					print("Done!")
				else:
					print("Failed!")
		
		if self.gui:
			self.vis.clear_geometries()
			self.vis.close()
		
		self.counter = 0
		self.out_dir = None

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
		self.counter+=1

	def exit(self, vis):
		self.isRunning = False

		return False

##############################################################################

	def run(self):
		if self.gui:
			self.vis.register_key_callback(256, self.exit)

			self.vis.create_window("Augmented Fabrication | ForMat Lab")
		
		try:
			pin15 = GPIO.input(15)
			pin16 = GPIO.input(16)
			if self.gui:
				print('Press ESC or CTRL+C to exit.')
			else:
				print('CTRL+C to exit.')
			while self.isRunning:
				curPin15 = GPIO.input(15)
				curPin16 = GPIO.input(16)

				if self.gui:
					self.vis.poll_events()
				if self.isRecording:
					# if pin15 0->1 | DO 1->0 (end recording)
					if not pin15 and curPin15:
						self.end()
						self.isRecording = False

					# if pin15=0 | DO 1 && pin16 1->0 (capture frame)
					if not curPin15 and (pin16 and not curPin16):
						self.frame()
				else:
					# if pin15 1->0 | DO 0->1 (start recording)
					if pin15 and not curPin15:
						print('---------------')
						self.start()
						self.isRecording = True

				pin15 = curPin15
				pin16 = curPin16

				time.sleep(.1)
			GPIO.cleanup()
			print('Bye!')

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

	config = parser.parse_args()

	recorder = azureKinectMKVRecorder(config.fn, config.gui, config.rec_config)
	recorder.run()

