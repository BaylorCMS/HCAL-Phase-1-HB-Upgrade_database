# coding=utf-8
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import os
from django.db import models
from django.utils import timezone
from card_db.settings import MEDIA_ROOT

# This file describes the models off of which the database tables
# will be based


LOCATION_LENGTH = 100            # Constant for maximum location size
MAX_COMMENT_LENGTH = 1000        # Constant for max comment length



def validate_card_id(value):
    """ This determines whether an input card ID is valid """

    # ID must be a string of digits
    if not value.isdigit():
        raise ValidationError('ID must only contain numbers')

    # ID must be 7 digits long
    if len(value) != 7:
        raise ValidationError('ID must be 7 digits long')

    curId = value[(len(value) - 3):]
    sameId = QieCard.objects.filter(barcode__iendswith=curId).exclude(barcode__exact=value)

    # Last 3 digits of ID must be unique
    if sameId:
        raise ValidationError(
            ('Card "%(value)s" is already recorded'),
            params={'value':curId},
        )


def validate_uid(uid):
    """ This determines whether a card UID is valid """

    parsed = uid.split(":")

    if uid == "":
        return ""

    #UID must have 6 sections
    if not len(parsed) == 6:
        raise ValidationError("UID must have six ':'-separated sections")

    for part in parsed:

        # All UID sections must have 2 characters
        if not len(part) == 2:
            raise ValidationError("Each section must contain two characters")
        for letter in part:

            # All characters in the UID must be valid hexadecimal digits
            if not letter.isdigit() and not (letter.lower() >= 'a' and letter.lower() <= 'f'):
                raise ValidationError("UID may only contain hexadecimal digits")


class Test(models.Model):
    """ This model stores information about each type of test """

    name            = models.CharField(max_length=100, default="")                  # The displayed name of the test
    abbreviation    = models.CharField(max_length=100, default="", unique=True, blank=True)     # The abbreviation of the test name (w/out spaces)
    description     = models.TextField(max_length=1500, default="", blank=True)                 # The verbose test description
    required        = models.BooleanField(default=True)                             # Whether the test is required to pass

    def __str__(self):
        return self.name


class Tester(models.Model):
    """ This model stores information about a tester of the cards """

    username    = models.CharField(max_length=100, default="", unique=True)     # The full name of the tester
    email       = models.EmailField(max_length=255)                             # The email address of the tester
    affiliation = models.CharField('Affiliation', max_length=200, default="")   # The university/lab affiliation of the tester
    color       = models.CharField('Color', max_length=100, default="")         # The color designation of the tester (blue is the best!)

    def __str__(self):
       return self.username


