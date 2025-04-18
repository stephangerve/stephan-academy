import mysql.connector
import Config




class DBInterface():
    cnx = None



    def __init__(self,):
        self.connectToDB()
        self.counter = 0
#☺
    def connectToDB(self) -> mysql.connector.connect:
        self.cnx = mysql.connector.connect(
            host=Config.HOSTNAME,
            user=Config.USERNAME,
            database=Config.DATABASENAME,
            password=Config.PASSWORD
        )
        print("Connected to DB.")

    def fetchBool(self, table_name, parameters):
        query_string = self.getQueryString("Check", table_name, parameters)
        cursor = self.executeQuery(query_string, [], modifying=False)
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

    def updateEntry(self, table_name, parameters):
        query_string = self.getQueryString("Update", table_name, parameters)
        print(query_string)
        self.executeQuery(query_string, parameters, modifying=True)

    def insertEntry(self, table_name, parameters):
        query_string = self.getQueryString("Insert", table_name, parameters)
        self.executeQuery(query_string, parameters, modifying=True)

    def deleteEntry(self, table_name, parameters):
        query_string = self.getQueryString("Delete", table_name, parameters)
        self.executeQuery(query_string, parameters, modifying=True)

    def fetchColumnNames(self, table_name, parameters):
        query_string = self.getQueryString("Fetch", table_name, parameters)
        cursor = self.executeQuery(query_string, parameters, modifying=False)
        column_names = list(cursor.column_names)
        cursor.fetchall()
        return column_names

    def fetchEntries(self, table_name, parameters):
        query_string = self.getQueryString("Fetch", table_name, parameters)
        cursor = self.executeQuery(query_string, parameters, modifying=False)
        entries = self.convertToDict(cursor.column_names, cursor.fetchall())
        return entries

    def convertToDict(self, column_names, entries):
        column_names = list(column_names)
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
            elif table_name == "Textbook Info":
                query = (
                    "SELECT * "
                    "FROM Textbooks "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                )
            elif table_name == "Sections":
                query = (
                    "SELECT * "
                    "FROM sections "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "ORDER BY CAST(ChapterNumber as unsigned), SectionNumber "
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
            elif table_name == "Textbook Exercises":
                query = (
                    "SELECT * "
                    "FROM exercises "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                )
            elif table_name == "Study Lists":
                query = (
                        "SELECT * "
                        "FROM study_lists "
                )
            elif table_name == "Study List Collection":
                query = (
                    "SELECT * "
                    "FROM study_list_collections "
                    "WHERE CollectionID = " + parameters[0] + " "
                )
            elif table_name == "Study List Collections":
                query = (
                    "SELECT * "
                    "FROM study_list_collections "
                )
            elif table_name == "Section Grade Counts":
                query = (
                    "SELECT "
                    "COUNT(CASE WHEN Grade = 'A' AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' THEN 1 ELSE NULL END) as NumExercisesA, "
                    "COUNT(CASE WHEN Grade = 'B' AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' THEN 1 ELSE NULL END) as NumExercisesB, "
                    "COUNT(CASE WHEN Grade = 'C' AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' THEN 1 ELSE NULL END) as NumExercisesC, "
                    "COUNT(CASE WHEN Grade = 'D' AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' THEN 1 ELSE NULL END) as NumExercisesD, "
                    "COUNT(CASE WHEN Grade = 'F' AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' THEN 1 ELSE NULL END) as NumExercisesF, "
                    "COUNT(CASE WHEN Attempts = 0 AND TextbookID = '" + parameters[0] + "' AND ChapterNumber = '" + parameters[1] + "' AND SectionNumber = '" + parameters[2] + "' AND SolutionExists = 'True' THEN 1 ELSE NULL END) as NoGrade "
                    "FROM exercises"
                )
            elif table_name == "All Study List Exercises":
                query = (
                        "SELECT * "
                        "FROM exercises "
                        "WHERE Tags != '' "
                        "AND Tags != 'None' "
                        "AND Tags IS NOT NULL"
                )
            elif table_name == "Flashcard Collections":
                query = (
                    "SELECT * "
                    "FROM flashcard_collections "
                )
            elif table_name == "Flashcard Sets":
                query = (
                    "SELECT * "
                    "FROM flashcard_sets "
                    "WHERE CollectionID = '" + parameters[0] + "' "
                    "ORDER BY CAST(ChapterNumber as unsigned), SectionNumber "
                )
            elif table_name == "Flashcards":
                query = (
                    "SELECT * "
                    "FROM flashcards "
                    "WHERE CollectionID = '" + parameters[0] + "' "
                    "AND SetID = '" + parameters[1] + "' "
                )
        elif operation == "Update":
            if table_name == "Update Exercise Tag":
                query = (
                    "UPDATE exercises "
                    "SET Tags = '" + parameters[0] + "' "
                    "WHERE TextbookID = '" + parameters[1] + "' "
                    "AND ExerciseID = '" + parameters[2] + "'"
                )
            if table_name == "Update SL Collection Tags":
                query = (
                        "UPDATE study_list_collections "
                        "SET Tags = '" + parameters[0] + "' "
                        "WHERE CollectionID = '" + parameters[1] + "' "
                )
            elif table_name == "AllExercisesExtracted":
                query = (
                        "Update sections "
                        "SET AllExercisesExtracted = 'True' "
                        "WHERE TextbookID = '" + parameters[0] + "' "
                        "AND ChapterNumber = '" + parameters[1] + "' "
                        "AND SectionNumber = '" + parameters[2] + "'"
                )
            elif table_name == "AllSolutionsExtracted":
                query = (
                        "Update sections "
                        "SET AllSolutionsExtracted = 'True' "
                        "WHERE TextbookID = '" + parameters[0] + "' "
                        "AND ChapterNumber = '" + parameters[1] + "' "
                        "AND SectionNumber = '" + parameters[2] + "'"
                )
            elif table_name == "Solution Path For Exercise":
                query = (
                        "UPDATE exercises "
                        "SET SolutionExists = '" + parameters[0] + "',"
                        "    SolutionPath = '" + parameters[1] + "' "
                        "WHERE TextbookID = '" + parameters[2] + "' "
                        "AND ExerciseID = '" + parameters[3] + "'"
                )
            elif table_name == "Exercise":
                if parameters[4] is not None and parameters[4] != 'None':
                    query = (
                        "UPDATE exercises "
                        "SET Seen = '" + parameters[0] + "', "
                        "Attempts = " + str(parameters[1]) + ", "
                        "LastAttempted = '" + parameters[2] + "', "
                        "LastAttemptTime = '" + parameters[3] + "', "
                        "Grade = '" + parameters[4] + "', "
                        "AverageTime = " + str(parameters[5]) + " "
                        "WHERE TextbookID = '" + parameters[6] + "' "
                        "AND ExerciseID = '" + parameters[7] + "' "
                    )
                else:
                    query = (
                            "UPDATE exercises "
                            "SET Seen = '" + parameters[0] + "' "
                            "WHERE TextbookID = '" + parameters[6] + "' "
                            "AND ExerciseID = '" + parameters[7] + "' "
                    )
            elif table_name == "Flashcard":
                if parameters[4] is not None and parameters[4] != 'None':
                    query = (
                        "UPDATE flashcards "
                        "SET Seen = '" + parameters[0] + "', "
                        "Attempts = " + str(parameters[1]) + ", "
                        "LastAttempted = '" + parameters[2] + "', "
                        "LastAttemptTime = '" + parameters[3] + "', "
                        "Grade = '" + parameters[4] + "', "
                        "AverageTime = " + str(parameters[5]) + " "
                        "WHERE CollectionID = '" + parameters[6] + "' "
                        "AND SetID = '" + parameters[7] + "' "
                        "AND FlashcardNumber = '" + parameters[8] + "' "
                    )
                else:
                    query = (
                            "UPDATE flashcards "
                            "SET Seen = '" + parameters[0] + "' "
                            "WHERE CollectionID = '" + parameters[6] + "' "
                            "AND SetID = '" + parameters[7] + "' "
                            "AND FlashcardNumber = '" + parameters[8] + "' "
                    )
        elif operation == "Insert":
            if table_name == "Study List Collection":
                query = (
                    "INSERT INTO study_list_collections "
                    "(CollectionID, CollectionName, Tags)"
                    "VALUES (%s, %s, %s)"
                )
            elif table_name == "Flashcard Collection":
                query = (
                    "INSERT INTO flashcard_collections "
                    "(CollectionID, TextbookID, CreationDate) "
                    "VALUES (%s, %s, %s)"
                )
            elif table_name == "Flashcard Set":
                query = (
                    "INSERT INTO flashcard_sets "
                    "(CollectionID, SetID, ChapterNumber, SectionNumber, CreationDate)"
                    "VALUES (%s, %s, %s, %s, %s)"
                )
            elif table_name == "New Flashcard":
                query = (
                    "INSERT INTO flashcards "
                    "(CollectionID, SetID, FlashcardNumber, CreationDate, LastEdited, Seen, Attempts, LastAttempted, LastAttemptTime, Grade, AverageTime, NextAttemptDate)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
            elif table_name == "New Exercise":
                query = (
                    "INSERT INTO exercises "
                    "(TextbookID, ExerciseID, ChapterNumber, SectionNumber, ExerciseNumber, SolutionExists, Seen, Attempts, LastAttempted, LastAttemptTime, Grade, AverageTime, Tags, UnmaskedExercisePath, MaskedExercisePath, SolutionPath) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
            elif table_name == "Textbooks":
                query = (
                    "INSERT INTO textbooks "
                    "(TextbookID, Category, Authors, Title, Edition, NumberOfSections, NumberOfSectionsCompleted, NumberOfChapters, NumberOfExercises, NumberOfSolutions) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
            elif table_name == "Section":
                query = (
                    "INSERT INTO sections "
                    "(TextbookID, ChapterNumber, SectionNumber, NumberOfExercises, NumberOfSolutions, AllExercisesExtracted, AllSolutionsExtracted, ChapterTitle, SectionTitle, Tags) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
            elif table_name == "Study List":
                query = (
                    "INSERT INTO study_lists "
                    "(StudyListID, StudyListName, CreationDate) "
                    "VALUES (%s, %s, %s)"
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
            elif table_name == "SolutionExists":
                query = (
                    "SELECT SolutionExists "
                    "FROM exercises "
                    "WHERE TextbookID = '" + parameters[0] + "' "
                    "AND ExerciseID = '" + parameters[1] + "' "
                )
        elif operation == "Delete":
            if table_name == "Study List":
                query = (
                    "DELETE "    
                    "FROM study_lists "
                    "WHERE StudyListID = '" + parameters[0] + "' "
                )
        return query

    def executeQuery(self, query_string, parameters, modifying):
        try:
            cursor = self.cnx.cursor()
            if type(parameters) is tuple:
                cursor.execute(query_string, parameters)
            else:
                cursor.execute(query_string)
            if modifying:
                self.cnx.commit()
        except mysql.connector.Error as err:
            self.counter += 1
            if self.counter < 5:
                if err.msg == "MySQL Connection not available":
                    print("Reconnecting to DB...")
                    self.connectToDB()
                    return self.executeQuery(query_string, parameters, modifying)
                else:
                    raise err
            else:
                raise err
        else:
            self.counter = 0
            return cursor




