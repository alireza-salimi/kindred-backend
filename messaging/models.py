from django.db import models
from django.utils.translation import ugettext_lazy as _


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Message'))
    content = models.TextField(verbose_name=_('Content'))
    sent_from = models.ForeignKey(
        'kindred.KindredMember', on_delete=models.DO_NOTHING, related_name='sent_messages', verbose_name=_('Sent from')
    )
    sent_to = models.ForeignKey(
        'kindred.KindredMember', on_delete=models.DO_NOTHING, related_name='received_messages', verbose_name=_('Sent to')
    )


class DefaultMessage(models.Model):
    content = models.TextField(verbose_name=_('Content'))
    kindred = models.ForeignKey(
        'kindred.Kindred', on_delete=models.CASCADE, related_name='default_messages', verbose_name=_('Kindred')
    )
