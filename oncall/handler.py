import requests
import slackweb
import boto3
import json


session = boto3.session.Session()
client = session.client(service_name='secretsmanager',region_name='ap-southeast-2')
get_secret_value_response = client.get_secret_value(SecretId='pagerduty')
secret = get_secret_value_response['SecretString']
json_secret = json.loads(secret)
# print(json_secret['pd_api_key'])

slack = slackweb.Slack(url=json_secret['slack_webhook'])

# Update to match your chosen parameters
TIME_ZONE = 'UTC'
INCLUDE = []
USER_IDS = []
ESCALATION_POLICY_IDS = [json_secret['escalation_policy']]
SCHEDULE_IDS = [json_secret['schedule_id']]
SINCE = ''
UNTIL = ''
EARLIEST = False

def list_oncalls():
    url = 'https://api.pagerduty.com/oncalls'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=json_secret['pd_api_key'])
    }
    payload = {
        'time_zone': TIME_ZONE,
        'include[]': INCLUDE,
        'user_ids[]': USER_IDS,
        'escalation_policy_ids[]': ESCALATION_POLICY_IDS,
        'schedule_ids[]': SCHEDULE_IDS,
        'since': SINCE,
        'until': UNTIL,
        'earliest': EARLIEST
    }
    r = requests.get(url, headers=headers, params=payload)
    print('Status Code: {code}'.format(code=r.status_code))
    user = r.json()['oncalls'][0]['user']['summary']
    print(user)
    slack.notify(text="engineer on call {0}".format(user))

    return r.status_code, user

def do(event, context):
    status_code, user = list_oncalls()

    response = {
        "statusCode": status_code,
        "body": user
    }
    
    return response

if __name__ == "__main__":
    do('', '')    