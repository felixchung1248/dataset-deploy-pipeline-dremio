import requests
import json
import sys
import os

url_sandbox = os.environ.get('DREMIO_SANDBOX_URL')
url_production = os.environ.get('DREMIO_PROD_URL')
sandbox_username = os.environ.get('DREMIO_SANDBOX_USR')
sandbox_password = os.environ.get('DREMIO_SANDBOX_PW')
production_username = os.environ.get('DREMIO_PROD_USR')
production_password = os.environ.get('DREMIO_PROD_PW')

def format_schema(schema):
    # Split the schema string by '.' and wrap each part with quotes
    return ".".join(f'"{part}"' for part in schema.split('.'))

def login(username, password, dremioServer):
  # we login using the old api for now
  loginData = {'userName': username, 'password': password}
  headers = {'content-type':'application/json'}
  response = requests.post('{server}/apiv2/login'.format(server=dremioServer), headers=headers, data=json.dumps(loginData))
  data = json.loads(response.text)
  # retrieve the login token
  token = data['token']
  return token

accesstoken_sandbox = login(sandbox_username, sandbox_password, url_sandbox)
accesstoken_production = login(production_username,production_password,url_production)

def query(payload,env):
    if env == 'PROD':
        endpoint = url_production
        token = accesstoken_production
    else:
        endpoint = url_sandbox
        token = accesstoken_sandbox
        
    response = requests.post(
        f"{endpoint}/api/v3/sql",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )   
        
    if response.status_code == 200:
        jobId = response.json().get("id")
        while True:
            response = requests.get(
                f"{endpoint}/api/v3/job/{jobId}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                jobStatus = response.json().get("jobState")
                if jobStatus == "COMPLETED":
                    result = requests.get(
                                    f"{endpoint}/api/v3/job/{jobId}/results",
                                    headers={"Authorization": f"Bearer {token}"},
                                )
                    rows = result.json().get("rows")
                    return rows
                if jobStatus == "CANCELED" or jobStatus == "FAILED":
                    return None
            else:  
                break
    else:
        print(f"Failed to get job details")

def get_sql(schema,dataset):
    payload = {
        "sql": f"""
                select 
                    v.VIEW_DEFINITION
                from 
                    INFORMATION_SCHEMA.VIEWS v
                where
                    v.TABLE_SCHEMA = '{schema}'
                    and v.TABLE_NAME = '{dataset}'
                """
    }
    result = query(payload,None)
    sql = result[0].get('VIEW_DEFINITION')
    return sql

def create_dataset(sql,schema,dataset):
    payload = {
        "sql": f"""
                CREATE OR REPLACE view {schema}."{dataset}"
                as
                {sql}
                """
    }
    return query(payload,'PROD')
    
        
def parse_key_value_pairs(argv):
    params = {}
    for arg in argv[1:]:  # Skip the script name
        key, value = arg.split('=', 1)
        params[key] = value
    return params

parameters = parse_key_value_pairs(sys.argv)
schema = parameters['schema']
dataset = parameters['dataset']

formatted_schema = format_schema(schema)

sql = get_sql(schema,dataset)
result = create_dataset(sql,formatted_schema,dataset)   

print(result)

