from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .response import success_response, paginated_response, created_response


class BaseModelViewSet(ModelViewSet):
    """
    Base viewset that wraps default responses in consistent success_response format.
    Overrides list/retrieve/create/update/destroy to use success_response and created_response.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = {
                'results': serializer.data,
                'count': self.paginator.page.paginator.count if hasattr(self.paginator, 'page') else len(serializer.data),
                'next': self.paginator.get_next_link() if hasattr(self.paginator, 'get_next_link') else None,
                'previous': self.paginator.get_previous_link() if hasattr(self.paginator, 'get_previous_link') else None,
            }
            return paginated_response(data=data, message='List retrieved successfully')

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='List retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Detail retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return created_response(data=serializer.data, message='Resource created successfully')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message='Resource updated successfully')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='Resource deleted successfully', status_code=status.HTTP_204_NO_CONTENT)
