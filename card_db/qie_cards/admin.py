from django.contrib import admin
from .models import QieCard, Variable, Attempt, Tester, Test, Location, ReadoutModule, QieShuntParams, RMBiasVoltage, CalibrationUnit, SipmControlCard, Channel

# This file describes the layout of the admin pages.


class AttemptInLine(admin.StackedInline):
    """ Provides the inline layout for Attempts """
    
    model = Attempt
    date_hierarchy = 'date_tested'
    ordering = ('test_type', 'attempt_number', 'date_tested')
    extra = 0


class LocationsInLine(admin.StackedInline):
    """ Provides the inline layout for Attempts """
    
    model = Location
    date_hierarchy = 'date_received'
    ordering = ('date_received',)
    extra = 0


class QieAdmin(admin.ModelAdmin):
    """ Provides the layout for QieCard editing """
    
    fieldsets = [
        ('QIE information', {'fields': ['barcode', 'readout_module', 'readout_module_slot', 'uid', 'bridge_major_ver', 'bridge_minor_ver', 'bridge_other_ver', 'igloo_top_major_ver', 'igloo_top_minor_ver', 'igloo_bot_major_ver', 'igloo_bot_minor_ver', 'comments']}),
   ]
    
    inlines = [AttemptInLine, LocationsInLine]
    list_display = ('barcode', 'uid',)
    ordering = ('barcode', 'uid',)
    searchfields = ('barcode')
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing objectx
            return self.readonly_fields + ('barcode', 'uid') + ('bridge_major_ver', 'bridge_minor_ver') +  ('bridge_other_ver', 'igloo_top_major_ver') + ('igloo_bot_major_ver', 'igloo_top_minor_ver') + ('igloo_bot_minor_ver', None)
        return self.readonly_fields


class TestAdmin(admin.ModelAdmin):
    """ Provides the layout for the Test editing """
    list_display = ('name', 'description',)
    ordering = ('name',)
    searchfields = ('name')
    fieldsets = [
        ('Test Information', {'fields': ['name', 'abbreviation', 'description', 'required']}),
    ]


    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('abbreviation', 'required') + ('variables', None) 
        return self.readonly_fields


class ReadoutAdmin(admin.ModelAdmin):
    """ Provides the layout for ReadoutModule editing """
    
    fieldsets = [
        (None, {'fields': ['assembler', 'date', 'rm_number', 'comments']}),
        ("Card Pack", {'fields':['card_pack_number',
                                 'card_1',
                                 'card_2',
                                 'card_3',
                                 'card_4',
                                 'mtp_optical_cable',
                                 'sipm_control_card',
                                ]}),
        ("LV Assembly", {'fields':['lv_assembly']}),
        ("Thermal Assembly", {'fields':['therm_assembly']}),
        ("SiPM Assembly", {'fields':['sipm_array_1',
                                     'sipm_array_2',
                                     'sipm_array_3',
                                     'sipm_array_4',
                                     'sipm_array_5',
                                     'mixed_sipm_array',
                                     'sipm_mounting',
                                     'odu_type',
                                     'odu_number', 
                                    ]}),
        ("Jtag", {'fields':[]}),
        ("RM Outer Shell", {'fields':['minsk']}),
        ("Other", {'fields':['dcdc_output', 'upload']}),
        ]
    
    list_display = ('rm_number',)
    ordering = ('rm_number',)
    searchfields = ('rm_number')

class CUAdmin(admin.ModelAdmin):
    """ Provides the layout for Calibration Unit (CU) editing. """

    fieldsets = [
        (None, {'fields': ['assembler', 'date', 'place', 'cu_number']}),
        ("Components", {'fields':['qie_card', 
                                  'qie_adapter',
                                  'pulser_board', 
                                  'optics_box',
                                  'pindiode_led1',
                                  'pindiode_led2',
                                  'pindiode_laser1',
                                  'pindiode_laser2',
                                  'pindiode_laser3',
                                  'pindiode_laser4']}),
        ("Connections", {'fields':['sma_connector_mounted',
                                   'quartz_fiber_connected',
                                   'hirose_signal_connected',
                                   'reference_cable_connected']}),
        ("Quality Control", {'fields':['qc_complete']}),
        ("Upload", {'fields':['upload']}),
        ]

    list_display = ('cu_number',)
    ordering = ('cu_number',)
    searchfields = ('cu_number')

class SipmAdmin(admin.ModelAdmin):
    """ Provides the layout for SiPM Control Card editing. """

    list_display = ('sipm_control_card',)
    ordering = ('sipm_control_card',)
    searchFields = ('sipm_control_card')

# Registration of the models
#admin.site.register(Variable)
admin.site.register(QieCard, QieAdmin)
admin.site.register(QieShuntParams)
admin.site.register(Tester)
admin.site.register(RMBiasVoltage)
admin.site.register(Test, TestAdmin)
admin.site.register(ReadoutModule, ReadoutAdmin)
admin.site.register(CalibrationUnit, CUAdmin)
admin.site.register(SipmControlCard, SipmAdmin)
