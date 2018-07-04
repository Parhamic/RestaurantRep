from django.utils import timezone
def addtime(request):
    return {'now':timezone.localtime(timezone.now())}
