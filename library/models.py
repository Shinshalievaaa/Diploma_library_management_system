from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    bio = models.TextField(blank=True, null=True, verbose_name="Биография")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name="Автор")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    published_date = models.DateField(verbose_name="Дата публикации")
    is_available = models.BooleanField(default=True, verbose_name="Доступна для выдачи")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title']

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records', verbose_name="Пользователь")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records', verbose_name="Книга")
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")
    return_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата возврата")
    is_returned = models.BooleanField(default=False, verbose_name="Возвращена")

    class Meta:
        verbose_name = "Запись о выдаче"
        verbose_name_plural = "Записи о выдачах"
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
