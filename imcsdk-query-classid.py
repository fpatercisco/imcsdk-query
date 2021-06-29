#!/usr/bin/python3
#
# dump all MO's of a class_id(s)

import sys
import argparse
import logging
import inspect
import imcsdk
from imcsdk.imchandle import ImcHandle
from imcsdk.imcexception import ImcException


class DumpClassID:
    """A class to dump all MO's with a given class_id(s)"""

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
        self.log.debug("Entering %s", inspect.stack()[0][3])
        argparser = argparse.ArgumentParser()
        argparser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
        argparser.add_argument('-d', '--debug', action='store_true', help="Debug output")
        argparser.add_argument('-c', '--connect', required=True, action='store', help="Host to connect to")
        argparser.add_argument('-C', '--class_id', required=True, action='store', help="Class ID to dump")
        argparser.add_argument('-u', '--username', required=True, action='store', help="Host username")
        argparser.add_argument('-p', '--password', required=True, action='append', help=
                               """Host password. Specify more than 1 to try multiple.""")

        self.args = argparser.parse_args()

        if self.args.debug == True:
            print("Debug mode enabled.")
            self.log.setLevel(logging.DEBUG)
        elif self.args.verbose == True:
            print("Verbose output enabled.")
            self.log.setLevel(logging.INFO)

        self.log.info("CLI processed. args=%s", str(self.args))
        self.log.debug("Leaving %s", inspect.stack()[0][3])

    def imc_connect(self):
        """Connect to the server's IMC"""
        self.log.debug("Entering %s", inspect.stack()[0][3])
        for password in self.args.password:
            try:
                self.imchandle = ImcHandle(self.args.connect,
                                           self.args.username,
                                           password)
                self.imchandle.login()
                self.log.info("Connected to %s.", self.args.connect)
                self.log.debug("Leaving %s", inspect.stack()[0][3])
                return True
            except ImcException as e:
                if int(e.error_code) == 551:
                    self.log.warning("Password %s rejected.", password)
                else:
                    self.log.warning("ImcException raised: %s", e)
        self.log.debug("Leaving %s", inspect.stack()[0][3])

    def imc_disconnect(self):
        """Disconnect from the server's IMC"""
        self.log.debug("Entering %s", inspect.stack()[0][3])
        self.imchandle.logout()
        self.log.info("Disconnected from %s.", self.args.connect)
        self.log.debug("Leaving %s", inspect.stack()[0][3])


    def dump_classid(self):
        """Dump the MO's with the requested class_id"""
        self.log.debug("Entering %s", inspect.stack()[0][3])

        self.log.info("Dumping class ID %s...", self.args.class_id)
        try:
            object_array = self.imchandle.query_classid(self.args.class_id)
            self.log.debug("object_array=%s", object_array)
            i=0
            for object in object_array:
                self.log.warning("object_array[%s]=%s", i, object)
                i = i + 1
        except Exception as e:
            self.log.info("Exception: %s", e)
            self.imc_disconnect()

        self.log.debug("Leaving %s", inspect.stack()[0][3])
        
if __name__ == "__main__":

    instance = DumpClassID(sys.argv)

    if instance.imc_connect():
        instance.dump_classid()
        instance.imc_disconnect()
    # ...
