from django.contrib import admin
from .models import*
# Register your models here.

# class NoticeAdmin(admin.ModelAdmin):
#     list_display = ('title', 'pdf', 'uploaded_at')
admin.site.register(Room_Type)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Notice)
admin.site.register(UserProfile)

# admin.site.register(User)