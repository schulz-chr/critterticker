from django.shortcuts import render

from .models import *

# Create your views here.


def home(request):
    return render(request, 'carousel/home.html')


def sea_creatures(request):
    month_list = Month.objects.order_by("month_num")
    dive_fish_list = DiveFish.objects.order_by("name")
    dfactive_number = DiveFish.objects.first().get_active_number()
    dfnot_active_number = DiveFish.objects.first().get_not_active_number()
    dfsoon_active_number = DiveFish.objects.first().get_soon_active_number()
    context = {
        'month_list': month_list,
        'dive_fish_list': dive_fish_list,
        'dfactive_number': dfactive_number,
        'dfnot_active_number': dfnot_active_number,
        'dfsoon_active_number': dfsoon_active_number
    }
    return render(request, 'carousel/sea_creatures.html', context)


def bugs(request):
    month_list = Month.objects.order_by("month_num")
    bug_list = Bug.objects.order_by("name")
    bactive_number = Bug.objects.first().get_active_number()
    bnot_active_number = Bug.objects.first().get_not_active_number()
    bsoon_active_number = Bug.objects.first().get_soon_active_number()
    context = {
        'month_list': month_list,
        'bug_list': bug_list,
        'bactive_number': bactive_number,
        'bnot_active_number': bnot_active_number,
        'bsoon_active_number': bsoon_active_number

    }
    return render(request, 'carousel/bugs.html', context)


def fish(request):
    month_list = Month.objects.order_by("month_num")
    fish_list = Fish.objects.order_by("name")
    factive_number = Fish.objects.first().get_active_number()
    fnot_active_number = Fish.objects.first().get_not_active_number()
    fsoon_active_number = Fish.objects.first().get_soon_active_number()
    context = {
        'month_list': month_list,
        'fish_list': fish_list,
        'factive_number': factive_number,
        'fnot_active_number': fnot_active_number,
        'fsoon_active_number': fsoon_active_number
    }
    return render(request, 'carousel/fish.html', context)
