import base64
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class Command(BaseCommand):
    help = 'Create persistent Web Push signing keys without printing the private key.'

    def handle(self,*args,**options):
        directory=Path(settings.BASE_DIR)/'.secrets';directory.mkdir(exist_ok=True)
        private=directory/'webpush-private.pem';public=directory/'webpush-public.txt'
        if private.exists():
            key=serialization.load_pem_private_key(private.read_bytes(),password=None)
        else:
            key=ec.generate_private_key(ec.SECP256R1())
            private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        point=key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
        public.write_text(base64.urlsafe_b64encode(point).decode().rstrip('='))
        self.stdout.write(self.style.SUCCESS('Web Push signing keys are ready in .secrets/. Restart Django to load them.'))
