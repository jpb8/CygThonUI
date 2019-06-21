from django.shortcuts import render, redirect
from .forms import DDSForm


# Create your views here.
def dds_upload(request):
    if request.method == 'POST':
        form = DDSForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print("form was saved")
            _form = DDSForm
            return render(request, 'files/file_upload.html', {'form': _form})
        else:
            print("Error in form")
    else:
        form = DDSForm
    return render(request, 'files/file_upload.html', {'form': form})
