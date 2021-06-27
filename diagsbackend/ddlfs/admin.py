from django.contrib import admin
from .models import Device
from .models import LeakyFeederGateway
from .models import Site
from .models import People
from .models import Alarm
from .models import AlarmSnapshot
from .models import AlarmSnapshotItem
from .models import UnmanagedDevice
from .models import TopologyNode
from .models import TopologySnapshot
from .models import TopologyConnection
from .models import ManualConnection
from .models import Acknowledgement


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'hw_id', 'status', 'parent_connection')
    list_filter = ('status', 'parent_connection')


admin.site.register(Device, DeviceAdmin)


admin.site.register(LeakyFeederGateway)
admin.site.register(Site)
admin.site.register(People)
admin.site.register(Alarm)
admin.site.register(AlarmSnapshot)
admin.site.register(AlarmSnapshotItem)
admin.site.register(UnmanagedDevice)
admin.site.register(TopologyNode)
admin.site.register(TopologySnapshot)
admin.site.register(TopologyConnection)
admin.site.register(ManualConnection)
admin.site.register(Acknowledgement)
