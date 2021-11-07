def cms_context(request):
    from django.conf import settings
    from django.urls import resolve
    current_url_name = resolve(request.path_info).url_name

    context = dict()

    context = {
        **context, 
        **side_menu_context(current_url_name),
        "BASE_TEMPLATE":settings.BASE_TEMPLATE,
    }

    return context

def side_menu_context(current_url_name):
    side_menu = []
    
    url_name = "live_dash"
    item = {
        "text":"Live Dashboard",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-bullet-list-67 text-primary",
        "childs":None,
        }
    side_menu.append(item)    

    url_name = "storico_dash"
    item = {
        "text":"Storico",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-tv-2 text-info",
        "childs":None,
        }
    side_menu.append(item)

    url_name = "icons"
    item = {
        "text":"Icons",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-planet text-blue",
        "childs":None,
        }
    side_menu.append(item)

    url_name = "maps"
    item = {
        "text":"Maps",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-pin-3 text-orange",
        "childs":None,
        }
    side_menu.append(item)

    url_name = "user_profile"
    item = {
        "text":"User profile",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-single-02 text-yellow",
        "childs":None,
        }
    side_menu.append(item)


    url_name = "logout"
    item = {
        "text":"Logout",
        "url":url_name,
        "active":current_url_name==url_name,
        "icon_classes":"ni ni-user-run text-red",
        "childs":None,
        }
    side_menu.append(item)

    return {
        "side_menu":side_menu,
    }