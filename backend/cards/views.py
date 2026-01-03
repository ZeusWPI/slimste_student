from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Card, Label
from .serializers import CardSerializer, LabelSerializer


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return labels owned by user or shared with user
        return Label.objects.filter(
            Q(owner=self.request.user) | Q(shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        label = self.get_object()
        if label.owner != request.user:
            return Response({'error': 'Only owner can share labels'}, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            label.shared_with.add(user)
            return Response({'success': True, 'message': f'Shared with {username}'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        label = self.get_object()
        if label.owner != request.user:
            return Response({'error': 'Only owner can unshare labels'}, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            label.shared_with.remove(user)
            return Response({'success': True, 'message': f'Unshared with {username}'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return cards owned by user or cards with labels shared with user
        queryset = Card.objects.filter(
            Q(owner=self.request.user) | Q(labels__shared_with=self.request.user)
        ).distinct().prefetch_related('labels')
        
        label_ids = self.request.query_params.get('labels', None)
        include_unlabeled = self.request.query_params.get('include_unlabeled', 'false').lower() == 'true'
        
        if label_ids:
            label_id_list = [int(id) for id in label_ids.split(',') if id.isdigit()]
            if label_id_list:
                if include_unlabeled:
                    queryset = queryset.filter(
                        Q(labels__id__in=label_id_list) | Q(labels__isnull=True)
                    ).distinct()
                else:
                    queryset = queryset.filter(labels__id__in=label_id_list).distinct()
        elif include_unlabeled:
            queryset = queryset.filter(labels__isnull=True)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search for users by username, excluding current user. Returns top 5 matches."""
    query = request.query_params.get('q', '').strip()
    
    # Exclude current user from results
    users = User.objects.exclude(id=request.user.id)
    
    if query:
        users = users.filter(username__icontains=query)
    
    # Get top 5 users
    users = users.order_by('username')[:5]
    
    return Response([{'username': user.username} for user in users])
