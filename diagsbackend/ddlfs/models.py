from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from macaddress.fields import MACAddressField


class Node(models.Model):
    x_coord = models.FloatField(null=True,
                                blank=True,
                                verbose_name='x-coordinate')
    y_coord = models.FloatField(null=True,
                                blank=True,
                                verbose_name='y-coordinate')
    parent_connection = models.ForeignKey('ManualConnection', models.SET_NULL,
                                          null=True,
                                          blank=True,
                                          related_name="child")


class ManualConnection(models.Model):
    distance = models.PositiveIntegerField(help_text='in meters',
                                           null=True,
                                           blank=True)
    parent_node_id = models.ForeignKey(Node, models.SET_NULL,
                                       null=True,
                                       blank=True,
                                       related_name="child_connections")

    class Meta:
        db_table = 'manual_connection'


class Site(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LeakyFeederGateway(models.Model):
    hostname = models.CharField(max_length=200,
                                help_text="IP address or hostname")
    port = models.PositiveIntegerField(validators=[MinValueValidator(1024),
                                                   MaxValueValidator(49151)],
                                       help_text="TCP port number")
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True)
    site = models.ForeignKey(Site, models.SET_NULL,
                             null=True,
                             blank=True,
                             related_name="gateways")

    class Meta:
        db_table = 'leaky_feeder_gateway'

    def __str__(self):
        if self.name:
            return "{} ({}:{})".format(self.name, self.hostname, self.port)
        else:
            return "{}:{}".format(self.hostname, self.port)


class Device(Node):
    class DeviceType(models.IntegerChoices):
        BDA = 1, _('LineAmp')
        GMC = 2, _('Gain management controller')
        QP2 = 3, _('QuadPort 2')
        __empty__ = _('(Unknown)')

    class AuxBoardType(models.IntegerChoices):
        LED = 1, _('LED')
        EOC_1C_4G = 2, _('EOC_1C_4G')
        EOC_2C_4G = 4, _('EOC_2C_4G')
        EOC_1C_2G = 6, _('EOC_1C_2G')
        EOC_2C_2G = 8, _('EOC_2C_2G')
        __empty__ = _('(Unknown)')

    class DeviceStatus(models.IntegerChoices):
        DISCOVERED = 1, _('Discovered')
        COMMISSIONED = 2, _('Commissioned')
        ARCHIVED = 3, _('Archived')
        IGNORED = 4, _('Ignored')
        __empty__ = _('(Unknown)')

    hw_id = MACAddressField(integer=False,
                            unique=True,
                            verbose_name='Hardware id')
    created = models.DateTimeField(auto_now_add=True)
    last_heard = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True)
    fw_version = models.CharField(max_length=20,
                                  null=True,
                                  blank=True,
                                  verbose_name="Firmware version")
    hw_revision = models.CharField(max_length=1,
                                   null=True,
                                   blank=True,
                                   verbose_name='Hardware revision')
    aux_board_revision = models.CharField(max_length=1,
                                          null=True,
                                          blank=True)
    serial_number = models.CharField(max_length=10,
                                     null=True,
                                     blank=True)
    product_id = models.CharField(max_length=20,
                                  null=True,
                                  blank=True)
    device_type = models.IntegerField(null=True,
                                      blank=True,
                                      choices=DeviceType.choices)
    aux_board_type = models.IntegerField(null=True,
                                         blank=True,
                                         choices=AuxBoardType.choices)
    status = models.IntegerField(null=True,
                                 blank=True,
                                 choices=DeviceStatus.choices)
    gateway = models.ForeignKey(LeakyFeederGateway, models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='devices')

    def __str__(self):
        if self.name:
            return "{} ({})".format(self.name, self.hw_id)
        else:
            return "{}".format(self.hw_id)


