import zlib
import struct
from Crypto.Cipher import AES


class cryptography:
  def __init__(self, parent=None):
    return None

  def _lazysecret( self, secret, blocksize=32, padding='}'):
    """pads secret if not legal AES block size (16, 24, 32)"""
    if not len(secret) in (16, 24, 32):
      return secret + (blocksize - len(secret)) * padding
    return secret

  def encrypt( self, plaintext, secret, lazy=True, checksum=True):
    """encrypt plaintext with secret
    plaintext   - content to encrypt
    secret      - secret to encrypt plaintext
    lazy        - pad secret if less than legal blocksize (default: True)
    checksum    - attach crc32 byte encoded (default: True)
    returns ciphertext
    """
    secret = self._lazysecret(secret) if lazy else secret
    encobj = AES.new(secret, AES.MODE_CFB)
    if checksum:
      plaintext += struct.pack("i", zlib.crc32(plaintext))
    return encobj.encrypt(plaintext)
  
  def decrypt( self, ciphertext, secret, lazy=True, checksum=True):
    """decrypt ciphertext with secret
    ciphertext  - encrypted content to decrypt
    secret      - secret to decrypt ciphertext
    lazy        - pad secret if less than legal blocksize (default: True)
    checksum    - verify crc32 byte encoded checksum (default: True)
    returns plaintext
    """
    secret = self._lazysecret(secret) if lazy else secret
    encobj = AES.new(secret, AES.MODE_CFB)
    plaintext = encobj.decrypt(ciphertext)
    if checksum:
      crc, plaintext = (plaintext[-4:], plaintext[:-4])
      if not crc == struct.pack("i", zlib.crc32(plaintext)):
        raise CheckSumError("checksum mismatch")
    return plaintext

  def encrypt_file( self, input_filename, output_filename, secret_key):
    file_input = open(input_filename, 'r')
    z = self.encrypt( file_input.read(), secret_key )
    file_input.close()
    file_output = open( output_filename, 'w')
    file_output.write(z)
    file_output.close()

  def decrypt_file( self, input_filename, output_filename, secret_key):
    file_input = open(input_filename, 'r')
    z = self.decrypt( file_input.read(), secret_key )
    file_input.close()
    file_output = open( output_filename, 'w')
    file_output.write(z)
    file_output.close()

class CheckSumError(Exception):
    pass

