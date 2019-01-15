import datetime, calendar

import sqlalchemy

import ReporterCaller as Reporter, EuroPrice

from tbooks.model.model import Session
from tbooks.model.model import Job, Invoice, Orderer, Customer, Payment, Supplier

iJOBS, iINVOICES, iORDERERS, iCUSTOMERS, iPAYMENTS, iSUPPLIERS, iVATINFO, iECSALES = range(8)

class DataModel():
	
	def __init__(self):
		
		self.cJobData = JobData(self)
		self.cInvoiceData = InvoiceData(self)
		self.cOrdererData = OrdererData(self)
		self.cCustomerData = CustomerData(self)
		self.cPaymentData = PaymentData(self)
		self.cSupplierData = SupplierData(self)
		self.cVATInfoData = VATInfoData(self)
		self.cECSalesData = ECSalesData(self)

		self.ItemData = {
			iJOBS: self.cJobData,
			iINVOICES: self.cInvoiceData,
			iORDERERS: self.cOrdererData,
			iCUSTOMERS: self.cCustomerData,
			iPAYMENTS: self.cPaymentData,
			iSUPPLIERS: self.cSupplierData,
			iVATINFO: self.cVATInfoData,
			iECSALES: self.cECSalesData }

	def Attach(self, observer):
		
		self.observer = observer
	
	def GetTableHeads(self, iDataSet):
		
		tViewHeads = self.ItemData[iDataSet].GetViewHeads()

		return tViewHeads
	
	def GetViewData(self, iDataSet):
		
		tViewData = self.ItemData[iDataSet].GetViewData()
		return tViewData
	
	def GetItemData(self, iDataSet, iNumber):
		
		tItemData = self.ItemData[iDataSet].GetItemData(iNumber)
		return tItemData
	

class JobData():
	
	def __init__(self, model):
		
		self.model = model
		self.session = Session()
		
	def GetViewHeads(self):
		
		return (
			('No.', 'int'), 
			('Orderer', 'text'), 
			('Customer Ref.', 'text'),
			('Task', 'text'), 
			('Quantity', 'float'), 
			('Billing Units', 'text'),
			('Description of Translated Document', 'text'),
			('Delivery Date', 'date'), 
			('Cncy', 'text'), 
			('Unit Price', 'decimal'),
			('Total Price', 'decimal'),	
			('Invoice No.', 'int'))

	def GetViewData(self):
		
		return [(job.Number,
				 job.Orderer.FamilyName,
				 job.CustOrderNo,
				 job.Task,
				 job.Quantity,
				 job.Units,
				 job.Description,
				 job.Delivered,
				 job.Currency,
				 job.UnitPrice,
				 job.UnitPrice * job.Quantity,
				 job.InvoiceNo)
				 for job in self.session.query(Job)]

	def GetItemData(self, iNumber):
		
		job = self.session.query(Job).filter(Job.Number == iNumber).one()
		return (job.Number,
				job.OrdererNo,
				job.CustOrderNo,
				job.Task,
				job.Quantity,
				job.Units,
				job.Description,
				job.Delivered,
				job.Currency,
				job.UnitPrice,
				job.InvoiceNo)

	def AddNew(self, tJob):
	
		job = Job(
			OrdererNo=tJob[0],
			CustOrderNo=tJob[1],
			Quantity=tJob[2],
			Units=tJob[3],
			Task=tJob[4],
			Description=tJob[5],
			Delivered=tJob[6],
			Currency=tJob[7],
			UnitPrice=tJob[8]
		)
		self.session.add(job)
		self.session.commit()
		self.model.observer.Update()

	def Update(self, iNumber, tJob):
	
		job = self.session.query(Job).filter(Job.Number == iNumber).one()
		job.OrdererNo = tJob[0]
		job.CustOrderNo = tJob[1]
		job.Quantity = tJob[2]
		job.Units = tJob[3]
		job.Task = tJob[4]
		job.Description = tJob[5]
		job.Delivered = tJob[6]
		job.Currency = tJob[7]
		job.UnitPrice = tJob[8]
		self.session.commit()
		self.model.observer.Update()


