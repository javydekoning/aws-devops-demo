import json
import os
import requests
import re
import boto3
import time


def lambda_handler(event, context):
    codedeploy = boto3.client('codedeploy')

    print('Got event:')
    print(json.dumps(event))

    count = 0
    while count <= 10:
        localtime = time.localtime()
        result = time.strftime("%I:%M:%S %p", localtime)

        r = requests.get(os.environ.get('TEST_LISTENER'))
        res = re.search(r"background\-color: \w+", r.text)
        print(result + ': ' + res.group())
        count += 1
        time.sleep(5)

    if re.match(r".*(blue|green).*", res.group()):
        status = 'Succeeded'
        response = "✅ *CONTINUING DEPLOYMENT {}*\n\n```\n{}\n```\nMatches BLUE or GREEN".format(
            event["DeploymentId"], res.group())

    else:
        status = 'Failed'
        response = "❌ *HALTING DEPLOYMENT {}*\n\n```\n{}\n```\nDoes not match BLUE or GREEN".format(
            event["DeploymentId"], res.group())

    print(response)

    try:
        codedeploy.put_lifecycle_event_hook_execution_status(
            deploymentId=event["DeploymentId"],
            lifecycleEventHookExecutionId=event["LifecycleEventHookExecutionId"],
            status=status
        )

        return True
    except Exception as e:
        print("Unexpected error: %s" % e)
        return False
