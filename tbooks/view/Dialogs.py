#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime

from tbooks.logic import DataModel

class RecordDialog(wx.Dialog):
    
    iMODE_INSERT, iMODE_UPDATE = range(2)
    
    def __init__(self, cParent, iID, sTitle, cDataModel):

        wx.Dialog.__init__(self, cParent, iID, sTitle)
        
        self.cDataModel = cDataModel
        
    def ControlSizer(self, sLabel, txtCtrl):
        
        szr = wx.BoxSizer(wx.VERTICAL)
        szr.Add(wx.StaticText(self, 0, sLabel), 0, wx.EXPAND)
        szr.Add(txtCtrl, 0, wx.EXPAND | wx.TOP, 2)
        return szr
    
    def Finalise(self, szrBody):
        
        btnOK = wx.Button(self, wx.ID_OK, 'OK')
        btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)
        btnCancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        
        szrFoot = wx.BoxSizer(wx.HORIZONTAL)
        szrFoot.Add(btnOK, 0, wx.ALL, 10)
        szrFoot.Add(btnCancel, 0, wx.ALL, 10)

        szrMain = wx.BoxSizer(wx.VERTICAL)
        szrMain.Add(szrBody, 0, wx.EXPAND)
        szrMain.Add(szrFoot, 0, wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(szrMain)
        self.SetFocus()
        self.Show(True)
    

class JobDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):

        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
        
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Job')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Job')
        else:
            assert False
        
        self.lCustomers = cDataModel.cCustomerData.GetList()
        self.lOrderers = None
            
        lUnits = ['Zeilen in EN(GB)', 'Zeilen in EN(US)', 'Zeilen EN(GB)', 'Zeilen EN(US)',
            'Wörter in EN(GB)', 'Wörter in EN(US)', 'Stunden', 'Words EN(GB)', 'Words EN(US)']
        
        self.cbxCustomer = wx.ComboBox(self, 0, choices = [c[1] for c in self.lCustomers], style = wx.CB_READONLY)
        self.cbxCustomer.Bind(wx.EVT_COMBOBOX, self.OnCustomerSelected)
        self.cbxOrderer = wx.ComboBox(self, 0, style = wx.CB_READONLY)
        self.txtCustOrderNo = wx.TextCtrl(self, 0)
        self.cbxTask = wx.ComboBox(self, 0, choices = ['Translation', 'Correction'], style = wx.CB_READONLY)
        self.cbxTask.SetSelection(0)
        self.txtQuantity = wx.TextCtrl(self, 0)
        self.cbxUnits = wx.ComboBox(self, 0, choices = lUnits)
        self.txtDescription = wx.TextCtrl(self, 0)
        self.txtDelivered = wx.TextCtrl(self, 0)
        self.txtDelivered.SetValue(datetime.date.today().isoformat())
        self.txtCurrency = wx.TextCtrl(self, 0)
        self.txtUnitPrice = wx.TextCtrl(self, 0)
        
        szrUpper = wx.BoxSizer(wx.HORIZONTAL)
        szrUpper.Add(self.ControlSizer('Customer:', self.cbxCustomer), 0, wx.EXPAND | wx.ALL, 10)
        szrUpper.Add(self.ControlSizer('Orderer:', self.cbxOrderer), 0, wx.EXPAND | wx.ALL, 10)
        szrUpper.Add(self.ControlSizer('Customer Order No:', self.txtCustOrderNo), 1, wx.ALL, 10)
        
        szrMiddle = wx.BoxSizer(wx.HORIZONTAL)
        szrMiddle.Add(self.ControlSizer('Task:', self.cbxTask), 1, wx.ALL, 10)
        szrMiddle.Add(self.ControlSizer('Quantity:', self.txtQuantity), 1, wx.ALL, 10)
        szrMiddle.Add(self.ControlSizer('Units:', self.cbxUnits), 1, wx.ALL, 10)
        
        szrLower = wx.BoxSizer(wx.HORIZONTAL)
        szrLower.Add(self.ControlSizer('Delivery Date:', self.txtDelivered), 1, wx.ALL, 10)
        szrLower.Add(self.ControlSizer('Currency:', self.txtCurrency), 1, wx.ALL, 10)
        szrLower.Add(self.ControlSizer('Unit Price:', self.txtUnitPrice), 1, wx.ALL, 10)
        
        szrBody = wx.BoxSizer(wx.VERTICAL)
        szrBody.Add(szrUpper, 0, wx.EXPAND)
        szrBody.Add(szrMiddle, 0, wx.EXPAND)
        szrBody.Add(self.ControlSizer('Description:', self.txtDescription), 0, wx.EXPAND | wx.ALL, 10)
        szrBody.Add(szrLower, 0, wx.EXPAND)
        
        self.Finalise(szrBody)
        
        if iNumber > 0:
            iNumber, iOrdererNo, sCustOrderNo, sTask, fQuantity, sUnits, \
            sDescription, cDelivered, sCurrency, fUnitPrice, iInvoiceNo = \
                self.cDataModel.GetItemData(DataModel.iJOBS, iNumber)
                
            iCustomerNo = cDataModel.cOrdererData.GetCustomerNo(iOrdererNo)
            for i in range(len(self.lCustomers)):
                if self.lCustomers[i][0] == iCustomerNo: break
            self.cbxCustomer.SetSelection(i)
            
            self.lOrderers = self.cDataModel.cCustomerData.GetOrderers(iCustomerNo)
            self.cbxOrderer.Clear()
            self.cbxOrderer.SetValue("")
            self.cbxOrderer.AppendItems(['%s %s %s' % (o[3], o[2], o[1]) for o in self.lOrderers])
            
            for i in range(len(self.lOrderers)):
                if self.lOrderers[i][0] == iOrdererNo: break
            self.cbxOrderer.SetSelection(i)
            
            self.txtCustOrderNo.SetValue(sCustOrderNo)
            self.cbxTask.SetValue('Translation' if sTask == 'T' else 'Correction')
            self.txtQuantity.SetValue(str(fQuantity))
            self.cbxUnits.SetValue(sUnits)
            self.txtDescription.SetValue(sDescription)
            self.txtDelivered.SetValue(cDelivered.isoformat())
            self.txtCurrency.SetValue(sCurrency)
            self.txtUnitPrice.SetValue(str(fUnitPrice))
            
    def OnCustomerSelected(self, cEvent):
        
        iSelectedCustomerNo = self.lCustomers[cEvent.GetSelection()][0]
        self.lOrderers = self.cDataModel.cCustomerData.GetOrderers(iSelectedCustomerNo)
        self.cbxOrderer.Clear()
        self.cbxOrderer.SetValue("")
        self.cbxOrderer.AppendItems(['%s %s %s' % (o[3], o[2], o[1]) for o in self.lOrderers])
        
    def OnBtnOK(self, cEvent):
        
        tJob = (
            self.lOrderers[self.cbxOrderer.GetSelection()][0],
            self.txtCustOrderNo.GetValue(),
            self.txtQuantity.GetValue(),
            self.cbxUnits.GetValue(),
            [u'T', u'C'][self.cbxTask.GetSelection()],
            self.txtDescription.GetValue(),
            datetime.datetime.strptime(self.txtDelivered.GetValue(), '%Y-%m-%d'), 
            self.txtCurrency.GetValue(),
            self.txtUnitPrice.GetValue())
        try:
            if self.iMode == self.iMODE_INSERT:
                self.cDataModel.cJobData.AddNew(tJob)
            elif self.iMode == self.iMODE_UPDATE:
                self.cDataModel.cJobData.Update(self.iNumber, tJob)
            else:
                assert False
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)
            

class InvoiceDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):

        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
        
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Invoice')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Invoice')
        else:
            assert False
            
        self.tCustNos, tCustOrgs = zip(*cDataModel.cCustomerData.GetUninvoiced())
        
        cToday = datetime.date.today()
        
        self.txtDate = wx.TextCtrl(self, 0)
        self.txtDate.SetValue(cToday.isoformat())
        self.txtNumber = wx.TextCtrl(self, 0)
        self.txtNumber.SetValue(cToday.strftime('%y%m%d01'))
        self.txtVAT = wx.TextCtrl(self, 0)
        self.cbxCustomer = wx.ComboBox(self, 0, choices = tCustOrgs, style = wx.CB_READONLY)
        
        szrLeft = wx.BoxSizer(wx.VERTICAL)
        szrLeft.Add(self.ControlSizer('Date:', self.txtDate), 1, wx.ALL, 10)
        szrLeft.Add(self.ControlSizer('Number:', self.txtNumber), 1, wx.ALL, 10)
        szrLeft.Add(self.ControlSizer('VAT:', self.txtVAT), 1, wx.ALL, 10)
        
        szrBody = wx.BoxSizer(wx.HORIZONTAL)
        szrBody.Add(szrLeft, 0, wx.EXPAND)
        szrBody.Add(self.ControlSizer('Customer:', self.cbxCustomer), 0, wx.EXPAND | wx.ALL, 10)
        
        self.Finalise(szrBody)
        
    def OnBtnOK(self, cEvent):
        
        tInvoice = (
            self.txtNumber.GetValue(),
            datetime.datetime.strptime(self.txtDate.GetValue(), '%Y-%m-%d'), 
            self.tCustNos[self.cbxCustomer.GetSelection()],
            self.txtVAT.GetValue())
        try:
            self.cDataModel.cInvoiceData.AddNew(tInvoice)
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)


