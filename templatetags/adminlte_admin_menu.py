# -*- coding: utf-8 -*-
# @Author: Phu Hoang
# @Date:   2017-01-19 17:20:24
# @Last Modified by:   Phu Hoang
# @Last Modified time: 2017-01-19 18:57:18

from django import template

import re

from django.urls import reverse

import logging, logging.config
import sys

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)

class _Menu:
    parents = []
    children = []
    models_icon = {}

    def clear(self):
        self.parents = []
        self.children = []

    def add(self, label, link='', icon='', id_='', parent=''):

        if id_ == '':
            id_ = label

        if parent != '':
            child = {
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            }

            self.children.append(child)

            for idx, parent_item in enumerate(self.parents):

                if parent in parent_item:
                    self.parents[idx][parent]['children'].append(child)
                else:
                    for idx, child_item in enumerate(self.children):
                        if parent in child_item:
                            self.children[idx][parent]['children'].append(child)

        else:
            self.parents.append({
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            })

    def render(self, context, menus=None):
        menus = {} if menus is None else menus
        request = context['request']

        r = ''

        if len(menus) <= 0:
            # sorted(self.parents)
            menus = self.parents
            if(request.path == reverse('admin:index')):
                r = '<li class="nav-item"><a href="' + reverse('admin:index') + '" class="nav-link active"><i class="nav-icon fas fa-tachometer-alt"></i> <p>Dashboard</p></a></li>'
            else:
                r = '<li class="nav-item"><a href="' + reverse('admin:index') + '" class="nav-link"><i class="nav-icon fas fa-tachometer-alt"></i> <p>Dashboard</p></a></li>'

        for group in menus:
            key = [key for key in group][0]
            icon = '<i class="far fa-circle nav-icon"></i>'

            if group[key]['icon'] != '':
                if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>', group[key]['icon']):
                    icon = group[key]['icon']
                else:
                    icon = '<i class="%s"></i>' % (group[key]['icon'])

            if len(group[key]['children']) > 0:
                r += '<li class="nav-item has-treeview"><a href="#" class="nav-link">%s <span>%s</span><span class="pull-right-container"><i class="fas fa-angle-left right"></i></span></a><ul class="treeview-menu">\n' % (
                    icon, group[key]['label'])

                r += self.render(context, group[key]['children'])

                r += '</ul></li>\n'

            else:
                if(request.path == reverse('admin:index')):
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s <p>%s</p></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])
                else:
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s <p>%s</p></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])

        return r

    def admin_apps(self, context, r):
        request = context['request']
        for app in context['available_apps']:
            logging.info(app)
            appName = app['name']
            app_icon = 'fa-edit'
            if app['app_label'] == 'auth':
                appName = 'Group Management'
                app_icon = 'fa-user-plus'
            if app['app_label'] == 'users':
                appName = 'User Management'
                app_icon = 'fa-users-cog'
            elif app['app_label'] == 'organizations':
                app_icon = 'fa-landmark'
            elif app['app_label'] == 'projects':
                app_icon = 'fa-briefcase'
            elif app['app_label'] == 'tasks':
                app_icon = 'fa-list'
            elif app['app_label'] == 'time_tracker':
                app_icon = 'fa-clock'

            if(str(app['app_url']) in request.path):
                    r += '<li class="nav-item has-treeview menu-open"><a href="#" class="nav-link active"><i class="nav-icon fas %s"></i> <p>%s</p><p><i class="fas fa-angle-left right"></i></p></a><ul class="nav nav-treeview">\n' % (app_icon,appName)
            else:
                r += '<li class="nav-item has-treeview"><a href="#" class="nav-link"><i class="nav-icon fas %s"></i> <p>%s</p><p><i class="fas fa-angle-left right"></i></p></a><ul class="nav nav-treeview">\n' % (app_icon,appName)

            for model in app['models']:
                if 'add_url' in model:
                    url = model['add_url']

                if 'change_url' in model:
                    url = model['change_url']

                # if 'delete_url' in model:
                #     url = model['delete_url']

                if 'admin_url' in model:
                    url = model['admin_url']

                icon = '<i class="far fa-circle nav-icon"></i>'
                if model['name'] == 'Users':
                    icon = '<i class="fas fa-users nav-icon"></i>'
                if model['name'] == 'Groups':
                    icon = '<i class="fas fa-layer-group nav-icon"></i>'
                elif model['name'] == 'Organizations':
                    icon = '<i class="fas fa-sitemap nav-icon"></i>'
                elif model['name'] == 'Projects':
                    icon = '<i class="fas fa-project-diagram nav-icon"></i>'
                elif model['name'] == 'Tasks':
                    icon = '<i class="fas fa-tasks nav-icon"></i>'
                elif model['name'] == 'Time Tracker':
                    icon = '<i class="fas fa-hourglass nav-icon"></i>'

                if model['object_name'].title() in self.models_icon:
                    if self.models_icon[model['object_name'].title()] != '':
                        if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>', self.models_icon[model['object_name'].title()]):
                            icon = self.models_icon[model['object_name'].title()]
                        else:
                            icon = '<i class="%s"></i>' % (self.models_icon[model['object_name'].title()])
                if(request.path == url):
                    r += '<li class="nav-item"><a href="%s" class="nav-link active">%s %s</a></li>' % (url, icon, model['name'])
                else:
                    r += '<li class="nav-item"><a href="%s" class="nav-link">%s %s</a></li>' % (url, icon, model['name'])

            r += '</ul></li>\n'

        return r

    def set_model_icon(self, model_name, icon):
        self.models_icon[model_name.title()] = icon

    def get_model_icon(self, context):

        icon = '<i class="far fa-circle nav-icon"></i>'
        if context['model']['object_name'].title() in self.models_icon:

            if self.models_icon[context['model']['object_name'].title()] != '':
                if re.match(r'<([a-z]*)\b[^>]*>(.*?)</\1>', self.models_icon[context['model']['object_name'].title()]):
                    icon = self.models_icon[context['model']['object_name']]
                else:
                    icon = '<i class="%s"></i>' % (self.models_icon[context['model']['object_name'].title()])

        return icon

register = template.Library()

Menu = _Menu()


@register.simple_tag(takes_context=True, name='menu')
def menu_tag(context):
    return Menu.admin_apps(context, Menu.render(context))


@register.simple_tag(takes_context=True, name='icon')
def icon_tag(context):
    return Menu.get_model_icon(context)



# from adminlte3_theme import admin_menu
# from django_adminlte3 import admin_menu
# #from adminlte3_theme.templatetags import admin_menu

# def get_admin_menu():
#     return [
#         {
#             'title': 'Dashboard',
#             'url': '/admin/',
#             'icon': 'fa fa-dashboard',
#         },
#         {
#             'title': 'Users',
#             'url': '/admin/auth/user/',
#             'icon': 'fa fa-users',
#             'children': [
#                 {
#                     'title': 'Groups',
#                     'url': '/admin/auth/group/',
#                     'icon': 'fa fa-group',
#                 },
#             ],
#         },
#     ]