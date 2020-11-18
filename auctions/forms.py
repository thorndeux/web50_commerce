"""
Contains form definitions
"""
from django import forms

from .models import Listing

class ListingForm(forms.ModelForm):
    """
    Form to create a new listing. Based on the listing model
    """
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startingBid', 'imageURL', 'category']
        labels = {
            'startingBid': "Starting Bid",
            'imageURL': "Image URL (optional)",
            'category': "Category (optional)"
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': "Add details about your item here"})
        }

    def __init__(self, *args, **kwargs):
        """
        __init__ function to customize fields
        """
        super(ListingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': "form-control"})
        self.fields['title'].widget.attrs.update({'placeholder': "Your title here"})
        self.fields['startingBid'].widget.attrs.update({'placeholder': "$0.00"})
        self.fields['imageURL'].widget.attrs.update({'placeholder': "Add an image url for your item"})

class AddBid(forms.Form):
    """
    Form to add a bid on a listing
    """
    bid = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput({
            'class': "form-control",
            'placeholder': "$0.00"
        })
    )

class AddComment(forms.Form):
    """
    Form to add a comment to a listing
    """
    comment = forms.CharField(
        max_length=500,
        widget=forms.Textarea({
            'class': "form-control",
            'placeholder': "Enter comment here",
            'rows': 3,
            'cols': 15
        })
    )