import pygame
import os
import sys
from pygame.locals import *
import time

# Константы
ШИРИНА, ВЫСОТА = 1000, 1000
РАЗМЕР_ДОСКИ = 8
РАЗМЕР_КЛЕТКИ = ШИРИНА // РАЗМЕР_ДОСКИ
ЧАСТОТА_КАДРОВ = 60
ЦВЕТ_ВЫДЕЛЕНИЯ = (177, 167, 252, 150)  # Цвет выделения с прозрачностью
ЦВЕТ_ВОЗМОЖНЫХ_ХОДОВ = (177, 167, 252, 150)    # Цвет возможных ходов

# Цвета клеток
ЦВЕТ_СВЕТЛОЙ_КЛЕТКИ = (232, 237, 249)
ЦВЕТ_ТЕМНОЙ_КЛЕТКИ = (183, 192, 216)

# Инициализация Pygame
pygame.init()
экран = pygame.display.set_mode((ШИРИНА, ВЫСОТА))
pygame.display.set_caption("Ghhs-chess")
часы = pygame.time.Clock()

# Цвета
БЕЛЫЙ = (255, 255, 255)
ЧЕРНЫЙ = (0, 0, 0)
КРАСНЫЙ = (255, 0, 0)
ЗЕЛЕНЫЙ = (0, 255, 0)

