from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PortForm
from django.contrib.auth.decorators import login_required
from port.models import OVSPort
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.openapi import AutoSchema
from .serializers import PortSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
    

@login_required
def add_port(request):
    if request.method == 'POST':
        form = PortForm(request.POST)
        if form.is_valid():
            form.save()
            ovs_name = form.cleaned_data.get('ovs_name')
            messages.success(request, f'OVS Port "{ovs_name}" created')
            return redirect('mirror-manage')
    else:
        form = PortForm()
    title = "Create New OVS Port"
    return render(request, 'add-edit.html', {'form': form, 'title': title})


@login_required
def delete_port(request):
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        ovs_name = splitted_url[3]
        if ovs_name != '':
            port = OVSPort.objects.get(ovs_name=ovs_name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)
    port.delete()
    messages.success(request, f'OVS Port "{ovs_name}" successfully deleted')
    return redirect('mirror-manage')


@login_required
def edit_port(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        ovs_name = splitted_url[3]      
        if ovs_name != '':
            edited_port = OVSPort.objects.get(ovs_name=ovs_name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    if request.method == 'POST':        
        # Update Port
        port_form = PortForm(request.POST, instance=edited_port)
        if port_form.is_valid():
            port_form.save()
            messages.success(request, f'The OVS Port "{edited_port.ovs_name}" has been updated')
            return redirect('mirror-manage')
        else:
            messages.error(request, f'The OVS Port could not be updated. Please try again')
            return redirect('mirror-manage')        
    else:
        # Load form to update the OVS Port
        port_form = PortForm(instance=edited_port)

        title = 'Update OVS Port'

        context = {
            'form': port_form,
            'title': title,
        }

        return render(request, 'add-edit.html', context)


##########

class PortApiView(ListCreateAPIView):
    serializer_class = PortSerializer
    queryset = OVSPort.objects.all()
    
    def get(self, request):
        fields = request.GET.get('fields', None)
        filtered_queryset = self.filter_queryset(self.queryset)
        if fields is not None:
            fields = fields.split(',')
            data = list(filtered_queryset.values(*fields))
            return Response(data)
        else:
            return Response(data= self.serializer_class(filtered_queryset.all(), many=True).data )
    


class PortDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = PortSerializer
    lookup_url_kwarg = 'ovs_name'
    queryset = OVSPort.objects.all()
