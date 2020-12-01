from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.sms.v20190711 import sms_client, models
from django.conf import settings

import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

from django.conf import settings


def send_sms_single(phone_num, template_id, template_param_List):
    """
    发送单条短信
    :param phone_num: 手机号
    :param template_id: 腾讯云短信模板ID
    :param template_param_List: 短信模板所需参数列表
    :return:
    """
    appid = settings.TENCENT_SMS_APP_ID  # 自己应用ID
    appkey = settings.TENCENT_SMS_APP_KEY  # 自己应用key
    sms_sign = settings.TENCENT_SMS_SIGN
    sender = SmsSingleSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num, template_id, template_param_List, sign=sms_sign)
    except HTTPError as e:
        response = {'result': 1000, 'errmsg': '网络异常发送失败'}
    return response


def send_sms_multi(phone_num_list, template_id, param_List):
    """
    批量发送短信
    :param phone_num_list: 手机号列表
    :param template_id: 腾讯云短信模板ID
    :param param_List: 短信模板所需参数列表
    :return:
    """
    appid = settings.TENCENT_SMS_APP_ID  # 自己应用ID
    appkey = settings.TENCENT_SMS_APP_KEY  # 自己应用key
    sms_sign = settings.TENCENT_SMS_SIGN
    sender = SmsMultiSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num_list, template_id, param_List, sign=sms_sign)
    except HTTPError as e:
        response = {'result': 1000, 'errmsg': '网络异常发送失败'}
    return response

# def send_message(phone, random_code, template_id="621794"):
#     try:
#         CHINA = "+86"
#         phone = "{}{}".format(CHINA, phone)
#
#         cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
#         client = sms_client.SmsClient(cred, settings.TENCENT_CITY)
#         req = models.SendSmsRequest()
#
#         # 短信应用ID: 短信SdkAppid在 [短信控制台] 添加应用后生成的实际SdkAppid，示例如1400006666
#         req.SmsSdkAppid = settings.TENCENT_APP_ID
#         # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，签名信息可登录 [短信控制台] 查看
#         req.Sign = settings.TENCENT_SIGN
#
#         # 下发手机号码，采用 e.164 标准，+[国家或地区码][手机号]
#         # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
#         req.PhoneNumberSet = [phone, ]
#         # 模板 ID: 必须填写已审核通过的模板 ID。模板ID可登录 [短信控制台] 查看
#         req.TemplateID = template_id
#         # 模板参数: 若无模板参数，则设置为空
#         req.TemplateParamSet = [random_code, ]
#         # 通过client对象调用DescribeInstances方法发起请求。注意请求方法名与请求对象是对应的。
#         # 返回的resp是一个DescribeInstancesResponse类的实例，与请求对象对应。
#         resp = client.SendSms(req)
#
#         # 输出json格式的字符串回包
#         if resp.SendStatusSet[0].Code == "Ok":
#             return True
#
#         print(resp.to_json_string(indent=2))
#
#     except TencentCloudSDKException as err:
#         print(err)
#         pass
