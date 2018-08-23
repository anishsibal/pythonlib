import sys, os, string, threading, getpass, time
from sshClient import SshClient
from queue import Queue
import logging

TIMEOUT=10
cmd = ""
username = ""
port = ""
password = ""
key = ""
passphrase = ""
timeout = ""
hosts = []
results = {}
parallel = 5
outlock = threading.Lock()

q = Queue(maxsize=0)

def psshClient(args, parallel=parallel):
  """ Parallel ssh using paramiko"""
  global username
  global port
  global password
  global key
  global passphrase
  global timeout
  global cmd
  global sftp_files
  global sftp_files_dest_dir
  global sftp_files_mode

  if 'hosts' not in args:
    raise ValueError("Hosts not specified")
  else:
    hosts = args['hosts']

  if ('cmd' not in args) and ('sftp_files' not in args):
    raise ValueError("Command or SFTP files not specified")

  if 'cmd' not in args:
    cmd = None
  else:
    cmd = args['cmd']

  if 'username' not in args:
    username = getpass.getuser()
  else:
    username = args['username']

  if 'port' not in args:
    port = 22
  else:
    port = args['port']

  if 'password' not in args:
    password = None
  else:
    password = args['password']

  if 'key' not in args:
    key = None
  else:
    key = args['key']

  if 'passphrase' not in args:
    passphrase = None
  else:
    passphrase = args['passphrase']

  if 'timeout' not in args:
    timeout = TIMEOUT
  else:
    timeout = args['timeout']

  if 'sftp_files_dest_dir' not in args:
    sftp_files_dest_dir = "/tmp"
  else:
    sftp_files_dest_dir = args['sftp_files_dest_dir']

  if 'sftp_files' not in args:
    sftp_files = None
  else:
    sftp_files = args['sftp_files']

  if 'sftp_files_mode' in args:
    sftp_files_mode = args['sftp_files_mode']
  else:
    sftp_files_mode = None

  if 'parallel' not in args:
    num_threads = parallel
  else:
    num_threads = args['parallel']

  if len(hosts) < num_threads:
    num_threads = len(hosts)

  logging.info("Launching " + str(num_threads) + " threads")

  for i in range(num_threads):
    worker = threading.Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True) # With setDaemon True, When main thread dies, the threads will die as well.
                           # If not set to true, the program will hang, as main thread will wait for all threads to die.
                           # which will not happen , as there is while True loop with do_stuff
    worker.start()

  for h in hosts:
    results[h] = {}
    q.put(h)

  q.join() # Waits for all tasks put in queue, to be task_done()
  return results

def do_stuff(q):
  # this while loop thread will die when q.join returns i.e parent dies along with it's threads
  while True:
    name = threading.currentThread().getName()
    logging.info("Thread: {0} start get item from queue[current size = {1}]"
                 .format(name, q.qsize()))
    host = q.get()
    workon(host)
    logging.info("Thread: {0} finish process item from queue[current size = {1}]"
                 .format(name, q.qsize()))
    q.task_done()

def workon(host):
  results[host] = {}
  try:
    client = SshClient(host, port=port, username=username,
                       password=password, key=key, passphrase=passphrase,
                       timeout=timeout)
  except:
    error = "ERROR: Can't make connection to host " + host
    print("\033[1;31;40m" + error + "\033[0;37;40m")
    return

  try:
    if sftp_files:
      results[host]['sftp'] = {}
      for name, src_file in sftp_files.items():
        dest_file = sftp_files_dest_dir + "/" + os.path.basename(src_file)
        if sftp_files_mode:
          sftp_out = client.upload(src_file, dest_file, file_mode=sftp_files_mode)
        else:
          sftp_out = client.upload(src_file, dest_file)
        with outlock:
          results[host]['sftp'][name] = sftp_out

    if cmd:
      ret = client.execute(cmd)
      with outlock:
        results[host]['cmd'] = ret
  finally:
    client.close()


"""
args = { 'hosts': [],
         'port': 22,
         'cmd': {'key1': 'command_to_run1',
                 'key2': 'commmand_to_run2'
                }
         'sftp_files': ['file1', 'file2'],
         'sftp_files_dest_dir': 'dest dir',
         'sftp_files_mode': 775
         'username': None,
         'password': None,
         'key': None,
         'passphrase': None,
         'timeout': TIMEOUT
        }
         for cmdKey, cmd in args['cmd'].items():
    try:
      ret = client.execute(cmd)
    finally:
      client.close()
    with outlock:
      results[host][cmdKey] = ret

"""