class People(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AlarmSeverity(models.IntegerChoices):
    CRITICAL = 1, _('Critical')
    MAJOR = 2, _('Major')
    MINOR = 3, _('Minor')
    __empty__ = _('(Unknown)')


class AlarmRule(models.IntegerChoices):
    CALIBRATION = 1, _('Calibration fault')
    HARDWARE = 2, _('Hardware fault')
    ENVIRONMENTAL = 3, _('Environmental fault')
    I2C_BUS = 4, _('I2C Bus fault')
    LINE = 10, _('Line fault')
    RF_OVER_DRIVE = 20, _('RF over-drive fault')
    NETWORK = 21, _('Network fault')
    AGC_LEVEL = 22, _('AGC level fault')
    PILOT = 23, _('Pilot fault')
    POE = 24, _('POE fault')
    __empty__ = _('(Unknown)')


class DeviceDiagnostic(models.IntegerChoices):
    LOWER_GAIN_LIMIT_REACHED = 0, _('Lower gain limit reached')
    UPPER_GAIN_LIMIT_REACHED = 1, _('Upper gain limit reached')
    WEAK_BEACON = 2, _('Weak beacon')
    IC2_MASTER_LOCK_UP = 3, _('I2C master lock up')
    HW_REV_UNKNOWN = 4, _('Hardware revision unknown')
    AUX_BOARD_NOT_FOUND = 5, _('Auxiliary board not found')
    ENV_SENSOR_NOT_FOUND = 6, _('Environmental sensor not found')
    DL_RADIO_NOT_FOUND = 7, _('Downlink radio not found')
    UL_RADIO_NOT_FOUND = 8, _('Uplink radio not found')
    MAIN_NVS_NOT_FOUND = 9, _('Main NVS not found')
    WP_NVS_NOT_FOUND = 10, _('WP NVS not found')
    MGC_POSITION_OUT_OF_RANGE = 11, _('MGC position out of range')
    __empty__ = _('(Unknown)')


class AlarmSnapshotItem(models.Model):
    age = models.IntegerField(help_text='in seconds',
                              null=True,
                              blank=True)
    alarm_rule = models.IntegerField(choices=AlarmRule.choices,
                                     verbose_name='Type of alarm')
    severity = models.IntegerField(choices=AlarmSeverity.choices,
                                   verbose_name='Severity of alarm')
    cause = models.IntegerField(choices=DeviceDiagnostic.choices,
                                verbose_name='Problem source')
    alarm_snapshot = models.ForeignKey('AlarmSnapshot', on_delete=models.CASCADE,
                                       related_name='alarms')

    class Meta:
        db_table = 'alarm_snapshot_item'

    def get_severity(self):
        return AlarmSeverity(self.severity)

    def get_rule(self):
        return AlarmRule(self.alarm_rule)

    def __str__(self):
        return "Alarm [type={}, severity={}]".format(self.get_type().label,
                                                     self.get_severity().label)


class Alarm(models.Model):
    # age = models.IntegerField(help_text='in seconds', verbose_name='Age of alarm')
    opened = models.DateTimeField(verbose_name='Alarm opened at')
    resolved = models.DateTimeField(null=True,
                                    blank=True,
                                    verbose_name='Alarm closed at')
    description = models.CharField(max_length=1000,
                                   null=True,
                                   blank=True)
    source_key = models.CharField(max_length=100,
                                  null=True,
                                  blank=True)
    node = models.ForeignKey(Node, models.PROTECT,
                             null=True,
                             blank=True,
                             related_name='node')
    alarm_rule = models.IntegerField(choices=AlarmRule.choices, default=1,
                                     verbose_name='Type of alarm')
    severity = models.IntegerField(choices=AlarmSeverity.choices, default=1,
                                   verbose_name='Severity of alarm')
    ack = models.ForeignKey('Acknowledgement', models.CASCADE,
                            null=True,
                            blank=True, related_name='ack')

    def __str__(self):
        return "{}:{}".format(self.node, self.opened)

    # def severity(self):
    #     for snapshot in self.alarm_snapshot_items.all():
    #         return snapshot.get_severity()
    #     return None

    # def is_active(self):
    #     if self.Alarm.closed(Null=True):
    #         return False
    #     else:
    #         return True


class Acknowledgement(models.Model):
    created = models.DateTimeField(null=True,
                                   blank=True)

    acknowledger = models.ForeignKey(People, models.SET_NULL,
                                     null=True,
                                     blank=True)

    comment = models.CharField(max_length=50000,
                               null=True,
                               blank=True)

    def __str__(self):
        return f"for {self.created}"


class AlarmSnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    critical_count = models.PositiveIntegerField(null=True,
                                                 blank=True,
                                                 verbose_name='Number of critical alarms')
    major_count = models.PositiveIntegerField(null=True,
                                              blank=True,
                                              verbose_name='Number of major alarms')
    minor_count = models.PositiveIntegerField(null=True,
                                              blank=True,
                                              verbose_name='Number of minor alarms')
    device = models.ForeignKey(Device, models.PROTECT,
                               related_name='alarm_snapshots')

    class Meta:
        db_table = 'alarm_snapshot'

    def __str__(self):
        return "{}:{}".format(self.device, self.created)


class BinaryStatus(models.IntegerChoices):
    ACTIVE = 1, _('Active')
    ARCHIVED = 0, _('Archived')
    __empty__ = _('(Unknown)')


class UnmanagedDevice(Node):
    name = models.CharField(max_length=100)
    is_active = models.IntegerField(default=BinaryStatus.ACTIVE,
                                    choices=BinaryStatus.choices,
                                    verbose_name='Status')

    class Meta:
        db_table = 'unmanaged_devices'


class TopologySnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100,
                                   null=True,
                                   blank=True)
    site_code = models.CharField(max_length=100,
                                 null=True,
                                 blank=True)
    gateway_code = models.CharField(max_length=100,
                                    null=True,
                                    blank=True)

    class Meta:
        db_table = 'topology_snapshot'


class TopologyNode(models.Model):
    name = models.CharField(max_length=100)
    hw_id = MACAddressField(integer=False,
                            verbose_name='Hardware id')
    x_coord = models.FloatField(verbose_name='x-coordinate')
    y_coord = models.FloatField(verbose_name='y-coordinate')
    node = models.ForeignKey(Node, models.PROTECT,
                             related_name='topology_records')
    parent_connection = models.ForeignKey('TopologyConnection', models.SET_NULL,
                                          null=True,
                                          blank=True,
                                          related_name='child')
    snapshot = models.OneToOneField(TopologySnapshot, on_delete=models.CASCADE,
                                    related_name='nodes')

    class Meta:
        db_table = 'topology_node'


class TopologyConnection(models.Model):
    distance = models.PositiveIntegerField(null=True,
                                           blank=True)
    parent = models.ForeignKey(TopologyNode, models.PROTECT,
                               related_name='child_connections')

    class Meta:
        db_table = 'topology_connection'