class QieCard(models.Model):
    """ This model stores information about a QIE card (charge integrator and encoder)"""

    barcode = models.CharField(max_length=7, validators=[validate_card_id], unique=True, default="")    # The data stored on the barcode sticker
    uid     = models.CharField(max_length=21, blank=True, default="")               # The data stored on the UID chip
    bridge_major_ver    = models.CharField(max_length=4, default="", blank=True)    # The major version of the Bridge FPGA
    bridge_minor_ver    = models.CharField(max_length=4, default="", blank=True)    # The minor version of the Bridge FPGA
    bridge_other_ver    = models.CharField(max_length=8, default="", blank=True)    # The other version of the Bridge FPGA
    igloo_top_major_ver     = models.CharField(max_length=4, default="", blank=True)    # The major version of the top IGLOO FPGA
    igloo_bot_major_ver     = models.CharField(max_length=4, default="", blank=True)    # The major version of the bottom IGLOO FPGA
    igloo_top_minor_ver     = models.CharField(max_length=4, default="", blank=True)    # The minor version of the top IGLOO FPGA
    igloo_bot_minor_ver     = models.CharField(max_length=4, default="", blank=True)    # The minor version of the bottom IGLOO FPGA
    readout_module      = models.IntegerField('RM №', default=-1)                   # The readout module that the QIE Card is installed (if applicable)
    readout_module_slot = models.IntegerField('RM Slot', default=-1)                # The readout module slot (1-4) that the QIE Card is installed (if applicable)
    calibration_unit    = models.IntegerField('CU №', default=-1)                   # The calibration unit in which the QIE Card is installed (if applicable)
    comments            = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")   # Any comments pertaining to the
                                                                                                    # testing/appearance of the card

    def update_readout_module(self):
        """ Sets the readout module and slot for a QIE card. """
        for rm in ReadoutModule.objects.all():
            if rm.card_1 == self:
                self.readout_module = rm.rm_number
                self.readout_module_slot = 1
                self.save()
                break
            if rm.card_2 == self:
                self.readout_module = rm.rm_number
                self.readout_module_slot = 2
                self.save()
                break
            if rm.card_3 == self:
                self.readout_module = rm.rm_number
                self.readout_module_slot = 3
                self.save()
                break
            if rm.card_4 == self:
                self.readout_module = rm.rm_number
                self.readout_module_slot = 4
                self.save()
                break

    def get_location(self):
        q_loc = Location.objects.filter(card=self).order_by("date_received")
        current_loc = q_loc.reverse()[0].geo_loc
        return current_loc

    def get_uid_split(self):
        """ Parses the raw UID into split form (first 4 bytes, last 4 bytes) """
        if self.uid == "":
            return "Not Uploaded"
        checkSum = self.uid[0:8].upper()
        familyName = self.uid[8:16].upper()
        return "0x" + checkSum + " 0x" + familyName

    def get_uid_flipped(self):
        """ Parses the raw UID into flipped-split form (last 4 bytes, first 4 bytes) """
        if self.uid == "":
            return "Not Uploaded"
        familyName = self.uid[8:16].upper()
        checkSum = self.uid[0:8].upper()
        return "0x" + familyName + " 0x" + checkSum

    def get_uid_mac(self):
        """ Parses the raw UID into a mac-address format with colons """
        if self.uid == "":
            return "Not Uploaded"
        raw = self.uid[2:]
        refined = ""
        for i in range(6):
            refined += raw[2*i : 2*(i + 1)].upper()
            refined += ':'
        return refined[:17]

    def get_uid_mac_simple(self):
        """ Parses the raw UID into 3 unique bytes (6 hex digits) """
        if self.uid == "":
            return "000000"
        if len(self.uid) != 16:
            return "Complete Unique ID not 8 bytes long (16 characters)."
        raw = self.uid[8:-2]
        return raw.upper()
    
    def get_bar_uid(self):
        """ Returns the unique 3-digit code of this card's ID """
        if self.barcode == "":
            return "QIE Card barcode not in database"
        return self.barcode[(len(self.barcode) - 3):]

    def get_bridge_ver(self):
        if self.bridge_major_ver == "" or self.bridge_minor_ver == "" or self.bridge_other_ver == "":
            return "Not Uploaded"
        major = str(int(self.bridge_major_ver, 16)).upper()
        minor = str(int(self.bridge_minor_ver, 16)).upper()
        other = str(int(self.bridge_other_ver, 16)).upper()
        return major + "." + minor + "." + other

    def get_bridge_ver_hex(self):
        if self.bridge_major_ver == "" or self.bridge_minor_ver == "" or self.bridge_other_ver == "":
            return "Not Uploaded"
        major = str(self.bridge_major_ver.zfill(2))[2:].upper()
        minor = str(self.bridge_minor_ver.zfill(2))[2:].upper()
        other = str(self.bridge_other_ver.zfill(4))[2:].upper()
        return major + "_" + minor + "_" + other

    def get_bot_igloo_ver(self):
        if self.igloo_bot_major_ver == "" or self.igloo_bot_minor_ver == "":
            return "Not Uploaded"
        major = str(int(self.igloo_bot_major_ver, 16)).upper()
        minor = str(int(self.igloo_bot_minor_ver, 16)).upper()
        return major + "." + minor

    def get_top_igloo_ver(self):
        if self.igloo_top_major_ver == "" or self.igloo_top_minor_ver == "":
            return "Not Uploaded"
        major = str(int(self.igloo_top_major_ver, 16)).upper()
        minor = str(int(self.igloo_top_minor_ver, 16)).upper()
        return major + "." + minor

    def get_bot_igloo_ver_hex(self):
        if self.igloo_bot_major_ver == "" or self.igloo_bot_minor_ver == "":
            return "Not Uploaded"
        major = str(self.igloo_bot_major_ver.zfill(2))[2:].upper()
        minor = str(self.igloo_bot_minor_ver.zfill(2))[2:].upper()
        return major + "_" + minor

    def get_top_igloo_ver_hex(self):
        if self.igloo_top_major_ver == "" or self.igloo_top_minor_ver == "":
            return "Not Uploaded"
        major = str(self.igloo_top_major_ver.zfill(2))[2:].upper()
        minor = str(self.igloo_top_minor_ver.zfill(2))[2:].upper()
        return major + "_" + minor

    def __str__(self):
       return str(self.barcode)

    def __iter__(self):
        for field in self._meta.get_fields():
            value = getattr(self, field.name, None)
            yield (field.name, value)


