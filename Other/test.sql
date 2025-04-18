SELECT
COUNT(CASE WHEN Grade = 'A' AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NumExercisesA,
COUNT(CASE WHEN Grade = 'B' AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NumExercisesB,
COUNT(CASE WHEN Grade = 'C' AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NumExercisesC,
COUNT(CASE WHEN Grade = 'D' AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NumExercisesD,
COUNT(CASE WHEN Grade = 'F' AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NumExercisesF,
COUNT(CASE WHEN Attempts = 0 AND TextbookID = 'otcqn' AND ChapterNumber = 6 AND SectionNumber = 2 THEN 1 ELSE NULL END) as NoGrade
FROM exercises