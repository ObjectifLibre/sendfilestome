# Copyright 2018 Gauvain Pocentek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid

from django import views
from django.http import Http404, HttpResponse, FileResponse
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sendfilestome import forms
from sendfilestome import models
from sendfilestome import utils


def _set_user_props(user):
    user.can_upload = True
    user.can_download = True

    if settings.SFTM_UPLOAD_AUTH_ENABLED:
        user.can_upload = user.is_authenticated

    if settings.SFTM_DOWNLOAD_AUTH_ENABLED:
        user.can_download = user.is_authenticated


def _get_env(local_env):
    env = {'auth_enabled': utils.auth_enabled()}
    env.update(local_env)
    return env


class Index(views.View):
    def _list_containers(self, request):
        containers = models.Container.objects.all()
        # Should we list containers marked as non-listable?
        if not (settings.SFTM_LIST_ALL_WHEN_AUTHENTICATED and
                request.user.is_authenticated):
            containers = containers.filter(listable=True)
        # don't list containers that require authentication is the user is
        # anonymous
        if not request.user.is_authenticated:
            containers = containers.filter(requires_auth=False)

        return containers

    def get(self, request):
        _set_user_props(request.user)

        if request.user.can_download:
            containers = self._list_containers(request)
        else:
            containers = []

        form = forms.ContainerCreateForm()
        env = _get_env({'containers': containers, 'form': form})
        return render(request, 'containers.html', env)

    def post(self, request):
        _set_user_props(request.user)
        if not request.user.can_upload:
            raise PermissionDenied

        form = forms.ContainerCreateForm(request.POST)
        if form.is_valid():
            container = form.save(commit=False)
            if not container.name:
                container.name = str(uuid.uuid4())
            container.save()
            return redirect(reverse('container', args=[container.name]))

        containers = self._list_containers(request)

        env = _get_env({'containers': containers, 'form': form})
        return render(request, 'containers.html', env)


class Container(views.View):
    def get(self, request, container_name):
        _set_user_props(request.user)
        if not request.user.can_download:
            raise Http404

        container = get_object_or_404(models.Container, name=container_name)
        if container.requires_auth and not request.user.is_authenticated:
            raise Http404

        files = models.SFTMFile.objects.filter(container=container)
        upload_form = forms.SFTMFileUpload(initial={'container': container})
        edit_form = forms.ContainerCreateForm(instance=container)
        env =_get_env({'container': container,
                       'files': files,
                       'upload_form': upload_form,
                       'edit_form': edit_form})
        return render(request, 'container.html', env)

    def post(self, request, container_name):
        _set_user_props(request.user)

        container = get_object_or_404(models.Container, name=container_name)
        upload_form = forms.SFTMFileUpload(request.POST, request.FILES)
        edit_form = forms.ContainerCreateForm(request.POST, instance=container)
        if 'upload' in request.POST:
            if not request.user.can_upload:
                raise PermissionDenied
            if upload_form.is_valid():
                uploaded_file = upload_form.save()
                url = reverse('container', args=[container_name])
                return redirect('%s?highlight=%s' % (url, uploaded_file.id))
        elif 'description' in request.POST:
            if edit_form.is_valid():
                if not container.name:
                    container.name = str(uuid.uuid4())
                edit_form.save()
                return redirect(reverse('container', args=[container.name]))

        files = models.SFTMFile.objects.filter(container=container)
        env =_get_env({'container': container,
                       'files': files,
                       'upload_form': upload_form,
                       'edit_form': edit_form})
        return render(request, 'container.html', env)

    def delete(self, request, container_name):
        _set_user_props(request.user)
        if not request.user.can_upload:
            raise PermissionDenied

        container = get_object_or_404(models.Container, name=container_name)
        container.delete()
        return HttpResponse(status=202)


class SFTMFile(views.View):
    def get(self, request, container_name, file_name):
        _set_user_props(request.user)
        if not request.user.can_download:
            raise Http404

        container = get_object_or_404(models.Container, name=container_name)
        uploaded_file = get_object_or_404(models.SFTMFile, name=file_name,
                                          container=container)
        response = FileResponse(uploaded_file.file)
        response['Content-Length'] = uploaded_file.file.size
        response['Content-Disposition'] = ('attachment; filename="%s"' %
                                           file_name)
        return response

    def delete(self, request, container_name, file_name):
        _set_user_props(request.user)
        if not request.user.can_upload:
            raise PermissionDenied

        container = get_object_or_404(models.Container, name=container_name)
        uploaded_file = get_object_or_404(models.SFTMFile, name=file_name,
                                          container=container)

        uploaded_file.delete()
        return HttpResponse(status=202)


class ContainerAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, container_name):
        _set_user_props(request.user)
        upload_form = forms.SFTMFileUpload(request.POST, request.FILES)
        if upload_form.is_valid():
            if not request.user.can_upload:
                raise PermissionDenied
            uploaded_file = upload_form.save(commit=False)

            try:
                container = models.Container.objects.get(name=container_name)
            except models.Container.DoesNotExist:
                # if container does not exist, we create it
                container_form = forms.ContainerCreateForm()
                container = container_form.save(commit=False)
                container.name = container_name
                container.listable = True
                container.requires_auth = True
                container.save()

            uploaded_file.container = container
            uploaded_file.save()
            return Response("file correctly upload in  " + container_name, status=200)
        return Response(upload_form.errors, status=500)
