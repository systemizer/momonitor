from django.contrib import admin

from momonitor.main.models import Service,UmpireServiceCheck,SimpleServiceCheck

class ServiceAdmin(admin.ModelAdmin):
    pass

class SimpleServiceCheckAdmin(admin.ModelAdmin):
    pass

class UmpireServiceCheckAdmin(admin.ModelAdmin):
    pass

admin.site.register(Service,ServiceAdmin)
admin.site.register(SimpleServiceCheck,SimpleServiceCheckAdmin)
admin.site.register(UmpireServiceCheck,UmpireServiceCheckAdmin)
