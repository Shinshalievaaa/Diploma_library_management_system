from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Author, Book, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    Регистрация доступна всем (AllowAny), управление профилями — авторизованным.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления авторами.
    Просмотр доступен всем, добавление/редактирование — только авторизованным.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления книгами.
    Поддерживает поиск по названию/описанию и фильтрацию по жанру, автору и доступности.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['genre', 'author', 'is_available']
    search_fields = ['title', 'description']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def borrow(self, request, pk=None):
        """Для выдачи книги текущему пользователю"""
        book = self.get_object()

        if not book.is_available:
            return Response(
                {'error': 'Книга в данный момент недоступна для выдачи'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Меняем статус книги и фиксируем запись о выдаче
        book.is_available = False
        book.save()

        record = BorrowRecord.objects.create(user=request.user, book=book)
        serializer = BorrowRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def return_book(self, request, pk=None):
        """Для возврата книги в библиотеку"""
        book = self.get_object()

        # Ищем активную запись выдачи этой книги для текущего пользователя
        record = BorrowRecord.objects.filter(
            book=book,
            user=request.user,
            is_returned=False
        ).first()

        if not record:
            return Response(
                {'error': 'Активная запись о выдаче этой книги для вашего аккаунта не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Фиксируем возврат книги
        record.is_returned = True
        record.return_date = timezone.now()
        record.save()

        book.is_available = True
        book.save()

        return Response({'status': 'Книга успешно возвращена в библиотеку'})


class BorrowRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра истории выдачи книг.
    Пользователи видят только свои книги, администраторы — всю историю.
    """
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return BorrowRecord.objects.all()
        return BorrowRecord.objects.filter(user=self.request.user)
