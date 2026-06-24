from django.urls import path

from search.views import SearchSelectView, SearchSuggestionsView

urlpatterns = [
    path(
        'suggestions/',
        SearchSuggestionsView.as_view(),
        name='search-suggestions',
    ),
    path(
        'select/',
        SearchSelectView.as_view(),
        name='search-select',
    ),
]
