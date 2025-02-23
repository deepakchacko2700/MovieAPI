from django.test import TestCase
import factory
from .models import Collection, Movie
import uuid
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.PostGenerationMethodCall('set_password', 'password')


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    uuid = factory.LazyFunction(uuid.uuid4)
    title = factory.Faker('sentence')
    description = factory.Faker('text')
    genres = factory.Faker('word')


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    uuid = factory.LazyFunction(uuid.uuid4)
    title = factory.Faker('sentence')
    description = factory.Faker('text')
    user = factory.SubFactory(UserFactory)
    
    @factory.post_generation
    def movies(self, create, extracted, **kwargs):
        if extracted:
            for movie in extracted:
                self.movies.add(movie)



@pytest.mark.django_db
class TestCollectionAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_create_collection(self):
        # Create  fixtures
        collection = CollectionFactory()
        movie1 = MovieFactory.create(collection=collection)
        movie2 = MovieFactory.create(collection=collection)

        # Create collection data with associated movies
        collection_data = {
            "title": "My Collection",
            "description": "A collection of movies",
            "movies": [
                {"uuid": str(movie1.uuid), "title": movie1.title, "description": movie1.description, "genres": movie1.genres},
                {"uuid": str(movie2.uuid), "title": movie2.title, "description": movie2.description, "genres": movie2.genres}
            ]
        }

        response = self.client.post('/collection/', collection_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'collection_uuid' in response.data

    def test_list_collections(self):
        collection1 = CollectionFactory.create(title="Collection 1")
        collection2 = CollectionFactory.create(title="Collection 2")

        # Fetch all collections
        response = self.client.get('/collection/')
        assert response.status_code == status.HTTP_200_OK
        print(response.data['data'])
        assert len(response.data['data']['collections']) == 2
        assert response.data['data']['collections'][0]['title'] == collection1.title
        assert response.data['data']['collections'][1]['title'] == collection2.title

    def test_update_collection(self):
        collection = CollectionFactory.create(title="Old Title")
        movie = MovieFactory.create(title="Movie Title", collection=collection)

        update_data = {
            "title": "Updated Title",
            "description": "Updated collection description",
            "movies": [
                {"uuid": str(movie.uuid), "title": movie.title, "description": movie.description, "genres": movie.genres}
            ]
        }

        response = self.client.put(f'/collection/{collection.uuid}/', update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Title"
        assert response.data['description'] == "Updated collection description"
        assert len(response.data['movies']) == 1
        assert response.data['movies'][0]['uuid'] == str(movie.uuid)

    def test_delete_collection(self):
        collection = CollectionFactory.create()
        response = self.client.delete(f'/collection/{collection.uuid}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Collection.objects.filter(uuid=collection.uuid).exists()

    def test_reset_request_count(self):
        response = self.client.post('/request-count/reset/')
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "request count reset successfully"
