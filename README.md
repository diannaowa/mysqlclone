# mysqlclone

It’s used to transfer a mysql database to the other.Clone MySQL database.

# How to use it?
```
[root@iZ2876x9bezZ ~]# python mysqlclone.py --help
usage: mysqlclone.py [-h] [--sourceHost SOURCEHOST] [--sourcePort SOURCEPORT]
                     [--sourcePasswd SOURCEPASSWD] [--sourceUser SOURCEUSER]
                     [--sourceDb SOURCEDB] [--dstDb DSTDB]
                     [--sourceTable SOURCETABLE] [--dstHost DSTHOST]
                     [--dstPort DSTPORT] [--dstPasswd DSTPASSWD]
                     [--dstUser DSTUSER] [--no-data] [--lock-all-tables]
                     [--events] [--routines] [--triggers]

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
  --no-data, -d         No row information;False is default
  --lock-all-tables, -X
                        Locks all tables,default[False:Lock the table to be
                        read]
  --events, -E          Clone events,default[False]
  --routines, -R        Clone stored routines (functions and
                        procedures),default[False]
  --triggers            Clone triggers for each dumped
                        table,default[False]
  
  [root@iZ2876x9bezZ ~]# python mysqlclone.py --sourceHost 127.0.0.1 --sourceUser root --sourcePasswd xxx --dstHost 127.0.0.1 --dstUser root --dstPasswd xxx --sourceDb test --dstDb test2 --no-data -E -R -X
  
  [2015-07-10 11:44:44] INFO: - Start clone database [127.0.0.1:test] To [127.0.0.1:test2]
[2015-07-10 11:44:44] INFO: - table [pcore_information_information] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_information_reply] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_item_item] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_consignee_address] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_member] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_region] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_region_district] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_region_district_exist] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_session] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_member_usergroup] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_adminsession] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_member] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_memberfield] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_seccode] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_session] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_passport_usergroup] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_data] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_field] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_file] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_global] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_module] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_system_schedule] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_trade_cart] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_trade_order] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_trade_order_detail] was transferred.
[2015-07-10 11:44:44] INFO: - table [pcore_trade_order_return_goods] was transferred.
  ```