class DatePaidDialog(wx.Dialog):
    
    def __init__(self, cParent, iID):

        wx.Dialog.__init__(self, cParent, iID, 'Record Invoice Paid')
        
        self.txtDate = wx.TextCtrl(self, 0)
        self.txtDate.SetValue(datetime.date.today().isoformat())
        
        self.btnOK = wx.Button(self, wx.ID_OK, 'OK')
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        
        szrBody = wx.BoxSizer(wx.VERTICAL)
        szrBody.Add(wx.StaticText(self, 0, 'Date:'), 0, wx.EXPAND)
        szrBody.Add(self.txtDate, 0, wx.EXPAND | wx.TOP, 2)
        
        szrFoot = wx.BoxSizer(wx.HORIZONTAL)
        szrFoot.Add(self.btnOK, 0, wx.ALL, 10)
        szrFoot.Add(self.btnCancel, 0, wx.ALL, 10)

        szrMain = wx.BoxSizer(wx.VERTICAL)
        szrMain.Add(szrBody, 0, wx.EXPAND | wx.ALL, 10)
        szrMain.Add(szrFoot, 0, wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(szrMain)
        self.SetFocus()
        self.Show(True)        
        
    def GetDate(self):
        
        return datetime.datetime.strptime(self.txtDate.GetValue(), '%Y-%m-%d')


class OrdererDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):

        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
        
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Orderer')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Orderer')
        else:
            assert False
            
        self.tCustomerNos, tNames, = zip(*cDataModel.cCustomerData.GetList())
        
        self.txtTitle = wx.TextCtrl(self, 0, size = (30, -1))
        self.txtGivenName = wx.TextCtrl(self, 0)
        self.txtFamilyName = wx.TextCtrl(self, 0)
        self.cbxCustomer = wx.ComboBox(self, 0, choices = tNames, style = wx.CB_READONLY)
        self.txtEmailAddress = wx.TextCtrl(self, 0)
        
        szrUpper = wx.BoxSizer(wx.HORIZONTAL)
        szrUpper.Add(self.ControlSizer('Title:', self.txtTitle), 0, wx.ALL, 10)
        szrUpper.Add(self.ControlSizer('Given Name:', self.txtGivenName), 1, wx.ALL, 10)
        szrUpper.Add(self.ControlSizer('Family Name:', self.txtFamilyName), 1, wx.ALL, 10)
        
        szrBody = wx.BoxSizer(wx.VERTICAL)
        szrBody.Add(szrUpper, 0, wx.EXPAND)
        szrBody.Add(self.ControlSizer('Customer:', self.cbxCustomer), 0, wx.EXPAND | wx.ALL, 10)
        szrBody.Add(self.ControlSizer('Email Address:', self.txtEmailAddress), 0, wx.EXPAND | wx.ALL, 10)
        
        self.Finalise(szrBody)
        
        if iNumber > 0:
            iNumber, sFamilyName, sGivenName, sTitle, iCustomerNo, sEmailAddress = \
                self.cDataModel.GetItemData(DataModel.iORDERERS, iNumber)
                
            self.txtFamilyName.SetValue(sFamilyName)
            self.txtGivenName.SetValue(sGivenName)
            self.txtTitle.SetValue(sTitle)
            for i in range(len(self.tCustomerNos)):
                if self.tCustomerNos[i] == iCustomerNo: break
            self.cbxCustomer.SetValue(tNames[i])
            self.txtEmailAddress.SetValue(sEmailAddress)
            
    def OnBtnOK(self, cEvent):
        
        tOrderer = (
            self.txtFamilyName.GetValue(),
            self.txtGivenName.GetValue(),
            self.txtTitle.GetValue(),
            self.tCustomerNos[self.cbxCustomer.GetSelection()],
            self.txtEmailAddress.GetValue())
        try:
            if self.iMode == self.iMODE_INSERT:
                self.cDataModel.cOrdererData.AddNew(tOrderer)
            elif self.iMode == self.iMODE_UPDATE:
                self.cDataModel.cOrdererData.Update(self.iNumber, tOrderer)
            else:
                assert False
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)


class CustomerDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):

        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
        
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Customer')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Customer')
        else:
            assert False
            
        self.txtOrganization = wx.TextCtrl(self, 0)
        self.txtAddress1 = wx.TextCtrl(self, 0)
        self.txtAddress2 = wx.TextCtrl(self, 0)
        self.txtAddress3 = wx.TextCtrl(self, 0)
        self.txtAddress4 = wx.TextCtrl(self, 0)
        self.txtCountry = wx.TextCtrl(self, 0)
        self.txtInvLanguage = wx.TextCtrl(self, 0)
        self.txtVATCode = wx.TextCtrl(self, 0)
        self.txtVATIDNo = wx.TextCtrl(self, 0)
        self.txtInvTitle = wx.TextCtrl(self, 0, size = (30, -1))
        self.txtInvGivenName = wx.TextCtrl(self, 0)
        self.txtInvFamilyName = wx.TextCtrl(self, 0)

        szrOrganization = self.ControlSizer('Organization:', self.txtOrganization)
        
        szrAddress = wx.BoxSizer(wx.VERTICAL)
        szrAddress.Add(wx.StaticText(self, 0, 'Address:'), 0, wx.EXPAND)
        szrAddress.Add(self.txtAddress1, 0, wx.EXPAND | wx.TOP, 2)
        szrAddress.Add(self.txtAddress2, 0, wx.EXPAND | wx.TOP, 2)
        szrAddress.Add(self.txtAddress3, 0, wx.EXPAND | wx.TOP, 2)
        szrAddress.Add(self.txtAddress4, 0, wx.EXPAND | wx.TOP, 2)
        
        szrCountry = self.ControlSizer('Country:', self.txtCountry)
        szrInvLanguage = self.ControlSizer('Language:', self.txtInvLanguage)
        szrVATCode = self.ControlSizer('VAT Code:', self.txtVATCode)
        szrVATIDNo = self.ControlSizer('VAT ID No:', self.txtVATIDNo)
        szrInvTitle = self.ControlSizer('Title:', self.txtInvTitle)
        szrInvGivenName = self.ControlSizer('Given Name:', self.txtInvGivenName)
        szrInvFamilyName = self.ControlSizer('Family Name:', self.txtInvFamilyName)
        
        szrBody = wx.BoxSizer(wx.VERTICAL)
        
        self.__AddRow(szrBody, ((szrOrganization, 1),))
        self.__AddRow(szrBody, ((szrAddress, 1),))
        self.__AddRow(szrBody, ((szrCountry, 1), (szrInvLanguage, 0)))
        self.__AddRow(szrBody, ((szrVATCode, 0), (szrVATIDNo, 1)))
        self.__AddRow(szrBody, ((szrInvTitle, 0), (szrInvGivenName, 1), (szrInvFamilyName, 1)))
        
        self.Finalise(szrBody)
                
        if iNumber > 0:
            iNumber, sOrganization, sAddress1, sAddress2, sAddress3, sAddress4, sCountry, \
            sInvLanguage, sVATCode, sVATIDNo, sInvFamilyName, sInvGivenName, sInvTitle = \
              self.cDataModel.GetItemData(DataModel.iCUSTOMERS, iNumber)
                
            self.txtOrganization.SetValue(sOrganization)
            self.txtAddress1.SetValue(sAddress1)
            self.txtAddress2.SetValue(sAddress2)
            self.txtAddress3.SetValue(sAddress3)
            self.txtAddress4.SetValue(sAddress4)
            self.txtCountry.SetValue(sCountry)
            self.txtInvLanguage.SetValue(sInvLanguage)
            self.txtVATCode.SetValue(sVATCode)
            self.txtVATIDNo.SetValue(sVATIDNo)
            self.txtInvFamilyName.SetValue(sInvFamilyName)
            self.txtInvGivenName.SetValue(sInvGivenName)
            self.txtInvTitle.SetValue(sInvTitle)

    def __AddRow(self, szrBody, tSizers):
        
        szrRow = wx.BoxSizer(wx.HORIZONTAL)
        for szr, iProp in tSizers:
            szrRow.Add(szr, iProp, wx.ALL, 5)
        szrBody.Add(szrRow, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
    def OnBtnOK(self, cEvent):
        
        tCustomer = (
            self.txtOrganization.GetValue(),
            self.txtAddress1.GetValue(),
            self.txtAddress2.GetValue(),
            self.txtAddress3.GetValue(),
            self.txtAddress4.GetValue(),
            self.txtCountry.GetValue(),
            self.txtInvLanguage.GetValue(),
            self.txtVATCode.GetValue(),
            self.txtVATIDNo.GetValue(),
            self.txtInvFamilyName.GetValue(),
            self.txtInvGivenName.GetValue(),
            self.txtInvTitle.GetValue())
        try:
            if self.iMode == self.iMODE_INSERT:
                self.cDataModel.cCustomerData.AddNew(tCustomer)
            elif self.iMode == self.iMODE_UPDATE:
                self.cDataModel.cCustomerData.Update(self.iNumber, tCustomer)
            else:
                assert False
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)
        

class PaymentDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):
        
        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
                    
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Payment')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Payment')
        else:
            assert False
            
        self.tSupplierNos, tSupplierNames = zip(*cDataModel.cSupplierData.GetList())
        self.txtDate = wx.TextCtrl(self, 0)
        self.cbxSupplier = wx.ComboBox(self, 0, choices = tSupplierNames, style = wx.CB_READONLY)
        self.txtProduct = wx.TextCtrl(self, 0)
        self.txtCurrency = wx.TextCtrl(self, 0)
        self.txtAmount = wx.TextCtrl(self, 0)
        self.txtVAT = wx.TextCtrl(self, 0)
        
        szrUpper = wx.BoxSizer(wx.HORIZONTAL)
        szrUpper.Add(self.ControlSizer('Date:', self.txtDate), 1, wx.ALL, 10)
        szrUpper.Add(self.ControlSizer('Supplier:', self.cbxSupplier), 1, wx.ALL, 10)
        
        szrLower = wx.BoxSizer(wx.HORIZONTAL)
        szrLower.Add(self.ControlSizer('Currency:', self.txtCurrency), 1, wx.ALL, 10)
        szrLower.Add(self.ControlSizer('Amount:', self.txtAmount), 1, wx.ALL, 10)
        szrLower.Add(self.ControlSizer('VAT Rate:', self.txtVAT), 1, wx.ALL, 10)
        
        szrBody = wx.BoxSizer(wx.VERTICAL)
        szrBody.Add(szrUpper, 0, wx.EXPAND)
        szrBody.Add(self.ControlSizer('Product:', self.txtProduct), 0, wx.EXPAND | wx.ALL, 10)
        szrBody.Add(szrLower, 0, wx.EXPAND)
        
        self.Finalise(szrBody)
        
        if iNumber > 0:
            iNumber, cDate, sSupplier, sProduct, sCurrency, fAmount, fVAT = \
                self.cDataModel.GetItemData(DataModel.iPAYMENTS, iNumber)
                
            self.txtDate.SetValue(cDate.isoformat())
            self.cbxSupplier.SetStringSelection(sSupplier)
            self.txtProduct.SetValue(sProduct)
            self.txtCurrency.SetValue(sCurrency)
            self.txtAmount.SetValue(str(fAmount))
            self.txtVAT.SetValue(str(fVAT))
        
    def OnBtnOK(self, cEvent):
        
        tPayment = (
            datetime.datetime.strptime(self.txtDate.GetValue(), '%Y-%m-%d'), 
            self.tSupplierNos[self.cbxSupplier.GetSelection()],
            self.txtProduct.GetValue(),
            self.txtCurrency.GetValue(),
            self.txtAmount.GetValue(),
            self.txtVAT.GetValue())
        try:
            if self.iMode == self.iMODE_INSERT:
                self.cDataModel.cPaymentData.AddNew(tPayment)
            elif self.iMode == self.iMODE_UPDATE:
                self.cDataModel.cPaymentData.Update(self.iNumber, tPayment)
            else:
                assert False
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)


