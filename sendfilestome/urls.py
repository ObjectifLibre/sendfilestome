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

from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from rest_framework.authtoken import views as rest_views

from sendfilestome import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(),
        name='account_login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(next_page='/'),
        name='account_logout'),
    url('^$', views.Index.as_view(), name='index'),
    url('c/(?P<container_name>[^/]+)/(?P<file_name>[a-zA-Z0-9-_.]+)$',
        views.SFTMFile.as_view(), name='file'),
    url('c/(?P<container_name>[^/]+)$', views.Container.as_view(),
        name='container'),
    url(r'^api/container/(?P<container_name>[^/]+)$', views.ContainerAPI.as_view()),
    url(r'^api/token', rest_views.obtain_auth_token)
]