class Channel(models.Model):
    """ This model stores information about a specific channel for a QIE Card """
    
    # Channel number for this specific channel
    CHANNEL = (
        (-1, "N/A"),
        (1, "Top Channel 1"),
        (2, "Top Channel 2"),
        (3, "Top Channel 3"),
        (4, "Top Channel 4"),
        (5, "Top Channel 5"),
        (6, "Top Channel 6"),
        (7, "Top Channel 7"),
        (8, "Top Channel 8"),
        (9, "Bot Channel 9"),
        (10, "Bot Channel 10"),
        (11, "Bot Channel 11"),
        (12, "Bot Channel 12"),
        (13, "Bot Channel 13"),
        (14, "Bot Channel 14"),
        (15, "Bot Channel 15"),
        (16, "Bot Channel 16"),
    )

    number = models.IntegerField(default=-1, choices=CHANNEL, blank=True, null=True)    # Number specifying which channel this is
    card = models.ForeignKey(QieCard, on_delete=models.CASCADE, blank=True, null=True)    # Card this channel is on
    
    def __str__(self):
        return str(self.number)


def images_location(upload, original_filename):
    cardName    = str(QieCard.objects.get(pk=upload.barcode).barcode) + "/"
    testAbbrev  = str(Test.objects.get(pk=upload.test_type_id).abbreviation) + "/"
    attemptNum  = str(upload.attempt_number) + "/"

    return os.path.join("images/", cardName, testAbbrev, attemptNum, original_filename)

def logs_location(upload, original_filename):
    cardName    = str(QieCard.objects.get(pk=upload.barcode).barcode) + "/"
    testAbbrev  = str(Test.objects.get(pk=upload.test_type_id).abbreviation) + "/"
    attemptNum  = str(upload.attempt_number) + "/"

    return os.path.join("uploads/", "user_uploaded_logs/", cardName, testAbbrev, attemptNum, original_filename)


class Attempt(models.Model):
    """ This model stores information about each testing attempt """

    card        = models.ForeignKey(QieCard, on_delete=models.CASCADE)      # The card object which this test is on
    plane_loc   = models.CharField(max_length=LOCATION_LENGTH, default="", blank=True)  # The location on the backplane where the test occured
    test_type   = models.ForeignKey(Test, on_delete=models.PROTECT)         # The test object which this test is of
    attempt_number  = models.IntegerField(default=0)                        # The number of this attempt on this card
    tester      = models.ForeignKey(Tester, on_delete=models.PROTECT, blank=True)       # the person who enterd this attempt
    date_tested = models.DateTimeField('date tested', blank=True)       # The date this test finished
    num_channels_passed  = models.IntegerField(default=0)           # The number of channels this test passed
    num_channels_failed  = models.IntegerField(default=0)           # The number of channels this test failed
    revoked     = models.BooleanField(default=False)        # Whether this test series is revoked
    overwrite_pass  = models.BooleanField(default=False)    # Whether this test was overwritten as a pass
    temperature = models.FloatField(default=-999.9)         # The temperature of the card during the test
    humidity    = models.FloatField(default=-999.9)         # The numidity of the card during the test
    comments    = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")   # Any comments pertaining to this test
    image       = models.ImageField(upload_to=images_location, default="default.png")       # Any image associated with this test

    log_file        = models.FileField(upload_to=logs_location, default='default.png')          # The log file from whence this test was uploaded    
    log_comments    = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")   # Any comments pertaining to the log file

    hidden_log_file = models.FileField(upload_to=logs_location, default='default.png')      # The verbose log file, only used for web-page generation
    result = models.NullBooleanField(default=None, blank=True, null=True)    # Whether the specific test passed or failed

    def passed(self): 
        return (self.result == 1)

    def has_image(self):
        """ This returns whether the attempt has a specified image """
        return (not self.image == "default.png")

    def has_log(self):
        """ This returns whether the attempt has a log folder """
        return (not self.log_file == "default.png")

    def get_status(self):
        if self.revoked:
            return "REVOKED"
        elif self.overwrite_pass:
            return "PASS (FORCED)"
        elif self.result:
            return "PASS"
        else:
            return "FAIL"

    def get_css_class(self):
        """ This returns the color which the Attempt template should take """
        if self.revoked:
            return "warn"
        elif self.overwrite_pass:
            return "forced"
        elif self.result:
            return "okay"
        else:
            return "bad"

    def get_images(self):
        path = MEDIA_ROOT + str(self.image)
        #images = [image for image in os.listdir(os.path.join(MEDIA_ROOT, self.image.url))]
        if not str(self.image)[-4:] == "uhtr" and not str(self.image)[-4:] == "r.gz":
            return os.listdir(path)

    def __str__(self):
        return str(self.test_type)


