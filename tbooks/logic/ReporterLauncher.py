import pickle
import Reporter

f = open('tbooks/logic/temp.buf', 'rb')
sNumber, sISOInvDate, tCustomerData, tJobData = pickle.load(f, encoding='bytes')
f.close()

reporter = Reporter.Reporter()
reporter.PostInvoice(sNumber, sISOInvDate, tCustomerData, tJobData)

