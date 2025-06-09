def appearance(intervals):
    """Возвращает время общего присутствия ученика и учителя на уроке"""
    
    def timestamps_to_intervals(timestamps):
        """Преобразует список временных меток в список интервалов (start, end)"""
        intervals = []
        for i in range(0, len(timestamps), 2):
            intervals.append((timestamps[i], timestamps[i + 1]))
        return intervals
    
    def intersect_intervals(interval1, interval2):
        """Находит пересечение двух интервалов"""
        start = max(interval1[0], interval2[0])
        end = min(interval1[1], interval2[1])
        
        if start < end:
            return (start, end)
        return None
    
    def intersect_all_intervals(intervals_list1, intervals_list2):
        """Находит все пересечения между двумя списками интервалов"""
        intersections = []
        
        for interval1 in intervals_list1:
            for interval2 in intervals_list2:
                intersection = intersect_intervals(interval1, interval2)
                if intersection:
                    intersections.append(intersection)
        
        return intersections
    
    # Получаем интервалы урока (всегда один)
    lesson_intervals = timestamps_to_intervals(intervals['lesson'])
    
    # Получаем интервалы ученика и учителя
    pupil_intervals = timestamps_to_intervals(intervals['pupil'])
    tutor_intervals = timestamps_to_intervals(intervals['tutor'])
    
    # Находим пересечения ученика с уроком
    pupil_lesson_intersections = intersect_all_intervals(pupil_intervals, lesson_intervals)
    
    # Находим пересечения учителя с уроком
    tutor_lesson_intersections = intersect_all_intervals(tutor_intervals, lesson_intervals)
    
    # Находим пересечения всех троих (ученик+учитель+урок)
    final_intersections = intersect_all_intervals(pupil_lesson_intersections, tutor_lesson_intersections)
    
    # Суммируем длительности всех пересечений
    total_time = 0
    for start, end in final_intersections:
        total_time += end - start
    
    return total_time


# Пример использования:
if __name__ == "__main__":
    # Тестовый пример
    test_data = {
        'lesson': [1594663200, 1594666800],  # урок с 12:00 до 13:00
        'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],  
        'tutor': [1594663290, 1594663430, 1594663443, 1594666473]
    }
    
    result = appearance(test_data)
    print(f"Общее время присутствия: {result} секунд")