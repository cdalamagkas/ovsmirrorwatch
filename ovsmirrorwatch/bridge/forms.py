from django import forms
from bridge.models import OVSBridge
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class BridgeForm(forms.ModelForm):

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = OVSBridge
        fields = ["ovs_name", "friendly_name", "ovsdb_manager", "description"]
    
    def __init__(self, *args, **kwargs):
        super(BridgeForm, self).__init__(*args, **kwargs)
        self.fields["ovs_name"].label = "Name of the OVS Bridge (assigned by the OVS system)"
        self.fields["friendly_name"].label = "User-defined name of the OVS Bridge (for administrative purposes)"
        self.fields["ovsdb_manager"].label = "OVSDB Manager"
        self.fields["description"].label = "Administrative information related to the OVS Bridge"
        self.fields["description"].required = False