class InvoiceData():
	
	def __init__(self, model):
		
		self.model = model
		self.session = Session()
		
	def GetViewHeads(self):
		
		return (
			('Invoice No.', 'int'), 
			('Invoice Date', 'date'),
			('Customer Name', 'text'), 
			('Total Amount', 'decimal'), 
			('Cncy', 'text'), 
			('GBP Amt', 'decimal'),
			('VAT Code', 'text'), 
			('VAT', 'float'), 
			('Payment Date', 'date'))

	def GetViewData(self):
		
		query = self.session.query(
			Invoice.Number,
			Invoice.Date,
			Customer.Organization,
			sqlalchemy.sql.func.sum(Job.UnitPrice * Job.Quantity).label('Total'),
			Job.Currency,
			Customer.VATCode,
			Invoice.VAT,
			Invoice.Paid
		).join(Job).join(Orderer).join(Customer).group_by(Invoice.Number)

		result = [(invoice.Number,
				   invoice.Date,
				   invoice.Organization,
				   invoice.Total,
				   invoice.Currency,
				   invoice.VATCode,
				   invoice.VAT,
				   invoice.Paid)
				   for invoice in query]

		return [t[:5] + ((EuroPrice.GetGBPValue(t[3], t[1])
			if t[4] == 'EUR' else t[3]),) + t[5:] for t in result]

	def IsPaid(self, iNumber):
		
		invoice = self.session.query(Invoice).filter(Invoice.Number == iNumber).one()
		return invoice.Paid is not None
	
	def SetPaid(self, (iNumber, cDate)):

		invoice = self.session.query(Invoice).filter(Invoice.Number == iNumber).one()
		invoice.Paid = cDate
		self.session.commit()
		self.observer.Update()

	def AddNew(self, tInvoice):
		
		cReporter = Reporter.Reporter()
		
		sNumber, cDate, iCustomerNo, sVAT = tInvoice
		
		customer = self.session.query(Customer).filter(Customer.Number == iCustomerNo).one()
		tCustomerData = ([
			customer.Language,
			customer.Organization,
			customer.Title,
			customer.GivenName,
			customer.FamilyName,
			customer.Address1,
			customer.Address2,
			customer.Address3,
			customer.Address4,
			customer.Country,
			customer.VATIDNo])

		query = self.session.query(Job).join(Orderer).join(Customer)\
			.filter(Job.InvoiceNo == None)\
			.filter(Customer.Number == iCustomerNo)\
			.order_by(Job.Number).limit(5)

		result = [(job.Number,
				   job.CustOrderNo,
				   job.Quantity,
				   job.Units,
				   job.Description,
				   job.Delivered,
				   job.UnitPrice)
				   for job in query]

		tJobData = zip(*result)

		cReporter.PostInvoice(sNumber, cDate, tCustomerData, tJobData)

		# Create invoice, add to database, and update corresponding jobs.
		# Note: Will crash if invoice number has already been used!

		invoice = Invoice(Number=sNumber, Date=cDate, VAT=sVAT)
		self.session.add(invoice)
		for iJobNo in tJobData[0]:
			job = self.session.query(Job).filter(Job.Number == iJobNo).one()
			job.InvoiceNo = sNumber
		self.session.commit()
		self.model.observer.Update()
	

