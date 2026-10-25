from django.core.management.base import BaseCommand
from ledger.models import PushDelivery
from ledger.push import deliver

class Command(BaseCommand):
    help='Retry up to 100 unsent notifications with fewer than 5 delivery attempts.'

    def handle(self,*args,**options):
        ids=list(PushDelivery.objects.filter(sent_at__isnull=True,attempts__lt=5).order_by('pk').values_list('pk',flat=True)[:100])
        sent=sum(bool(deliver(pk)) for pk in ids)
        self.stdout.write(f'Sent {sent} of {len(ids)} pending deliveries.')
