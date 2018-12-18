import subprocess, pickle

class Reporter:

	def PostInvoice(self, sNumber, sISOInvDate, tCustomerData, tJobData):
	
		f = open('tbooks/logic/temp.buf', 'wb')
		pickle.dump((sNumber, sISOInvDate, tuple(tCustomerData), tuple(tJobData)), f)
		f.close()
		
		subprocess.call(['python3', 'tbooks/logic/ReporterLauncher.py'])