class OrdererData():
	
	def __init__(self, model):
		
		self.model = model
		self.session = Session()

	def GetViewHeads(self):
		
		return (
			('No.', 'int'), 
			('Family Name', 'text'), 
			('Given Name', 'text'),
			('Title', 'text'), 
			('Customer Name', 'text'), 
			('Email Address', 'text'))

	def GetViewData(self):
		
		return [(orderer.Number,
				 orderer.FamilyName,
				 orderer.GivenName,
				 orderer.Title,
				 orderer.Customer.Organization,
				 orderer.EmailAddress)
				 for orderer in self.session.query(Orderer)]

	def GetItemData(self, iNumber):
		
		orderer = self.session.query(Orderer).filter(Orderer.Number == iNumber).one()
		return (orderer.Number,
				orderer.FamilyName,
				orderer.GivenName,
				orderer.Title,
				orderer.CustomerNo,
				orderer.EmailAddress)

	def GetList(self):
		
		return [(orderer.Number,
				 orderer.Customer.Organization,
				 orderer.FamilyName,
				 orderer.GivenName)
				 for orderer in self.session.query(Orderer).order_by(Orderer.Customer.Organization)]

	def GetCustomerNo(self, iOrdererNo):
		
		return self.session.query(Orderer).filter(Orderer.Number == iOrdererNo).one().CustomerNo
		
	def AddNew(self, tOrderer):
	
		orderer = Orderer(
			FamilyName=tOrderer[0],
			GivenName=tOrderer[1],
			Title=tOrderer[2],
			CustomerNo=tOrderer[3],
			EmailAddress=tOrderer[4]
		)
		self.session.add(orderer)
		self.session.commit()
		self.model.observer.Update()

	def Update(self, iNumber, tOrderer):
	
		orderer = self.session.query(Orderer).filter(Orderer.Number == iNumber).one()
		orderer.FamilyName = tOrderer[0]
		orderer.GivenName = tOrderer[1]
		orderer.Title = tOrderer[2]
		orderer.CustomerNo = tOrderer[3]
		orderer.EmailAddress = tOrderer[4]
		self.session.commit()
		self.model.observer.Update()


class CustomerData():
	
	def __init__(self, model):
		
		self.model = model
		self.session = Session()
		
	def GetViewHeads(self):
		
		return (
			('No.', 'int'), 
			('Organization', 'text'),
			('Address Line 1', 'text'), 
			('Address Line 2', 'text'), 
			('Address Line 3', 'text'),
			('Address Line 4', 'text'), 
			('Country', 'text'), 
			('Language', 'text'), 
			('VAT Code', 'text'),
			('VAT ID No', 'text'), 
			('Family Name', 'text'), 
			('Given Name', 'text'),
			('Title', 'text'))

	def GetViewData(self):
		
		return [self._astuple(customer) for customer in self.session.query(Customer)]

	def GetItemData(self, iNumber):
		
		return self._astuple(self.session.query(Customer).filter(Customer.Number == iNumber).one())

	def GetOrderers(self, iNumber):
		
		return [(orderer.Number, orderer.FamilyName, orderer.GivenName, orderer.Title)
				for orderer in self.session.query(Orderer).filter(Orderer.CustomerNo == iNumber)]
		
	def _astuple(self, customer):

		return (customer.Number,
				customer.Organization,
				customer.Address1,
				customer.Address2,
				customer.Address3,
				customer.Address4,
				customer.Country,
				customer.Language,
				customer.VATCode,
				customer.VATIDNo,
				customer.FamilyName,
				customer.GivenName,
				customer.Title)

	def GetList(self):
		
		return [(customer.Number, customer.Organization)
				for customer in self.session.query(Customer).order_by(Customer.Organization)]

	def GetUninvoiced(self):
		
		customers = self.session.query(Customer).join(Orderer).join(Job).filter(Job.InvoiceNo == None).distinct()
		return [(customer.Number, customer.Organization) for customer in customers]
		
	def AddNew(self, tCustomer):
	
		customer = Customer(
			Organization=tCustomer[0],
			Address1=tCustomer[1],
			Address2=tCustomer[2],
			Address3=tCustomer[3],
			Address4=tCustomer[4],
			Country=tCustomer[5],
			Language=tCustomer[6],
			VATCode=tCustomer[7],
			VATIDNo=tCustomer[8],
			FamilyName=tCustomer[9],
			GivenName=tCustomer[10],
			Title=tCustomer[11])
		self.session.add(customer)
		self.session.commit()
		self.model.observer.Update()

	def Update(self, iNumber, tCustomer):
	
		customer = self.session.query(Customer).filter(Customer.Number == iNumber).one()
		customer.Organization = tCustomer[0]
		customer.Address1 = tCustomer[1]
		customer.Address2 = tCustomer[2]
		customer.Address3 = tCustomer[3]
		customer.Address4 = tCustomer[4]
		customer.Country = tCustomer[5]
		customer.Language = tCustomer[6]
		customer.VATCode = tCustomer[7]
		customer.VATIDNo = tCustomer[8]
		customer.FamilyName = tCustomer[9]
		customer.GivenName = tCustomer[10]
		customer.Title = tCustomer[11]
		self.session.commit()
		self.model.observer.Update()


