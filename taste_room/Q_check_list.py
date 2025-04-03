from django.db.models import Q

# ===== БАЗОВЫЕ ФИЛЬТРЫ =====
Q(title__icontains="суп")          # Проверяет наличие "суп" в title (регистронезависимо)
Q(cooking_time__lt=30)             # Время готовки < 30 минут
Q(is_published=True)               # Поле равно True

# ===== КОМБИНИРОВАНИЕ =====
Q(title__icontains="суп") & Q(is_published=True)  # И (AND)
Q(title__icontains="суп") | Q(description__icontains="суп")  # ИЛИ (OR)
~Q(category="десерты")            # НЕ (NOT)

# ===== РАСШИРЕННЫЕ ВОЗМОЖНОСТИ =====
# Поиск по связанным моделям
Q(author__username="admin")       # По ForeignKey
Q(ingredients__name="картофель")  # По ManyToMany

# Сложные условия
(Q(title__icontains="курица") | Q(title__icontains="цыплёнок")) & ~Q(is_spicy=True)

# Динамическое построение
filters = Q()
if search_query:
    filters &= Q(title__icontains=search_query)
if category:
    filters &= Q(category=category)

# ===== СПЕЦИАЛЬНЫЕ ОПЕРАТОРЫ =====
Q(id__in=[1, 2, 3])              # ID в списке
Q(created_at__year=2023)          # По году
Q(metadata__tags__contains=["вегетарианское"])  # Для JSONField

# ===== ПРИМЕР ИСПОЛЬЗОВАНИЯ =====
from recipes.models import Recipe

# Поиск опубликованных супов или бульонов с готовкой < 1 часа
queryset = Recipe.objects.filter(
    (Q(title__icontains="суп") | Q(title__icontains="бульон")) &
    Q(cooking_time__lt=60) &
    Q(is_published=True)
)

# Вывод SQL для отладки
print(queryset.query)