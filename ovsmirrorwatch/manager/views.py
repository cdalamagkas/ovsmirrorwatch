from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ManagerForm, ManagerFormEdit
from django.contrib.auth.decorators import login_required
from manager.models import OVSManager
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.openapi import AutoSchema
from .serializers import ManagerSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


@login_required
def manage_managers(request):
    return render(request, 'manager/manage.html', {'title': 'OVSDB Managers'})
    

@login_required
def add_manager(request):
    if request.method == 'POST':
        form = ManagerForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'OVSDB Manager "{name}" created')
            return redirect('manager-manage')
    else:
        form = ManagerForm()
    title = "Create New Manager"
    return render(request, 'manager/add.html', {'form': form, 'title': title})


@login_required
def delete_manager(request):
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        name = splitted_url[3]
        if name != '':
            manager = OVSManager.objects.get(name=name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)
    manager.delete()
    messages.success(request, f'OVSDB Manager "{name}" successfully deleted')
    return redirect('manager-manage')


@login_required
def edit_manager(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        name = splitted_url[3]      
        if name != '':
            edited_manager = OVSManager.objects.get(name=name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    if request.method == 'POST':        
        # Update Manager
        manager_form = ManagerFormEdit(request.POST, instance=edited_manager)
        if manager_form.is_valid():
            manager_form.save()
            messages.success(request, f'The OVSDB Manager "{edited_manager.name}" has been updated')
            return redirect('manager-manage')
        else:
            messages.error(request, f'The ID Tag could not be updated. Please try again')
            return redirect('manager-manage')        
    else:
        # Load form to update the OVSDB Manager
        manager_form = ManagerFormEdit(instance=edited_manager)

        title = 'Update OVSDB Manager'

        context = {
            'manager_form': manager_form,
            'title': title,
        }

        return render(request, 'manager/edit.html', context)


##########

class ManagerApiView(ListCreateAPIView):
    authentication_classes = []
    serializer_class = ManagerSerializer
    queryset = OVSManager.objects.all()
    
    def get(self, request):
        fields = request.GET.get('fields', None)
        filtered_queryset = self.filter_queryset(self.queryset)
        if fields is not None:
            fields = fields.split(',')
            data = list(filtered_queryset.values(*fields))
            return Response(data)
        else:
            return Response(data= self.serializer_class(filtered_queryset.all(), many=True).data )
    


class ManagerDetailApiView(RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    serializer_class = ManagerSerializer
    lookup_url_kwarg = 'name'
    queryset = OVSManager.objects.all()
