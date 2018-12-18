#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import gettext
import sys, os

cLangDE = gettext.translation('TBooks', os.path.join(sys.path[0], '../../locale') , languages=['de'])

from urllib.parse import urljoin
from datetime import datetime
from time import sleep, strptime

import loutils
import unohelper 

sInvoiceURL = unohelper.systemPathToFileUrl('~/Documents/Translation/Invoices/')

class Reporter:
	
	def __init__(self):
		
		self.oLOR = loutils.LORunner()

	def PostInvoice(self, sNumber, cDate, tCustomerData, tJobData):

		sLang, sCompanyName, sTitle, sGivenName, sFamilyName, sAddr1, sAddr2, sAddr3, sAddr4, sCountryCode, sVATIDNo = tCustomerData
		tJobNos, tCustOrderNos, tJobQtys, tJobUnits, tJobDescs, tJobDlyDates, tJobRates = tJobData
			
		sCountry = {'GB': '', 'DE': 'Germany', 'LU': 'Luxembourg', 'IT': 'Italy'}[sCountryCode]
		
		_ = cLangDE.gettext if sLang == 'DE' else lambda s: s

		cDesktop = self.oLOR.connect()
		sTemplate = _('Invoice') + '.ots'
		cDocument = cDesktop.loadComponentFromURL(urljoin(sInvoiceURL, sTemplate),
			'_default', 0, ())
			
		sInvoiceID = 'T%08i' % int(sNumber)
		sSalutation = _('Dear Sir/Madam') + ','
		sDeliveryDateText = _('I respectfully request payment for the following translation work:')

		cSpreadsheet = cDocument.getSheets().getByIndex(0)
		cSpreadsheet.getCellByPosition(5, 14).setFormula(sInvoiceID)
		cSpreadsheet.getCellByPosition(5, 15).setFormula(cDate.isoformat())
		cSpreadsheet.getCellByPosition(0, 4).setFormula(sCompanyName)
		if sTitle:
			cSpreadsheet.getCellByPosition(0, 6).setFormula('%s %s %s' \
				% (sTitle, sGivenName, sFamilyName))
			iRow = 7
		else:
			iRow = 6
		if sAddr1: cSpreadsheet.getCellByPosition(0, iRow).setFormula(sAddr1); iRow += 1
		if sAddr2: cSpreadsheet.getCellByPosition(0, iRow).setFormula(sAddr2); iRow += 1
		if sAddr3: cSpreadsheet.getCellByPosition(0, iRow).setFormula(sAddr3); iRow += 1
		if sAddr4: cSpreadsheet.getCellByPosition(0, iRow).setFormula(sAddr4); iRow += 1
		if sCountry: cSpreadsheet.getCellByPosition(0, iRow).setFormula(sCountry)
		
		if sVATIDNo: cSpreadsheet.getCellByPosition(2, 14).setFormula(sVATIDNo)
		
		cSpreadsheet.getCellByPosition(0, 19).setFormula(sSalutation)
		cSpreadsheet.getCellByPosition(0, 21).setFormula(sDeliveryDateText)
		
		for iItem in range(len(tJobDescs)):
			if iItem > 0:
				cSpreadsheet.getRows().insertByIndex(24 + iItem, 1)
				cSpreadsheet.getCellRangeByPosition(2, 24 + iItem, 3, 24 + iItem).merge(True)
			cSpreadsheet.getCellByPosition(0, 24 + iItem).setFormula(iItem + 1)
			cSpreadsheet.getCellByPosition(1, 24 + iItem).setFormula(tJobQtys[iItem])
			sJobDlyDate = tJobDlyDates[iItem].strftime('%d.%m.%y')
			sJobDescription = tJobUnits[iItem] + ', ' + tCustOrderNos[iItem] + ', ' + _('del.') + ' ' + sJobDlyDate + ':\n' + tJobDescs[iItem]
			cSpreadsheet.getCellByPosition(2, 24 + iItem).setFormula(sJobDescription)
			cSpreadsheet.getCellByPosition(4, 24 + iItem).setFormula(float(tJobRates[iItem]))
			cSpreadsheet.getCellByPosition(5, 24 + iItem).setFormula('=B%d*E%d' % (25 + iItem,
				25 + iItem))
		cSpreadsheet.getCellByPosition(5, 25 + iItem).setFormula('=SUM(F25:F%d)' % (25 + iItem))
		
		sAccIDText = _('Account number') + ':'
		sBnkIDText = _('Bank sort code') + ':'
		if sCountryCode == 'GB':
			sBankName = 'The Cooperative Bank'
			sAccIDVal = '11045465'
			sBnkIDVal = '08-93-00'
		else:
			sBankName = 'Postbank Dortmund'
			if sCountryCode == 'DE':
				sAccIDVal = '495 465 464'
				sBnkIDVal = '440 100 46'
			elif sCountryCode in ('LU', 'IT'):
				sAccIDText = 'IBAN:'
				sBnkIDText = 'BIC:'
				sAccIDVal = 'DE56 4401 0046 0495 4654 64'
				sBnkIDVal = 'PBNKDEFF'
			else:
				assert False
		
		cSpreadsheet.getCellByPosition(3, 34 + iItem).setFormula(sAccIDText)
		cSpreadsheet.getCellByPosition(3, 35 + iItem).setFormula(sBnkIDText)
		cSpreadsheet.getCellByPosition(4, 33 + iItem).setFormula(sBankName)
		cSpreadsheet.getCellByPosition(4, 34 + iItem).setFormula(sAccIDVal)
		cSpreadsheet.getCellByPosition(4, 35 + iItem).setFormula(sBnkIDVal)

		cDocument.storeAsURL(urljoin(sInvoiceURL, '%s.ods' % sInvoiceID), ())
		
	def __del__(self):

			self.oLOR.shutdown()
