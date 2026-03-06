from apps.shared.models.settings import SiteSettings

def site_settings_context(request):
    """
    Injects global SiteSettings into every template context.
    """
    return {
        'site_settings': SiteSettings.get_instance()
    }
