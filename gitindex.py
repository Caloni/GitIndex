import os
from git import Repo
import subprocess
from subprocess import check_output as qx
import argparse


def correctPath(start, path):
  'Returns a unix-type case-sensitive path, works in windows and linux'
  b = ''
  if path[-1] == '/':
    path = path[:-1]
  parts = path.split('\\')
  d = start
  c = 0;
  for p in parts:
    listing = os.listdir(d)
    _ = None;
    for l in listing:
      if p.lower() == l.lower():
        if p != l:
          c += 1
        d = os.path.join(d, l)
        _ = os.path.join(b, l)
        break
    if not _:
      return None
    b = _
  return b


def indexpdb(pdbpath):
  output = qx([args.srcTool, pdbpath, '-r'])
  outputFiles = output.split('\r\n')

  pdbStreamFile = open('pdbstream.txt', 'w')
  print >>pdbStreamFile, 'SRCSRV: ini ------------------------------------------------'
  print >>pdbStreamFile, 'VERSION=1'
  print >>pdbStreamFile, 'INDEXVERSION=2'
  print >>pdbStreamFile, 'VERCTRL=GitHub'
  print >>pdbStreamFile, 'DATETIME=Sun May 24 22:51:33 2015'
  print >>pdbStreamFile, 'SRCSRV: variables ------------------------------------------'
  print >>pdbStreamFile, 'GIT_REVNO=' + revno
  print >>pdbStreamFile, 'GIT_WEB_ADDRESS=' + args.webAddr
  print >>pdbStreamFile, 'GIT_URL=%git_web_address%/%git_revno%/%var2%'
  print >>pdbStreamFile, 'GIT_EXTRACT_TARGET=%targ%\%fnfile%(%var1%)'
  print >>pdbStreamFile, 'GIT_EXTRACT_CMD=cmd /c curl.exe "%git_url%" > "%git_extract_target%"'
  print >>pdbStreamFile, 'SRCSRVTRG=%git_extract_target%'
  print >>pdbStreamFile, 'SRCSRVCMD=%git_extract_cmd%'
  
  print >>pdbStreamFile, 'SRCSRV: source files ---------------------------------------'
  for f in outputFiles:
    if os.path.commonprefix([args.repo, f.lower()]) == args.repo:
      relPath = os.path.relpath(f, args.repo)
      relPath = correctPath(args.repo, relPath)
      if f:
        print >>pdbStreamFile, f + '*' + relPath.replace('\\', '/')
  print >>pdbStreamFile, 'SRCSRV: end ------------------------------------------------'
  pdbStreamFile.close()
  
  subprocess.call([args.pdbStr, '-w', '-p:' + pdbpath, '-s:srcsrv', '-i:pdbstream.txt'])


def iterpdbs(path):
  ret = []
  for dirname, dirnames, filenames in os.walk(path):
    # print path to all filenames.
    for filename in filenames:
      if filename.lower().endswith('.pdb'):
        ret.append(os.path.join(dirname, filename))
  return ret


parser = argparse.ArgumentParser(description='GitHub Index: source index PDBs to use with WinDbg/Curl v. Tosca')
parser.add_argument('--dbgtools', dest='dbgtools', required=True, help='directory where are Debugging Tools installed')
parser.add_argument('--pdbpath', dest='pdbpath', required=True, help='directory where are PDBs')
parser.add_argument('--projname', dest='projname', required=True, help='GitHub projname (e.g. UserName/ProjName)')
parser.add_argument('--repo', dest='repo', required=True, help='directory where is the local repo')
args = parser.parse_args()

args.srcTool = args.dbgtools + r'\srcsrv\srctool.exe'
args.pdbStr= args.dbgtools + r'\srcsrv\pdbstr.exe'
args.repo = args.repo.lower()
args.webAddr = 'https://raw.githubusercontent.com/' + args.projname

repo = Repo(args.repo)
revno = repo.head.object.hexsha
for pdb in iterpdbs(args.pdbpath):
  print pdb
  indexpdb(pdb)

