#!/usr/bin/python3
#
# dump a server's serial number

import sys
import argparse
import logging
import imcsdk
from imcsdk.imchandle import ImcHandle


class DumpSN:
    """A class to dump a SN"""

    def __init__(self, args):
        """Initialize instance: Logging"""
        self.log = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s'))
        self.log.addHandler(handler)
        self.imchandle = None
        self.process_cli(args)


    def process_cli(self, args):
        """Parse CLI args & set log level"""
        self.log.debug("Entering process_cli.")
        argparser = argparse.ArgumentParser()
        argparser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
        argparser.add_argument('-d', '--debug', action='store_true', help="Debug output")
        argparser.add_argument('-c', '--connect', required=True, action='store', help="Host to connect to")
        argparser.add_argument('-u', '--username', required=True, action='store', help="Host username")
        argparser.add_argument('-p', '--password', required=True, action='store', help="Host password")

        self.args = argparser.parse_args()

        if self.args.debug == True:
            print("Debug mode enabled.")
            self.log.setLevel(logging.DEBUG)
        elif self.args.verbose == True:
            print("Verbose output enabled.")
            self.log.setLevel(logging.INFO)

        self.log.info("CLI processed. args=%s", str(self.args))
        self.log.debug("Leaving process_cli.")

    def imc_connect(self):
        self.log.debug("Entering imc_connect.")
        self.imchandle = ImcHandle(self.args.connect,
                                   self.args.username,
                                   self.args.password)
        self.imchandle.login()
        self.log.info("Connected to %s.", self.args.connect)
        self.log.debug("Leaving imc_connect.")

    def imc_disconnect(self):
        self.log.debug("Entering imc_disconnect.")
        self.imchandle.logout()
        self.log.info("Disconnected from %s.", self.args.connect)
        self.log.debug("Leaving imc_connect.")


    def dump_SN(self):
        self.log.debug("Entering dump_classid.")

        try:
            object_array = self.imchandle.query_classid('computeRackUnit')
            self.log.debug("object_array=%s", object_array)
            i=0
            for object in object_array:
                self.log.debug("object_array[%s]=%s", i, object)
                self.log.warning("Serial Number %s: %s", i, object.serial)
                i = i + 1
        except Exception as e:
            self.log.info("Exception: %s", e)
            self.imc_disconnect()

        self.log.debug("Leaving dump_MIT.")
        
if __name__ == "__main__":

    instance = DumpSN(sys.argv)

    instance.imc_connect()
    instance.dump_SN()
    instance.imc_disconnect()
    # ...
