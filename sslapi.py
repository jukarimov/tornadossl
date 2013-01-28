#!/usr/bin/env python

from OpenSSL import crypto, SSL, rand
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from os.path import exists, join
from subprocess import PIPE, Popen

def gencert(
  keylen,
  countryName,
  stateOrProvinceName,
  localityName,
  organizationName,
  organizationUnitName,
  commonName,
  emailAddress):
  '''
    create a new self-signed cert and keypair
  '''

  # create a key pair
  k = crypto.PKey()
  k.generate_key(crypto.TYPE_RSA, keylen or 1024)

  # create a self-signed cert
  cert = crypto.X509()
  cert.get_subject().C            = countryName
  cert.get_subject().ST           = stateOrProvinceName
  cert.get_subject().L            = localityName
  cert.get_subject().O            = organizationName
  cert.get_subject().OU           = organizationUnitName
  cert.get_subject().CN           = commonName
  cert.get_subject().emailAddress = emailAddress
  cert.set_serial_number(1000)
  cert.gmtime_adj_notBefore(0)
  cert.gmtime_adj_notAfter(365*24*60*60)
  cert.set_issuer(cert.get_subject())
  cert.set_pubkey(k)
  cert.sign(k, 'sha1')

  return {
    'cert': crypto.dump_certificate(crypto.FILETYPE_PEM, cert),
    'pkey': crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
  }

def getrandom(keylen=8):
  return rand.bytes(keylen)

def certext(certstr):
  p1 = Popen(['printf', certstr], stdout=PIPE)
  p2 = Popen(['openssl', 'x509', '-text'], stdin=p1.stdout, stdout=PIPE)
  p1.stdout.close()
  output = p2.communicate()[0]
  return output
