# imcsdk-query
A utility for querying the CIMC of Cisco UCS servers. Supports individual and batch (input file-based) queries, trying multiple passwords, filtering based on field contents and limiting the fields included in the resulting output.
## TODO
* convert imcsdk-dump-classid.py to a universal tool for querying by class_id or dn, i.e. imcsdk-query
* option to walk+dump tree from a starting DN?
* Refactor individual utilities, i.e. imcsdk-get-SN.py as ImcToolbox? So a single module with multiple utility functions:
  1. set dns
  2. set fan policy
  3. query by class ID
  4. dump drive details
  5. query storagecontroller
  6. dump power data
  7. more as needed
  There should simply be an Imc class with init, connect, disconnect and then the util functions
