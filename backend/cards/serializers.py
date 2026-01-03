from rest_framework import serializers
from .models import Card, Label, QuizResult


class LabelSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField()
    shared_with_usernames = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    card_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = ['id', 'name', 'color', 'owner_username', 'shared_with_usernames', 'is_owner', 'card_count', 'created_at']
        read_only_fields = ['id', 'owner_username', 'card_count', 'created_at']

    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else 'Unknown'

    def get_shared_with_usernames(self, obj):
        return [user.username for user in obj.shared_with.all()]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.owner == request.user
        return False

    def get_card_count(self, obj):
        return obj.cards.count()


class CardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Label.objects.all(), 
        source='labels', 
        write_only=True,
        required=False
    )
    owner_username = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'title', 'icon', 'quick_facts', 'keywords', 'labels', 'label_ids', 'owner_username', 'is_owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner_username', 'is_owner', 'created_at', 'updated_at']

    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else 'Unknown'

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.owner == request.user
        return False


class QuizResultSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Label.objects.all(), 
        source='labels', 
        write_only=True,
        required=False
    )

    class Meta:
        model = QuizResult
        fields = ['id', 'labels', 'label_ids', 'total_questions', 'correct_answers', 'wrong_answers', 'time_remaining', 'is_untimed', 'completed_at']
        read_only_fields = ['id', 'completed_at']
