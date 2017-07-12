import cx_Oracle

conn = cx_Oracle.connect('system', '123456', 'localhost' + ":" + ('1521') + "/" + 'orcl')
cursor = conn.cursor()
table = 'http_restore_info'
total_q = ("select count(*) from user_tables where table_name = '{}'").format(table.upper())
x = cursor.execute(total_q)
resss = x.fetchone()
totalcount = resss[0]

print(resss)
print(type(totalcount))

cursor.close()
conn.close()










