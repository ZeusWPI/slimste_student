from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Card, Label, QuizResult
from .serializers import CardSerializer, LabelSerializer, QuizResultSerializer


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

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
    pagination_class = None

    def get_queryset(self):
        # Return cards:
        # 1. Owned by user
        # 2. With labels shared with user
        # 3. With labels owned by user (so we see cards others create with our labels)
        queryset = Card.objects.filter(
            Q(owner=self.request.user) | 
            Q(labels__shared_with=self.request.user) |
            Q(labels__owner=self.request.user)
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

    def update(self, request, *args, **kwargs):
        card = self.get_object()
        if card.owner != request.user:
            return Response(
                {'error': 'You can only edit cards you created'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        card = self.get_object()
        if card.owner != request.user:
            return Response(
                {'error': 'You can only edit cards you created'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        card = self.get_object()
        if card.owner != request.user:
            return Response(
                {'error': 'You can only delete cards you created'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


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


class QuizResultViewSet(viewsets.ModelViewSet):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only quiz results for the current user
        return QuizResult.objects.filter(user=self.request.user).order_by('-completed_at')

    def list(self, request, *args, **kwargs):
        # Check if 'all' parameter is set to bypass pagination
        if request.query_params.get('all') == 'true':
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
