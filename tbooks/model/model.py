from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy import Date as SQLDate

import sys, os

Base = declarative_base()


class Job(Base):

	__tablename__ = 'Job'

	Number = Column(Integer, primary_key=True)
	OrdererNo = Column(Integer, ForeignKey('Orderer.Number'))
	CustOrderNo = Column(String)
	Task = Column(String)
	Quantity = Column(Float)
	Units = Column(String)
	Description = Column(String)
	Delivered = Column(SQLDate)
	Currency = Column(String)
	UnitPrice = Column(Float)
	InvoiceNo = Column(Integer, ForeignKey('Invoice.Number'))

	Orderer = relationship('Orderer')


class Invoice(Base):

	__tablename__ = 'Invoice'

	Number = Column(Integer, primary_key=True)
	Date = Column(SQLDate)
	VAT = Column(Float)
	Paid = Column(SQLDate)


class Orderer(Base):

	__tablename__ = 'Orderer'

	Number = Column(Integer, primary_key=True)
	FamilyName = Column(String)
	GivenName = Column(String)
	Title = Column(String)
	CustomerNo = Column(Integer, ForeignKey('Customer.Number'))
	EmailAddress = Column(String)

	Customer = relationship('Customer')


class Customer(Base):

	__tablename__ = 'Customer'

	Number = Column(Integer, primary_key=True)
	Organization = Column(String)
	Address1 = Column(String)
	Address2 = Column(String)
	Address3 = Column(String)
	Address4 = Column(String)
	Country = Column(String)
	Language = Column(String)
	VATCode = Column(String)
	VATIDNo = Column(String)
	FamilyName = Column(String)
	GivenName = Column(String)
	Title = Column(String)


class Payment(Base):

	__tablename__ = 'Payment'

	Number = Column(Integer, primary_key=True)
	Date = Column(SQLDate)
	SupplierNo = Column(Integer, ForeignKey('Supplier.Number'))
	Product = Column(String)
	Currency = Column(String)
	Amount = Column(Float)
	VAT = Column(Float)

	Supplier = relationship('Supplier')


class Supplier(Base):

	__tablename__ = 'Supplier'

	Number = Column(Integer, primary_key=True)
	Name = Column(String)


engine = create_engine(URL('sqlite', database=os.path.join(sys.path[0], 'tbooks/model/TBooks.dbs')))

Session = sessionmaker()
Session.configure(bind=engine)

Base.metadata.create_all(engine)
