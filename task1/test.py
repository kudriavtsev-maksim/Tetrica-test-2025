import unittest
from solution import strict

class TestStrictDecorator(unittest.TestCase):
    def test_correct_types(self):
        """Проверка корректных типов"""
        @strict
        def sum_two(a: int, b: int) -> int:
            return a + b
        
        self.assertEqual(sum_two(1, 2), 3)

    def test_incorrect_types(self):
        """Проверка неправильных типов"""
        @strict
        def concat(s1: str, s2: str) -> str:
            return s1 + s2
        
        with self.assertRaises(TypeError) as cm:
            concat("a", 2)  # s2 должно быть str, передаем int
        
        self.assertIn("Argument 's2' must be str, not int", str(cm.exception))

    def test_mixed_arguments(self):
        """Проверка позиционных и именованных аргументов"""
        @strict
        def mixed(a: int, b: str, c: float) -> str:
            return f"{a}{b}{c}"
        
        # Позиционные
        self.assertEqual(mixed(1, "text", 3.0), "1text3.0")
        
        # Именованные
        self.assertEqual(mixed(a=1, b="text", c=3.0), "1text3.0")
        
        # Смешанные
        self.assertEqual(mixed(1, b="text", c=3.0), "1text3.0")
        
        # Неправильный тип в смешанных
        with self.assertRaises(TypeError):
            mixed(1, "text", c="3.0")  # c должно быть float

    def test_all_supported_types(self):
        """Проверка всех гарантированных типов"""
        @strict
        def type_check(
            b: bool, 
            i: int, 
            f: float, 
            s: str
        ) -> tuple:
            return (b, i, f, s)
        
        # Корректные значения
        self.assertEqual(type_check(True, 1, 1.0, "text"), (True, 1, 1.0, "text"))
        
        # Неправильные типы
        with self.assertRaises(TypeError):
            type_check(1, True, "1.0", 42)  # Все аргументы неправильные

    def test_no_return_check(self):
        """Проверка, что возвращаемое значение не проверяется"""
        @strict
        def returns_wrong_type(a: int) -> str:
            return a  # Возвращаем int вместо str
        
        self.assertEqual(returns_wrong_type(10), 10)  # Должно работать без ошибок

    def test_no_annotations(self):
        """Проверка функции без аннотаций"""
        @strict
        def no_annotations(a, b):
            return a + b
        
        self.assertEqual(no_annotations(1, 2), 3)
        self.assertEqual(no_annotations("a", "b"), "ab")

if __name__ == '__main__':
    unittest.main()