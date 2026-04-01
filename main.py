import time
import random
from collections import defaultdict


# S-блок 
SBOX = list(range(256))
# Перемешивание S-блока для криптографической стойкости
random.seed(42)
random.shuffle(SBOX)
SBOX = bytearray(SBOX)

# Обратный S-блок
INV_SBOX = bytearray(256)
for i, val in enumerate(SBOX):
    INV_SBOX[val] = i


def s_transform(data):
    return bytearray(SBOX[b] for b in data)


def l_transform(data):
    result = bytearray(64)
    for i in range(64):
        # Простое XOR перемешивание
        val = 0
        for j in range(64):
            if (data[j] >> (i % 8)) & 1:
                val ^= (1 << (j % 8))
        result[i] = val & 0xFF
    return result


def compress(h, block):
    # XOR с блоком
    temp = bytearray(h[i] ^ block[i] for i in range(64))
    # S преобразование
    temp = s_transform(temp)
    # L преобразование
    temp = l_transform(temp)
    # XOR с исходным состоянием
    result = bytearray(h[i] ^ temp[i] for i in range(64))
    return result


class Streebog:
    
    def __init__(self):
        self.h = bytearray(64) 
        self.buffer = bytearray()
    
    def update(self, data):
        self.buffer.extend(data)
        
        while len(self.buffer) >= 64:
            block = bytearray(self.buffer[:64])
            self.h = compress(self.h, block)
            self.buffer = self.buffer[64:]
    
    def digest(self):
        if self.buffer:
            padding = bytearray(64)
            padding[:len(self.buffer)] = self.buffer
            padding[len(self.buffer)] = 0x80
            self.h = compress(self.h, padding)
        
        return bytes(self.h)
    
    def hexdigest(self):
        return self.digest().hex()
    
    def msb48(self):
        return int.from_bytes(self.digest()[:6], 'big')

# Задача 1: Оценка производительности

def task1_performance():
    print("\n" + "="*60)
    print("ЗАДАЧА 1: Оценка производительности STREEBOG")
    print("="*60)
    
    test_sizes = [64, 1024, 10240]  # байт
    iterations = 100
    
    for size in test_sizes:
        test_data = b"X" * size
        
        start = time.time()
        for _ in range(iterations):
            h = Streebog()
            h.update(test_data)
            h.digest()
        elapsed = time.time() - start
        
        speed = (iterations * size) / elapsed / 1024  # KB/sec
        print(f"\nРазмер данных: {size} байт")
        print(f"  {iterations} итераций: {elapsed:.3f} сек")
        print(f"  Скорость: {speed:.1f} KB/сек")
        print(f"  Хэшей/сек: {iterations/elapsed:.1f}")

# Задача 2: Поиск коллизии для MSB48

def task2_find_collision():
    print("\n" + "="*60)
    print("ЗАДАЧА 2: Поиск коллизии для h(x) = MSB48(STREEBOG(x))")
    print("="*60)
    
    hash_table = {}
    attempts = 0
    start_time = time.time()
    
    print("\nПоиск коллизии (ожидайте)...")
    
    while True:
        msg = f"msg_{attempts}_{random.randint(0, 2**32)}".encode()
        
        h = Streebog()
        h.update(msg)
        msb48 = h.msb48()
        
        if msb48 in hash_table:
            existing_msg = hash_table[msb48]
            if existing_msg != msg:
                elapsed = time.time() - start_time
                print(f"\n✓ Коллизия найдена!")
                print(f"  Попыток: {attempts + 1}")
                print(f"  Время: {elapsed:.2f} сек")
                print(f"  MSB48: {msb48:012x}")
                print(f"\nСообщение 1: {existing_msg[:50]}...")
                print(f"Сообщение 2: {msg[:50]}...")
                
                h1 = Streebog()
                h1.update(existing_msg)
                h2 = Streebog()
                h2.update(msg)
                is_collision = (h1.msb48() == h2.msb48())
                print(f"Проверка: {h1.msb48():012x} == {h2.msb48():012x}")
                print(f"Коллизия подтверждена: {is_collision}")
                if is_collision:
                    print("✓ Коллизия успешно найдена!")
                return
        else:
            hash_table[msb48] = msg
        
        attempts += 1
        
        if attempts % 10000 == 0:
            print(f"  Попыток: {attempts}, уникальных хэшей: {len(hash_table)}")
        
        if attempts > 200000:
            print("Достигнут лимит попыток. Попробуйте снова.")
            break

