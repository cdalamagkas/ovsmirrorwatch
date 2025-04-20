from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BridgeForm
from django.contrib.auth.decorators import login_required
from bridge.models import OVSBridge
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.openapi import AutoSchema
from .serializers import BridgeSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
    

@login_required
def add_bridge(request):
    if request.method == 'POST':
        form = BridgeForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('ovs_name')
            messages.success(request, f'OVS Bridge "{name}" created')
            return redirect('mirror-manage')
    else:
        form = BridgeForm()
    title = "Create New OVS Bridge"
    return render(request, 'add-edit.html', {'form': form, 'title': title})


@login_required
def delete_bridge(request):
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        ovs_name = splitted_url[3]
        if ovs_name != '':
            bridge = OVSBridge.objects.get(ovs_name=ovs_name)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)
    bridge.delete()
    messages.success(request, f'OVS Bridge "{ovs_name}" successfully deleted')
    return redirect('mirror-manage')


@login_required
def edit_bridge(request):
    
    splitted_url = request.get_full_path().split('/')
    if len(splitted_url) > 3:
        id = splitted_url[3]      
        if id != '':
            edited_bridge = OVSBridge.objects.get(id=id)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    if request.method == 'POST':        
        # Update Bridge
        bridge_form = BridgeForm(request.POST, instance=edited_bridge)
        if bridge_form.is_valid():
            bridge_form.save()
            messages.success(request, f'The OVS Bridge "{edited_bridge.ovs_name}" has been updated')
            return redirect('mirror-manage')
        else:
            messages.error(request, f'The OVS Bridge could not be updated. Please try again')
            return redirect('mirror-manage')        
    else:
        # Load form to update the OVS Bridge
        bridge_form = BridgeForm(instance=edited_bridge)

        title = 'Update OVS Bridge'

        context = {
            'form': bridge_form,
            'title': title,
        }

        return render(request, 'add-edit.html', context)


##########

class BridgeApiView(ListCreateAPIView):
    serializer_class = BridgeSerializer
    queryset = OVSBridge.objects.all()
    
    def get(self, request):
        fields = request.GET.get('fields', None)
        filtered_queryset = self.filter_queryset(self.queryset)
        if fields is not None:
            fields = fields.split(',')
            data = list(filtered_queryset.values(*fields))
            return Response(data)
        else:
            return Response(data= self.serializer_class(filtered_queryset.all(), many=True).data )
    


class BridgeDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = BridgeSerializer
    lookup_url_kwarg = 'ovs_name'
    queryset = OVSBridge.objects.all()
