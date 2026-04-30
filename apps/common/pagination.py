from rest_framework.pagination import PageNumberPagination


class OptionalPageSizePagination(PageNumberPagination):
    """
    PageNumberPagination that allows the client to request a custom page size.
    Special values for `page_size` query param:
      - `0`, `all`, or `infinite` will return the full queryset (no pagination)
    Otherwise behaves like normal PageNumberPagination with a `page_size_query_param`.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def paginate_queryset(self, queryset, request, view=None):
        # allow special values to disable pagination and return all results
        ps = request.query_params.get(self.page_size_query_param)
        if ps is not None:
            ps_lower = ps.lower()
            if ps_lower in ('0', 'all', 'infinite'):
                # set page_size to full count so PageNumberPagination will include everything
                try:
                    self.page_size = queryset.count()
                except Exception:
                    # fallback: leave as default if count() fails
                    self.page_size = None

        return super().paginate_queryset(queryset, request, view)
