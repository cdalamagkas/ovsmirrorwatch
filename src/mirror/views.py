from django.shortcuts import render

# Create your views here.
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MirrorForm
from django.contrib.auth.decorators import login_required
from mirror.models import OVSMirror
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.openapi import AutoSchema
from .serializers import MirrorSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


@login_required
def manage_mirrors(request):
    return render(request, 'mirror/manage.html', {'title': 'Mirrors, Switches and Ports'})
    

@login_required
def add_mirror(request):
    if request.method == 'POST':
        form = MirrorForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'OVS Mirror "{name}" created')
            return redirect('mirror-manage')
    else:
        form = MirrorForm()
    title = "Create New OVS Mirror"
    return render(request, 'add-edit.html', {'form': form, 'title': title})


@login_required
def delete_mirror(request):
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        name = splitted_url[3]
        if name != '':
            mirror = OVSMirror.objects.get(name=name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)
    mirror.delete()
    messages.success(request, f'OVSDB Manager "{name}" successfully deleted')
    return redirect('mirror-manage')


@login_required
def edit_mirror(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        name = splitted_url[3]      
        if name != '':
            edited_mirror = OVSMirror.objects.get(name=name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    if request.method == 'POST':        
        # Update Manager
        mirror_form = MirrorForm(request.POST, instance=edited_mirror)
        if mirror_form.is_valid():
            mirror_form.save()
            messages.success(request, f'The OVSDB Manager "{edited_mirror.name}" has been updated')
            return redirect('mirror-manage')
        else:
            messages.error(request, f'The ID Tag could not be updated. Please try again')
            return redirect('mirror-manage')        
    else:
        # Load form to update the OVSDB Manager
        mirror_form = MirrorForm(instance=edited_mirror)

        title = 'Update OVSDB Manager'

        context = {
            'mirror_form': mirror_form,
            'title': title,
        }

        return render(request, 'mirror/edit.html', context)


##########

class MirrorApiView(ListCreateAPIView):
    serializer_class = MirrorSerializer
    queryset = OVSMirror.objects.all()
    
    def get(self, request):
        fields = request.GET.get('fields', None)
        filtered_queryset = self.filter_queryset(self.queryset)
        if fields is not None:
            fields = fields.split(',')
            data = list(filtered_queryset.values(*fields))
            return Response(data)
        else:
            return Response(data= self.serializer_class(filtered_queryset.all(), many=True).data )
    


class MirrorDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = MirrorSerializer
    lookup_url_kwarg = 'name'
    queryset = OVSMirror.objects.all()
