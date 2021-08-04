import json
import requests
from app import app
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkalimt.request.v20181012 import TranslateGeneralRequest

def translate(text,  source_language, dest_language):
    if source_language == 'zh-cn':
        source_language = 'zh'
    if dest_language == 'zh-cn':
        dest_language = 'zh'
    
    client = AcsClient(app.config['ALI_ACCESSKEY_ID'],
                        app.config['ALI_ACCESSKEY_SECRET'],
                        'cn-hangzhou')
    req = TranslateGeneralRequest.TranslateGeneralRequest()
    req.set_SourceLanguage(source_language)
    if isinstance(text, unicode):
        req.set_SourceText(text.encode('utf-8'))
    else:
        req.set_SourceText(text)
    req.set_FormatType('text')
    req.set_TargetLanguage(dest_language)
    req.set_method('POST')

    try:
        resp = client.do_action_with_exception(req)
    except ClientException, ServerException:
        return 'Error: the translation service failed'
   
    data = json.loads(resp)
    if int(data.get('Code')) != 200:
        return data.get('Message', 'unknown error')
    else:
        return json.loads(resp)['Data']['Translated']
    
    