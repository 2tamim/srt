from django.shortcuts import render, redirect, get_object_or_404


def home(request):
    return render(request, 'main/projects/home.html')


# def single(request):
#     try:
#         return render(request, 'main/access/single.html')
#     except:
#         return render(request, 'main/access/home.html')
#
#
# def edit(request):
#     try:
#         return render(request, 'main/access/edit.html')
#     except:
#         return render(request, 'main/access/home.html')
