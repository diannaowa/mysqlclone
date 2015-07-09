#!/bin/env python
#coding=utf-8

import MySQLdb,datetime,sys,time

__author__ = "liuzhenwei"

class MySQLClone2(object):

	def __init__(self,**kwargs):
		print >> sys.stdout,"[%s] INFO: - Start clone database [%s:%s] To [%s:%s]" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),kwargs['sourceHost'],kwargs['sourceDb'],kwargs['dstHost'],kwargs['dstDb'])
		self.sourceTable = kwargs['sourceTable']
		self.noData = kwargs['noData']
		try:
			self.sourceConn=MySQLdb.connect(host=kwargs['sourceHost'],user=kwargs['sourceUser'],passwd=kwargs['sourcePasswd'],port=kwargs['sourcePort'])
			self.sourceCur=self.sourceConn.cursor()
			self.sourceConn.select_db(kwargs['sourceDb'])
			self.sourceCur.execute("SET NAMES utf8;")
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])

		try:
			self.dstConn=MySQLdb.connect(host=kwargs['dstHost'],user=kwargs['dstUser'],passwd=kwargs['dstPasswd'],port=kwargs['dstPort'],local_infile=1)
			self.dstCur=self.dstConn.cursor()
			self.dstConn.select_db(kwargs['dstDb'])
			self.dstCur.execute("SET NAMES utf8;")
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])

	def __dstCommit(self):
	 	 self.dstConn.commit()
    
	def __sourceColse(self):
		self.sourceCur.close()
		self.sourceConn.close()

	def __dstColse(self):
		self.dstCur.close()
		self.dstConn.close()

	def clone(self):

    	#single table clone
		if self.sourceTable:
			self.__cloneSingleTable(self.sourceTable)
    	#clone a database
		else:
			self.__cloneDatabase()


	def __cloneSingleTable(self,table):
		#create table
		count = self.sourceCur.execute('SHOW CREATE TABLE %s;' % table)
		results=self.sourceCur.fetchone()
		try:
			self.dstCur.execute(results[1])
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
			return False
		else:
			curTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print >> sys.stdout,"%s INFO: - table [%s] was transferred." % (curTime,table)
		#load data
		if not self.noData:
			pass

	def __cloneDatabase(self):
		count = self.sourceCur.execute('SHOW TABLES;')
		results=self.sourceCur.fetchall()
		for table in results:
			self.__cloneSingleTable(table[0])

	def __del__(self):
		self.__dstCommit()
		self.__sourceColse()
		self.__dstColse()

if __name__ == "__main__":
	k = {"sourceHost":"127.0.0.1","sourceUser":"root","sourcePasswd":"chrdw.com","sourceDb":"yishiwei","sourceTable":"","noData":True,
		"dstHost":"127.0.0.1","dstUser":"root","dstPasswd":"chrdw.com","dstDb":"test","sourcePort":3306,"dstPort":3306
		}

	m = MySQLClone2(**k)
	m.clone()
