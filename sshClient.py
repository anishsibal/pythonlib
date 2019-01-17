### Author : Anish Sibal
import io
import paramiko
import socks
import re
import os
import logging
import getpass


class SshClient:
  "Wrapper for paramiko SSHClient. Supports socks5 proxy, reading ssh agent keys and sudo passwords"
  TIMEOUT = 20
  username = getpass.getuser()
  def __init__(self, host, port=22, username=username, password=None, key=None, passphrase=None, timeout=TIMEOUT):
    self.username = username
    self.password = password
    self.client = paramiko.SSHClient()
    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    agent = paramiko.Agent()
    agent_keys = agent.get_keys()
    if 'http_proxy' in os.environ:
      if re.match(r'socks5', os.environ['http_proxy']):
        # For production use socks5 proxy
        proxy_host, proxy_port = (re.sub(r'^socks5://', "",os.environ['http_proxy'])).split(':')
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port), False)
        paramiko.client.socket.socket = socks.socksocket
        logging.info("Using Socks5 Proxy")

    conn = False

    if len(agent_keys) > 0:
      for mykey in agent_keys:
        try:
          self.client.connect(host, port, username=username, password=password,
                              pkey=mykey, timeout=timeout, allow_agent=False)
          conn = True
          break
        except:
          pass

    if conn is False:
      if key is not None:
        key = paramiko.RSAKey.from_private_key(io.StringIO(key), password=passphrase)

      logging.info("Making connection to host " + host)
      self.client.connect(host, port, username=username, password=password, pkey=key,
                          timeout=timeout, allow_agent=False)

  def close(self):
    if self.client is not None:
      self.client.close()
      self.client = None

  def execute(self, command, sudo=False):
    feed_password = False
    if sudo and self.username != "root":
      loggging.info("Using sudo")
      command = "sudo -S -p '' %s" % command
      feed_password = self.password is not None and len(self.password) > 0

    logging.info("Running Command " + command)
    stdin, stdout, stderr = self.client.exec_command(command)

    if feed_password:
      stdin.write(self.password + "\n")
      stdin.flush()
    exit_status = stdout.channel.recv_exit_status()
    logging.info("Command exit status is " + str(exit_status))
    return {'out': stdout.read(),
            'err': stderr.read(),
            'retval': exit_status}

  def upload(self, src_path, dest_path, file_mode=None):
    sftp = self.client.open_sftp()
    out = sftp.put(src_path, dest_path)
    if file_mode:
      sftp.chmod(dest_path, file_mode)
    return out
if __name__ == "__main__":
  client = SshClient(host='localhost', port=22, username='root')
  try:
    ret = client.execute('dmesg', sudo=True)
    print ("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
  finally:
    client.close()
