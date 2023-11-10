
"""
PostgreSQL Role management 
"""

import sys


# changing path to access rds/helpers package/modules
sys.path.append('../')

from package_helpers import module_global as helpers

# main program
if __name__ == "__main__":

    # load the configuration
    config=helpers.load_configuration()

    # validate the configuration
    try:
        helpers.validate_configuration(config)
    except ValueError as e:
        helpers.generate_log('ERROR', config, str(e))
        sys.exit(1)

    if config['use_iam'] == 'true':
        # Initialize the RDS client with attached iam role to an ec2 instance
        # for tf workstation like environments
        client = boto3.client('rds', region_name=config['region_name'])
    else:
        # Initialize the RDS client using secret keys
        client = boto3.client('rds', aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            aws_session_token=config['aws_session_token'],
            region_name=config['region_name'])

    # List of RDS instances to upgrade from the config.yaml file
    db_instance_identifiers = config.get('db_instance_identifiers', [])

    for db_instance_identifier in db_instance_identifiers:

        # validate if the instance identifier mentioned in the config file exists
        helpers.validate_instance_identifier(db_instance_identifier, client)

        # minor version updgrade
        helpers.minor_version_upgrade_rds_instance(config, db_instance_identifier, client)

    # track the modified instances status
    helpers.track_db_instances_status(db_instance_identifiers, client)

# end of script