class Variable(models.Model):
    """ This model stores the information about each variable for a test """

    name = models.CharField(max_length=100, default="", blank=True)    # Name of the variable being tested
    value = models.FloatField(blank=True, null=True)      # Specific value of this variable
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, blank=True, null=True)           # Which test this variable is a part of
    test_pass = models.BooleanField(default=False)                     # Whether it passed said test or not

    def __str__(self):
        return (self.name + ": " + str(self.test_pass))


class ReadoutModule(models.Model):
    """ This model stores information about an RM (Readout Module). """
    ODU_TYPE_OPTIONS = [                    # Optical Decoder Unit (ODU) types 1, 2, 3, 4.
                        ("1", "1"),
                        ("2", "2"),
                        ("3", "3"),
                        ("4", "4"),
                       ]
    MOUNTING_OPTIONS = [                    # SiPM Mounting Board types 1/3, 2/4.
                        ("1/3", "1/3"),
                        ("2/4", "2/4"),
                       ]
    
    assembler   = models.CharField('Assembler', max_length=50, default="")      # The name of the assembler of the RM
    date        = models.DateTimeField('Date Received', default=timezone.now)   # The date on which the RM was received
    rm_number   = models.IntegerField('RM №', default=-1)                       # The number of the RM
    card_pack_number    = models.IntegerField('CardPack №', default=-1)         # The cardpack number of the RM
    rm_uid  = models.CharField(max_length=27, blank=True, default="")           # The RM UID created from the UIDs of the 4 QIE cards in the RM
    card_1  = models.ForeignKey(QieCard, verbose_name='QIE card 1 №', related_name="rm_1", on_delete=models.PROTECT)    # The QIE Card in Slot 1 of the RM 
    card_2  = models.ForeignKey(QieCard, verbose_name='QIE card 2 №', related_name="rm_2", on_delete=models.PROTECT)    # The QIE Card in Slot 2 of the RM
    card_3  = models.ForeignKey(QieCard, verbose_name='QIE card 3 №', related_name="rm_3", on_delete=models.PROTECT)    # The QIE Card in Slot 3 of the RM
    card_4  = models.ForeignKey(QieCard, verbose_name='QIE card 4 №', related_name="rm_4", on_delete=models.PROTECT)    # The QIE Card in Slot 4 of the RM
    mtp_optical_cable   = models.CharField('1 MTP to 8 LC optical cable №', max_length=50, default="")                  # MTP Optical cable number used in RM
    sipm_control_card   = models.IntegerField('1 SiPM Control Card with BV mezzanine №', default=-1)                    # SiPM Control Card number used in RM
    
    lv_assembly = models.IntegerField('LV Assembly Number', default=-1)                                                 # Low Voltage Assembly of 6 DC-DC converters for RM

    therm_assembly  = models.IntegerField('Thermal Assembly Number', default=-1)                                        # Thermal assembly number for RM

    sipm_array_1    = models.IntegerField('SiPM Array S10943-4732 № (BV1-8)', default=-1)                               # SiPM Array 1 for BV 1-8
    sipm_array_2    = models.IntegerField('SiPM Array S10943-4732 № (BV17-24)', default=-1)                             # SiPM Array 2 for BV 17-24
    sipm_array_3    = models.IntegerField('SiPM Array S10943-4732 № (BV25-32)', default=-1)                             # SiPM Array 3 for BV 25-32
    sipm_array_4    = models.IntegerField('SiPM Array S10943-4732 № (BV33-40)', default=-1)                             # SiPM Array 4 for BV 33-40
    sipm_array_5    = models.IntegerField('SiPM Array S10943-4732 № (BV41-48)', default=-1)                             # SiPM Array 5 for BV 41-48
    mixed_sipm_array    = models.IntegerField('Mixed SiPM array S10943-4733 № (BV9-16)', default=-1)                    # SiPM Array Mixed for BV 9-16
    sipm_mounting   = models.CharField('SiPM Mounting Board Type', choices=MOUNTING_OPTIONS, max_length=3, default="")  # SiPM Mounting Board for RM
    odu_type    = models.CharField('ODU type', choices=ODU_TYPE_OPTIONS, max_length=3, default="")                      # ODU (Optical Decoder Unit) type for RM
    odu_number  = models.IntegerField('ODU №', default=-1)                                                              # ODU (Optical Decoder Unit) number for RM
    
    minsk       = models.IntegerField('White box with RM mechanics from Minsk №', default=-1)
    
    dcdc_output = models.CharField('Output of 5V DC-DC', max_length=50, default="")                                     # Measured voltage of 5V output of DC-DC converter
    upload      = models.FileField('Image Upload', upload_to='readout_module/', default='default.png')                  # Image of RM assembly form
    comments    = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")                               # Initial comments given when uploading RM to database

    def update(self):
        """ Update RM Unique ID """
        uid = ""
        uid += self.card_1.get_uid_mac_simple() + "_"
        uid += self.card_2.get_uid_mac_simple() + "_" 
        uid += self.card_3.get_uid_mac_simple() + "_" 
        uid += self.card_4.get_uid_mac_simple() 
        self.rm_uid = uid[:27]
        self.save()
        """ Update RM Number for each QIE Card """
        self.card_1.readout_module = self.rm_number 
        self.card_1.readout_module_slot = 1
        self.card_1.save()
        self.card_2.readout_module = self.rm_number
        self.card_2.readout_module_slot = 2
        self.card_2.save()
        self.card_3.readout_module = self.rm_number
        self.card_3.readout_module_slot = 3
        self.card_3.save()
        self.card_4.readout_module = self.rm_number
        self.card_4.readout_module_slot = 4
        self.card_4.save()

    def get_location(self):
        r_loc = RmLocation.objects.filter(rm=self).order_by("date_received")
        current_loc = r_loc.reverse()[0].geo_loc
        return current_loc

    def __str__(self):
        return str(self.rm_number)

    def __iter__(self):
        for field in self._meta.get_fields():
            value = getattr(self, field.name, None)
            yield (field.name, value)


