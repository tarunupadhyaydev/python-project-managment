from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User,Permission
from django.contrib.auth.admin import GroupAdmin, UserAdmin


class VSTAdminSite(AdminSite):
    site_header = "VST"
    site_title = "VST Admin Portal"
    index_title = "Welcome to VST Admin Portal"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            if app['app_label'] == 'auth':
                app['name'] = 'User Management'
        return app_list

admin_site = VSTAdminSite(name='vstadmin')

# Register models with the custom admin site
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
