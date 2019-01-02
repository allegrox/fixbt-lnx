#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser


class MyConfigParser(ConfigParser.ConfigParser):
	def __init__(self,defaults=None):
		ConfigParser.ConfigParser.__init__(self,defaults=None)
	def optionxform(self, optionstr):
		return optionstr

def getDevName(fname):
	try:
		cfginfo = ConfigParser.ConfigParser()
		cfginfo.read(fname)
		print(cfginfo.sections())
		return cfginfo.get('General', 'Name')
	except:
		return None

def DevMenu(m):
	try:
		os.system('clear')
		print('Which one do you want to fix?')
		i = 1
		c = []
		for dname in m:
			print(str(i) + ': ' + dname)
			c.append(dname)
			i += 1;
		print(str(i) + ': Exit')
		x = input('Please enter a number: ')
		if x == i:
			return ''
		return m[c[None if x == 0 else x - 1]]
	except:
		return None


if __name__ == "__main__":

	if (os.geteuid() != 0) or (len(sys.argv) != 2):
		print('Usage: sudo python fixbt.py BTInfo.ini')
		sys.exit(1)

	cfg = MyConfigParser()
	with open(sys.argv[1], 'r') as fr:
		print('open config file')
		cfg.readfp(fr)

	if 'general' in cfg.sections():
		adapter = cfg.get('general', 'adapter').upper().replace('-', ':')
		print(adapter)
		device = cfg.get('general', 'device').upper().replace('-', ':')
		print(device)

	if not os.path.exists('/var/lib/bluetooth/' + adapter):
		print('adapter info not found.')
		sys.exit(1)
	else:
		rdir = '/var/lib/bluetooth/' + adapter + '/'

	DevNameDict = {}
	alist = os.listdir(rdir)
	for i in range(0, len(alist)):
		DevPath = os.path.join(rdir, alist[i])
		if os.path.isdir(DevPath):
			dname = getDevName(DevPath + '/info')
			if dname is not None:
				DevNameDict.update({dname : alist[i]})

	while True:
		FixMac = DevMenu(DevNameDict)
		if FixMac == '':
			print('Exit...')
			sys.exit(1)
		if FixMac is not None:
			break
	print('Replace device name %s with %s .' % (FixMac, device))
	os.rename(rdir + FixMac, rdir + device) 

	print('Modifying BT device parameters.')
	cfgw = MyConfigParser()
	cfgw.read(rdir + device + '/info')
	if 'LongTermKey' not in cfgw.sections():
		print('info file is invalid')
		sys.exit(1)
	else:
		cfgw.set('LongTermKey', 'Rand', int(cfg.get('linux', 'rand'), 16))
		cfgw.set('LongTermKey', 'EDiv', int(cfg.get('linux', 'ediv'), 16))
		cfgw.set('LongTermKey', 'Key', cfg.get('linux', 'ltk').upper())

	with open(rdir + device + '/info', 'w+') as fw:
		cfgw.write(fw)
	print('done.')
