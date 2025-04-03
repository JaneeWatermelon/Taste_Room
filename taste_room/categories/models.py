from django.db import models
from django.db.models import ManyToManyField
from django.utils.text import slugify

def transliterate_russian_to_pseudo_english(text):
    transliteration_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
        'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
        'ь': '', 'э': 'e', 'ы': 'y', 'ю': 'yu', 'я': 'ya',
    }

    # Заменяем каждую букву на соответствующую
    transliterated_text = ''.join(transliteration_table.get(char.lower(), char.lower()) for char in text)
    return transliterated_text

def get_unique_slug(instance, model_class, old_slug):
    new_slug = old_slug
    all_slug_models = model_class.objects.filter(slug=new_slug)
    if all_slug_models.exists() and all_slug_models.first().id != instance.id:
        new_slug = f"{old_slug}-{instance.id}"
    return new_slug


class RecipeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(name), verbose_name="Ссылочное название")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Подкатегория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        old_slug = slugify(transliterate_russian_to_pseudo_english(self.name))
        self.slug = get_unique_slug(self, RecipeCategory, old_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CategoryGroup(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    categories = ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    class Meta:
        verbose_name = "Группа категорий"
        verbose_name_plural = "Группы категорий"

    def save(self, *args, **kwargs):
        old_slug = slugify(transliterate_russian_to_pseudo_english(self.title))
        self.slug = get_unique_slug(self, CategoryGroup, old_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
