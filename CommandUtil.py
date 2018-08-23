import subprocess

def runCmd(args, timeout=180):
    """
    Runs a command with  timeout . Default timeout is 180 seconds

    Args:
     args: List of command args
     timeout: Defaults to 180

   Returns:
     bool: True if command ran succesfully, otherwise False
     errmsg or None: Error message if command fails, otherwise None
     CompletedProcess Object or None: On command successful completion subprocess.CompletedProcess
                                      object, othersie None
   Example:
    import CommandUtil
    args=["ls", "-las"]
    status,errmsg,p=runCmd(args)
    
    if status is False:
     print(errmsg)
     sys.exit(1)

    for line in p.stdout.splitlines():
     print(line)
    """

    
    try:
        p=subprocess.run(args,stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE,timeout=timeout,check=True,
                         universal_newlines=True)
        
    except subprocess.CalledProcessError as e:
        errmsg=" ". join(args)
        errmsg+="\nProgram exited with " + str(e.returncode) + " exit status"
        if e.stdout:
            errmsg+="\n" + e.stdout
        if e.stderr:
            errmsg+="\n" + e.stderr            
        return(False,errmsg,None)
    
    except subprocess.TimeoutExpired as e:
        errmsg=" ". join(args)
        errmsg+="\nProgram timedout with " + str(e.timeout) + " seconds"
        if e.stdout:
            errmsg+="\n" + e.stdout
        if e.stderr:
            errmsg+="\n" + e.stderr
        return(False,errmsg,None)

    except OSError as e:
        errmsg=" ". join(args)
        errmsg+="\nProgram exited with error number " + str(e.errno)
        if e.strerror:
            errmsg+="\n" + e.strerror
        return(False,errmsg,None)
    
    return(True,None,p)


############# Test Cases ####################
if __name__ == "__main__":
    print("TESTCASE 1: Testing ls -las output")
    args=["ls", "-las"]
    status,errmsg,p=runCmd(args)
    
    if status is False:
        print(errmsg)
        sys.exit(1)     

    for line in p.stdout.splitlines():
         print(line)

