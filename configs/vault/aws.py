import boto3
from botocore.exceptions import ClientError
import json
import logging
from pprint import pprint

class Aws:

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("configs")
        session = boto3.session.Session()
        client = session.client(
            service_name = 'secretsmanager'
        )
        self.secretsmanager = client

    def provision(self, secrets):
        secrets = Aws._build_secrets(secrets)

        for k in secrets.keys():
            secret_path = k
            if 'base_path' in self.config:
                secret_path = self.config['base_path'] + k

            secret_arn = None

            try:
                get_secret_value_response = self.secretsmanager.get_secret_value(
                        SecretId=secret_path
                    )
                secret_arn = get_secret_value_response['ARN']
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    secret_arn = None
                else:
                    raise e

            if secret_arn is None:
                self.logger.debug('Creating ' + secret_path)
                self.secretsmanager.create_secret(
                    Name=secret_path,
                    # KmsKeyId
                    SecretString = json.dumps(secrets[k])
                )
            else:
                self.logger.debug('Updating ' + secret_path)
                self.secretsmanager.put_secret_value(
                    SecretId=secret_arn,
                    SecretString=json.dumps(secrets[k])
                )


    def _build_secrets(data, path=[]):
        secrets = {}
        path_str = "/".join(path)
        for k in data.keys():
            if type(data[k]) is dict:
                path.append(k)
                sub_secrets = Aws._build_secrets(data[k], path)
                path.pop()
                secrets.update(sub_secrets)
            else:
                if path_str not in secrets.keys():
                    secrets[path_str] = {}
                secrets[path_str][k] = data[k]
        return secrets

    def resolve(self, config, path):
        path = Aws._local_path_to_secretmanager_path(path.split("."))

        secret_path = path[0]
        if "base_path" in self.config:
            secret_path = self.config['base_path'] + secret_path

        self.logger.debug("Resolving " + secret_path + "." + path[1])

        try:
            get_secret_value_response = self.secretsmanager.get_secret_value(
                    SecretId=secret_path
                )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise Exception("Secret not found")
            else:
                raise e
        
        if not 'SecretString' in get_secret_value_response:
            raise Exception('Only support resolving JSON-formatted SecretString')
        
        secret = json.loads(get_secret_value_response['SecretString'])

        return Aws._resolve_from_json(secret, path[1].split('.'))

    def _local_path_to_secretmanager_path(path):
        return "/".join(path[:len(path)-1]), ".".join(path[-1:])


    def _resolve_from_json(obj, path):
        nextkey = path.pop(0)

        if not nextkey in obj:
            return None

        if len(path) == 0:
            return obj[nextkey]
        else:
            return Aws._resolve_from_json(obj[nextkey], path)


