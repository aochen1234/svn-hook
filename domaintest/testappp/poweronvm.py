from __future__ import print_function

from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

import argparse
import atexit
import getpass
import sys
import ssl
host = '192.168.134.236'
user = 'root'
port = 443
password = 'Kuaile@2017614'

vnames = {"vname1":"ESXI6.0"}
#,"vname2":"vCENTER6.0"
def GetArgs():
   """
   Supports the command-line arguments listed below.
   """

   parser = argparse.ArgumentParser(description='Process args for powering on a Virtual Machine')
   parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store', help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store', help='Password to use when connecting to host')
   parser.add_argument('-v', '--vmname', required=True, action='append', help='Names of the Virtual Machines to power on')
   args = parser.parse_args()
   return args

def WaitForTasks(tasks, si):
   """
   Given the service instance si and tasks, it returns after all the
   tasks are complete
   """

   pc = si.content.propertyCollector

   taskList = [str(task) for task in tasks]

   # Create filter
   objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                                                            for task in tasks]
   propSpec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                         pathSet=[], all=True)
   filterSpec = vmodl.query.PropertyCollector.FilterSpec()
   filterSpec.objectSet = objSpecs
   filterSpec.propSet = [propSpec]
   filter = pc.CreateFilter(filterSpec, True)

   try:
      version, state = None, None

      # Loop looking for updates till the state moves to a completed state.
      while len(taskList):
         update = pc.WaitForUpdates(version)
         for filterSet in update.filterSet:
            for objSet in filterSet.objectSet:
               task = objSet.obj
               for change in objSet.changeSet:
                  if change.name == 'info':
                     state = change.val.state
                  elif change.name == 'info.state':
                     state = change.val
                  else:
                     continue

                  if not str(task) in taskList:
                     continue

                  if state == vim.TaskInfo.State.success:
                     # Remove task from taskList
                     taskList.remove(str(task))
                  elif state == vim.TaskInfo.State.error:
                     raise task.info.error
         # Move to next version
         version = update.version
   finally:
      if filter:
         filter.Destroy()

# Start program
def main():
   try:
      for vmname in vnames.values():
         if not len(vmname):
            print("No virtual machine specified for poweron")
            sys.exit()

         context = None
         if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
         si = SmartConnect(host=host,
                           user=user,
                           pwd=password,
                           port=int(port),
                           sslContext=context)
         if not si:
            print("Cannot connect to specified host using specified username and password")
            sys.exit()

         atexit.register(Disconnect, si)

         # Retreive the list of Virtual Machines from the inventory objects
         # under the rootFolder
         content = si.content
         objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.VirtualMachine],
                                                           True)
         vmList = objView.view
         objView.Destroy()

         # Find the vm and power it on
         tasks = [vm.PowerOn() for vm in vmList if vm.name in vnames]

         # Wait for power on to complete
         WaitForTasks(tasks, si)

         print("Virtual Machine(s) have been powered on successfully")
   except vmodl.MethodFault as e:
      print("Caught vmodl fault : " + e.msg)
   except Exception as e:
      print("Caught Exception : " + str(e))

# Start program
if __name__ == "__main__":
   main()
