from django import forms

from categories.models import CategoryGroup, RecipeCategory


class CategoryGroupForm(forms.ModelForm):
    class Meta:
        model = CategoryGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Фильтруем категории, чтобы отображались только те, у которых parent = None
        self.fields['categories'].queryset = RecipeCategory.objects.filter(parent__isnull=True)