import subprocess, os

user="bbdebian"
ip="[fe80::df62:1759:93d4:cc23%eth0]"
dest="ASTEP_networking/data/"
password="redacted"

def rsync(fname):

    askpass_script_name='/tmp/askssh.sh'

    with open(askpass_script_name, 'w') as file:
        file.write(f"#!/bin/sh\necho '{password}'\n")
    os.chmod(askpass_script_name, 0o700)

    env = os.environ.copy()
    env["SSH_ASKPASS"] = askpass_script_name
    env["SSH_ASKPASS_REQUIRE"] = "force"
    env["DISPLAY"] = ":0"


    rsync_result=subprocess.run(["rsync", "-v",  f"/home/debian/astep-fw/sw/{fname}", f"{user}@{ip}:{dest}"], # -v verbose tag is important to get stdout describing the files transfered
                                env=env, start_new_session=True,
                                capture_output=True, text=True)
    return rsync_result.stdout

print(rsync("test_rsync_transfer.txt"))
