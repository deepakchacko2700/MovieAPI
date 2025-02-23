from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Collection, Movie


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],password=validated_data['password'])
        return user
    

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['uuid', 'title', 'description', 'genres']

    # when reading, modify the representation of genres
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['genres'] = instance.get_genres_list()
        return representation
    

class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['title', 'description', 'movies']

    def create(self, validated_data):
        movies_data = validated_data.pop('movies')
        collection = Collection.objects.create(**validated_data)
        for movie_data in movies_data:
            Movie.objects.create(collection=collection, **movie_data)
        return collection
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save() # update and save collection instance

        movies_data = validated_data.get('movies', [])
        current_movie_uuids = {movie.uuid for movie in instance.movies.all()} # existing movies in the collection

        for movie_data in movies_data:
            movie_uuid = movie_data.get('uuid')
            if movie_uuid in current_movie_uuids:
                # Update existing movie
                movie = instance.movies.get(uuid=movie_uuid)
                movie.title = movie_data.get('title', movie.title)
                movie.description = movie_data.get('description', movie.description)
                movie.genres = movie_data.get('genres', movie.genres)
                movie.save()
                current_movie_uuids.remove(movie_uuid)  # Remove from the current movie UUIDs
            else:
                # Add new movie to the collection
                Movie.objects.create(
                    uuid=movie_uuid,
                    title=movie_data['title'],
                    description=movie_data['description'],
                    genres=movie_data['genres'],
                    collection=instance
                )       
        # Delete the movies that are no longer in the updated list
        instance.movies.filter(uuid__in=current_movie_uuids).delete()

        return instance