class PaymentData():
	
	def __init__(self, model):
		
		self.model = model
		self.session = Session()

	def GetViewHeads(self):
		
		return (
			('No.', 'int'), 
			('Payment Date', 'date'), 
			('Supplier Name', 'text'),
			('Description of Product or Service', 'text'), 
			('Cncy', 'text'), 
			('Amount', 'decimal'),
			('GBP Amt', 'decimal'),	
			('VAT', 'float'))

	def GetViewData(self):
		
		payments = self.session.query(Payment).order_by(Payment.Date).all()
		result = [self._astuple(payment) for payment in payments]
		return [t[:6] + ((EuroPrice.GetGBPValue(t[5], t[1])
			if t[4] == 'EUR' else t[5]),) + t[6:] for t in result]

	def GetItemData(self, iNumber):
		
		return self._astuple(self.session.query(Payment).filter(Payment.Number == iNumber).one())

	def _astuple(self, payment):

		return (payment.Number,
				payment.Date,
				payment.Supplier.Name,
				payment.Product,
				payment.Currency,
				payment.Amount,
				payment.VAT)

	def AddNew(self, tPayment):
	
		payment = Payment(Date=tPayment[0],
						  SupplierNo=tPayment[1],
						  Product=tPayment[2],
						  Currency=tPayment[3],
						  Amount=tPayment[4],
						  VAT=tPayment[5])
		self.session.add(payment)
		self.session.commit()
		self.model.observer.Update()

	def Update(self, iNumber, tPayment):
	
		payment = self.session.query(Payment).filter(Payment.Number == iNumber).one()
		payment.Date = tPayment[0]
		payment.SupplierNo = tPayment[1]
		payment.Product = tPayment[2]
		payment.Currency = tPayment[3]
		payment.Amount = tPayment[4]
		payment.VAT = tPayment[5]
		self.session.commit()
		self.model.observer.Update()


class SupplierData():
	
	def __init__(self, model):

		self.model = model
		self.session = Session()

	def __del__(self):

		self.session.close()

	def GetViewHeads(self):
		
		return (('No.', 'int'), ('Supplier Name', 'text'))

	def GetViewData(self):
		
		return [self._astuple(supplier) for supplier in self.session.query(Supplier)]

	def GetItemData(self, iNumber):
		
		return self.session.query(Supplier).filter(Supplier.Number == iNumber).one().Name,

	def GetList(self):
		
		return [self._astuple(supplier) for supplier in self.session.query(Supplier).order_by(Supplier.Name)]

	def _astuple(self, supplier):

		return supplier.Number, supplier.Name

	def AddNew(self, tSupplier):
	
		supplier = Supplier(Name=tSupplier[0])
		self.session.add(supplier)
		self.session.commit()
		self.model.observer.Update()

	def Update(self, iNumber, tSupplier):
	
		supplier = self.session.query(Supplier).filter(Supplier.Number == iNumber).one()
		supplier.Name = tSupplier[0]
		self.session.commit()
		self.model.observer.Update()