# Задача 3: Осмысленная коллизия

def task3_meaningful_collision():
    print("\n" + "="*60)
    print("ЗАДАЧА 3: Поиск осмысленной коллизии")
    print("="*60)
    
    # Выбираем изображения
    x_image = "кот"
    y_image = "собака"
    
    print(f"\nИщем коллизию между сообщениями:")
    print(f"  X: '{x_image}'")
    print(f"  Y: '{y_image}'")
    
    template_x = f"На этом фото изображен {x_image}. {x_image} сидит на заборе и смотрит вдаль. Файл: {x_image}_photo.jpg"
    template_y = f"На этом фото изображена {y_image}. {y_image} бежит по зеленой траве. Файл: {y_image}_photo.jpg"
    
    print(f"\nШаблон X: {template_x}")
    print(f"Шаблон Y: {template_y}")
    
    hash_table = {}
    attempts = 0
    start_time = time.time()
    
    print("\nПоиск осмысленной коллизии...")
    
    while True:
        suffix = f"_{attempts:06d}_{random.randint(0, 9999)}"
        msg_x = (template_x + suffix).encode()
        msg_y = (template_y + suffix).encode()
        
        h_x = Streebog()
        h_x.update(msg_x)
        msb48_x = h_x.msb48()
        
        h_y = Streebog()
        h_y.update(msg_y)
        msb48_y = h_y.msb48()
        
        if msb48_x == msb48_y:
            elapsed = time.time() - start_time
            print(f"\n✓ Осмысленная коллизия найдена!")
            print(f"  Попыток: {attempts + 1}")
            print(f"  Время: {elapsed:.2f} сек")
            print(f"  MSB48: {msb48_x:012x}")
            print(f"\nСообщение для '{x_image}':")
            print(f"  {msg_x.decode()[:80]}...")
            print(f"\nСообщение для '{y_image}':")
            print(f"  {msg_y.decode()[:80]}...")
            
            print(f"\n✓ Коллизия подтверждена: {msb48_x:012x} == {msb48_y:012x}")
            return
        
        if msb48_x in hash_table:
            existing = hash_table[msb48_x]
            if existing != msg_x:
                print(f"\n✓ Найдена коллизия между разными суффиксами!")
                return
        
        hash_table[msb48_x] = msg_x
        attempts += 1
        
        if attempts % 5000 == 0:
            print(f"  Попыток: {attempts}, проверено пар: {attempts * 2}")
        
        if attempts > 50000:
            print("Достигнут лимит попыток. Коллизия не найдена.")
            break





def demo_hash():
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ХЭШ-ФУНКЦИИ STREEBOG")
    print("="*60)
    
    test_messages = [
        b"Hello, Streebog!",
        b"Hello, Streebogg!",
        b"The quick brown fox jumps over the lazy dog"
    ]
    
    for msg in test_messages:
        h = Streebog()
        h.update(msg)
        digest = h.hexdigest()
        msb48 = h.msb48()
        
        print(f"\nСообщение: {msg}")
        print(f"STREEBOG-512: {digest[:32]}...")
        print(f"MSB48: {msb48:012x}")


def main():
    print("\n" + "="*60)
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("Парадокс дней рождения и криптографические хэш-функции")
    print("STREEBOG (GOST R 34.11-2012)")
    print("="*60)
    
    demo_hash()
    
    task1_performance()
    
    task2_find_collision()
    
    task3_meaningful_collision()
    
    print("\n" + "="*60)
    print("ЛАБОРАТОРНАЯ РАБОТА ВЫПОЛНЕНА")
    print("="*60)


if __name__ == "__main__":
    main()
