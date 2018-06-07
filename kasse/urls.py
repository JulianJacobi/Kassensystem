from django.urls import path
from .views import *
from . import ajax_views

urlpatterns = [
    path('', kasse_view, name="kasse"),
    path('<int:menu_id>', menu_view, name='single_menu'),
    path('settings', settings_view, name="settings"),
    path('settings/<int:menu_id>', menu_edit_view, name="edit_menu"),
    path('settings/<int:menu_id>/delete', menu_delete_view, name="delete_menu"),

    path('settings/menus/add', add_menu_view, name="add_menu"),

    path('settings/products', product_list_view, name="product_list"),
    path('settings/products/add', add_product_view, name="add_product"),
    path('settings/products/<int:product_id>/edit', edit_product_view, name="edit_product"),
    path('settings/products/<int:product_id>/delete', remove_product, name="delete_product"),

    path('settings/events', events_view, name="events"),
    path('settings/events/create', create_event_view, name="create_event"),
    path('settings/events/<int:event_id>', event_view, name="event"),
    path('settings/events/<int:event_id>/edit', edit_event_view, name="edit_event"),
    path('settings/events/<int:event_id>/remove', delete_event_view, name="remove_event"),
    path('settings/events/<int:event_id>/stats', event_stats_view, name="event_stats"),

    path('settings/users', users_view, name="users"),
    path('settings/users/create', add_user_view, name="add_user"),
    path('settings/users/<int:user_id>/set_password', set_password_view, name="set_password"),
    path('settings/users/<int:user_id>/remove', remove_user_view, name="remove_user"),

    path('settings/general_settings', general_settings_view, name="general_settings"),

    path('ajax/settings/menus/<int:menu_id>/remove_product', ajax_views.update_menu_view, name="ajax_update_menu"),
    path('ajax/searchProducts', ajax_views.search_products, name="search_products"),
    path('ajax/add_sale', ajax_views.add_sale_view, name="add_sale"),
    path('ajax/open_drawer', ajax_views.open_drawer, name="open_drawer"),
    path('ajax/time', ajax_views.time_view, name="time"),

]
