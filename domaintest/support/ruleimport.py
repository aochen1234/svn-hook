import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from testappp.models import TestDomain


a = TestDomain.objects.all()
a.delete()

res = {'wso.aspx': '&cmd=.*&Button123=Run', 'r57142.php': 'post:cmd=.*&dir=.*&submit=Execute', 'dx.php': 'post:dxval=.*(同时url=dxmode=CMD)', 'c37.php': 'get:action=CLI&dir=.*', 'silic.php': 'post:cmd=.*&show=%BB%D8%CF%D4或admin_silicpass=759df00ad725b46faef0a0f00daaaaa3', 'ce.asp': 'post:sp=.*&cmd=.*', 'cmd.asp': 'SP=cmd.exe&', 'websniff.aspx': 'ddlist=.*&txtport=\\d+&txtMinisize=\\d+&txtkeywords=.*&txtlogfile=.*&txtpackets=.*&Starts=Start', 'webadmin.aspx': 'multipart/form-data:Content-Disposition:\\s+form-data;\\s+name="Button_cmdRun"', 'strong.php': 'cmd=.*&show=%BB%D8%CF%D4%B4%B0%BF%DA或admin_spiderpass=006b9cc00c32c5204465978fbdf012a4', 'job.asp': 'post:action=filesystem&curPath=.*&fsAction=.*', 'JFolder.jsp': 'post:cmd=.*&tabID=2&path=.*&submit=Execute', 'help.asp': 'theAct=ReadReg\\&thePath=.*', 'devshell.(asp|php)': 'cmd\\=.*\\&btnCommand\\=Execute或pass=devilzc0der', 'r57.php': 'Show\\s*phpinfo\\(\\)[\\s\\S]*php\\.ini[\\s\\S]*cpu[\\s\\S]*mem[\\s\\S]*tmp', 'JspSpy': 'JspSpy\\s*Ver[\\s\\S]*\\<a[^>]*\\>File\\s*Manager\\</a\\>', 'ASPXSpy': '\\<a[^>]*www\\.rootkit\\.net\\.cn[^>]*\\>ASPXSpy\\s*Ver或ASPXSpy=21232f297a57a5a743894a0e4a801fc3', 'jsp': '([^&=\\s]+)=\\w&z0=[^&]*?&z1=', 'php': '([^&=\\s]+)=@eval\\(', 'aspx': '([^&=\\s]+)=retponse\\.Write\\("->\\|"\\)', 'asp': '([^&=\\s]+)=eval\\(', 'zombie.asp': 'ip\\=.*\\&port=.*&scan=.*', 'comment_webshell_2': '[?&]cmd=或[?&]cmd=', 'comment_webshell': 'pass=或pass=', 'g3.php': 'tool=Files&action=view&file=.*', 'Backdoor.PHP.Agent.php': 'pass=dulgandul', 'darkblade.asp': 'DarkBladePass', 'virtule.asp': 'SP=.*&cmd=.*', 'deadman.asp': 'post:sp\\=.*\\&rwpath\\=.*&action\\=.*\\&cmd=.*', 'devshell.aspx': 'cmd\\=.*\\&btnCommand\\=Execute', 'C99': "c99[\\s\\S]*document.todo.act.value='phpinfo'", 'PhpSpy': 'loginpass=', 'comment_webshell_3': '[?&]icesword=或[?&]icesword='}
ret = {'用户': 'user', '密码': 'pass', '邮箱': 'email', '命令': 'cmd'}

for i in ret:
    TestDomain.objects.create(name=i, content=ret[i], ruletype='domain')
print('ret done')
for i in res:
    TestDomain.objects.create(name=i, content=res[i], ruletype='webshell')
print('res done')

