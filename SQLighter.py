import sqlite3

class SQLighter:
    
    def __init__(self, database) :        
        try:
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()

        except sqlite3.Error as error:
            print('Error', error)

    def select_all_members(self):
        """Повертаєм всіх мемберів """
        with self.connection:            
            return self.cursor.execute("SELECT * FROM 'members' WHERE 'deleted' = 0").fetchall()    
        
    def select_all_projects(self):
        """Повертаєм всі проєкти"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'projects'").fetchall()
        
    def select_members_to_projects(self):
        """Повертаєм зв'язки мемберів до проєктів"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'members_to_projects'").fetchall()        

        
    def add_member(self, login, password,telegram_username):
        """ Додаєм мембера в базу"""
        with self.connection: 
            self.cursor.execute("INSERT INTO 'members' ('login','password','telegram_username') VALUES (?,?,?)",
                                                        (login, password, telegram_username))
            return self.connection.commit()
        
    def delete_member_with_telegram_username(self, t_username):
        """ Видаляєм мемебра з заданим login"""
        with self.connection:
            self.cursor.execute("UPDATE 'members' SET deleted = 1 WHERE t_username = ?", (t_username,))
            return self.connection.commit()        

    def close(self):
        """ Закриваємо поточне з'єднання  БД """
        self.connection.close()
    
