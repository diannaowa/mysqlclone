#!/bin/env python
#coding=utf-8

import MySQLdb,datetime,sys,time,os,argparse

__author__ = "liuzhenwei"

class MySQLClone(object):

	def __init__(self,**kwargs):
		self.pid = os.getpid()
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
			if self.noData:
				self.__printInfo(table)
		#load data
		if not self.noData:
			tmpFile = '/tmp/'+table+'_'+str(self.pid)
			try:
				outFileSQL = "SELECT * INTO OUTFILE '%s' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' FROM %s;" % (tmpFile,table)
				count = self.sourceCur.execute(outFileSQL)
			except MySQLdb.Error,e:
				print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
			else:
				self.__loadData(tmpFile,table)
	
	def __loadData(self,dataFile,table):
		try:
			intoFileSQL = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s CHARACTER SET utf8 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" % (dataFile,table)
			self.dstCur.execute(intoFileSQL)
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
		else:
			os.remove(dataFile)
			self.__printInfo(table)

	def __cloneDatabase(self):
		count = self.sourceCur.execute('SHOW TABLES;')
		results=self.sourceCur.fetchall()
		for table in results:
			self.__cloneSingleTable(table[0])

	def __printInfo(self,table):
		'''
			print info 
		'''
		curTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		print >> sys.stdout,"[%s] INFO: - table [%s] was transferred." % (curTime,table)

	def __del__(self):
		self.__dstCommit()
		self.__sourceColse()
		self.__dstColse()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--sourceHost',action='store',dest='sourceHost',default='localhost',help='The source database host,default[localhost]')
	parser.add_argument('--sourcePort',action='store',dest='sourcePort',default=3306,help='The source database port,defalut[3306]')
	parser.add_argument('--sourcePasswd',action='store',dest='sourcePasswd',default="",help='The source databas passwd,default[NULL]')
	parser.add_argument('--sourceUser',action='store',dest='sourceUser',default='root',help='The source databas username,default[root]')
	parser.add_argument('--sourceDb',action='store',dest='sourceDb',default=None,help='The source databas name')
	parser.add_argument('--dstDb',action='store',dest='dstDb',default=None,help='The dst databas name')
	parser.add_argument('--sourceTable',action='store',dest='sourceTable',default=None,help='The source table,default[None]')
	parser.add_argument('--dstHost',action='store',dest='dstHost',default='localhost',help='The dst database host,default[localhost]')
	parser.add_argument('--dstPort',action='store',dest='dstPort',default=3306,help='The dst database port,defalut[3306]')
	parser.add_argument('--dstPasswd',action='store',dest='dstPasswd',default="",help='The dst databas passwd,default[NULL]')
	parser.add_argument('--dstUser',action='store',dest='dstUser',default='root',help='The dst databas username,default[root]')

	parser.add_argument('--noData',action='store',dest='noData',default=False,help='No row information;[True|False] False is default')
	
	args = parser.parse_args()

	if args.sourceDb is None:
		print >> sys.stderr,"ERROR: parameter --sourceDb cant not be NULL"
		sys.exit(1)

	if args.dstDb is None:
		print >> sys.stderr,"ERROR: parameter --dstDb cant not be NULL"
		sys.exit(1)

	conInfo = {
		"sourceHost":args.sourceHost,
		"sourceUser":args.sourceUser,
		"sourcePasswd":args.sourcePasswd,
		"sourceDb":args.sourceDb,
		"sourceTable":args.sourceTable,
		"noData":args.noData,
		"dstHost":args.dstHost,
		"dstUser":args.dstUser,
		"dstPasswd":args.dstPasswd,
		"dstDb":args.dstDb,
		"sourcePort":args.sourcePort,
		"dstPort":args.dstPort
		}
	print >> sys.stdout,"[%s] INFO: - Start clone database [%s:%s] To [%s:%s]" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),conInfo['sourceHost'],conInfo['sourceDb'],conInfo['dstHost'],conInfo['dstDb'])
	
	m = MySQLClone(**conInfo)
	m.clone()