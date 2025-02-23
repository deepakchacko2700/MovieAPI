from django.shortcuts import render
from .utils import get_movies
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet
from collections import Counter
from django.shortcuts import get_object_or_404

class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
        refresh = RefreshToken.for_user(user) # get jwt tokens for user
        return Response({'access_token': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def list_movies(request):
    """Get movies list from third party api"""

    try:
        movies_list = get_movies()
        return Response(movies_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Unable to fetch the list of movies'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class CollectionViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return user.collections.all()
    
    def list(self, request):
        try:
            collections = Collection.objects.prefetch_related('movies').filter(user=request.user) # prefetch movies for collections          
            genre_counter = Counter()
            # Loop through each collection and its movies
            collection_data = []
            for collection in collections:
                collection_data.append({
                    'title': collection.title,
                    'uuid': str(collection.uuid),
                    'description': collection.description
                })        
                for movie in collection.movies.all():
                    genre_counter.update(movie.get_genres_list())

            top_genres = genre_counter.most_common(3)  # Top 3 most common genres
            response_data = {
                'is_success': True,
                'data': {
                    'collections': collection_data,
                    'favourite_genres': [genre for genre, _ in top_genres]
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
    
        except Exception as e:
            print(f'Error when listing collection: {str(e)}')
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection = serializer.save(user=request.user)
            return Response({'collection_uuid': collection.uuid}, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, pk):
        instance = get_object_or_404(Collection.objects.all(), pk=pk)
        serializer = CollectionSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_collection = serializer.save()
            return Response(Response({
                'title': updated_collection.title,
                'description': updated_collection.description,
                'movies': serializer.data['movies']
            }, status=status.HTTP_200_OK)
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.all(), pk=pk)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
