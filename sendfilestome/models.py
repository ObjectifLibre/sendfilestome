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

from  django.core.validators import RegexValidator
from django.db import models


name_validator = RegexValidator(r'^[0-9a-zA-Z-_.]+$',
                                'Only [0-9a-zA-Z-_.] characters are allowed')


class Container(models.Model):
    name = models.CharField(
        max_length=64, validators=[name_validator], unique=True, blank=True,
        help_text="Leave empty to generate a random name (UUID)")
    description = models.CharField(max_length=256, blank=True)
    listable = models.BooleanField(
        default=True,
        help_text="Uncheck this option to hide the container from the listing")
    requires_auth = models.BooleanField(
        default=False,
        help_text=("Check this option to make the container available to "
                   "authenticated users only"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SFTMFile(models.Model):
    name = models.CharField(max_length=64, blank=False,
                            validators=[name_validator])
    file = models.FileField()
    container = models.ForeignKey('Container', on_delete=models.CASCADE,
                                  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'file'
        unique_together = ('name', 'container')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
