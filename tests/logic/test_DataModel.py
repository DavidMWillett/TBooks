#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import shutil
import datetime

from tbooks.logic import DataModel


class DummyObserver:

	def Update(self):

		pass


class JobDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.jobData = DataModel.JobData(model)

	def test_get_item_data(self):

		job = self.jobData.GetItemData(486)
		self.assertEqual(job, (486, 29, "2801333", "T", 44.0, "Zeilen in EN(GB)",
			"Cornelsen: Berlese-Apparatur", datetime.date(2018, 8, 2), "EUR", 0.75, None))


class InvoiceDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.invoiceData = DataModel.InvoiceData(model)


class OrdererDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.ordererData = DataModel.OrdererData(model)

	def test_get_item_data(self):

		orderer = self.ordererData.GetItemData(29)
		self.assertEqual(orderer, (29, "Azevedo", "Blandine", "Frau", 8, "context@contextinc.com"))


class CustomerDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.customerData = DataModel.CustomerData(model)

	def test_get_item_data(self):

		customer = self.customerData.GetItemData(8)
		self.assertEqual(customer,
			(8,	"Contextinc GmbH", "Elisenstr. 4-10", u"50667 Köln", "", "",
				"DE", "DE",	"E", "DE 122776247", "None", "None", ""))


class PaymentDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.paymentData = DataModel.PaymentData(model)

	def test_get_item_data(self):

		payment = self.paymentData.GetItemData(655)
		self.assertEqual(payment,
			(655, datetime.date(2018, 9, 21), "Plusnet plc",
			"Telephone and internet (30% of GBP 33.41)", "GBP", 10.02, 20.0))


class SupplierDataTestCase(unittest.TestCase):

	def setUp(self):

		shutil.copy('tests/model/Reference.dbs', 'tbooks/model/TBooks.dbs')
		model = DataModel.DataModel()
		model.observer = DummyObserver()
		self.supplierData = DataModel.SupplierData(model)

	def test_get_item_data(self):

		supplier = self.supplierData.GetItemData(36)
		self.assertEqual(supplier, ("Plusnet plc",))

	def test_add_new_supplier(self):

		supplier = ("Octopus Energy",)

		self.supplierData.AddNew(supplier)
		self.assertEqual(self.supplierData.GetItemData(43), supplier)

	def test_update_supplier(self):

		supplier = ("Plusnet PLC",)

		self.supplierData.Update(36, supplier)
		self.assertEqual(self.supplierData.GetItemData(36), supplier)
