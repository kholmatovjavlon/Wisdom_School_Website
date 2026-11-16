from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AdmissionEnquiry, ContactMessage, LearningStage


class HoneypotMixin(forms.Form):
    """Hidden field that real visitors leave empty; bots usually fill it."""

    website = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("spam")
        return ""


class AdmissionEnquiryForm(HoneypotMixin, forms.ModelForm):
    consent = forms.BooleanField(required=True, initial=True, label=_(
        "I agree to the processing of my personal data."))

    class Meta:
        model = AdmissionEnquiry
        fields = ["parent_name", "phone", "stage", "next_step", "consent"]
        labels = {
            "parent_name": _("Parent's name"),
            "phone": _("Phone"),
            "stage": _("Child's stage"),
            "next_step": _("How should we contact you?"),
        }
        widgets = {
            "parent_name": forms.TextInput(attrs={"placeholder": _("For example, Dilnoza"), "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+998 __ ___ __ __", "autocomplete": "tel",
                                            "inputmode": "tel"}),
            "next_step": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        self.fields["stage"].queryset = LearningStage.objects.filter(is_active=True)
        self.fields["stage"].required = False
        self.fields["stage"].empty_label = _("Select a stage")
        self.fields["next_step"].choices = list(AdmissionEnquiry.NextStep.choices)
        self.fields["next_step"].required = False
        self.fields["next_step"].initial = AdmissionEnquiry.NextStep.CALL


class ContactForm(HoneypotMixin, forms.ModelForm):
    consent = forms.BooleanField(required=True, label=_(
        "I have read the privacy policy and agree to be contacted about my message."))

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message", "consent"]
        labels = {
            "name": _("Full name"),
            "email": _("Email address"),
            "subject": _("Subject"),
            "message": _("Message"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Your full name"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "message": forms.Textarea(attrs={"placeholder": _("How can we help?"), "rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].choices = [("", _("Select a subject"))] + list(ContactMessage.Subject.choices)
