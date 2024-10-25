from rest_framework.throttling import UserRateThrottle

class BurstThrottle(UserRateThrottle):
    scope= 'burst'
    
class RapidThrottle(UserRateThrottle):
    scope='rapid'
    
class DailyThrottle(UserRateThrottle):
    scope= 'daily'