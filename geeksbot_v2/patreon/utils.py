from rest_framework.response import Response
from rest_framework import status


def create_error_response(msg, status=status.HTTP_404_NOT_FOUND):
    return Response({'details': msg},
                    status=status)


def create_success_creator_response(creator_data, status, many: bool = False):
    from .serializers import PatreonCreatorSerializer
    
    return Response(PatreonCreatorSerializer(creator_data, many=many).data,
                    status=status)


def create_success_tier_response(tier_data, status, many: bool = False):
    from .serializers import PatreonTierSerializer
    
    return Response(PatreonTierSerializer(tier_data, many=many).data,
                    status=status)
