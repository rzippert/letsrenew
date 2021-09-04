#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from socket import socket
from OpenSSL import SSL
from datetime import datetime
import idna
from cryptography import x509
from cryptography.x509.oid import NameOID 
import argparse
import json

"""Let's Renew main file"""

class cert:
    """Represents a certificate and its data"""
    def __init__(self, host, port=443, check_address=None, threshold=0):
        """As a minimum, a host has te be provided as the cert is instantiated"""
        self.host = host
        self.port = port
        self.check_address = check_address
        self.cert = None
        self.certsan = None
        self.certisuer = None
        self.threshold = threshold
        self.alert = False

        self.get_cert()


    def read_cert(self):
        try:
            self.certsan = self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            self.certissuer = self.cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            self.CN = self.cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            self.SAN = self.certsan.value.get_values_for_type(x509.DNSName)
            self.notAfter = self.cert.not_valid_after
        except SSL.Error as e:
            print('Parse Error: {0}'.format(str(e)))
            exit(1)
        self.verify_cert()
    
    def verify_cert(self):
        if self.threshold >= int((self.notAfter - datetime.now()).total_seconds() / 86400):
            self.alert = True
        elif self.threshold == 0:
            self.alert = True
    
    def get_dict(self):
        selfdict = {"CN": self.CN,
                    "SAN": self.SAN,
                    "NotAfter": str(self.notAfter),
                    "DaysToExpire": int((self.notAfter - datetime.now()).total_seconds() / 86400),
                    "Issuer": self.certissuer[0].value }
        return selfdict

    def get_json(self):
        return json.dumps(self.get_dict())

    def json(self):
        if self.alert is True:
            print(self.get_json())

    def print(self):
        if self.alert is True:
            print(f'CN="{self.CN}" SAN={self.SAN} NotAfter="{self.notAfter}"')
            print(f'  TimeToExpire="{self.notAfter - datetime.now()}" Issuer="{self.certissuer[0].value}"')

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

        self.read_cert()



def parse_arguments():
    parser = argparse.ArgumentParser(prog="letsrenew", epilog="Author: Renato Zippert",
                                     description="Actively tracks short lived certificates (like those from Let's Encrypt) for renewal failures.")
    parser.add_argument("hostname",
                        action="store", help="Hostname that will be requested from the webserver.")
    parser.add_argument("-a", "--address",
                        action="store", required=False, help="Alternate address to connect (to circumvent proxies, balancers, etc...).")
    parser.add_argument("-p", "--port", default=443, type=int,
                        action="store", required=False, help="Alternate port to connect to.")
    parser.add_argument("-j", "--json", default=False,
                        action="store_true", required=False, help="Output in JSON format.")
    parser.add_argument("-l", "--alert", default=0, type=int,
                        action="store", required=False, help="Output only on alerts. Specify it as the validity threshold in days. 0 for Always output (default).")

    userArguments = parser.parse_args()
    configs = dict()

    configs["address"] = None
    configs["port"] = None
    configs["json"] = None
    configs["alert"] = None

    configs["hostname"] = userArguments.hostname
    if userArguments.address != None:
        configs["address"] = userArguments.address
    if userArguments.port != None:
        configs["port"] = userArguments.port
    if userArguments.json != None:
        configs["json"] = userArguments.json
    if userArguments.alert != None:
        configs["alert"] = userArguments.alert

    return configs

def main():
    configs = parse_arguments()
    checkcert = None
    if configs["address"] != None:
        checkcert = cert(host=configs["hostname"], port=configs["port"], check_address=configs["address"], threshold=configs["alert"])
    else:
        checkcert = cert(host=configs["hostname"], port=configs["port"], threshold=configs["alert"])
    if configs["json"] is True:
        checkcert.json()
    else:
        checkcert.print()

main()

#ideas
#alert for less than 30 days left (failed automation)
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