class RMBiasVoltage(models.Model):
    readout_module = models.ForeignKey(ReadoutModule, on_delete=models.CASCADE, default=1)
    channel_01 = models.CharField(max_length=50, default="")
    channel_02 = models.CharField(max_length=50, default="")
    channel_03 = models.CharField(max_length=50, default="")
    channel_04 = models.CharField(max_length=50, default="")
    channel_05 = models.CharField(max_length=50, default="")
    channel_06 = models.CharField(max_length=50, default="")
    channel_07 = models.CharField(max_length=50, default="")
    channel_08 = models.CharField(max_length=50, default="")
    channel_09 = models.CharField(max_length=50, default="")
    channel_10 = models.CharField(max_length=50, default="")
    channel_11 = models.CharField(max_length=50, default="")
    channel_12 = models.CharField(max_length=50, default="")
    channel_13 = models.CharField(max_length=50, default="")
    channel_14 = models.CharField(max_length=50, default="")
    channel_15 = models.CharField(max_length=50, default="")
    channel_16 = models.CharField(max_length=50, default="")
    channel_17 = models.CharField(max_length=50, default="")
    channel_18 = models.CharField(max_length=50, default="")
    channel_19 = models.CharField(max_length=50, default="")
    channel_20 = models.CharField(max_length=50, default="")
    channel_21 = models.CharField(max_length=50, default="")
    channel_22 = models.CharField(max_length=50, default="")
    channel_23 = models.CharField(max_length=50, default="")
    channel_24 = models.CharField(max_length=50, default="")
    channel_25 = models.CharField(max_length=50, default="")
    channel_26 = models.CharField(max_length=50, default="")
    channel_27 = models.CharField(max_length=50, default="")
    channel_28 = models.CharField(max_length=50, default="")
    channel_29 = models.CharField(max_length=50, default="")
    channel_30 = models.CharField(max_length=50, default="")
    channel_31 = models.CharField(max_length=50, default="")
    channel_32 = models.CharField(max_length=50, default="")
    channel_33 = models.CharField(max_length=50, default="")
    channel_34 = models.CharField(max_length=50, default="")
    channel_35 = models.CharField(max_length=50, default="")
    channel_36 = models.CharField(max_length=50, default="")
    channel_37 = models.CharField(max_length=50, default="")
    channel_38 = models.CharField(max_length=50, default="")
    channel_39 = models.CharField(max_length=50, default="")
    channel_40 = models.CharField(max_length=50, default="")
    channel_41 = models.CharField(max_length=50, default="")
    channel_42 = models.CharField(max_length=50, default="")
    channel_43 = models.CharField(max_length=50, default="")
    channel_44 = models.CharField(max_length=50, default="")
    channel_45 = models.CharField(max_length=50, default="")
    channel_46 = models.CharField(max_length=50, default="")
    channel_47 = models.CharField(max_length=50, default="")
    channel_48 = models.CharField(max_length=50, default="")

    def __str__(self):
        return str(self.readout_module)