class VATInfoData():
	
	def __init__(self, model):
		
		self.session = Session()

	def GetHeadings(self):
		
		return (
			('Period', 'text'), 
			('VAT (Sales)', 'decimal'), 
			('VAT (EC Acqns)', 'decimal'),
			('VAT Due', 'decimal'),	
			('VAT Reclaimed', 'decimal'), 
			('Net VAT', 'decimal'),
			('Total Sales', 'decimal'), 
			('Purchases', 'decimal'), 
			('EC Supplies', 'decimal'),
			('EC Acquns', 'decimal'))
	
	def GetItems(self):
		
		lVATInfoData = []
		
		for iPeriod in range(1, self.GetFinalVATReturnNumber()):
		
			iEndYear, iEndMonth = self.GetVATReturnPeriod(iPeriod)
			
			iStartYear = iEndYear
			iStartMonth = iEndMonth - 2
			if iStartMonth < 1:
				iStartYear -= 1
				iStartMonth = iStartMonth + 12
			
			cStartDate = datetime.date(iStartYear, iStartMonth, 1)
			cEndDate = datetime.date(iEndYear, iEndMonth, calendar.monthrange(iEndYear, iEndMonth)[1])
			
			query = self.session.query(
				Invoice.Date,
				Job.Currency,
				sqlalchemy.func.sum(sqlalchemy.cast(Job.Quantity * Job.UnitPrice, sqlalchemy.Numeric(10, 2))).label('Total'),
				(Invoice.VAT / 100).label('VAT')
			).join(Job).filter(Invoice.Date.between(cStartDate, cEndDate)).group_by(Invoice.Number)
			result = [(record.Date, record.Currency, record.Total, record.VAT) for record in query]

			fSales, fSalesVAT = self.GetTotals(result)
			
			query = self.session.query(
				Payment.Date,
				Payment.Currency,
				Payment.Amount,
				(Payment.VAT / 100).label('VAT')
			).filter(Payment.Date.between(cStartDate, cEndDate))
			result = [(record.Date, record.Currency, record.Amount, record.VAT) for record in query]

			fPurchases, fPurchasesVAT = self.GetTotals(result)
				
			lVATInfo = [None] * 10
			lVATInfo[0] = '%02d %02d' % (iEndMonth, iEndYear % 100)
			lVATInfo[1] = fSalesVAT
			lVATInfo[2] = 0.0
			lVATInfo[3] = lVATInfo[1] + lVATInfo[2]
			lVATInfo[4] = fPurchasesVAT
			lVATInfo[5] = lVATInfo[3] - lVATInfo[4]
			lVATInfo[6] = fSales
			lVATInfo[7] = fPurchases
			lVATInfo[8] = 0.0
			lVATInfo[9] = 0.0
			
			lVATInfoData.append(tuple(lVATInfo))
		
		return lVATInfoData
	
	def GetFinalVATReturnNumber(self):
		
		today = datetime.date.today()
		return (12 * (today.year - 2008) + (today.month - 8)) / 3 + 1

	def GetVATReturnPeriod(self, iNumber):
	
		iEndYear = 2008 + (iNumber + 2) / 4
		iEndMonth = ((iNumber + 2) % 4) * 3 + 1
		
		return iEndYear, iEndMonth

	def GetTotals(self, tItems):
		
		fTotal = 0.0
		fTotalVAT = 0.0
		for cDate, sCurrency, fValue, fVAT in tItems:
			if sCurrency == 'GBP':
				fGBPValue = float(fValue)
			elif sCurrency == 'EUR':
				fGBPValue = EuroPrice.GetGBPValue(float(fValue), cDate)
			else:
				assert False
			fTotal    += fGBPValue
			fTotalVAT += fGBPValue * fVAT
		return fTotal, fTotalVAT


# Provides data for EC Sales page in a format matching that required for HMRC

class ECSalesData():

	def __init__(self, model):

		self.session = Session()

	def GetHeadings(self):

		return (('Period', 'date'), ('VAT Reg. No.', 'text'), ('Total Value', 'decimal'))

	# Returns list of invoice totals in GBP grouped by quarter and VAT ID No for display

	def GetItems(self):

		query = self.session.query(
			Invoice.Date,
			Customer.VATIDNo,
			Job.Currency,
			sqlalchemy.func.sum(Job.Quantity * Job.UnitPrice).label('Total'))\
			.join(Job).join(Orderer).join(Customer).group_by(Invoice.Number)
		records = []
		for invoice in query:
			period = self._quarter_from_date(invoice.Date)
			vatidno = invoice.VATIDNo
			total = invoice.Total
			if invoice.Currency == 'GBP':
				pass
			elif invoice.Currency == 'EUR':
				total = EuroPrice.GetGBPValue(total, invoice.Date)
			else:
				assert False
			for record in records:
				if record[0] == period and record[1] == vatidno:
					record[2] += total
					break
			else:
				records.append([period, vatidno, total])

		return records

	# Returns quarter in format "mm/yy" for date object, where mm is number of final month in quarter.

	def _quarter_from_date(self, date):

		return "{:02d}/{:02d}".format(((date.month - 1) / 3 + 1) * 3, date.year % 100)
