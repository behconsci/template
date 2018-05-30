from django.contrib import admin

from .models import Profile, UserPayments


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'paid_at', 'api_token', 'idate', 'country')
    # readonly_fields = ('confirm_hash', 'country', 'user')

    def paid_at(self, obj):
        if not obj.user.user_payments.last():
            # no payment done
            return 'no payment yet'

        user_payment = obj.user.user_payments.latest('paid_at')
        return user_payment.paid_at.strftime('%d.%m.%Y at %H:%M')
    paid_at.short_description = 'Payment'


admin.site.register(Profile, ProfileAdmin)


class UserPaymentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'paid_at', 'amount')
    # readonly_fields = ('paid_at', 'amount', 'user')


admin.site.register(UserPayments, UserPaymentsAdmin)
