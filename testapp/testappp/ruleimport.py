#  原始38条检验规则的导入
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from testappp.models import TestRule, TestSet
b = TestSet.objects.all().delete()
c = TestRule.objects.all().delete()
c1 = ['火狐NEW WebShell.asp', '法克僵尸大马.asp', '土司搞基asp大马.asp', '传说中的草泥马4.0.asp', '不灭之魂2014改进版本.asp', 'wso.aspx', 'r57142.php', 'dx.php', 'c37.php', 'silic.php', 'ce.asp', 'cmd.asp', 'websniff.aspx', 'webadmin.aspx', 'strong.php', 'job.asp', 'JFolder.jsp', 'help.asp', 'devshell.(asp|php)', 'r57.php', 'JspSpy', 'ASPXSpy', 'jsp', 'php', 'aspx', 'asp', 'zombie.asp', 'comment_webshell_2', 'comment_webshell', 'g3.php', 'Backdoor.PHP.Agent.php', 'darkblade.asp', 'virtule.asp', 'deadman.asp', 'devshell.aspx', 'C99', 'PhpSpy', 'comment_webshell_3']
c2 = ['SP=.*&cmd=.*', 'sp=.*&cmd=.*', 'SP=.*&cmd=.*', 'sp=.*&cmd=.*', 'sp=.*&wscript=(yes|no)&cmd=.*', '&cmd=.*&Button123=Run', 'post:cmd=.*&dir=.*&submit=Execute', 'post:dxval=.*(同时url=dxmode=CMD)', 'get:action=CLI&dir=.*', 'post:cmd=.*&show=%BB%D8%CF%D4', 'post:sp=.*&cmd=.*', 'SP=cmd.exe&', 'ddlist=.*&txtport=\\d+&txtMinisize=\\d+&txtkeywords=.*&txtlogfile=.*&txtpackets=.*&Starts=Start', 'multipart/form-data:Content-Disposition:\\s+form-data;\\s+name="Button_cmdRun"', 'cmd=.*&show=%BB%D8%CF%D4%B4%B0%BF%DA', 'post:action=filesystem&curPath=.*&fsAction=.*', 'post:cmd=.*&tabID=2&path=.*&submit=Execute', 'theAct=ReadReg\\&thePath=.*', 'cmd\\=.*\\&btnCommand\\=Execute', 'Show\\s*phpinfo\\(\\)[\\s\\S]*php\\.ini[\\s\\S]*cpu[\\s\\S]*mem[\\s\\S]*tmp', 'JspSpy\\s*Ver[\\s\\S]*\\<a[^>]*\\>File\\s*Manager\\</a\\>', '\\<a[^>]*www\\.rootkit\\.net\\.cn[^>]*\\>ASPXSpy\\s*Ver', '([^&=\\s]+)=\\w&z0=[^&]*?&z1=', '([^&=\\s]+)=@eval\\(', '([^&=\\s]+)=Response\\.Write\\("->\\|"\\)', '([^&=\\s]+)=eval\\(', 'ip\\=.*\\&port=.*&scan=.*', '[?&]cmd=', 'pass=', 'tool=Files&action=view&file=.*', '', '', 'SP=.*&cmd=.*', 'post:sp\\=.*\\&rwpath\\=.*&action\\=.*\\&cmd=.*', 'cmd\\=.*\\&btnCommand\\=Execute', "c99[\\s\\S]*document.todo.act.value='phpinfo'", '', '[?&]icesword=']
c3 = ['', '', '', '', '', '', '', '', '', 'admin_silicpass=759df00ad725b46faef0a0f00daaaaa3', '', '', '', '', 'admin_spiderpass=006b9cc00c32c5204465978fbdf012a4', '', '', '', 'pass=devilzc0der', '', '', 'ASPXSpy=21232f297a57a5a743894a0e4a801fc3', '', '', '', '', '', '[?&]cmd=', 'pass=', '', 'pass=dulgandul', 'DarkBladePass', '', '', '', '', 'loginpass=', '[?&]icesword=']
d = []
d.append(c1)
d.append(c2)
d.append(c3)
try:
    for i in range(38):
        TestRule.objects.create(name=d[0][i], url=d[1][i], cookie=d[2][i])
    TestSet.objects.create(host='127.0.0.1', port='1521', username='web', password='123456', type='orcl', table='http_restore_info', lastid=0, speed=10000)
    print('done')
except:
    print('failed')