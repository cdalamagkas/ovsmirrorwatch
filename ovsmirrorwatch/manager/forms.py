from django import forms
from manager.models import OVSManager
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class ManagerForm(forms.ModelForm):

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = OVSManager
        fields = ["ip_address", "port", "name", "description"]
    
    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)
        self.fields["ip_address"].label = "IP address of the OVSDB manager"
        self.fields["port"].label = "TCP port of the OVSDB manager"
        self.fields["name"].label = "Friendly name for the OVSDB manager"
        self.fields["description"].label = "Administrative information related to the OVSDB manager"


class ManagerFormEdit(forms.ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = OVSManager
        fields = ["ip_address", "port", "name", "monitor", "description" ]
    
    def __init__(self, *args, **kwargs):
        super(ManagerFormEdit, self).__init__(*args, **kwargs)
        self.fields["ip_address"].label = "IP address of the OVSDB manager"
        self.fields["ip_address"].disabled = True
        self.fields["port"].label = "TCP port of the OVSDB manager"
        self.fields["port"].disabled = True
        self.fields["name"].label = "Friendly name for the OVSDB manager"
        self.fields["name"].disabled = True
        self.fields["monitor"].label = "Enable OVSDB Manager monitoring by OVSMirrorWatch"
        self.fields["description"].label = "Administrative information related to the OVSDB manager"