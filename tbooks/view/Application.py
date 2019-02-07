#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

from tbooks.logic import DataModel
from Dialogs import *

class MainWindow(wx.Frame):

	def __init__(self, cDataModel):
    
		wx.Frame.__init__(self, None, wx.ID_ANY, "TBooks", size = (1100, 600))
		
		self.cNotebook = TBNotebook(self, cDataModel)
		
		self.Show(True)
    
    
class TablePage(wx.NotebookPage):
	
	def __init__(self, cParent, cDataModel):
		
		wx.NotebookPage.__init__(self, cParent, wx.ID_ANY)
		
		self.cDataModel = cDataModel
		
		self.pnlMain = wx.Panel(self, wx.ID_ANY)
		self.lctList = ItemList(self.pnlMain, cDataModel.GetTableHeads(self.iDATASET))
		self.lctList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
	
		self.btnNew = wx.Button(self.pnlMain, wx.ID_ANY, 'New')
		self.btnNew.Bind(wx.EVT_BUTTON, self.OnButtonNew)
		
		self.btnEdit = wx.Button(self.pnlMain, wx.ID_ANY, 'Edit')
		self.btnEdit.Bind(wx.EVT_BUTTON, self.OnButtonEdit)
		self.btnEdit.Enable(False)
		
		self.szrButtons = wx.BoxSizer(wx.HORIZONTAL)
		self.szrButtons.Add(self.btnNew, 0)
		self.szrButtons.Add(self.btnEdit, 0, wx.LEFT, 5)
	
		szrMain = wx.BoxSizer(wx.VERTICAL)
		szrMain.Add(self.lctList, 1, wx.EXPAND | wx.ALL, 5)
		szrMain.Add(self.szrButtons, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
		self.pnlMain.SetSizerAndFit(szrMain)
		self.Update()
		
	def Update(self):
		
		self.lctList.UpdateItems(self.cDataModel.GetViewData(self.iDATASET))
		
	def OnListItemSelected(self, cEvent):
		
		self.btnEdit.Enable()
		
	def OnButtonNew(self, cEvent):
		
		iIndex = self.lctList.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
		iNumber = self.lctList.GetItemData(iIndex) if iIndex >= 0 else 0
		
		cDialog = self.NewDialog(self, wx.ID_ANY, RecordDialog.iMODE_INSERT, iNumber, self.cDataModel)
		cDialog.ShowModal()
		cDialog.Destroy()
	
	def OnButtonEdit(self, cEvent):
		
		iIndex = self.lctList.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
		iNumber = self.lctList.GetItemData(iIndex)
		
		cDialog = self.NewDialog(self, wx.ID_ANY, RecordDialog.iMODE_UPDATE, iNumber, self.cDataModel)
		cDialog.ShowModal()
		cDialog.Destroy()
	
	
class JobsPage(TablePage):
	
	sNAME = 'Jobs'
	iDATASET = DataModel.iJOBS
	
	def __init__(self, cParent, cDataModel):
		
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = JobDialog
		

class InvoicesPage(TablePage):
	
	sNAME = 'Invoices'
	iDATASET = DataModel.iINVOICES
	
	def __init__(self, cParent, cDataModel):
	
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = InvoiceDialog
		
		self.szrButtons.Detach(self.btnEdit)
		self.btnEdit.Destroy()
		
		self.btnPaid = wx.Button(self.pnlMain, wx.ID_ANY, 'Mark Paid')
		self.szrButtons.Insert(1, self.btnPaid, 0, wx.LEFT, 5)
		
		self.lctList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
		self.btnPaid.Bind(wx.EVT_BUTTON, self.OnButtonPaid)
		self.btnPaid.Enable(False)
		
	def OnListItemSelected(self, cEvent):
		
		iInvoiceNo = self.lctList.GetItemData(cEvent.GetIndex())
		self.btnPaid.Enable(not self.cDataModel.cInvoiceData.IsPaid(iInvoiceNo))
		
	def OnButtonPaid(self, cEvent):
		
		cDialog = DatePaidDialog(self, 0)
		iResult = cDialog.ShowModal()
		
		if iResult == wx.ID_OK:
			iIndex = self.lctList.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
			iNumber = self.lctList.GetItemData(iIndex)
			self.cDataModel.cInvoiceData.SetPaid((iNumber, cDialog.GetDate()))
			self.UpdateTableView(self.cDataModel.GetViewData(self.iDATASET))
			
		cDialog.Destroy()
		

class OrderersPage(TablePage):
	
	sNAME = 'Orderers'
	iDATASET = DataModel.iORDERERS
	
	def __init__(self, cParent, cDataModel):
	
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = OrdererDialog
		

class CustomersPage(TablePage):
	
	sNAME = 'Customers'
	iDATASET = DataModel.iCUSTOMERS
	
	def __init__(self, cParent, cDataModel):
	
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = CustomerDialog
		

class PaymentsPage(TablePage):
	
	sNAME = 'Payments'
	iDATASET = DataModel.iPAYMENTS
	
	def __init__(self, cParent, cDataModel):
		
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = PaymentDialog
		

class SuppliersPage(TablePage):
	
	sNAME = 'Suppliers'
	iDATASET = DataModel.iSUPPLIERS
	
	def __init__(self, cParent, cDataModel):
	
		TablePage.__init__(self, cParent, cDataModel)
		
		self.NewDialog = SupplierDialog
		
		self.lctList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)

	def OnListItemSelected(self, cEvent):
		
		#iSupplierNo = self.lctList.GetItemData(cEvent.GetIndex())
		self.btnEdit.Enable()
		

