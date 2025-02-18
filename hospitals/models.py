from typing import Optional

from django.core.mail import EmailMessage
from django.db import models
from appconf.manager import SettingManager
from clients.models import Card
from directory.models import Researches
from laboratory.settings import EMAIL_HOST_USER


class Hospitals(models.Model):
    title = models.CharField(max_length=255, help_text="Наименование")
    short_title = models.CharField(max_length=128, blank=True, default='', help_text="Краткое наименование", db_index=True)
    code_tfoms = models.CharField(max_length=128, blank=True, default='', help_text="Код больницы", db_index=True)
    oid = models.CharField(max_length=128, blank=True, default='', help_text="Код больницы", db_index=True)
    hide = models.BooleanField(default=False, blank=True, help_text='Скрытие больницы', db_index=True)
    is_default = models.BooleanField(default=False, blank=True, help_text='Больница по умолчанию для пустых полей', db_index=True)
    address = models.CharField(max_length=128, blank=True, default='', help_text="Адрес больницы")
    phones = models.CharField(max_length=128, blank=True, default='', help_text="Телефон больницы")
    ogrn = models.CharField(max_length=16, blank=True, default='', help_text="ОГРН больницы")
    www = models.CharField(max_length=128, blank=True, default='', help_text="Сайт больницы")
    rmis_org_id = models.CharField(max_length=12, blank=True, default='', help_text="ID организации в РМИС")
    email = models.CharField(max_length=128, blank=True, default='', help_text="email")
    remote_url = models.CharField(max_length=128, blank=True, default='', help_text="Адрес L2")
    remote_token = models.CharField(max_length=128, blank=True, default='', help_text="Токен L2")
    license_data = models.CharField(max_length=128, blank=True, default='', help_text="Лицензия")
    client = models.ForeignKey(Card, default=None, blank=True, null=True, db_index=True, help_text='Суррогатный пациент для мониторинга', on_delete=models.SET_NULL)
    research = models.ManyToManyField(Researches, blank=True, default=None, help_text="Обязательные мониторинги")
    current_manager = models.CharField(max_length=128, blank=True, default='', help_text="Руководитель/ИО учреждения")
    okpo = models.CharField(max_length=10, blank=True, default='', help_text="ОКПО")
    okato = models.CharField(max_length=11, blank=True, default='', help_text="ОКАТО")
    n3_id = models.CharField(max_length=40, help_text='N3_ID', blank=True, default="")
    ecp_id = models.CharField(max_length=16, default="", blank=True, verbose_name="Код для ECP")
    legal_auth_doc_id = models.CharField(max_length=9, default="", blank=True, verbose_name="Код для кто заверил")
    oktmo = models.CharField(max_length=8, default="", blank=True, verbose_name="ОКТМО")
    need_send_result = models.BooleanField(default=False, blank=True, help_text='Требуется email-отправка результатов', db_index=True)

    @staticmethod
    def get_default_hospital() -> Optional['Hospitals']:
        hosp = Hospitals.objects.filter(hide=False, is_default=True).first()

        if not hosp:
            hosp = Hospitals.objects.filter(hide=False, code_tfoms=SettingManager.get("org_id", default='', default_type='s')).first()
            if hosp:
                hosp.is_default = True
                hosp.save()

        return hosp

    @property
    def safe_full_title(self):
        return self.title or self.short_title

    @property
    def safe_short_title(self):
        return self.short_title or self.title

    @property
    def safe_address(self):
        return self.address or SettingManager.get("org_address")

    @property
    def safe_phones(self):
        return self.phones or SettingManager.get("org_phones")

    @property
    def safe_ogrn(self):
        return self.ogrn or SettingManager.get("org_ogrn")

    @property
    def safe_www(self):
        return self.www or SettingManager.get("org_www")

    @property
    def safe_email(self):
        # если отсутствует email, то адрес сайта
        return self.email or SettingManager.get("org_www")

    def send_email_with_pdf_file(self, subject, message, file, to=None):
        email = EmailMessage(
            subject,
            message,
            from_email=f"{self.safe_short_title} <{EMAIL_HOST_USER}>",
            to=[to or self.email],
        )
        email.attach(file.name, file.read(), 'application/pdf')
        email.send()

    def __str__(self):
        return f"{self.short_title} – {self.code_tfoms}"

    class Meta:
        verbose_name = 'Больница'
        verbose_name_plural = 'Больницы'


class HospitalsGroup(models.Model):

    REQUIREMENT_MONITORING_HOSP = 'REQUIREMENT_MONITORING_HOSP'
    REGION_HOSP = 'REGION_HOSP'
    CHILD_HOSP = 'CHILD_HOSP'

    HOSPITAL_TYPES = (
        (REQUIREMENT_MONITORING_HOSP, 'Обязательные мониторинги'),
        (REGION_HOSP, 'По районам'),
        (CHILD_HOSP, 'Детские'),
    )

    title = models.CharField(max_length=255, help_text="Наименование")
    hospital = models.ManyToManyField(Hospitals, blank=True, default=None, help_text="Какие больница")
    research = models.ManyToManyField(Researches, blank=True, default=None, help_text="Обязательные мониторинги")
    type_hospital = models.CharField(default=None, blank=True, null=True, max_length=100, db_index=True, choices=HOSPITAL_TYPES, help_text="Тип группы")
    access_black_list_edit_monitoring = models.ManyToManyField(Researches, blank=True, default=None, help_text="Запрещенные мониторинги(Черный список)", related_name='ResearchesBlackList')
    access_white_list_edit_monitoring = models.ManyToManyField(Researches, blank=True, default=None, help_text="Разрешенные мониторинги(Белый список)", related_name='ResearchesWhiteList')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Группа больница'
        verbose_name_plural = 'Группы больницы'


class DisableIstochnikiFinansirovaniya(models.Model):
    hospital = models.ForeignKey(Hospitals, blank=False, null=False, help_text="Больница", on_delete=models.CASCADE)
    fin_source = models.ForeignKey("directions.IstochnikiFinansirovaniya", blank=False, null=False, help_text="Больница", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hospital.title}-{self.fin_source}"

    class Meta:
        verbose_name = 'Запрещенные источники оплаты для Больницы'
        verbose_name_plural = 'Запрещенные источники оплаты для Больницы'


class HospitalParams(models.Model):
    hospital = models.ForeignKey(Hospitals, blank=False, null=False, help_text="Больница", on_delete=models.CASCADE)
    param_title = models.CharField(max_length=255, help_text="Наименование параметра")
    param_value = models.CharField(max_length=255, help_text="Значение параметра")

    def __str__(self):
        return f"{self.hospital.title}-{self.param_value}"

    class Meta:
        verbose_name = 'Параметр больницы произвольный'
        verbose_name_plural = 'Параметры больницы произвольные'
