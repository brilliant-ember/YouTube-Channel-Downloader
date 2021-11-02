import logging
from utils import get_now_date


class Log:

	def __init__(self, log_file_path):
		logging.basicConfig(filename=log_file_path, format='%(levelname)s - %(message)s', level=logging.INFO)
	def log(self, msg:str, level="info", print_log=True) -> None:
		#TODO add more log levels like debug, warn , critical ...etc
		level = level.lower()
		msg = f'{get_now_date()} - {msg}'
		# print(msg, level)
		if level=="info":
			logging.info(msg)
		elif level == "error":
			logging.error(msg)
		elif level == "warn" or level == "warning":
			logging.warning(msg)
		else:
			print ("unknown level, will default to info")
			logging.warn("Passed error level is not good, will use info level to print next log entry")
			logging.info(msg)

		if print_log:
			print(msg)
	def exit(self):
		self.log("Exiting", print_log=True)
		logging.shutdown()
