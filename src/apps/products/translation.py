from modeltranslation.translator import translator, TranslationOptions

from apps.products.models import Category, Product, Collection


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Category, CategoryTranslationOptions)
translator.register(Product, ProductTranslationOptions)

class CollectionTranslationOptions(TranslationOptions):
    fields = ("name", "description")

translator.register(Collection, CollectionTranslationOptions)
