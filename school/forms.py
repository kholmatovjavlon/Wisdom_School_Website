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
    consent = forms.BooleanField(required=True, label=_(
        "I agree to be contacted about my enquiry and have read the privacy policy."))

    class Meta:
        model = AdmissionEnquiry
        fields = ["parent_name", "email", "phone", "stage", "next_step", "message", "consent"]
        labels = {
            "parent_name": _("Parent / guardian name"),
            "email": _("Email address"),
            "phone": _("Phone number"),
            "stage": _("Learning stage of interest"),
            "next_step": _("Preferred next step"),
            "message": _("Anything you would like us to know?"),
        }
        widgets = {
            "parent_name": forms.TextInput(attrs={"placeholder": _("Your full name"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": _("Include country code"), "autocomplete": "tel",
                                            "inputmode": "tel"}),
            "message": forms.Textarea(attrs={"placeholder": _("Tell us how we can help your family…"), "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stage"].queryset = LearningStage.objects.filter(is_active=True)
        self.fields["stage"].required = True
        self.fields["stage"].empty_label = _("Select learning stage")
        self.fields["next_step"].choices = [("", _("Select an option"))] + list(
            AdmissionEnquiry.NextStep.choices)


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
