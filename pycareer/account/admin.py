from django.contrib import admin
from .models import Profile, Skill, Subscription


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', )
    ordering = ('name', )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_email',  'is_active', 'type', 'city', 'country', 'phone_number', 'company_name', 'created_at', )
    ordering = ('-created_at',)
    list_filter = ('type', 'country', )

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def is_active(self, obj):
        return obj.user.is_active
    is_active.short_description = 'Active'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'first_name', 'email', 'active','subscribe_at', 'unsubscribe_at' )
    list_filter = ('active', )


admin.site.register(Skill, SkillAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
