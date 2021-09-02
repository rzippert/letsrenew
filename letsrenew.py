#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from socket import socket
from OpenSSL import SSL
#from OpenSSL import crypto
from datetime import datetime
import idna
from cryptography import x509
from cryptography.x509.oid import NameOID 

"""Let's Renew main file"""

class cert:
    """Represents a certificate and its data"""
    def __init__(self, host, port=443, check_address=None):
        """As a minimum, a host has te be provided as the cert is instantiated"""
        self.host = host
        self.port = port
        self.check_address = check_address
        self.cert = None
        self.certsan = None
        self.certisuer = None
        self.get_cert()
        self.read_cert()

    def read_cert(self):
        try:
            self.certsan = self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            self.certissuer = self.cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)

        except SSL.Error as e:
            print('Parse Error: {0}'.format(str(e)))
            exit(1)

    def print(self):
        print(f'CN="{self.cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}" SAN={self.certsan.value.get_values_for_type(x509.DNSName)} NotAfter="{self.cert.not_valid_after}"')
        print(f'  TimeToExpire="{self.cert.not_valid_after - datetime.now()}" Issuer="{self.certissuer[0].value}"')

    def get_cert(self):
        hostidna = idna.encode(self.host)
        sslcontext = SSL.Context(SSL.TLSv1_2_METHOD)
        sslcontext.check_hostname = False
        sslcontext.verify_mode = SSL.VERIFY_NONE

        try:
            sslsocket = socket()
            if self.check_address != None:
                sslsocket.connect((self.check_address, self.port))
            else:
                sslsocket.connect((self.host, self.port))
            sslconnection = SSL.Connection(sslcontext, sslsocket)
            sslconnection.set_connect_state()
            sslconnection.set_tlsext_host_name(hostidna)
            sslconnection.do_handshake()
            self.cert = sslconnection.get_peer_certificate().to_cryptography()
            sslconnection.close()
            sslsocket.close()

        except SSL.Error as e:
            print(f'Download error: {str(e)}')
            exit(0)




#ideas
#alert for less than 30 days left (failed automation)
#print json for javascript dashboard
#monitor unexpected renews (before schedule)
#detect renew schedule (soonest and latest registered renew)
#quick cert issue (dns validation, manual install)
#monitor CA transparency logs
#check if the cert received covers the queried host (wrong cert installed)
#monitor CA changes
#autodetect fronted hosts (single entry for both internal and externally checked certs)
#check if chain is valid (for each browser/system)
#monitor VPN certs
#monitor certs from folder
#keylength keyalg best practices monitor

#https://gist.github.com/gdamjan/55a8b9eec6cf7b771f92021d93b87b2c
