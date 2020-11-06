from django import forms

from .models import Category, Listing

def get_categories():
    """
    Function to generate a list of categories for use in a dropdown menu

    Returns:
        List: List of tuples containing id and name of all categories
    """
    categories = [(0, "Choose category")]
    for category in Category.objects.all():
        categories.append((category.pk, category.name))
    return categories

# Form class for the listings form, using Bootstrap class for base styling
class NewListing(forms.Form):
    title = forms.CharField(
        label="Title",
        max_length=128,
        widget=forms.TextInput({
            'class': "form-control",
            'placeholder': "Enter title here"}))
    description = forms.CharField(
        label="Description",
        max_length=2000,
        widget=forms.Textarea({
            'class': "form-control",
            'placeholder': "Describe your item here..."}))
    bid = forms.DecimalField(
        label="Starting bid",
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput({
            'class': "form-control",
            'placeholder': "$0.00"}))
    image = forms.URLField(
        label="Image URL",
        required=False,
        widget=forms.URLInput({
            'class': "form-control",
            'placeholder': "Add an image url here"}))
    category = forms.ChoiceField(
        label="Category",
        widget=forms.Select(
            {'class': "form-control"},
            choices=get_categories()))

    def __init__(self, *args, **kwargs):
        """
        __init__ function to updated category choices on initialization
        """
        super(NewListing, self).__init__(*args, **kwargs)
        self.fields['category'].choices = get_categories()

class ListingForm(forms.ModelForm):
    """
    Form to populate the Listing module from a 'Create new listing' view
    """
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startingBid', 'imageURL', 'category']
        labels = {
            'startingBid': "Starting Bid",
            'imageURL': "Image URL"
        }
        placeholder = {
            'title': "Your title here",
        }

    def __init__(self, *args, **kwargs):
        """
        __init__ function to customize fields
        """
        super(ListingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': "form-control"})
        # self.fields['startingBid'].widget.attrs.update({'placeholder': "Starting Bid"})


class AddBid(forms.Form):
    """
    Form to add a bid on a listing
    """
    bid = forms.DecimalField(
        label="Your Bid",
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput({
            'class': "form-control",
            'placeholder': "$0.00"}))
