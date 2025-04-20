from django import forms
from mirror.models import OVSMirror
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class MirrorForm(forms.ModelForm):

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = OVSMirror
        fields = ["name", "src_ports", "dst_ports", "out_port", "description"]
    
    def __init__(self, *args, **kwargs):
        super(MirrorForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Name of the Mirroring session"
        self.fields["src_ports"].label = "Source Ports"
        self.fields["dst_ports"].label = "Destination Ports"
        self.fields["out_port"].label = "Output Port"
        self.fields["description"].label = "Administrative information related to the Mirroring session"
        self.fields["description"].required = False