class ChessGame:
    def __init__(self):
        self.board = self.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.selected_piece = None
        self.valid_moves = []
        self.current_player = 'white'
        self.game_over = False
        self.winner = None # победитель
        self.vs_computer = False

        # Таймеры
        self.white_time = 180  # 3 минуты в секундах
        self.black_time = 180
        self.start_time = time.time()

        self.load_images()
        self.font = pygame.font.SysFont('Calibri', 30)  # Шрифт для таймера
        self.large_font = pygame.font.SysFont('Calibri', 60) # шрифт для объявление победителя
        self.coord_font = pygame.font.SysFont('Calibri', 20)  # шрифт для координат

    def load_images(self):
        """Загружает изображения фигур"""
        self.piece_images = {}
        pieces = {
            'white_pawn': 'assets/White_Pawn.png',
            'white_rook': 'assets/White_rook.png',
            'white_knight': 'assets/White_Knight.png',
            'white_bishop': 'assets/White_Bishop.png',
            'white_queen': 'assets/White_Queen.png',
            'white_king': 'assets/White_King.png',
            'black_pawn': 'assets/Black_Pawn.png',
            'black_rook': 'assets/Black_Rook.png',
            'black_knight': 'assets/Black_Knight.png',
            'black_bishop': 'assets/Black_Bishop.png',
            'black_queen': 'assets/Black_Queen.png',
            'black_king': 'assets/Black_King.png'
        }
        
        for piece, filename in pieces.items():
            try:
                path = os.path.join(r"", filename)
                image = pygame.image.load(path)
                self.piece_images[piece] = pygame.transform.scale(image, (РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ))
            except:
                print(f"Не удалось загрузить {filename}")
                # Заглушка для отсутствующих изображений
                surf = pygame.Surface((РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ))
                surf.fill((255, 0, 0) if 'white' in piece else (0, 0, 255))
                self.piece_images[piece] = surf

    def fen_to_board(self, fen):
        """Преобразует FEN в доску"""
        board = [[None for _ in range(8)] for _ in range(8)]
        parts = fen.split()
        rows = parts[0].split('/')
        
        piece_map = {
            'p': 'black_pawn', 'r': 'black_rook', 'n': 'black_knight',
            'b': 'black_bishop', 'q': 'black_queen', 'k': 'black_king',
            'P': 'white_pawn', 'R': 'white_rook', 'N': 'white_knight',
            'B': 'white_bishop', 'Q': 'white_queen', 'K': 'white_king'
        }
        
        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    board[row_idx][col_idx] = piece_map[char]
                    col_idx += 1
        return board

    def draw_board(self):
        """Рисует доску и фигуры"""
        # Рисуем клетки
        for row in range(8):
            for col in range(8):
                color = ЦВЕТ_СВЕТЛОЙ_КЛЕТКИ if (row + col) % 2 == 0 else ЦВЕТ_ТЕМНОЙ_КЛЕТКИ
                pygame.draw.rect(экран, color, (col*РАЗМЕР_КЛЕТКИ, row*РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ))

                # Рисуем координаты
                if row == 7: # Нижняя строка (буквы)
                    letter = chr(ord('a') + col) # Преобразуем номер столбца в букву
                    text_surface = self.coord_font.render(letter, True, ЧЕРНЫЙ if (row + col) % 2 == 0 else БЕЛЫЙ)
                    text_rect = text_surface.get_rect(bottomright=( (col + 1) * РАЗМЕР_КЛЕТКИ - 5, (row + 1) * РАЗМЕР_КЛЕТКИ - 5))
                    экран.blit(text_surface, text_rect)

                if col == 0: # Левый столбец (цифры)
                    number = str(8 - row) # Преобразуем номер строки в цифру (обратный порядок)
                    text_surface = self.coord_font.render(number, True, ЧЕРНЫЙ if (row + col) % 2 == 0 else БЕЛЫЙ)
                    text_rect = text_surface.get_rect(bottomleft=(col * РАЗМЕР_КЛЕТКИ + 5, (row + 1) * РАЗМЕР_КЛЕТКИ - 5))
                    экран.blit(text_surface, text_rect)
        
        # Подсветка возможных ходов
        if self.selected_piece:
            row, col = self.selected_piece
            s = pygame.Surface((РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ), pygame.SRCALPHA)
            s.fill(ЦВЕТ_ВЫДЕЛЕНИЯ)
            экран.blit(s, (col*РАЗМЕР_КЛЕТКИ, row*РАЗМЕР_КЛЕТКИ))
            
            for move in self.valid_moves:
                s = pygame.Surface((РАЗМЕР_КЛЕТКИ, РАЗМЕР_КЛЕТКИ), pygame.SRCALPHA)
                s.fill(ЦВЕТ_ВОЗМОЖНЫХ_ХОДОВ)
                экран.blit(s, (move[1]*РАЗМЕР_КЛЕТКИ, move[0]*РАЗМЕР_КЛЕТКИ))
        
        # Рисуем фигуры
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    экран.blit(self.piece_images[piece], (col*РАЗМЕР_КЛЕТКИ, row*РАЗМЕР_КЛЕТКИ))
    
    def draw_timer(self):
       # Рамка для таймеров
        pygame.draw.rect(экран, ЧЕРНЫЙ, (5, ВЫСОТА - 310, 200, 50), 2)  # Рамка для белого таймера
        pygame.draw.rect(экран, ЧЕРНЫЙ, (ШИРИНА - 205, ВЫСОТА - 310, 200, 50), 2)  # Рамка для черного таймера
        """Отображает таймеры для игроков"""
        white_time_str = time.strftime("%M:%S", time.gmtime(self.white_time))
        black_time_str = time.strftime("%M:%S", time.gmtime(self.black_time))

        white_text = self.font.render(f"White: {white_time_str}", True, ЧЕРНЫЙ)
        black_text = self.font.render(f"Black: {black_time_str}", True, ЧЕРНЫЙ)

        экран.blit(white_text, (10, ВЫСОТА - 300))  # Позиция для белого таймера
        экран.blit(black_text, (ШИРИНА - black_text.get_width() - 10, ВЫСОТА - 300))  # Позиция для черного таймера
    
    def update_timer(self):
        """Обновляет таймеры игроков"""
        if not self.game_over:
            elapsed_time = time.time() - self.start_time
            self.start_time = time.time()  # Сбрасываем время

            if self.current_player == 'white':
                self.white_time -= elapsed_time
                if self.white_time <= 0:
                    self.white_time = 0
                    self.game_over = True
                    self.winner = 'black'
                    print("Black wins on time!")
            else:
                self.black_time -= elapsed_time
                if self.black_time <= 0:
                    self.black_time = 0
                    self.game_over = True
                    self.winner = 'white'
                    print("White wins on time!")
            self.white_time = max(0, self.white_time)
            self.black_time = max(0, self.black_time)

    def get_valid_moves(self, row, col):
       """Возвращает допустимые ходы для фигуры, исключая те, после которых король под шахом."""
       piece = self.board[row][col]
       if not piece or not piece.startswith(self.current_player):
           return []

       moves = []
       piece_type = piece.split('_')[1]

       if piece_type == 'pawn':
           moves = self.get_pawn_moves(row, col)
       elif piece_type == 'rook':
           moves = self.get_rook_moves(row, col)
       elif piece_type == 'knight':
           moves = self.get_knight_moves(row, col)
       elif piece_type == 'bishop':
           moves = self.get_bishop_moves(row, col)
       elif piece_type == 'queen':
           moves = self.get_queen_moves(row, col)
       elif piece_type == 'king':
           moves = self.get_king_moves(row, col)

       real_moves = []
       for move in moves:
           # Имитируем ход
           temp_board = [r[:] for r in self.board]  # Создаем копию доски
           temp_board[move[0]][move[1]] = temp_board[row][col]  # Перемещаем фигуру
           temp_board[row][col] = None  # Освобождаем исходную клетку

           # Проверяем, не под шахом ли свой король после хода
           if not self.is_king_in_check(self.current_player, temp_board):
               real_moves.append(move)

       return real_moves

    def get_pawn_moves(self, row, col):
        """Возвращает допустимые ходы для пешки"""
        moves = []
        direction = -1 if self.current_player == 'white' else 1

        # Ход на 1 вперед
        if 0 <= row + direction < 8 and not self.board[row + direction][col]:
            moves.append((row + direction, col))

            # Ход на 2 вперед из начальной позиции
            if (row == 6 and self.current_player == 'white') or (row == 1 and self.current_player == 'black'):
                if not self.board[row + 2 * direction][col] and not self.board[row + direction][col]:
                    moves.append((row + 2 * direction, col))

        # Взятие
        for dc in [-1, 1]:
            if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                target = self.board[row + direction][col + dc]
                if target and target.startswith('black' if self.current_player == 'white' else 'white'):
                    moves.append((row + direction, col + dc))

        return moves

    def get_rook_moves(self, row, col):
        """Возвращает допустимые ходы для ладьи"""
        moves = []
        # Проверка по горизонтали и вертикали
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.startswith('black' if self.current_player == 'white' else 'white'):
                        moves.append((new_row, new_col))
                        break  # Останавливаемся после взятия фигуры
                    else:
                        break  # Упираемся в свою фигуру
                else:
                    break  # Выход за пределы доски
        return moves

    def get_knight_moves(self, row, col):
        """Возвращает допустимые ходы для коня"""
        moves = []
        # Возможные смещения для коня
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target is None or target.startswith('black' if self.current_player == 'white' else 'white'):
                    moves.append((new_row, new_col))
        return moves

    def get_bishop_moves(self, row, col):
        """Возвращает допустимые ходы для слона"""
        moves = []
        # Проверка по диагоналям
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.startswith('black' if self.current_player == 'white' else 'white'):
                        moves.append((new_row, new_col))
                        break  # Останавливаемся после взятия фигуры
                    else:
                        break  # Упираемся в свою фигуру
                else:
                    break  # Выход за пределы доски
        return moves

    def get_queen_moves(self, row, col):
        """Возвращает допустимые ходы для ферзя"""
        # Ферзь объединяет ходы ладьи и слона
        rook_moves = self.get_rook_moves(row, col)
        bishop_moves = self.get_bishop_moves(row, col)
        return rook_moves + bishop_moves

    def get_king_moves(self, row, col):
        """Возвращает допустимые ходы для короля"""
        moves = []
        # Возможные смещения для короля
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),         (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in king_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target is None or target.startswith('black' if self.current_player == 'white' else 'white'):
                    moves.append((new_row, new_col))
        return moves

    def handle_click(self, row, col):
        """Обрабатывает клик на доске"""
        if self.game_over:
            return
    
        # Если фигура уже выбрана, пытаемся сделать ход
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                self.make_move(self.selected_piece, (row, col))
                self.selected_piece = None
                self.valid_moves = []
                self.switch_player()
                self.start_time = time.time()  # Сбрасываем таймер после хода
                
                if self.is_checkmate(self.current_player):
                    self.game_over = True
                    self.winner = 'white' if self.current_player == 'black' else 'black'
                    print(f"{'Белые' if self.current_player == 'black' else 'Черные'} выиграли матом!")
                elif self.is_stalemate(self.current_player):
                    self.game_over = True
                    print("Пат!")
                elif self.is_king_in_check(self.current_player):
                    print("Шах!")
        
                if self.vs_computer and self.current_player == 'black':
                    self.computer_move()
            elif self.board[row][col] and self.board[row][col].startswith(self.current_player):
                # Выбрали другую свою фигуру
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
            else:
                # Клик на пустую клетку или чужую фигуру
                self.selected_piece = None
                self.valid_moves = []
        else:
            # Выбираем фигуру
            if self.board[row][col] and self.board[row][col].startswith(self.current_player):
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)

    def make_move(self, start, end):
        """Выполняет ход"""
        start_row, start_col = start
        end_row, end_col = end
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = None

    def switch_player(self):
        """Меняет текущего игрока"""
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.start_time = time.time() # Сбрасываем таймер

    def computer_move(self):
        """Простой ИИ для игры против компьютера"""
        # Находим все возможные ходы
        all_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith('black'):
                    moves = self.get_valid_moves(row, col)
                    for move in moves:
                        all_moves.append(((row, col), move))
    
        # Выбираем случайный ход
        if all_moves:
            import random
            start, end = random.choice(all_moves)
            self.make_move(start, end)
            self.switch_player()

            if self.is_checkmate(self.current_player):
                self.game_over = True
                self.winner = 'white' if self.current_player == 'black' else 'black'
                print(f"{'Белые' if self.current_player == 'black' else 'Черные'} выиграли матом!")
            elif self.is_stalemate(self.current_player):
                self.game_over = True
                print("Пат!")
            elif self.is_king_in_check(self.current_player):
                print("Шах!")

    def is_king_in_check(self, player, board=None):
        """Проверяет, находится ли король под шахом."""
        if board is None:
            board = self.board

        # Находим позицию короля
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == f'{player}_king':
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # Король не найден

        # Проверяем каждую вражескую фигуру, может ли она атаковать короля
        opponent = 'black' if player == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.startswith(opponent):
                    # !!! Ключевое изменение: Передаем opponent, чтобы получить ходы атакующей стороны
                    moves = self.get_valid_moves(row, col)
                    if king_pos in moves:
                        return True  # Король под шахом

        return False

    def is_checkmate(self, player):
        """Проверяет, есть ли мат"""
        if not self.is_king_in_check(player):
            return False  # Нет шаха - нет мата
    
        # Проверяем, есть ли хоть один ход, чтобы спасти короля
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith(player):
                    moves = self.get_valid_moves(row, col)
                    if moves: # проверяем что ходы вообще есть
                      for move in moves:
                          # Имитируем ход
                          temp_board = [r[:] for r in self.board]
                          temp_board[move[0]][move[1]] = temp_board[row][col]
                          temp_board[row][col] = None
                          # Если после хода нет шаха, это не мат
                          if not self.is_king_in_check(player, temp_board):
                              return False
        return True  # Ходов нет, это мат

    def is_stalemate(self, player):
        """Проверяет, есть ли пат"""
        if self.is_king_in_check(player):
            return False # Если есть шах, то это не пат
        
        # Проверяем, есть ли у игрока фигуры на доске
        has_pieces = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith(player):
                    has_pieces = True
                    break
            if has_pieces:
                break
        
        # Если у игрока нет фигур, это не пат, а проигрыш
        if not has_pieces:
            return False

        has_valid_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.startswith(player):
                    moves = self.get_valid_moves(row, col)
                    if len(moves) > 0:
                        has_valid_moves = True
                        break
            if has_valid_moves:
                break
        
        if has_valid_moves:
            return False # Если есть ходы, то это не пат
        else:
            return True # Если нет шаха и ходов, то это пат

    def draw_winner(self):
      """Отображает окно с объявлением победителя."""
      if self.winner:
          winner_text = self.large_font.render(f"{'Белые' if self.winner == 'white' else 'Черные'} выиграли!", True, ЗЕЛЕНЫЙ)
          text_rect = winner_text.get_rect(center=(ШИРИНА // 2, ВЫСОТА // 2))

          #Затемнение фона
          overlay = pygame.Surface((ШИРИНА, ВЫСОТА), pygame.SRCALPHA)
          overlay.fill((0, 0, 0, 150))  # Черный цвет с прозрачностью 150
          экран.blit(overlay, (0, 0))

          экран.blit(winner_text, text_rect)

    def handle_game_over(self):
      """Обрабатывает завершение игры, отображая победителя."""
      self.draw_winner()  # Отображаем сообщение о победе
      pygame.display.flip()  # Обновляем экран

      # Ждем, пока игрок не нажмет клавишу или закроет окно
      waiting = True
      while waiting:
          for event in pygame.event.get():
              if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                  pygame.quit()
                  sys.exit()
              elif event.type == pygame.KEYDOWN:
                  waiting = False  # Нажата клавиша, выходим из цикла ожидания и возвращаемся в меню
                  

def main_menu():
    """Главное меню для выбора режима игры"""
    game = None
    font = pygame.font.SysFont('Arial', 40)

    while True:
        экран.fill((50, 50, 50))

        title = font.render("Шахматы", True, (255, 255, 255))
        pvp = font.render("1 - Игра против друга", True, (255, 255, 255))
        pvc = font.render("2 - Игра против компьютера", True, (255, 255, 255))

        экран.blit(title, (ШИРИНА // 2 - title.get_width() // 2, 100))
        экран.blit(pvp, (ШИРИНА // 2 - pvp.get_width() // 2, 300))
        экран.blit(pvc, (ШИРИНА // 2 - pvc.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    game = ChessGame()
                    game.vs_computer = False
                    return game
                elif event.key == K_2:
                    game = ChessGame()
                    game.vs_computer = True
                    return game

def main():
    game = main_menu()
    if game is None:
        return

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    x, y = event.pos
                    col = x // РАЗМЕР_КЛЕТКИ
                    row = y // РАЗМЕР_КЛЕТКИ
                    game.handle_click(row, col)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Если игра закончена, возвращаемся в главное меню. Иначе ничего не делаем.
                    if game.game_over:
                        game = main_menu()
                        if game is None:
                            return
                    else:
                        # Пауза или подтверждение выхода
                        print("Игра приостановлена. Нажмите ESC еще раз для выхода в меню.")
                        waiting_for_esc = True
                        while waiting_for_esc:
                            for event2 in pygame.event.get():
                                if event2.type == KEYDOWN and event2.key == K_ESCAPE:
                                    game = main_menu()
                                    if game is None:
                                        return
                                    waiting_for_esc = False
                                elif event2.type == QUIT:
                                    pygame.quit()
                                    sys.exit()

        game.update_timer()
        экран.fill(ЧЕРНЫЙ)
        game.draw_board()
        game.draw_timer()

        if game.game_over:
           game.handle_game_over()
        
        pygame.display.flip()
        часы.tick(ЧАСТОТА_КАДРОВ)

if __name__ == "__main__":
    main()
