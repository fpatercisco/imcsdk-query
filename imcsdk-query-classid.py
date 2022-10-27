#!/usr/bin/python3
#
# Query all MO's of a class_id
#
# TODO - support multiple class_ids?
# TODO - improve filtering (booleans?)
# TODO - standardize output 

import sys
import argparse
import logging
import inspect
import imcsdk
from imcsdk.imchandle import ImcHandle
from imcsdk.imcexception import ImcException
import csv


class QueryClassID:
    """A class to output all MO's with a given class_id(s)"""

    def __init__(self, args):
        """Initialize instance: Logging"""
        self.log = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s'))
        self.log.addHandler(handler)
        self.imchandle = None
        self.process_cli(args)
        self.log.debug("Leaving %s", inspect.stack()[0][3])

    def process_cli(self, args):
        """Parse CLI args & set log level"""
        self.log.debug("Entering %s", inspect.stack()[0][3])
        argparser = argparse.ArgumentParser()
        argparser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
        argparser.add_argument('-d', '--debug', action='store_true', help="Debug output")
        argparser.add_argument('-C', '--class_id', required=True, action='store', help="Class ID to dump")
        argparser.add_argument('-c', '--connect', required=False, action='store', help="Host to connect to")
        argparser.add_argument('-u', '--username', required=False, action='store', help="Host username")
        argparser.add_argument('-p', '--password', required=False, action='append', help=
                               """Host password. Specify more than 1 to try multiple.""")
        argparser.add_argument('-i', '--infile', required=False, action='append', help="CSV file with line format \"connect_host,username,password\". Username and password are optional, and those specified on the command-line will be attempted after any that are specified in the file.")
        argparser.add_argument('-f', '--fields', required=False, action='append', help="Only display the named fields in the output, and format output as CSV. Use multiple times for multiple fields. Good for batch queries that will be post-processed.")
        argparser.add_argument('-F', '--filter', required=False, action='append', help="String in the format \"field=value\". Only records where the field \"field\" has value \"value\" will be output. Can be used multiple times.")

        self.args = argparser.parse_args()

        if self.args.debug == True:
            self.log.setLevel(logging.DEBUG)
            self.log.debug("Debug mode enabled.")
        elif self.args.verbose == True:
            self.log.setLevel(logging.INFO)
            self.log.info("Verbose output enabled.")

        if self.args.infile == None and (self.args.connect == None or
                                         self.args.username == None or
                                         self.args.password == None):
            self.log.error("connect, username and password arguments are all required when infile is not given.")
            exit(1)

        self.filters = {}
        if self.args.filter != None:
            for f in self.args.filter:
                l=f.split('=')
                try:
                    self.filters[l[0].strip()] = l[1].strip()
                    self.log.debug("self.filters[%s]=%s", l[0].strip(), l[1].strip())
                except IndexError as e:
                    self.log.warning("Invalid filter ignored: %s", f)

        self.log.info("CLI processed. args=%s, filters=%s", str(self.args), str(self.filters))
        self.log.debug("Leaving %s", inspect.stack()[0][3])

    def imc_connect(self, connect=None, username=None, password=None):
        """Connect to a server's IMC"""
        self.log.debug("Entering %s connect=%s, username=%s, password=%s", inspect.stack()[0][3] , connect, username, password)

        if connect == None:
            connect = self.args.connect
            
        if username == None:
            username = self.args.username

        if username == None:
            self.log.warning("No username was supplied. Trying default of 'admin'")
            username = 'admin'
            
        if self.args.password != None:
            passwords=self.args.password
        else:
            passwords = []
        if password != None:
            passwords = [password] + passwords
            
        self.log.debug("passwords=%s", passwords)

        for password in passwords:
            try:
                self.log.debug("Trying password %s...", password)
                self.imchandle = ImcHandle(connect, username, password)
                self.imchandle.login()
                self.log.info("Connected to %s.", self.args.connect)
                # TODO -- is this a hack? Could it backfire?
                self.args.connect = connect
                self.log.debug("Leaving %s", inspect.stack()[0][3])
                return True
            except ImcException as e:
                self.log.debug("ImcException=%s", e)
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

    def matches_any_filter(self, object):
        self.log.debug("Entering %s", inspect.stack()[0][3])
        """Return True if the object matches any of the current instance's filters"""
        for field in self.filters.keys():
            self.log.debug(f"Checking filter {field}...")
            if getattr(object, field) == self.filters[field]:
                self.log.debug("Matched filter %s", field)
                self.log.debug("Leaving %s", inspect.stack()[0][3])        
                return True
        self.log.debug("Leaving %s", inspect.stack()[0][3])
        return False

    def print_object(self, object):
        """Print the object's fields"""
        self.log.debug("Entering %s", inspect.stack()[0][3])
        self.log.debug("object=%s", object)

        if self.args.fields == None:
            print(object)
        else:
            output = ""
            for field in self.args.fields:
                value = getattr(object, field)
                if len(output) > 1:
                    output = output + ","
                output = output + f"{value}"
            print(str(self.args.connect) + "," + output)
        self.log.debug("Leaving %s", inspect.stack()[0][3])        

    def print_header(self, object):
        self.log.debug("Entering %s", inspect.stack()[0][3])        
        """Print the output header"""

        if self.args.fields != None:
            output = ""
            for field in self.args.fields:
                if len(output) > 0:
                    output = output + ","
                output = output + f"{field}"
            print("connect," + output)
        self.log.debug("Leaving %s", inspect.stack()[0][3])        

    def query_classid(self, print_header=True):
        """ the MO's with the requested class_id"""
        self.log.debug("Entering %s", inspect.stack()[0][3])

        self.log.info("Dumping class ID %s...", self.args.class_id)
        try:
            object_array = self.imchandle.query_classid(self.args.class_id)
            self.log.debug("object_array=%s", object_array)
            i=0
            for object in object_array:
                if i == 0 and print_header == True:
                    self.print_header(object)
                if self.filters == {} or self.matches_any_filter(object):
                    self.print_object(object)
                i = i + 1
        except Exception as e:
            self.log.info("Exception: %s", e)
            self.imc_disconnect()

        self.log.debug("Leaving %s", inspect.stack()[0][3])
        
if __name__ == "__main__":

    instance = QueryClassID(sys.argv)

    if instance.args.infile != None:
        for file in instance.args.infile:
            with open(file) as f:
                reader = csv.reader(f)
                print_header = True
                for row in reader:
                    instance.log.debug("Read row: %s", row)
                    username = None
                    password = None
                    try:
                        password = row[2]
                    except IndexError as e:
                        instance.log.debug(" Password not supplied on this row.")
                    try:
                        username = row[1]
                    except IndexError as e:
                        instance.log.debug(" Username not supplied on this row.")
                    connect = row[0]

                    if instance.imc_connect(connect, username, password):
                        #print(connect)
                        instance.query_classid(print_header=print_header)
                        instance.imc_disconnect()
                    print_header = False # this feels like kind of a hack 

    else:
        # CLI-only mode (no infile)
        if instance.imc_connect():
            instance.query_classid()
            instance.imc_disconnect()
    # ...
