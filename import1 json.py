import json
import os

class Book:
    def __init__(self, book_id: str, title: str, author: str, year: int, is_issued: bool = False):
        self._id, self._title, self._author, self._year = book_id, title, author, year
        self.is_issued = is_issued

    @property
    def book_id(self): return self._id
    @property
    def title(self): return self._title
    @property
    def author(self): return self._author
    @property
    def year(self): return self._year

    def get_info(self) -> str:
        status = "Видана" if self.is_issued else "В наявності"
        return f"ID: {self._id} | '{self._title}' - {self._author} ({self._year}) [{status}]"

    def to_dict(self) -> dict:
        return {"type": "Book", "book_id": self._id, "title": self._title, "author": self._author, "year": self._year, "is_issued": self.is_issued}

    @staticmethod
    def from_dict(data: dict):
        b_type, id, title, author, year = data.get("type"), data["book_id"], data["title"], data["author"], data["year"]
        issued = data.get("is_issued", False)
        if b_type == "PaperBook":
            return PaperBook(id, title, author, year, data.get("shelf_number", "A1"), issued)
        elif b_type == "EBook":
            return EBook(id, title, author, year, data.get("file_size_mb", 0.0), data.get("format_type", "PDF"), issued)
        return Book(id, title, author, year, issued)


class PaperBook(Book):
    def __init__(self, book_id, title, author, year, shelf_number, is_issued=False):
        super().__init__(book_id, title, author, year, is_issued)
        self.shelf_number = shelf_number

    def get_info(self) -> str:
        return f"[Паперова] {super().get_info()} | Полиця: {self.shelf_number}"

    def to_dict(self) -> dict:
        return {**super().to_dict(), "type": "PaperBook", "shelf_number": self.shelf_number}


class EBook(Book):
    def __init__(self, book_id, title, author, year, file_size_mb, format_type, is_issued=False):
        super().__init__(book_id, title, author, year, is_issued)
        self.file_size_mb, self.format_type = file_size_mb, format_type

    def get_info(self) -> str:
        return f"[Електронна] {super().get_info()} | Розмір: {self.file_size_mb}MB, Формат: {self.format_type}"

    def to_dict(self) -> dict:
        return {**super().to_dict(), "type": "EBook", "file_size_mb": self.file_size_mb, "format_type": self.format_type}


class Reader:
    def __init__(self, reader_id: str, name: str, phone: str):
        self.reader_id, self.name, self.phone, self.borrowed_books = reader_id, name, phone, []

    def to_dict(self) -> dict:
        return {"reader_id": self.reader_id, "name": self.name, "phone": self.phone, "borrowed_books": self.borrowed_books}

    @staticmethod
    def from_dict(data: dict):
        reader = Reader(data["reader_id"], data["name"], data["phone"])
        reader.borrowed_books = data.get("borrowed_books", [])
        return reader


class LibraryManager:
    def __init__(self, filename: str = "library_data.json"):
        self.filename = filename
        self.books, self.readers = {}, {}
        self.load_data()

    def search_books(self, query: str):
        q = query.lower()
        return [b for b in self.books.values() if q in b.title.lower() or q in b.author.lower()]

    def issue_book(self, b_id: str, r_id: str) -> bool:
        if b_id in self.books and r_id in self.readers and not self.books[b_id].is_issued:
            self.books[b_id].is_issued = True
            self.readers[r_id].borrowed_books.append(b_id)
            return True
        return False

    def return_book(self, b_id: str, r_id: str) -> bool:
        if b_id in self.books and r_id in self.readers and self.books[b_id].is_issued and b_id in self.readers[r_id].borrowed_books:
            self.books[b_id].is_issued = False
            self.readers[r_id].borrowed_books.remove(b_id)
            return True
        return False

    def save_data(self):
        data = {"books": [b.to_dict() for b in self.books.values()], "readers": [r.to_dict() for r in self.readers.values()]}
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if not os.path.exists(self.filename): return
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.books = {b["book_id"]: Book.from_dict(b) for b in data.get("books", [])}
                self.readers = {r["reader_id"]: Reader.from_dict(r) for r in data.get("readers", [])}
        except Exception as e:
            print(f"Помилка завантаження: {e}")


def main():
    manager = LibraryManager()
    menu = (
        "\n==================================================\n"
        "       СИСТЕМА УПРАВЛІННЯ БІБЛІОТЕКОЮ \n"
        "==================================================\n"
        "1. Переглянути всі книги\n2. Додати книгу\n3. Вилучити книгу\n"
        "4. Пошук книг\n5. Зареєструвати читача\n6. Список читачів\n"
        "7. Видати книгу\n8. Прийняти книгу\n9. Зберегти та вийти\n"
        "=================================================="
    )

    while True:
        print(menu)
        choice = input("Виберіть пункт (1-9): ").strip()

        if choice == '1':
            print("\n--- КАТАЛОГ ---") if manager.books else print("Каталог порожній.")
            for b in manager.books.values(): print(b.get_info())

        elif choice == '2':
            b_id, title, author = input("ID: ").strip(), input("Назва: ").strip(), input("Автор: ").strip()
            year = int(input("Рік: ").strip() or 2024)
            if input("Тип (1-Паперова, 2-Ел.): ").strip() == '1':
                book = PaperBook(b_id, title, author, year, input("Полиця: ").strip())
            else:
                book = EBook(b_id, title, author, year, float(input("Розмір (MB): ").strip() or 0), input("Формат: ").strip() or "PDF")
            manager.books[b_id] = book
            print("Книгу додано!")

        elif choice == '3':
            b_id = input("ID книги для видалення: ").strip()
            print("Вилучено." if manager.books.pop(b_id, None) else "Не знайдено.")

        elif choice == '4':
            results = manager.search_books(input("Пошуковий запит: ").strip())
            print(f"Знайдено: {len(results)}")
            for b in results: print(b.get_info())

        elif choice == '5':
            r_id = input("ID читача: ").strip()
            manager.readers[r_id] = Reader(r_id, input("ПІБ: ").strip(), input("Телефон: ").strip())
            print("Читача зареєстровано!")

        elif choice == '6':
            print("\n--- ЧИТАЧІ ---") if manager.readers else print("Список порожній.")
            for r in manager.readers.values(): print(f"ID: {r.reader_id} | {r.name} | Книги: {r.borrowed_books}")

        elif choice == '7':
            print("Успіх!" if manager.issue_book(input("ID книги: ").strip(), input("ID читача: ").strip()) else "Помилка видачі.")

        elif choice == '8':
            print("Успіх!" if manager.return_book(input("ID книги: ").strip(), input("ID читача: ").strip()) else "Помилка повернення.")

        elif choice == '9':
            manager.save_data()
            print("Дані збережено. Вихід!")
            break
        else:
            print("Невірний вибір.")

if __name__ == "__main__":
    main()