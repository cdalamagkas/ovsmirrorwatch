from django import forms
from mirror.models import OVSPort
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class PortForm(forms.ModelForm):

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = OVSPort
        fields = ["ovs_name", "friendly_name", "bridge", "description"]
    
    def __init__(self, *args, **kwargs):
        super(PortForm, self).__init__(*args, **kwargs)
        self.fields["ovs_name"].label = "Name of the OVS Port (assigned by the OVS system)"
        self.fields["friendly_name"].label = "User-defined name of the OVS Port (for administrative purposes)"
        self.fields["bridge"].label = "OVS Bridge that the Port belongs to"
        self.fields["description"].label = "Administrative information related to the OVS Port"
        self.fields["description"].required = False
