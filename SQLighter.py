import sqlite3

class SQLighter:
    
    def __init__(self, database) :        
        try:
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()

        except sqlite3.Error as error:
            print('Error', error)


    def select_all_members(self):
        """ Отримуєм всіх мемберів """
        with self.connection:            
            return self.cursor.execute("SELECT * FROM 'members' WHERE 'deleted' = 0").fetchall()    

    def get_member_id_by_telegram_username(self, t_username):
        """ Дістаєм id юзера в базі за його telegram_username"""
        with self.connection: 
            result = self.cursor.execute("SELECT 'id' FROM 'members' WHERE 'deleted' = 0 AND 't_username' = ?", (t_username,))
            return result.fetchone()[0]
        
    def login_exist(self, login):
        """ Перевіряє чи існує користувач у базі з login
        Returns: 
            True - користувач існує
            False - користувач НЕ існує"""    
        
        result = self.cursor.execute("SELECT 'id' FROM 'members' WHERE 'deleted' = 0 AND'login' = ?", (login,))
        return result.fetchone() is not None
    
    def get_password_for_login(self, login):
        """ Повертаєм пароль для login"""
        with self.connection: 
            result = self.cursor.execute("SELECT 'password' FROM 'members' WHERE 'deleted' = 0 AND'login' = ?", (login,))
            return result.fetchone()[0]
        
    def add_member(self, login, password, first_name, surname, patronymic, t_username):
        """ Додаєм мембера в базу"""
        with self.connection: 
            self.cursor.execute("INSERT INTO 'members' ('login','password','first_name','surname','patronymic','t_username') VALUES (?,?,?,?,?,?)",
                                                        (login, password, first_name, surname, patronymic, t_username))
            return self.connection.commit()
        
    def delete_member_with_telegram_username(self, t_username):
        """ Видаляєм мемебра з заданим login"""
        with self.connection:
            self.cursor.execute("UPDATE 'members' SET deleted = 1 WHERE t_username = ?", (t_username,))
            return self.connection.commit()

    def count_members(self):
        """ Рахуємо кількість мемберів """
        with self.connection:           
            return self.cursor.execute("SELECT COUNT(*) FROM 'members'").fetchall()
        

    def close(self):
        """ Закриваємо поточне з'єднання  БД """
        self.connection.close()
    
