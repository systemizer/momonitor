from django.contrib import admin

from momonitor.main.models import Service,ServiceCheck

class ServiceAdmin(admin.ModelAdmin):
    pass

class ServiceCheckAdmin(admin.ModelAdmin):
    pass

admin.site.register(Service,ServiceAdmin)
admin.site.register(ServiceCheck,ServiceCheckAdmin)
