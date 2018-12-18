#!/usr/bin/env python

import xml.dom.minidom

class ECBReferenceRateDocument():
	
	def __init__(self):
		
		self.elements = xml.dom.minidom.parse('tbooks/logic/gbp.xml').getElementsByTagName('Obs')
		
	def GetGBPValue(self, fEurVal, cDate):
		
		sISODate = cDate.isoformat()
		isFirst = True
		for element in reversed(self.elements):
			d = element.getAttribute('TIME_PERIOD')
			if d <= sISODate: break
			isFirst = False
		else:
			return
		if not isFirst:
			return fEurVal * float(element.getAttribute('OBS_VALUE'))


cECBReferenceRateDocument = ECBReferenceRateDocument()


def GetGBPValue(fEurVal, cDate):
	
	return cECBReferenceRateDocument.GetGBPValue(fEurVal, cDate)

if __name__ == '__main__':
	
	print cECBReferenceRateDocument.GetGBPValue(1.00, datetime.date(2009, 12, 25))
