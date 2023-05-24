import mysql.connector
import Config




class DBInterface():
    cnx = None



    def __init__(self,):
        self.initUI()


    def initUI(self):
        self.cnx = mysql.connector.connect(
            host=Config.HOSTNAME,
            user=Config.USERNAME,
            database=Config.DATABASENAME,
            password=Config.PASSWORD
        )
    def fetchBool(self, table_name, parameters):
        query_string = self.getQueryString("Check", table_name, parameters)
        cursor = self.cnx.cursor()
        cursor.execute(query_string)
        entries = cursor.fetchall()
        if len(entries) == 0:
            return False
        else:
            if table_name == "SolutionExists":
                if entries[0][0] == None:
                    return False
                else:
                    return eval(entries[0][0])
            else:
                return True


    def insertEntry(self, table_name, parameters):
        query_string = self.getQueryString("Insert", table_name, parameters)
        cursor = self.cnx.cursor()
        cursor.execute(query_string, parameters[0])
        self.cnx.commit()
        pass
        pass

    def fetchColumnNames(self, table_name, parameters):
        query_string = self.getQueryString("Fetch", table_name, parameters)
        cursor = self.cnx.cursor()
        cursor.execute(query_string)
        column_names = list(cursor.column_names)
        column_names[0] = "ID"
        cursor.fetchall()
        return column_names

    def fetchEntries(self, table_name, parameters):
        query_string = self.getQueryString("Fetch", table_name, parameters)
        cursor = self.cnx.cursor()
        cursor.execute(query_string)
        entries = self.convertToDict(cursor.column_names, cursor.fetchall())
        return entries

    def convertToDict(self, column_names, entries):
        column_names = list(column_names)
        column_names[0] = "ID"
        return [dict(zip(column_names, entry)) for entry in entries]


    def getQueryString(self, operation, table_name, parameters):
        if operation == "Fetch":
            if table_name == "Categories":
                query = (
                    "SELECT * "
                    "FROM categories "
                )
            elif table_name == "Textbooks":
                query = (
                    "SELECT * "
                    "FROM Textbooks "
                    "WHERE Category = '" + parameters[0] + "' "
                    "ORDER BY Authors, Title, Edition "
                )
            elif table_name == "Sections":
                query = (
                    "SELECT ChapterNumber, SectionNumber, TextbookID "
                    "FROM sections "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "ORDER BY CAST(ChapterNumber as unsigned), CAST(SectionNumber as unsigned) "
                )
            elif table_name == "Exercises":
                query = (
                    "SELECT * "
                    "FROM exercises "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "AND ChapterNumber = '" + parameters[1] + "' "
                    "AND SectionNumber = '" + parameters[2] + "' "
                    "ORDER BY ExerciseID "
                )
            elif table_name == "ExerciseStats":
                query = (
                    "SELECT * "
                    "FROM exercisestatistics "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "AND ExerciseID IN (SELECT ExerciseID "
                    "FROM exercises "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "AND ChapterNumber = '" + parameters[1] + "' "
                    "AND SectionNumber = '" + parameters[2] + "') "
                )
        elif operation == "Insert":
            if table_name == "ExerciseStats":
                query = (
                    ""
                )
            elif table_name == "Textbooks":
                query = (
                    "INSERT INTO textbooks "
                    "(TextbookID, Category, Authors, Title, Edition, NumberOfSections, NumberOfSectionsCompleted, NumberOfChapters, NumberOfExercises, NumberOfSolutions)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
            elif table_name == "Section":
                query = (
                    "INSERT INTO sections "
                    "(TextbookID, ChapterNumber, SectionNumber, NumberOfExercises, NumberOfSolutions, AllExercisesExtracted, AllSolutionsExtracted, ChapterTitle, SectionTitle, Tags) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
        elif operation == "Check":
            if table_name == "Textbooks":
                query = (
                        "SELECT * "
                        "FROM Textbooks "
                        "WHERE Category = '" + parameters[0] + "' "
                        "AND Authors = '" + parameters[1] + "' "
                        "AND Title = '" + parameters[1] + "' "
                        "AND Edition = '" + parameters[2] + "' "
                )
            elif table_name == "Section Exist":
                query = (
                        "SELECT * "
                        "FROM sections "
                        "WHERE EXISTS(SELECT * FROM sections WHERE TextbookID = '" +
                        parameters[0] +
                        "' AND ChapterNumber = '" +
                        parameters[1] +
                        "' AND SectionNumber = '" +
                        parameters[2] +
                        "')"
                )
            elif table_name == "SolutionExist":
                query = (
                    "SELECT SolutionExists "
                    "FROM exercises "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "AND ExerciseID = '" + parameters[1] + "' "
                )

        return query