class VATInfoPage(wx.NotebookPage):
	
	sNAME = 'VAT Info'
	iDATASET = DataModel.iVATINFO
	
	def __init__(self, cParent, cDataModel):
		
		wx.NotebookPage.__init__(self, cParent, wx.ID_ANY)

		pnlMain = wx.Panel(self, wx.ID_ANY)
		lctMain = ItemList(pnlMain, cDataModel.cVATInfoData.GetHeadings())
		lctMain.UpdateItems(cDataModel.cVATInfoData.GetItems())
		
		szrMain = wx.BoxSizer(wx.VERTICAL)
		szrMain.Add(lctMain, 1, wx.EXPAND | wx.ALL, 5)
		pnlMain.SetSizerAndFit(szrMain)


class ECSalesPage(wx.NotebookPage):
	sNAME = 'EC Sales'
	iDATASET = DataModel.iECSALES

	def __init__(self, cParent, cDataModel):
		wx.NotebookPage.__init__(self, cParent, wx.ID_ANY)

		pnlMain = wx.Panel(self, wx.ID_ANY)
		lctMain = ItemList(pnlMain, cDataModel.cECSalesData.GetHeadings())
		lctMain.UpdateItems(cDataModel.cECSalesData.GetItems())

		szrMain = wx.BoxSizer(wx.VERTICAL)
		szrMain.Add(lctMain, 1, wx.EXPAND | wx.ALL, 5)
		pnlMain.SetSizerAndFit(szrMain)


class TBNotebook(wx.Notebook):

	lItemPages = \
		JobsPage, InvoicesPage, OrderersPage, CustomersPage, PaymentsPage, SuppliersPage, VATInfoPage, ECSalesPage

	def __init__(self, cParent, cDataModel):
		
		wx.Notebook.__init__(self, cParent, wx.ID_ANY)
		
		self.cDataModel = cDataModel
		
		for ItemPage in self.lItemPages:
			self.AddPage(ItemPage(self, cDataModel), ItemPage.sNAME)
		
		self.cDataModel.Attach(self)
		
	def Update(self):
		
		for iPage in range(self.GetPageCount()):
			self.GetPage(iPage).Update()
		
		
class ItemList(wx.ListCtrl):
	
	def __init__(self, cParent, tHeadings):
		
		wx.ListCtrl.__init__(self, cParent, wx.ID_ANY, style = wx.LC_REPORT | wx.LC_SINGLE_SEL)
		
		self.tHeadings = tHeadings

		for sField, sType in self.tHeadings:
			iAlign = wx.LIST_FORMAT_RIGHT if sType in ['decimal', 'float', 'int'] else wx.LIST_FORMAT_LEFT
			self.InsertColumn(self.GetColumnCount(), sField, iAlign, wx.LIST_AUTOSIZE_USEHEADER)

		self.SetColumnWidth(0, 80) # Autosize doesn't work on column 0 in MSW, so set to standard width

	def UpdateItems(self, tTableData):

		self.DeleteAllItems()
		if tTableData:
			for iRecord in range(len(tTableData)):
				tRecord = tTableData[iRecord]
				self.InsertStringItem(iRecord, str(tRecord[0]))
				for iField in range(1, len(tRecord)):
					sFormat = '{0:0.2f}' if self.tHeadings[iField][1] == 'decimal' and tRecord[iField] is not None else u'{0!s}'
					self.SetStringItem(iRecord, iField, sFormat.format(tRecord[iField]))
				if self.tHeadings[0][1] == 'int':
					self.SetItemData(iRecord, long(tRecord[0]))
			self.EnsureVisible(iRecord)
		

def Start():
	cApplication = wx.App()
	cDataModel = DataModel.DataModel()
	cMainWindow = MainWindow(cDataModel)
	cApplication.MainLoop()
