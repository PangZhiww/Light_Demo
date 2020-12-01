import random
from django.shortcuts import render, HttpResponse

from django.conf import settings

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django_redis import get_redis_connection

from django import forms
from web import models
from utils.tencent.sms import send_sms_single
import random
from utils import encrypt
from web.forms.bootstrap import BootStrapForm


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    """
    表单
    """

    password = forms.CharField(
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "密码长度不能小于8个字符",
            "max_length": "密码长度不能大于64个字符"
        },
        label='密码',
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码'})
    )

    confirm_password = forms.CharField(
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "确认密码长度不能小于8个字符",
            "max_length": "确认密码长度不能大于64个字符"
        },
        label='确认密码',
        widget=forms.PasswordInput(attrs={'placeholder': '请再次输入密码'})
    )

    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r"^(1[3|4|5|6|7|8|9])\d{9}$", '手机号格式错误'), ]
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={'placeholder': '请输入验证码'})
    )

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在!')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在!')

        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    def clean_confirm_password(self):

        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])

        if pwd != confirm_pwd:
            raise ValidationError("两次密码不一致")

        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')

        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        # mobile_phone = self.cleaned_data['mobile_phone']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码输入错误，请重新输入')

        return code


class SendSmsForm(forms.Form):
    """
    验证码表单验证
    """
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r"^(1[3|4|5|6|7|8|9])\d{9}$", '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """
        手机号检验的钩子
        :return:
        """
        mobile_phone = self.cleaned_data['mobile_phone']
        # 判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')

        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()

        if tpl == 'login':
            if not exists:
                raise ValidationError("手机号不存在")
        else:
            # 校验数据库中食肉已有手机号
            if exists:
                raise ValidationError('手机号已存在')

        # 发短信 & 写入redis
        code = random.randrange(100000, 999999)
        print(code)
        # sms = send_sms_single(mobile_phone, template_id, [code, ])
        # if sms['result'] != 0:
        #     raise ValidationError('短信发送失败，{}'.format(sms['errmsg']))

        # 验证码写入redis
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=300)

        return mobile_phone


class LoginSMSForm(BootStrapForm, forms.Form):
    """
    短信登录
    """
    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r"^(1[3|4|5|6|7|8|9])\d{9}$", '手机号格式错误'), ]
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={'placeholder': '请输入验证码'})
    )

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not exists:
            raise ValidationError('手机号不存在')

        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # 手机号不存在，则验证码无需校验
        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码输入错误，请重新输入')

        return code


class LoginForm(BootStrapForm, forms.Form):
    """
    账号密码登录
    """
    username = forms.CharField(label="用户名/邮箱/手机号")
    password = forms.CharField(label="密码", widget=forms.PasswordInput())  # render_value=True 保留密码
    code = forms.CharField(label="图片验证码")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return encrypt.md5(pwd)

    def clean_code(self):
        """
        钩子
        图片验证码是否正确？
        :return:
        """
        # 读取用户输入的验证码
        code = self.cleaned_data['code']
        # 去session获取自己的验证码
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期，请点击验证码重新获取')

        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码输入错误')

        return code
