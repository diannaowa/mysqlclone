# mysqlclone

It’s used to transfer a mysql database to the other.

# How to use it?
```
[root@iZ2876x9bezZ ~]# python mysqlclone.py --help
usage: mysqlclone.py [-h] [--sourceHost SOURCEHOST] [--sourcePort SOURCEPORT]
                     [--sourcePasswd SOURCEPASSWD] [--sourceUser SOURCEUSER]
                     [--sourceDb SOURCEDB] [--dstDb DSTDB]
                     [--sourceTable SOURCETABLE] [--dstHost DSTHOST]
                     [--dstPort DSTPORT] [--dstPasswd DSTPASSWD]
                     [--dstUser DSTUSER] [--noData NODATA]

optional arguments:
  -h, --help            show this help message and exit
  --sourceHost SOURCEHOST
                        The source database host,default[localhost]
  --sourcePort SOURCEPORT
                        The source database port,defalut[3306]
  --sourcePasswd SOURCEPASSWD
                        The source databas passwd,default[NULL]
  --sourceUser SOURCEUSER
                        The source databas username,default[root]
  --sourceDb SOURCEDB   The source databas name
  --dstDb DSTDB         The dst databas name
  --sourceTable SOURCETABLE
                        The source table,default[None]
  --dstHost DSTHOST     The dst database host,default[localhost]
  --dstPort DSTPORT     The dst database port,defalut[3306]
  --dstPasswd DSTPASSWD
                        The dst databas passwd,default[NULL]
  --dstUser DSTUSER     The dst databas username,default[root]
  --noData NODATA       No row information;[True|False] False is default
  
  [root@iZ2876x9bezZ ~]# python mysqlclone.py --sourceHost 127.0.0.1 --sourceUser root --sourcePasswd xxx --dstHost 127.0.0.1 --dstUser root --dstPasswd xxx --sourceDb test --dstDb test2 --noData True
  ```
