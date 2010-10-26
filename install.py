#!/usr/bin/env python
import os
import glob
import sys
from os.path import join,normpath,abspath
from pprint import pprint

cfgname = '.cfg'
bkpname = 'backup.cfg'
gitrepo = 'git@github.com:durdn/cfg.git'
ignored = ['install.py',
           'install.pyc',
           '.git',
           '.gitignore',
           'README'
           ]

home = normpath(os.environ['HOME'])
backup_folder = normpath(join(home,bkpname)) 
cfg_folder = normpath(join(home,cfgname))

def raw_call(command):
    """
        raw_call(command) --> (result, output)
        Runs the command in the local shell returning a tuple 
        containing :
            - the return result (None for 0, otherwise an int), and
            - the full, stripped standard output.

        You wouldn't normally use this, instead consider call(), test() and system()
    """
    process = os.popen(command)
    output = []
    line = process.readline()

    while not line == "":
        sys.stdout.flush()
        output.append(line)
        line = process.readline()
    result = process.close()

    return (result, "".join(output).strip())

def list_all(path):
    "lists all files in a folder, including dotfiles"
    tmp = sum([glob.glob(normpath(join(a[0],'*')))  for a in os.walk(path)],[])
    return tmp + sum([glob.glob(normpath(join(a[0],'.*')))  for a in os.walk(path)],[])

def assets(rootpath,flist,test):
    return filter(lambda x: test(x), [normpath(join(rootpath,f)) for f in flist])

def local_assets(flist,test):
    return assets(home,flist,test)

def cfg_assets(flist,test):
    return filter(lambda x: test(x) and os.path.split(x)[1] not in ignored,
                  assets(cfg_folder,flist,test))

def backup_affected_assets(cfg_folder, backup_folder):
    "Backup files that would be overwritten by config tracking into backup folder"
    files = local_assets(os.listdir(cfg_folder),lambda x: True)
    for f in files:
        if os.path.exists(f):
            name = os.path.split(f)[1]
            print '    $ mv %s %s' % (f,join(backup_folder,name))

def install_tracked_assets(cfg_folder, destination_folder):
    "Install tracked configuration files into destination folder"
    files = cfg_assets(os.listdir(cfg_folder),os.path.isfile)
    for f in files:
        name = os.path.split(f)[1]
        print '    $ ln %s %s' % (f,join(destination_folder,name))
    dirs = cfg_assets(os.listdir(cfg_folder),os.path.isdir)
    for d in dirs:
        name = os.path.split(d)[1]
        print '    $ ln -s %s %s' % (d,join(destination_folder,name))


if __name__ == '__main__':
    print '|* cfg version 0.1'
    print '|* home is ',home
    print '|* backup folder is',backup_folder
    print '|* cfg folder is',cfg_folder

    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)

    if not os.path.exists(cfg_folder):
        #clone cfg repo
        raw_call("git clone %s %s" % (gitrepo,cfg_folder))
    else:
        if os.path.exists(join(cfg_folder,'.git')):
            print '|-> cfg already cloned to',cfg_folder
        else:
            print '|-> git tracking projects not found in %s, ending program in shame' % cfg_folder
    #print 'local assets'
    #pprint(local_assets(os.listdir(cfg_folder),os.path.isfile))
    #pprint(local_assets(os.listdir(cfg_folder),os.path.isdir))
    #print 'cfg assets'
    #pprint(cfg_assets(os.listdir(cfg_folder),os.path.isfile))
    #pprint(cfg_assets(os.listdir(cfg_folder),os.path.isdir))
    stats = cfg_assets(os.listdir(cfg_folder),lambda x: True)
    print '|* tracking %d assets in %s' % (len(stats),cfgname)
    print '|* backing up affected files...'
    backup_affected_assets(cfg_folder,backup_folder)
    print '* installing tracked config files...'
    install_tracked_assets(cfg_folder,home)