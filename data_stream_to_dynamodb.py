import re
from string import ascii_letters
import json
import base64
import time
import boto3
import uuid
from datetime import datetime
from pytz import timezone
from decimal import Decimal
db = boto3.resource('dynamodb', region_name='cn-north-1').Table('data_stream')


def lambda_handler(event, context):
    for record in event['Records']:
        try:
            payload = base64.b64decode(record["kinesis"]["data"])
            timestamp=int(time.time())
            Item = {
                'id': str(uuid.uuid4()),
                'time_ns': datetime.now(tz=timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': int(round(time.time() * 1000)),
                'ttl':timestamp + 300,
            }
            data = json.loads(payload)
            for item in data:
                Item.update(dict(zip(re.findall('[%s]+' % ascii_letters, item), re.findall('\d+.?\d+', item))))
            for key in ['CO','AQI','humidity','temperature']:
                try:
                    Item[key]=Decimal(Item[key])
                except Exception as r :
                    print(r)
            db.put_item(Item=Item)
        except Exception as e :
            print(e)