class CalibrationUnit(models.Model):
    """ This model stores information about a particular Calibration Unit (CU). """

    assembler   = models.CharField('Assembler', max_length=50, default="")                                      # Assembler of CU
    date        = models.DateTimeField('Date of Assembly', default=timezone.now)                                # Date of assembly
    place       = models.CharField('Location of Assembly', max_length=50, default="")                           # Location of assembly
    cu_number   = models.IntegerField('Calibration Unit №', default=-1)                                         # CU number
    cu_uid      = models.CharField(max_length=6, blank=True, default="")                                        # The CU UID created from the UID of the QIE card in the CU 
    qie_card    = models.ForeignKey(QieCard, verbose_name='QIE Card №', on_delete=models.PROTECT)               # QIE Card installed in CU, barcode 0601XXX
    qie_adapter      = models.IntegerField('QIE Adapter №', default=-1)                                         # QIE adapter number
    pulser_board     = models.IntegerField('Pulser Board №', default=-1)                                        # Pulser board installed in CU
    optics_box       = models.IntegerField('Optics Box №', default=-1)                                          # Optics box in CU
    pindiode_led1    = models.IntegerField('Pindiode_LED1 №', default=-1)                                       # Pin diode for LED 1
    pindiode_led2    = models.IntegerField('Pindiode_LED2 №.', default=-1)                                      # Pin diode for LED 2
    pindiode_laser1  = models.IntegerField('Pindiode board_laser1 №', default=-1)                               # Pin diode laser 1
    pindiode_laser2  = models.IntegerField('Pindiode board_laser2 №', default=-1)                               # Pin diode laser 2
    pindiode_laser3  = models.IntegerField('Pindiode board_laser3 №', default=-1)                               # Pin diode laser 3
    pindiode_laser4  = models.IntegerField('Pindiode board_laser4 №', default=-1)                               # Pin diode laser 4
    sma_connector_mounted = models.BooleanField('SMA Connector Mounted', default=False)                         # Confirmation that the SMA Connector is mounted
    quartz_fiber_connected = models.BooleanField('Quartz Fiber Connected', default=False)                       # Confirmation that the Quartz Fiber is connected
    hirose_signal_connected = models.BooleanField('Hirose Signal Connected', default=False)                     # Confirmation that the Hirose Signal is connected
    reference_cable_connected = models.BooleanField('Reference Cable Conncected', default=False)                # Confirmation that the Reference Cable is connected
    qc_complete      = models.BooleanField('QC Complete', default=False)                                        # Confirmation that Quality Control has been completed for the CU
    upload           = models.FileField('QC Data File', upload_to='cu_calibration/', default='default.png')     # Uploaded Quality Control data file for CU
    comments         = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")                  # Comments for a Calibration Unit

    def update(self):
        self.qie_card.calibration_unit = self.cu_number
        self.cu_uid = self.qie_card.get_uid_mac_simple()
        self.qie_card.save()
        self.save()

    def get_location(self):
        c_loc = CuLocation.objects.filter(cu=self).order_by("date_received")
        current_loc = c_loc.reverse()[0].geo_loc
        return current_loc
    
    def __str__(self):
        return str(self.cu_number)

