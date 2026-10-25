import base64
import json
import logging
from urllib.parse import urlsplit
from django.conf import settings
from django.utils import timezone
from cryptography.hazmat.primitives.asymmetric import ec
from pywebpush import webpush, WebPushException
from .models import PushDelivery

logger = logging.getLogger(__name__)
PUSH_HOSTS = ('fcm.googleapis.com','updates.push.services.mozilla.com','push.services.mozilla.com','web.push.apple.com','notify.windows.com')

def validate_subscription(data):
    if not isinstance(data,dict):
        raise ValueError('Invalid subscription.')
    endpoint=data.get('endpoint','')
    if not isinstance(endpoint,str) or len(endpoint)>2048:
        raise ValueError('Invalid push endpoint.')
    url=urlsplit(endpoint)
    if url.scheme!='https' or url.username or url.password or url.fragment or url.port not in (None,443) or not any(url.hostname==host or (url.hostname or '').endswith('.'+host) for host in PUSH_HOSTS):
        raise ValueError('Unsupported push provider.')
    keys=data.get('keys',{})
    if not isinstance(keys,dict):
        raise ValueError('Invalid device keys.')
    try:
        key=keys['p256dh'];auth=keys['auth']
        if not isinstance(key,str) or not isinstance(auth,str) or len(key)>128 or len(auth)>64:
            raise ValueError()
        point=base64.urlsafe_b64decode(key+'='*(-len(key)%4))
        secret=base64.urlsafe_b64decode(auth+'='*(-len(auth)%4))
        ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(),point)
        if len(secret)!=16: raise ValueError()
    except (KeyError,ValueError,TypeError) as error:
        raise ValueError('Invalid device keys.') from error
    return endpoint,{'p256dh':key,'auth':auth}

def deliver(pk):
    item=PushDelivery.objects.select_related('subscription__user','notification__recipient').filter(pk=pk,sent_at__isnull=True).first()
    if not item or not settings.WEBPUSH_PRIVATE_KEY or not settings.WEBPUSH_PUBLIC_KEY:
        return False
    if item.subscription.user_id!=item.notification.recipient_id or not item.subscription.user.is_active:
        return False
    item.attempts+=1;item.save(update_fields=['attempts'])
    # Detailed expense information is shown only after login, never on the lock screen.
    payload={'title':'New expense recorded','body':'A new car expense has been recorded. Open AutoLedger BD to view it.',
             'url':f'/notifications/{item.notification_id}/open/','tag':f'expense-{item.notification_id}'}
    try:
        webpush(subscription_info={'endpoint':item.subscription.endpoint,'keys':item.subscription.keys},
                data=json.dumps(payload),vapid_private_key=settings.WEBPUSH_PRIVATE_KEY,
                vapid_claims={'sub':settings.WEBPUSH_SUBJECT},ttl=3600,timeout=5)
    except WebPushException as error:
        status=error.response.status_code if error.response is not None else getattr(error,'status_code',None)
        if status in (404,410):
            item.subscription.delete()
        logger.warning('Push delivery %s failed with status %s',pk,status)
        return False
    except Exception:
        logger.warning('Push delivery %s could not be sent',pk)
        return False
    item.sent_at=timezone.now();item.save(update_fields=['sent_at'])
    return True
