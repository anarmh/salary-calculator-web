from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .utils import (
    calculate_salary,
)
from .forms import (
    SalaryCalculationForm,
)
from .models import (
    WorkCalendar,
    Year,
    Month,
    Shift,
    SalaryCalculation,
)


# Create your views here.


@login_required
def index_view(request):
    if request.method == "POST":
        form = SalaryCalculationForm(data=request.POST)
        if form.is_valid():
            group_name = form.cleaned_data["group_name"]
            year_month = form.cleaned_data["year_month"]
            overtime = form.cleaned_data["overtime"] or 0
            bonus_percent = form.cleaned_data["bonus_percent"] or 0
            monthly_salary = form.cleaned_data["monthly_salary"]

            data = calculate_salary(group_name, year_month, monthly_salary, overtime, bonus_percent)

            if data is None:
                messages.error(request, _("Maaş hesablanması zamanı xəta baş verdi. Zəhmət olmasa bir daha cəhd edin. Əgər xəta təkrarlanarsa bizimlə əlaqə saxlayın."))
                return redirect(reverse_lazy("core:index_view"))
            else:
                try:
                    SalaryCalculation.objects.create(
                        user=request.user,
                        year=data["year"],
                        month=data["month"],
                        shift=data["shift"],
                        salary=data["salary"],
                        overtime=data["overtime"],
                        bonus_percent=data["bonus_percent"],
                        hourly_wage=data["hourly_wage"],
                        night_work_pay=data["night_work_pay"],
                        extra_hour_pay=data["extra_hour_pay"],
                        holiday_hour_pay=data["holiday_hour_pay"],
                        overtime_pay=data["overtime_pay"],
                        bonus_pay=data["bonus_pay"],
                        gross=data["gross"],
                        nett=data["nett"],
                        income_tax=data["income_tax"],
                        dsmf_tax=data["dsmf_tax"],
                        unemployment_insurance_tax=data["unemployment_insurance_tax"],
                        compulsory_health_insurance_tax=data["compulsory_health_insurance_tax"]
                    )

                    messages.success(request, _("Maaş hesablama ugurla tamamlandi."))
                    return redirect(reverse_lazy("core:index_view"))
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    messages.error(request, _("Maaş hesablanması zamanı xəta baş verdi. Zəhmət olmasa bir daha cəhd edin."))
                    return redirect(reverse_lazy("core:index_view"))
    else:
        form = SalaryCalculationForm()
    
    user_salary_calculations = SalaryCalculation.objects.filter(user=request.user, is_active=True).order_by("-created_at")[:10]

    context = {
        "form": form,
        "user_salary_calculations": user_salary_calculations
    }
    return render(request, "core/index.html", context)


def work_calendar_view(request):
    years = WorkCalendar.get_years_list()
    months = Month.objects.all()
    work_calendar_data = WorkCalendar.get_work_calendar_data()

    context = {
        "years": years,
        "months": months,
        "work_calendar_data": work_calendar_data
    }
    return render(request, "core/work-calendar.html", context)


def groos_to_nett_view(request):
    return render(request, "core/gross-to-nett.html")