class SipmControlCard(models.Model):
    """ This model stores information about a particular SiPM Control Card."""
    
    sipm_control_card  = models.IntegerField('SiPM Control Card №', default=-1)
    bv_converter_card  = models.IntegerField('BV Converter Card №', default=-1)
    rm_number          = models.IntegerField('Readout Module №', default=-1)
    comments           = models.TextField(max_length=MAX_COMMENT_LENGTH, blank=True, default="")
    upload             = models.FileField('Calibration Data File', upload_to='sipm_control_card', default='default.png')

    def get_rm(self):
        if self.rm_number > 0:  return self.rm_number
        else:                   return "Not Installed"

    def get_calibration_data(self):
        data = []
        f = self.upload
        f.open(mode='rb')
        for line in f.readlines():
            # In each line, the first two values are Card ID and Channel, which we don't convert to floats.
            if line != '\n':
                items = line[:-2].split(',')
                final = []
                final.append(int(items[0][3:]))
                final.append(int(items[1]))
                final = final + list(float(a) for a in items[2:])
                data.append(final)
        f.close()
        return data[:48]

    def __str__(self):
        return str(self.sipm_control_card)

class Location(models.Model):
    """ This model stores information about a particular location where a card has been """

    card = models.ForeignKey(QieCard, on_delete=models.CASCADE)                 # The card which the location refers to
    date_received = models.DateTimeField('date received', default=timezone.localtime(timezone.now())) # The date the card was received at this location
    geo_loc = models.CharField('Location',max_length=200, default="")           # The geographical location of this card

class RmLocation(models.Model):
    """ This model stores information about Readout Module location history """

    rm = models.ForeignKey(ReadoutModule, on_delete=models.CASCADE)              # The RM which the location refers to
    date_received = models.DateTimeField('date received', default=timezone.now)  # The date the RM was received at this location
    geo_loc = models.CharField('Location', max_length=200, default="")           # The geographic location of the RM

class CuLocation(models.Model):
    """ This model stores information about Calibration Unit location history """

    cu = models.ForeignKey(CalibrationUnit, on_delete=models.CASCADE)            # The CU which the location refers to
    date_received = models.DateTimeField('date received', default=timezone.now)  # The date the CU was received at this location
    geo_loc = models.CharField('Location', max_length=200, default="")           # The geographic location of the CU  

# An appendage to the save function
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save


class QieShuntParams(models.Model): 
    card    = models.ForeignKey(QieCard, on_delete=models.CASCADE, default=151)     # The card which the parameters relate to
    group   = models.IntegerField(default=-1)
    date    = models.DateTimeField('Date', default=timezone.now)
    plots       = models.FileField(upload_to=logs_location, default='default.png')
    mappings    = models.FileField(upload_to=logs_location, default='default.png')
    results     = models.FileField(upload_to=logs_location, default='default.png')
    download    = models.FileField(upload_to=logs_location, default='default.png')
    failed      = models.BooleanField(default=False)

    def __str__(self):
        return str(self.card)


@receiver(pre_save)
def pre_save_full_clean_handler(sender, instance, *args, **kwargs):
   """ Force all models to call full_clean before save """
   from django.contrib.sessions.models import Session
   if sender != Session:
       instance.full_clean()

# An appendage to the delete function
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import shutil
from card_db.settings import MEDIA_ROOT


@receiver(pre_delete, sender=Attempt)
def mymodel_delete(sender, instance, **kwargs):
    """ Deletes the stored image """
    if len(Attempt.objects.filter(card=instance.card)) == 1:
        if instance.image != "default.png":
            instance.image.delete(False)
        if instance.log_file != "default.png" and os.path.exists(os.path.join(MEDIA_ROOT, os.path.dirname(instance.log_file.name))):
            shutil.rmtree(os.path.join(MEDIA_ROOT, os.path.dirname(instance.log_file.name)))
