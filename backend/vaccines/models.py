from django.contrib.auth import get_user_model
from django.db import models

from vaccines.constants import CHAR_MAX_LEN

User = get_user_model()


class VaccineCard(models.Model):
    """Карточка вакцины."""

    current_version = models.ForeignKey(
        'VaccineCardVersion', null=True, on_delete=models.SET_NULL, related_name='cards_as_current'
    )
    published_version = models.ForeignKey(
        'VaccineCardVersion', null=True, on_delete=models.SET_NULL, related_name='cards_as_published'
    )
    status = models.CharField(max_length=CHAR_MAX_LEN, blank=True, null=True)
    is_visible = models.BooleanField(default=False)
    search_select_count = models.PositiveIntegerField(default=0)
    search_weight = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_vaccine_cards')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_vaccine_cards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Карточка вакцины'
        verbose_name_plural = 'Карточки вакцин'
        ordering = ('-updated_at',)
        db_table = 'vaccine_cards'

    def __str__(self):
        return f'Карточка {self.id} - {self.status}'


class VaccineCardVersion(models.Model):
    """Версия карточки вакцины."""

    vaccine_card = models.ForeignKey(VaccineCard, related_name='versions', on_delete=models.CASCADE)
    version_number = models.PositiveIntegerField(blank=True, null=True)
    version_status = models.CharField(max_length=CHAR_MAX_LEN, blank=True, null=True)
    parent_version = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='children')
    moderation_request = models.PositiveIntegerField(blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LEN, blank=True, null=True)
    official_name = models.CharField(max_length=CHAR_MAX_LEN, blank=True, null=True)
    is_available_in_rf = models.BooleanField(default=False)
    revision_date = models.DateField(blank=True, null=True)
    min_age = models.PositiveIntegerField(blank=True, null=True)
    max_age = models.PositiveIntegerField(blank=True, null=True)
    pregnancy_usage_status = models.CharField(max_length=CHAR_MAX_LEN, blank=True, null=True)
    storage_conditions = models.TextField(blank=True, null=True)
    interaction_info = models.TextField(blank=True, null=True)
    compatibility_info = models.TextField(blank=True, null=True)
    comment_ANO = models.TextField(blank=True, null=True)
    ohlp_url = models.URLField(blank=True, null=True)
    nonspec_url = models.URLField(blank=True, null=True)
    instruction_url = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_versions')
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_versions', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Версия вакцины'
        verbose_name_plural = 'Версии вакцин'
        ordering = ('-created_at',)
        db_table = 'vaccine_card_versions'
        constraints = [models.UniqueConstraint(fields=['vaccine_card', 'version_number'], name='unique_version')]

    def __str__(self):
        return self.name