class SupplierDialog(RecordDialog):
    
    def __init__(self, cParent, iID, iMode, iNumber, cDataModel):

        RecordDialog.__init__(self, cParent, iID, '', cDataModel)
        
        self.iMode = iMode
        self.iNumber = iNumber
                    
        if iMode == self.iMODE_INSERT:
            self.SetTitle('Enter New Supplier')
        elif iMode == self.iMODE_UPDATE:
            self.SetTitle('Edit Supplier')
        else:
            assert False
            
        self.txtName = wx.TextCtrl(self, 0)

        szrBody = wx.BoxSizer(wx.VERTICAL)
        szrBody.Add(self.ControlSizer('Name:', self.txtName), 0, wx.EXPAND | wx.ALL, 10)
        
        self.Finalise(szrBody)
        
        if iNumber > 0:
            sName, = self.cDataModel.GetItemData(DataModel.iSUPPLIERS, iNumber)
            self.txtName.SetValue(sName)
        
    def OnBtnOK(self, cEvent):
        
        tSupplier = (self.txtName.GetValue(),)
        try:
            if self.iMode == self.iMODE_INSERT:
                self.cDataModel.cSupplierData.AddNew(tSupplier)
            elif self.iMode == self.iMODE_UPDATE:
                self.cDataModel.cSupplierData.Update(self.iNumber, tSupplier)
            else:
                assert False
        except ValueError:
            wx.Bell()
        else:
            self.EndModal(wx.ID_OK)
