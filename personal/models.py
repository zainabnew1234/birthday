"""This handles all database connection"""
import datetime

from sqlalchemy.orm import backref
from personal import db




guest_gift =db.Table('guest_gift',
db.Column('guest_id',db.Integer(),db.ForeignKey('guest.id')),
db.Column('gift_id',db.Integer(),db.ForeignKey('gift.id')),
db.Column('qty',db.Integer() ))  


class Guest(db.Model):
    id =db.Column(db.Integer(),primary_key=True,autoincrement=True)
    profilepix=db.Column(db.String(59),nullable=False)
    fname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    pwd=db.Column(db.String(255),nullable=False)
    datereg=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    stateid=db.Column(db.Integer(),db.ForeignKey('state.id'))
    gif=db.relationship('State',backref='gifts')
    questions=db.relationship('Question',back_populates='quest')
    
    
class State(db.Model):
    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    name=db.Column(db.String(50),nullable=False)  

class Gift(db.Model): 
    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    giftname=db.Column(db.String(50),nullable=False)  


class Document(db.Model):
    doc_id =db.Column(db.Integer(),primary_key=True,autoincrement=True)
    doc_filename=db.Column(db.String(55),nullable=False)
    doc_msg=db.Column(db.String(200),nullable=False) 
    doc_date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    
  
class Question(db.Model):
    q_id =db.Column(db.Integer(),primary_key=True,autoincrement=True)
    guest_id=db.Column(db.Integer,db.ForeignKey('guest.id'))
    question=db.Column(db.String(255),nullable=False) 
    date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    quest=db.relationship('Guest',back_populates='questions')


class Lga(db.Model):
    lga_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    state_id=db.Column(db.Integer(),db.ForeignKey('state.id'))  
    lga_name=db.Column(db.String(55),nullable=False)

class Transaction(db.Model):
    trx_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    trx_guestid = db.Column(db.Integer(),db.ForeignKey('guest.id'), nullable=False)
    trx_amt = db.Column(db.Float(), nullable=False)
    trx_status = db.Column(db.String(40), nullable=False)
    trx_others = db.Column(db.String(255), nullable=True)
    trx_ref= db.Column(db.String(12), nullable=False)
    trx_ipaddress=db.Column(db.String(20),nullable=True)
    trx_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)    

    #set relationship
    guest=db.relationship("Guest",backref="guesttrx")

  
    # def __repr__(self):
    #     return "<{}:{}:{}:{}>".format(self.id,self.post_title[:10],self.post_content,self.post_created_on)
