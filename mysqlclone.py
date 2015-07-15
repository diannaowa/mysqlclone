#!/bin/env python
#coding=utf-8

import MySQLdb,datetime,sys,time,os,argparse
from abc import ABCMeta, abstractmethod
__author__ = "liuzhenwei"
__version__ = "1.1"

class Clone():
	__metaclass__ = ABCMeta

	def __init__(self,**kwargs):
		self.pid = os.getpid()
		self.sourceCur = kwargs['sourceCur']
		self.dstCur =  kwargs['dstCur']
		self.noData =  kwargs['noData']
		self.sourceTable =  kwargs['sourceTable']
		self.lockAllTables =  kwargs['lockAllTables']
		self.sourceDb = kwargs['sourceDb']
		#print kwargs
	@abstractmethod
	def clone(self):
		pass

class MySQLClone(object):

	def __init__(self,**kwargs):
		self.sourceTable = kwargs['sourceTable']
		self.noData = kwargs['noData']
		self.lockAllTables = kwargs['lockAllTables']
		self.triggers = kwargs['triggers']
		self.routines = kwargs['routines']
		self.events = kwargs['events']
		self.sourceDb = kwargs['sourceDb']
		try:
			self.sourceConn=MySQLdb.connect(host=kwargs['sourceHost'],user=kwargs['sourceUser'],passwd=kwargs['sourcePasswd'],port=kwargs['sourcePort'])
			self.sourceCur=self.sourceConn.cursor()
			self.sourceConn.select_db(kwargs['sourceDb'])
			self.sourceCur.execute("SET NAMES utf8;")
			self.sourceCur.execute("SET AUTOCOMMIT=0;")
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])

		try:
			self.dstConn=MySQLdb.connect(host=kwargs['dstHost'],user=kwargs['dstUser'],passwd=kwargs['dstPasswd'],port=kwargs['dstPort'],local_infile=1)
			self.dstCur=self.dstConn.cursor()
			self.dstConn.select_db(kwargs['dstDb'])
			self.dstCur.execute("SET NAMES utf8;")
			#stop bin log
			self.dstCur.execute("SET sql_log_bin=0;")
			#
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
		kwargs = {}
		kwargs['sourceCur'] = self.sourceCur
		kwargs['dstCur'] = self.dstCur
		kwargs['noData'] = self.noData
		kwargs['sourceTable'] = self.sourceTable
		kwargs['lockAllTables'] = self.lockAllTables
		kwargs['sourceDb'] = self.sourceDb
		c = DatabaseClone(**kwargs)
		c.clone()

		if self.triggers:
			t = TriggersClone(**kwargs)
			t.clone()

		if self.routines:
			#print kwargs
			r = RoutinesClone(**kwargs)
			r.clone()

		if self.events:
			e = EventsClone(**kwargs)
			e.clone()

	def __del__(self):
		self.__dstCommit()
		self.__sourceColse()
		self.__dstColse()


class DatabaseClone(Clone):
	'''
	clone database
	'''
	def __init__(self,**kwargs):
		Clone.__init__(self,**kwargs)
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
				PrintInfo.say('table',table)
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
		if not self.lockAllTables:
			self.sourceCur.execute("COMMIT;")
			self.sourceCur.execute("UNLOCK TABLES;")
	
	def __loadData(self,dataFile,table):
		try:
			intoFileSQL = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s CHARACTER SET utf8 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n';" % (dataFile,table)
			self.dstCur.execute(intoFileSQL)
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
		else:
			os.remove(dataFile)
			PrintInfo.say('table',table)

	def clone(self):
		tableList = []
		if self.sourceTable:
			tableList.append(self.sourceTable)
		else:
			count = self.sourceCur.execute('SHOW TABLES;')
			results=self.sourceCur.fetchall()
			for table in results:
				tableList.append(table[0])
			#lock all tables
			if self.lockAllTables:
				lockSQL = "LOCK TABLES %s;" % ','.join([t+' READ' for t in tableList])
				self.sourceCur.execute(lockSQL)

		for t in tableList:
			#lock single table
			if not self.lockAllTables:
				self.sourceCur.execute("LOCK TABLES %s READ;"% t)
			self.__cloneSingleTable(t)
		
		if self.lockAllTables:
			self.sourceCur.execute("COMMIT;")
			self.sourceCur.execute("UNLOCK TABLES;")


class EventsClone(Clone):
	'''
	clone events
	'''
	def __init__(self,**kwargs):
		pass
	def clone(self):
		print "clone events"

class TriggersClone(Clone):
	'''
	clone triggers
	'''
	def __init__(self,**kwargs):
		pass
	def clone(self):
		print "clone triggers"

class RoutinesClone(Clone):
	'''
	clone routines (functions and procedures).
	'''
	def __init__(self,**kwargs):
		Clone.__init__(self,**kwargs)

	def clone(self):
		for proc in self.__getProcList():
			self.__cloneProc(proc)

		for func in self.__getFunctionList():
			self.__cloneFunc(func)

	def __getProcList(self):
		try:
			count = self.sourceCur.execute("SHOW PROCEDURE STATUS WHERE db='%s';" % (self.sourceDb))
			results=self.sourceCur.fetchall()
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
		else:
			for proc in results:
				yield proc[1]

	def __cloneProc(self,proc):
		try:
			count = self.sourceCur.execute("SHOW CREATE PROCEDURE %s;" % proc)
			results=self.sourceCur.fetchone()
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])

		else:
			try:
				self.dstCur.execute(results[2])
			except MySQLdb.Error,e:
				print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
			else:
				PrintInfo.say('procedure',proc)
	def __getFunctionList(self):
		try:
			count = self.sourceCur.execute("SHOW FUNCTION STATUS WHERE db='%s';" % (self.sourceDb))
			results=self.sourceCur.fetchall()
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
		else:
			for func in results:
				yield func[1]

	def __cloneFunc(self,func):
		try:
			count = self.sourceCur.execute("SHOW CREATE FUNCTION %s;" % func)
			results=self.sourceCur.fetchone()
		except MySQLdb.Error,e:
			print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])

		else:
			try:
				self.dstCur.execute(results[2])
			except MySQLdb.Error,e:
				print >> sys.stderr,"Mysql Error %d: %s" % (e.args[0], e.args[1])
			else:
				PrintInfo.say('function',func)

class PrintInfo(object):
	'''
	print info
	'''
	@staticmethod
	def say(item,name):
		'''
		print info 
		'''
		curTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		print >> sys.stdout,"[%s] INFO: - %s [%s] was transferred." % (curTime,item,name)



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

	parser.add_argument('--no-data','-d',action='store_true',dest='noData',help='No row information;False is default')
	
	parser.add_argument('--lock-all-tables','-X',action='store_true',dest='lockAllTables',help='Locks all tables,default[False:Lock the table to be read]')

	parser.add_argument('--events','-E',action='store_true',dest='events',help='Clone events,default[False]')
	parser.add_argument('--routines','-R',action='store_true',dest='routines',help='Clone stored routines (functions and procedures),default[False]')
	parser.add_argument('--triggers',action='store_true',dest='triggers',help='Clone triggers for each dumped table,default[False]')

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
		"dstPort":args.dstPort,
		"lockAllTables":args.lockAllTables,
		"events":args.events,
		"routines":args.routines,
		"triggers":args.triggers
		}
	print >> sys.stdout,"[%s] INFO: - Start clone database [%s:%s] To [%s:%s]" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),conInfo['sourceHost'],conInfo['sourceDb'],conInfo['dstHost'],conInfo['dstDb'])
	
	m = MySQLClone(**conInfo)
	m.clone()