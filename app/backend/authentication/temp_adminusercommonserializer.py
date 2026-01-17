class AdminUserCommonSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    company_name = serializers.CharField(source='company_name')

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'user_type',
            'project',
            'admin_type',
            'company_name',
            'registered_address',
            'name',
            'surname',
            'department',
            'designation',
            'phone_number',
            'created_by',
        ]
        read_only_fields = ['created_by']
