import logging, logging.config
from collections import OrderedDict

from django import template
from django.conf import settings
from django.contrib import admin
from django.urls import resolve, reverse, NoReverseMatch
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django import VERSION
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

register = template.Library()

PERM = 'view' if (VERSION[0] == 2 and VERSION[1] > 0) or (VERSION[0] > 2) else 'change'


class MenuItem:
    url = None
    title = None
    children = None
    weight = 10
    active = False
    icon = 'fa-circle'
    count = 0

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if self.children is None:
            self.children = list()

    def __repr__(self):
        return "<MenuItem url=%s title=%s icon=%s count=%s>" % (self.url, self.title,self.icon,self.count)

class MenuGroup(MenuItem):
    pass


def get_admin_site(context):
    try:
        current_resolver = resolve(context.get('request').path)
        index_resolver = resolve(reverse('%s:index' % current_resolver.namespaces[0]))

        if hasattr(index_resolver.func, 'admin_site'):
            return index_resolver.func.admin_site

        for func_closure in index_resolver.func.__closure__:
            if isinstance(func_closure.cell_contents, admin.AdminSite):
                return func_closure.cell_contents
    except:
        pass

    return admin.site
    

def get_app_list(context, order=True):
    admin_site = get_admin_site(context)
    request = context['request']

    app_dict = {}
    for model, model_admin in admin_site._registry.items():
        app_label = model._meta.app_label
        try:
            has_module_perms = model_admin.has_module_permission(request)
        except AttributeError:
            has_module_perms = request.user.has_module_perms(app_label)  # Fix Django < 1.8 issue

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.model_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                    'model_admin': model_admin,
                    'count': model.objects.count(),
                }
                if perms.get(PERM, False):
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    try:
                        name = model._meta.app_config.verbose_name
                    except NameError:
                        name = app_label.title()
                    app_dict[app_label] = {
                        'name': name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=admin_site.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                        'count': model.objects.count(),
                    }

    # Sort the apps alphabetically.
    app_list = list(app_dict.values())

    if order:
       # app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

    return app_list


def get_group_weight(title):
    weights = getattr(settings, 'MENU_WEIGHT', {})
    return weights.get(title, 10)


def make_menu_item(url, title, weight=10,icon='fa-circle',count=0):
    return MenuItem(url=url, title=title, weight=weight,icon=icon,count=count)


def make_menu_group(title, children=None, weight=None):
    return MenuGroup(title=title, children=children, weight=weight or get_group_weight(title))


@register.simple_tag(takes_context=True)
def get_admin_menu(context):
    request = context['request']
    apps = get_app_list(context, True)
    #logging.info(apps)
    menu = OrderedDict({
        _('Dashboard'): make_menu_group(_('Dashboard'), weight=1, children=[
            make_menu_item(reverse('admin:index'), _('Dashboard'), weight=0,icon='fa-tachometer-alt',count=0)
        ])
    })

    for app in apps:
        if not app['has_module_perms']:
            continue

        
        #logging.info(app['app_label'])
        app_icon = 'fa-edit'
        if app['app_label'] == 'auth':
            app_icon = 'fa-user-plus'
            appName = 'Groups'
            # appLabel = 'auth'
        if app['app_label'] == 'users':
            app_icon = 'fa-users'
            appName = 'Users'
            # appLabel = 'users'
        elif app['app_label'] == 'organizations':
            app_icon = 'fa-landmark'
            appName = 'Organizations'
            # appLabel = 'organizations'
        elif app['app_label'] == 'projects':
            app_icon = 'fa-briefcase'
            appName = 'Projects'
            # appLabel = 'projects'
        elif app['app_label'] == 'tasks':
            app_icon = 'fa-list'
            appName = 'Tasks'
            # appLabel = 'tasks'
        elif app['app_label'] == 'time_tracker':
            app_icon = 'fa-clock'
            appName = 'Timesheet'
            #appLabel = 'time_tracker'
           
        for model in app['models']:
            if not model['perms'][PERM]:
                continue

            model_admin = model['model_admin']
            #menu[icon] = app_icon
            # title = capfirst(getattr(model_admin, 'menu_group', app['name']))
            title = capfirst(getattr(model_admin, 'menu_group', appName))
            if title not in menu:
                menu[title] = make_menu_group(title)

            group = menu[title]
            #logging.info(app_icon)
            appIcon = app_icon
            count = model['count']
            submenu = make_menu_item(
                url=model['admin_url'],
                title=capfirst(getattr(model_admin, 'menu_title', model['name'])),
                weight=getattr(model_admin, 'menu_order', 10),
                icon=appIcon,
                count=count,
            )
            group.children.append(submenu)

            extra = getattr(model_admin, 'extra_menu_items', [])
            extra_func = getattr(model_admin, 'get_extra_menu_items', None)
            if extra_func:
                extra = extra_func(request)

            for item in extra:
                if len(item) == 2:
                    url, extra_title = item
                    weight = 1
                else:
                    url, extra_title, extra_group, weight = item
                    if extra_group not in menu:
                        menu[extra_group] = make_menu_group(extra_group)
                    group = menu[extra_group]

                submenu = make_menu_item(
                    url=url,
                    title=capfirst(extra_title),
                    weight=weight,
                    icon=appIcon,
                    count=count,
                )
                group.children.append(submenu)

    # sort the menu by weight
    menu = OrderedDict(sorted(menu.items(), key=lambda x: x[1].weight))
    for title in reversed(list(menu.keys())):
        menu[title].children.sort(key=lambda x: x.weight)

        for idx, sub in enumerate(menu[title].children):
            #logging.info(sub)
            menu[title].icon = sub.icon
            #menu[count] = sub.count
            if idx == 0:
                menu[title].url = sub.url
            if sub.url == reverse('admin:index'):
                if request.path == sub.url:
                    sub.active = True
                    menu[title].active = True
            else:
                if request.path.startswith(sub.url):
                    sub.active = True
                    menu[title].active = True
    #logging.info(menu)
    return menu