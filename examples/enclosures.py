# -*- coding: utf-8 -*-
###
# (C) Copyright [2020] Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

from pprint import pprint

from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewException
from config_loader import try_load_from_file

# This example is compatible only for C7000 enclosures
config = {
    "ip": "<oneview_ip>",
    "credentials": {
        "userName": "<username>",
        "password": "<password>"
    },
    "api_version": "<api_version>",
    "enclosure_group_uri": "/rest/enclosure-groups/06475bf3-084b-4874",
    "enclosure_hostname": "",
    "enclosure_username": "",
    "enclosure_password": "",
}

enclosure_name = "Enc"

# Declare a CA signed certificate file path.
certificate_file = ""

# Try load config from a file (if there is a config file)
config = try_load_from_file(config)

# The hostname, enclosure group URI, username, and password must be set on the configuration file
options = {
    "enclosureGroupUri": config['enclosure_group_uri'],
    "hostname": config['enclosure_hostname'],
    "username": config['enclosure_username'],
    "password": config['enclosure_password'],
    "licensingIntent": "OneView"
}

# Get Enclosure resource object
oneview_client = OneViewClient(config)
enclosure_resource = oneview_client.enclosures

# Get all enclosures
print("Get all enclosures")
enclosures = enclosure_resource.get_all()
for enc in enclosures:
    print('  {name}'.format(**enc))

enclosure = enclosure_resource.get_by_name(enclosure_name)
if not enclosure:
    # Creates an enclosure and reurns created enclosure object
    enclosure = enclosure_resource.add(options)
print("Enclosure '{name}'.\n  URI = '{uri}'".format(**enclosure.data))

# Get by URI.
print("Find an enclosure by URI")
uri = enclosure.data['uri']
enclosure = enclosure_resource.get_by_uri(uri)
pprint(enclosure.data)

# Update name of the newly added enclosure
update_name = "Enc-Updated"
print("Updating the enclosure with name " + update_name)
headers = {'If-Match': '*'}
enclosure.patch('replace', '/name', update_name, custom_headers=headers)
print("  Done.\n  URI = '{uri}', name = {name}".format(**enclosure.data))

# Update configuration
print("Reapplying the appliance's configuration on the enclosure")
try:
    enclosure.update_configuration()
    print("  Done.")
except HPOneViewException as e:
    print(e.msg)

print("Retrieve the environmental configuration data for the enclosure")
try:
    environmental_configuration = enclosure.get_environmental_configuration()
    print("  Enclosure calibratedMaxPower = {calibratedMaxPower}".format(**environmental_configuration))
except HPOneViewException as e:
    print(e.msg)

# Set the calibrated max power of an unmanaged or unsupported enclosure
print("Set the calibrated max power of an unmanaged or unsupported enclosure")

try:
    configuration = {
        "calibratedMaxPower": 2500
    }
    enclosure_updated_encConf = enclosure.update_environmental_configuration(configuration)
    print("  Done.")
except HPOneViewException as e:
    print(e.msg)

# Refresh the enclosure
print("Refreshing the enclosure")
try:
    refresh_state = {"refreshState": "RefreshPending"}
    enclosure.refresh_state(refresh_state)
    print("  Done")
except HPOneViewException as e:
    print(e.msg)

# Buid the SSO URL parameters
print("Build the SSO (Single Sign-On) URL parameters for the enclosure")
try:
    sso_url_parameters = enclosure.get_sso('Active')
    pprint(sso_url_parameters)
except HPOneViewException as e:
    print(e.msg)

# Get Statistics specifying parameters
print("Get the enclosure statistics")
try:
    enclosure_statistics = enclosure.get_utilization(fields='AveragePower',
                                                     filter='startDate=2016-06-30T03:29:42.000Z',
                                                     view='day')
    pprint(enclosure_statistics)
except HPOneViewException as e:
    print(e.msg)

# Create a Certificate Signing Request (CSR) for the enclosure.
bay_number = 1  # Required for C7000 enclosure
csr_data = {
    "type": "CertificateDtoV2",
    "organization": "organization",
    "organizationalUnit": "organization unit",
    "locality": "locality",
    "state": "state",
    "country": "country",
    "commonName": "name"
}
try:
    enclosure.generate_csr(csr_data, bay_number=bay_number)
    print("Generated CSR for the enclosure.")
except HPOneViewException as e:
    print(e.msg)

# Get the certificate Signing Request (CSR) that was generated by previous POST.
try:
    csr = enclosure.get_csr(bay_number=bay_number)
    with open('enclosure.csr', 'w') as csr_file:
        csr_file.write(csr["base64Data"])
    print("Saved CSR(generated by previous POST) to 'enclosure.csr' file")
except HPOneViewException as e:
    print(e.msg)

# Import CA signed certificate to the enclosure.
try:
    # Certificate has to be signed by CA before running the task.
    certificate_file = "enclosure.csr"
    with open(certificate_file, "r") as file_object:
        certificate = file_object.read()

    certificate_data = {
        "type": "CertificateDataV2",
        "base64Data": certificate
    }

    enclosure.import_certificate(certificate_data, bay_number=bay_number)
    print("Imported Signed Certificate  to the enclosure.")
except HPOneViewException as e:
    print(e.msg)

# Get Enclosure by scope_uris
if oneview_client.api_version >= 600:
    try:
        enclosures_by_scope_uris = enclosure.get_all(scope_uris="\"'/rest/scopes/a070577f-0dfa-4b86-ba48-863f3cac291e'\"")
        if len(enclosures_by_scope_uris) > 0:
            print("Found %d Enclosures" % (len(enclosures_by_scope_uris)))
            i = 0
            while i < len(enclosures_by_scope_uris):
                print("Found Enclosures by scope_uris: '%s'.\n  uri = '%s'" % (enclosures_by_scope_uris[i]['name'], enclosures_by_scope_uris[i]['uri']))
                i += 1
            pprint(enclosures_by_scope_uris)
        else:
            print("No Enclosures Group found.")
    except HPOneViewException as e:
        print(e.msg)

# Remove the recently added enclosure
enclosure.remove()
print("Enclosure removed successfully")
